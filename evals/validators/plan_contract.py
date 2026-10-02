"""Offline effective-contract checks; trusted inputs must be evaluator-owned.

Records contain provider URL, author, exact body, and semantic digest. Full-plan
bodies are already extracted semantic payloads under their approved convention;
amendments contain one JSON fence. The caller authenticates that normalization.
This does not establish live permissions, semantic compatibility or review quality.
"""
from __future__ import annotations

import hashlib
import json
import re


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _canonical_types(value):
    if value is None or type(value) in (str, bool, int):
        return True
    if isinstance(value, list):
        return all(_canonical_types(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _canonical_types(item) for key, item in value.items())
    return False


def _sha(value, length):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{" + str(length) + "}", value) is not None


def validate_effective_contract(packet, trusted):
    """Return failures for observed artifacts against separate trusted anchors."""
    try:
        if trusted["readback_complete"] is not True:
            return ["ambiguous or incomplete readback"]
        if type(packet.get("ready", False)) is not bool:
            return ["invalid readiness claim"]
        plan = packet["plan"]
        if type(plan["revision"]) is not int or plan["revision"] < 1 or not _sha(plan["digest"], 64):
            return ["invalid full-plan identity"]
        if plan.get("supersedes_effective") != trusted["previous_epoch"]:
            return ["previous amendment epoch not closed"]
        records = [plan, *packet["amendments"]]
        if len({r["url"] for r in records}) != len(records):
            return ["duplicate publication identity"]
        if {r["url"] for r in records} != set(trusted["bodies"]):
            return ["incomplete or unexpected publication history"]
        for record in records:
            if record["author"] != trusted["author"]:
                return ["foreign publication author"]
            if _digest(record["body"]) != trusted["bodies"].get(record["url"]):
                return ["missing trusted body anchor or foreign edit"]
        if {key: plan[key] for key in ("url", "digest", "revision")} != trusted["plan"]:
            return ["stale full-plan identity"]
        if _digest(plan["body"]) != plan["digest"]:
            return ["full-plan digest mismatch"]
        previous = {"url": plan["url"], "digest": plan["digest"]}
        base = trusted["initial_base"]
        payload = None
        for sequence, record in enumerate(packet["amendments"], 1):
            fences = re.findall(r"```json\n(.*?)\n```", record["body"], re.S)
            if len(fences) != 1 or record["body"].count("<!-- to-plan:integration-amendment:v1 -->") != 1:
                return ["ambiguous or unsupported amendment payload"]
            payload = json.loads(fences[0], object_pairs_hook=_unique_object)
            if not isinstance(payload, dict) or not _canonical_types(payload):
                return ["non-canonical amendment payload"]
            if type(payload["sequence"]) is not int:
                return ["invalid amendment sequence"]
            if not all(_sha(payload[key], 40) for key in ("old_base", "new_base", "candidate", "expected_head")):
                return ["invalid base/candidate SHA"]
            if payload["result_candidate"] is not None and not _sha(payload["result_candidate"], 40):
                return ["invalid resulting candidate SHA"]
            if payload["source"] != trusted["source"] or payload["plan"] != {
                "url": plan["url"], "digest": plan["digest"]
            }:
                return ["source/full-plan anchor mismatch"]
            for key in ("owner", "worktree", "branch", "pr"):
                if payload[key] != trusted[key]:
                    return [f"retained {key} mismatch"]
            if payload["old_base"] != base:
                return ["base continuity mismatch"]
            base = payload["new_base"]
            if payload["expected_head"] != payload["candidate"]:
                return ["candidate/PR head mismatch"]
            if payload["classification"] != "unchanged-scope":
                return ["material or unknown change is not an amendment"]
            if not isinstance(payload["rationale"], str) or not payload["rationale"].strip():
                return ["missing materiality rationale"]
            for key in ("overlap", "integration", "retained_work", "invalidated_evidence", "required_evidence"):
                values = payload[key]
                if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                    return [f"missing concrete {key}"]
            if sequence > 1:
                result = trusted.get("prior_results", {}).get(previous["url"])
                if result != {"effective": previous, "base": payload["old_base"], "candidate": payload["candidate"]}:
                    return ["missing or stale preceding integration result"]
            if payload["sequence"] != sequence or payload["previous"] != previous:
                return ["amendment sequence/predecessor mismatch"]
            if _digest(_canonical(payload)) != record["digest"]:
                return ["amendment digest mismatch"]
            previous = {"url": record["url"], "digest": _digest(_canonical({
                "previous": previous["digest"], "amendment": record["digest"]}))}
        if packet["effective"] != previous:
            return ["effective tip/digest mismatch"]
        result = packet["result"]
        head = payload["candidate"] if payload else trusted["head"]
        if result is not None:
            if payload is None or result != trusted["result"]:
                return ["untrusted integration result"]
            for key, expected in {
                "base": base, "effective": previous,
                "starting_candidate": payload["candidate"],
                "pr": trusted["pr"], "owner": trusted["owner"],
            }.items():
                if result[key] != expected:
                    return [f"integration result {key} mismatch"]
            head = result["candidate"]
            if not _sha(head, 40):
                return ["invalid result candidate SHA"]
            for key in ("checks", "review_coverage"):
                values = result[key]
                if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                    return ["missing final candidate evidence"]
        elif packet.get("ready", False):
            return ["pending integration result cannot claim ready"]
        if payload is not None and payload["result_candidate"] is not None:
            if result is None or payload["result_candidate"] != result["candidate"]:
                return ["existing result lacks exact provenance"]
        if base != trusted["base"] or head != trusted["head"]:
            return ["stale live base/candidate"]
        return []
    except (KeyError, TypeError, ValueError, IndexError, AttributeError, RecursionError):
        return ["malformed effective-contract packet"]
