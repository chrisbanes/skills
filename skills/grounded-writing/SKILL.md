---
name: grounded-writing
description: Use when drafting or reviewing public developer documentation, other text the user will publish or send, or a user-owned draft under an explicit editorial review, including review comments, replies, and internal technical reports.
---

# Grounded Writing

## Core principle

Make the reasoning visible at the scale the artifact supports. Build clear,
evidence-led writing in a conversational tone, then remove anything invented,
generic, or included only to imitate a personality.

## Procedure

1. Confirm that the text is for the user to publish or send, or that the user
   explicitly requested an editorial review of their own draft. Apply this
   style at any length for publication or sending, including one-sentence
   review comments and replies. For an internal report review, apply the truth
   and material-edit checks without imposing public-documentation style. Do
   not apply the skill to an ordinary assistant reply, quoted source text, or
   prose attributed to someone else.
2. Read [the style profile](references/style-profile.md) before drafting or
   revising.
3. Establish the audience, purpose, requested format, supplied facts, and
   the user's actual position. Preserve the requested artifact shape rather than
   turning every deliverable into a blog post.
4. In public developer documentation, explain the observable difference between
   settings and the practical trade-off in supported terms: what each gains and
   gives up, and when to choose each setting. For a publication review, name
   these as separate checks even when the draft lacks evidence to fill them in.
   In a review, explicitly recommend removing each implementation mechanic
   present in the draft that has no established reader-facing significance;
   merely identifying it as a mechanic leaves the edit ambiguous.
   If the draft lacks evidence for that choice,
   name the missing information instead of inferring it. Remove implementation,
   test, or diagnostic mechanics such as sampling thresholds, CPU masks, and
   interpolation details. Retain an observable transition or associated timing
   only when supplied or verified evidence shows it is part of the public
   contract or materially informs how to use or choose the setting. If a draft
   says one setting returns to another, preserve that observable transition
   conditionally while checking whether its timing is a public contract. Say
   that it returns to the other setting without carrying over a “cooldown” term
   or numeric delay unless that timing is verified as reader-facing behavior.
   Do not remove the return behavior merely because its implementation timing
   is unverified. Technical specificity alone does not establish public relevance.
   If relevance could
   change the recommendation but is unknown, flag it for verification rather
   than treating it as settled behavior. Describe retained effects in outcome
   terms and omit their implementation mechanics. Include a mechanic only when
   it is required for correct API use, necessary to distinguish a reader-facing
   setting choice, or explicitly requested. Do not ask to expand internal
   mechanics as a way to fill a public-documentation gap. Before drafting or
   revising public developer documentation, identify its public contracts and
   guarantees shared across alternatives, including compatibility expectations,
   and check that supported guarantees remain explicit in the result. If the
   source leaves a contract uncertain, verify it when research is in scope or
   flag the gap rather than silently dropping or inventing it. Retain the
   context needed to interpret claims. This boundary does not apply to internal
   design documents or technical reports.
5. Resolve missing material before writing:
   - Look up discoverable public facts when the task calls for research.
   - If a missing personal opinion or experience would materially change the
     text, ask the user and stop drafting that part.
   - If the gap is minor, use a conspicuous placeholder or state the uncertainty
     honestly. Never invent a first-person claim, result, preference, or memory.
6. Choose the register from the style profile. Match the length and formality to
   the destination; short working comments should remain short.
7. Shape the reasoning before polishing sentences. Prefer a concrete problem or
   observation, explain the mechanism, support it with evidence or an example,
   acknowledge the important limit, state the practical consequence, and end on
   the clearest remaining point. Omit any stage the artifact does not need. For
   a short comment, this may be only the actionable point and one supporting
   fact.
8. Use the user's default language and regional conventions unless the request
   specifies otherwise. Keep paragraphs focused, mix sentence lengths, use first
   person only when grounded, and make headings earn their place.
9. Edit once for style and once for truth. Remove generic scene-setting,
   marketing language, repeated conclusions, decorative catchphrases, and
   unsupported certainty. Treat the headline and opening claim as substantive:
   remove or qualify promotional framing that the supplied evidence does not
   directly support.
10. For a review that permits edits only for material clarity or truth problems,
   identify the exact claim that is false or the specific misreading that would
   prevent the document's intended use before touching the file. If neither is
   present, leave an adequate draft unchanged. Rewording an already usable
   instruction to make it more explicit is optional polish, not a material
   clarity fix. Do not turn an internal report into a rerun protocol: missing
   identifiers or reproducibility details justify an edit only when a stated
   claim or action depends on them. Do not add a placeholder for an unverified
   detail unless it blocks the draft's intended use. Explain the material facts,
   mechanism, and qualification that make a no-change result appropriate; a
   bare “no edit needed” does not show that the checks
   were completed.

## Finish gate

Finish only when all of these are true:

- The result still satisfies the requested format and purpose.
- For reader-facing setting documentation, a developer can tell what changes,
  what each setting gains and gives up, when to choose each, the public
  contract, including supported guarantees shared across options, and the
  meaningful limitation. Include transitions or timing only when evidence
  establishes their public or decision relevance; otherwise omit them with the
  implementation detail or flag material uncertainty. Keep implementation
  mechanics out unless they are required for correct API use, necessary to
  distinguish the setting choice, or explicitly requested. In a review, ask
  separately for the visible difference, the practical trade-off, and when to
  choose each setting; a request for a trade-off alone does not cover the
  visible difference. Explicitly recommend removing unsupported mechanics
  present in the draft.
- Every personal claim and substantive fact is supplied, verified, qualified,
  or clearly marked as missing.
- The argument is concrete enough to follow without promotional filler.
- Any caveat included changes the reader's understanding rather than acting as
  a disclaimer.
- Spelling and grammar follow the user's default language and regional
  conventions.
- The ending lands once and does not recap the whole piece.
- The prose sounds natural when read aloud, without an accumulation of borrowed
  phrases, rhetorical questions, asides, or emoji.

If a check fails, revise the draft. If the failure depends on an unknown personal
position, ask the user rather than smoothing over the gap.
