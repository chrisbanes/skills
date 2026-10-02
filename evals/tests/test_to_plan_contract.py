import copy
import hashlib
import json
import unittest
import tempfile
import subprocess
import shutil
import sys
from pathlib import Path

from evals.validators.plan_contract import validate_effective_contract


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def fixture():
    plan = {'url': 'https://example.test/issues/1#plan', 'author': 'runner',
            'body': 'Approved plan: preserve private receipt identities.', 'revision': 1}
    plan['digest'] = digest(plan['body'])
    source = {'url': 'https://example.test/issues/1', 'digest': '1' * 64}
    payload = {
        'source': source, 'plan': {'url': plan['url'], 'digest': plan['digest']},
        'sequence': 1, 'previous': {'url': plan['url'], 'digest': plan['digest']},
        'old_base': 'a' * 40, 'new_base': 'b' * 40, 'candidate': 'c' * 40,
        'expected_head': 'c' * 40, 'result_candidate': None,
        'owner': 'runner', 'worktree': '/task', 'branch': 'cb/task',
        'pr': 'https://example.test/pull/2', 'classification': 'unchanged-scope',
        'rationale': 'Same approved exclusions and receipt semantics.',
        'overlap': ['validator relocation'], 'integration': ['Use canonical validator'],
        'retained_work': ['receipt implementation at c'],
        'invalidated_evidence': ['old validator test at c'],
        'required_evidence': ['validator tests and interaction review at resulting head'],
    }
    body = '<!-- to-plan:integration-amendment:v1 -->\n```json\n' + canonical(payload) + '\n```\n'
    amendment = {'url': 'https://example.test/issues/1#amendment', 'author': 'runner',
                 'body': body, 'digest': digest(canonical(payload))}
    effective = digest(canonical({'previous': plan['digest'], 'amendment': amendment['digest']}))
    packet = {'plan': plan, 'amendments': [amendment],
              'effective': {'url': amendment['url'], 'digest': effective}, 'result': None}
    trusted = {
        'author': 'runner', 'plan': {'url': plan['url'], 'digest': plan['digest'], 'revision': 1},
        'source': source, 'initial_base': 'a' * 40, 'head': 'c' * 40, 'base': 'b' * 40,
        'owner': 'runner', 'worktree': '/task', 'branch': 'cb/task', 'pr': payload['pr'],
        'bodies': {plan['url']: digest(plan['body']), amendment['url']: digest(body)},
        'previous_epoch': None, 'result': None, 'readback_complete': True,
    }
    return packet, trusted


def replace_payload(packet, trusted, change, index=0):
    record = packet['amendments'][index]
    payload = json.loads(record['body'].split('```json\n')[1].split('\n```')[0])
    payload.update(change)
    record['body'] = '<!-- to-plan:integration-amendment:v1 -->\n```json\n' + canonical(payload) + '\n```\n'
    record['digest'] = digest(canonical(payload))
    trusted['bodies'][record['url']] = digest(record['body'])
    packet['effective'] = {'url': record['url'], 'digest': digest(canonical({
        'previous': payload['previous']['digest'], 'amendment': record['digest']}))}


class ContractTest(unittest.TestCase):
    def test_verified_amendment_accepts_pending_result_for_integration(self):
        packet, trusted = fixture()
        self.assertEqual([], validate_effective_contract(packet, trusted))

    def test_untrusted_edits_cannot_supply_their_own_anchors(self):
        packet, trusted = fixture()
        for target, field, value in [('plan', 'author', 'foreign'),
                                     ('amendment', 'author', 'foreign'),
                                     ('plan', 'body', 'Changed accepted contract'),
                                     ('amendment', 'body', 'Rewritten publication')]:
            with self.subTest(target=target, field=field):
                changed = copy.deepcopy(packet)
                record = changed['plan'] if target == 'plan' else changed['amendments'][0]
                record[field] = value
                if field == 'body':
                    record['digest'] = digest(record['body'])
                changed['trusted'] = {'author': 'foreign', 'bodies': {record['url']: digest(record['body'])}}
                self.assertTrue(validate_effective_contract(changed, trusted))
        missing = copy.deepcopy(trusted)
        missing['bodies'].clear()
        self.assertTrue(validate_effective_contract(packet, missing))

    def test_stale_live_identity_blocks_even_authenticated_payloads(self):
        packet, trusted = fixture()
        for field in ['source', 'initial_base', 'head', 'base', 'owner', 'worktree', 'branch', 'pr']:
            with self.subTest(field=field):
                changed = copy.deepcopy(trusted)
                changed[field] = {'url': 'elsewhere', 'digest': '2' * 64} if field == 'source' else 'different'
                self.assertTrue(validate_effective_contract(packet, changed), field)
        for change in [{'classification': 'unknown'}, {'classification': 'material'},
                       {'old_base': 'd' * 40}, {'expected_head': 'd' * 40},
                       {'plan': {'url': 'another', 'digest': '3' * 64}},
                       {'overlap': []}, {'integration': []}, {'required_evidence': []}]:
            with self.subTest(change=change):
                p, t = fixture()
                replace_payload(p, t, change)
                self.assertTrue(validate_effective_contract(p, t), change)

    def test_second_amendment_requires_verified_previous_result_and_full_history(self):
        packet, trusted = fixture()
        prior = copy.deepcopy(packet['effective'])
        second = copy.deepcopy(packet['amendments'][0])
        second['url'] += '-2'
        packet['amendments'].append(second)
        replace_payload(packet, trusted, {'sequence': 2, 'previous': prior,
                        'old_base': 'b' * 40, 'new_base': 'd' * 40,
                        'candidate': 'e' * 40, 'expected_head': 'e' * 40}, 1)
        trusted['base'], trusted['head'] = 'd' * 40, 'e' * 40
        self.assertTrue(validate_effective_contract(packet, trusted), 'unexecuted predecessor')
        trusted['prior_results'] = {prior['url']: {'effective': prior, 'base': 'b' * 40,
                                                'candidate': 'e' * 40, 'starting_candidate': 'c' * 40,
                                                'pr': trusted['pr'], 'owner': trusted['owner']}}
        incomplete = copy.deepcopy(trusted)
        for field in ['starting_candidate', 'pr', 'owner']:
            incomplete['prior_results'][prior['url']].pop(field)
        self.assertTrue(validate_effective_contract(packet, incomplete), 'unbound prior result')
        self.assertEqual([], validate_effective_contract(packet, trusted))
        for mutation in ['gap', 'fork', 'missing', 'stale-tip', 'unrelated-result', 'unrelated-start', 'unrelated-owner', 'unrelated-pr']:
            with self.subTest(mutation=mutation):
                p, t = copy.deepcopy(packet), copy.deepcopy(trusted)
                if mutation == 'gap':
                    replace_payload(p, t, {'sequence': 3}, 1)
                elif mutation == 'fork':
                    replace_payload(p, t, {'previous': {'url': p['plan']['url'], 'digest': p['plan']['digest']}}, 1)
                elif mutation == 'missing':
                    p['amendments'].pop(0)
                elif mutation == 'stale-tip':
                    p['amendments'].pop()
                    p['effective'] = prior
                    t['base'], t['head'] = 'b' * 40, 'c' * 40
                elif mutation == 'unrelated-result':
                    t['prior_results'][prior['url']]['candidate'] = 'f' * 40
                else:
                    field = {'unrelated-start': 'starting_candidate', 'unrelated-owner': 'owner', 'unrelated-pr': 'pr'}[mutation]
                    t['prior_results'][prior['url']][field] = 'unrelated'
                self.assertTrue(validate_effective_contract(p, t))

    def test_ready_requires_trusted_exact_result_and_evidence(self):
        packet, trusted = fixture()
        packet['ready'] = True
        self.assertTrue(validate_effective_contract(packet, trusted), 'pending result cannot be ready')
        result = {'candidate': 'd' * 40, 'base': 'b' * 40,
                  'starting_candidate': 'c' * 40, 'effective': packet['effective'],
                  'pr': trusted['pr'], 'owner': trusted['owner'],
                  'checks': ['tests at d'], 'review_coverage': ['full candidate review at d']}
        packet['result'] = copy.deepcopy(result)
        self.assertTrue(validate_effective_contract(packet, trusted), 'self-authored result is not an anchor')
        trusted['result'] = copy.deepcopy(result)
        trusted['head'] = 'd' * 40
        self.assertEqual([], validate_effective_contract(packet, trusted))
        for field, value in [('candidate', 'e' * 40), ('base', 'e' * 40),
                             ('starting_candidate', 'e' * 40), ('checks', []),
                             ('review_coverage', []), ('effective', {'url': 'stale', 'digest': '0'*64})]:
            with self.subTest(field=field):
                p, t = copy.deepcopy(packet), copy.deepcopy(trusted)
                p['result'][field] = value
                # Trusted records may exist but must still bind the current contract.
                t['result'] = copy.deepcopy(p['result'])
                self.assertTrue(validate_effective_contract(p, t))
        p, t = fixture()
        replace_payload(p, t, {'result_candidate': 'd' * 40})
        self.assertTrue(validate_effective_contract(p, t), 'claimed existing result needs provenance')

    def test_new_full_plan_closes_prior_epoch_and_noop_is_stable(self):
        p, t = fixture()
        closed = copy.deepcopy(p['effective'])
        p['amendments'] = []
        p['plan']['revision'] = 2
        p['plan']['url'] += '-2'
        p['plan']['body'] = 'Replanned contract; closes previous effective tip.'
        p['plan']['digest'] = digest(p['plan']['body'])
        p['plan']['supersedes_effective'] = closed
        p['effective'] = {k: p['plan'][k] for k in ['url', 'digest']}
        t['plan'] = {k: p['plan'][k] for k in ['url', 'digest', 'revision']}
        t['bodies'] = {p['plan']['url']: digest(p['plan']['body'])}
        t['initial_base'] = t['base']
        t['previous_epoch'] = copy.deepcopy(closed)
        self.assertEqual([], validate_effective_contract(p, t))
        self.assertEqual([], validate_effective_contract(copy.deepcopy(p), t))
        p['plan']['supersedes_effective']['digest'] = '0' * 64
        self.assertTrue(validate_effective_contract(p, t))

    def test_ambiguous_or_malformed_packets_fail_closed(self):
        for malformed in [None, [], {}, {'plan': []}]:
            with self.subTest(malformed=malformed):
                self.assertTrue(validate_effective_contract(malformed, {}))
        p, t = fixture()
        t['readback_complete'] = False
        self.assertTrue(validate_effective_contract(p, t))
        for change in [{'sequence': True}, {'sequence': 1.0}, {'new_base': 'short'},
                       {'candidate': 'not-a-sha'}, {'unknown': 1.5}, {'result_candidate': 'pending'},
                       {'source': {'url': '', 'digest': '1' * 64}}]:
            with self.subTest(change=change):
                p, t = fixture()
                replace_payload(p, t, change)
                self.assertTrue(validate_effective_contract(p, t))
        for suffix in ['duplicate-key', 'second-fence', 'unsupported-marker']:
            p, t = fixture()
            record = p['amendments'][0]
            if suffix == 'duplicate-key':
                record['body'] = record['body'].replace('"sequence":1', '"sequence":1,"sequence":1')
            elif suffix == 'second-fence':
                record['body'] += '\n```json\n{}\n```'
            else:
                record['body'] = record['body'].replace('amendment:v1', 'amendment:v99')
            t['bodies'][record['url']] = digest(record['body'])
            self.assertTrue(validate_effective_contract(p, t), suffix)

    def test_cli_reads_trust_only_from_evaluator_case_directory(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            validators = temp / 'evals/validators'
            validators.mkdir(parents=True)
            for name in ['text_case.py', 'plan_contract.py']:
                shutil.copyfile(root / 'evals/validators' / name, validators / name)
            case = temp / 'evals/cases/contract-test'
            case.mkdir(parents=True)
            (case / 'expectations.json').write_text(json.dumps({'files': [], 'effective_contract': {
                'artifact': 'contract.json', 'trusted': 'trusted.json'}}))
            p, t = fixture()
            (case / 'trusted.json').write_text(json.dumps(t))
            workspace = temp / 'workspace'
            workspace.mkdir()
            (workspace / 'contract.json').write_text(json.dumps(p))
            command = [sys.executable, str(validators / 'text_case.py'), 'contract-test']
            self.assertEqual(0, subprocess.run(command, cwd=workspace, capture_output=True).returncode)
            p['amendments'][0]['author'] = 'foreign'
            (workspace / 'contract.json').write_text(json.dumps(p))
            (workspace / 'trusted.json').write_text(json.dumps({'author': 'foreign'}))
            result = subprocess.run(command, cwd=workspace, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('foreign publication author', result.stderr)
            (workspace / 'contract.json').write_text('{broken')
            self.assertNotEqual(0, subprocess.run(command, cwd=workspace, capture_output=True).returncode)

    def test_result_evidence_and_ready_flag_have_unambiguous_types(self):
        for value in ['false', 1, []]:
            p, t = fixture()
            p['ready'] = value
            self.assertTrue(validate_effective_contract(p, t), repr(value))
        p, t = fixture()
        result = {'candidate': 'd' * 40, 'base': 'b' * 40,
                  'starting_candidate': 'c' * 40, 'effective': p['effective'],
                  'pr': t['pr'], 'owner': t['owner'],
                  'checks': True, 'review_coverage': 'claimed'}
        p['result'], t['result'], t['head'] = copy.deepcopy(result), result, 'd' * 40
        self.assertTrue(validate_effective_contract(p, t))

    def test_prepared_case_packets_validate_against_separate_evaluator_anchors(self):
        cases = Path(__file__).resolve().parents[1] / 'cases'
        for kind in ['direct', 'novel']:
            case = cases / ('to-plan-integration-amendment-' + kind)
            p = json.loads((case / 'overlay/observations.json').read_text())['packet']
            t = json.loads((case / 'trusted.json').read_text())
            self.assertEqual([], validate_effective_contract(p, t), kind)
            p['amendments'][0]['body'] += 'foreign edit'
            self.assertTrue(validate_effective_contract(p, t))

    def test_preexisting_integration_pins_current_head_separately_from_start(self):
        p, t = fixture()
        replace_payload(p, t, {'expected_head': 'd' * 40, 'result_candidate': 'd' * 40})
        result = {'candidate': 'd' * 40, 'base': 'b' * 40,
                  'starting_candidate': 'c' * 40, 'effective': copy.deepcopy(p['effective']),
                  'pr': t['pr'], 'owner': t['owner'],
                  'checks': ['tests at d'], 'review_coverage': ['review at d']}
        p['result'], t['result'], t['head'] = copy.deepcopy(result), result, 'd' * 40
        self.assertEqual([], validate_effective_contract(p, t))
        t['head'] = 'e' * 40
        self.assertTrue(validate_effective_contract(p, t))
        t['head'] = 'd' * 40
        replace_payload(p, t, {'expected_head': 'c' * 40})
        p['result']['effective'] = copy.deepcopy(p['effective'])
        t['result'] = copy.deepcopy(p['result'])
        self.assertTrue(validate_effective_contract(p, t), 'historical head is not the preexisting current head')

    def test_mixed_amendment_versions_are_ambiguous_even_with_body_anchor(self):
        p, t = fixture()
        record = p['amendments'][0]
        record['body'] += '\n<!-- to-plan:integration-amendment:v99 -->'
        t['bodies'][record['url']] = digest(record['body'])
        self.assertTrue(validate_effective_contract(p, t))

    def test_v1_rejects_unknown_semantic_fields(self):
        for value in [1, 'new policy', None, {}]:
            p, t = fixture()
            replace_payload(p, t, {'unknown': value})
            self.assertTrue(validate_effective_contract(p, t))

    def test_restraint_case_checks_decisions_not_fixture_heading(self):
        root = Path(__file__).resolve().parents[2]
        case = 'to-plan-integration-amendment-negative'
        command = [sys.executable, str(root / 'evals/validators/text_case.py'), case]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / 'state.md').write_text('Immutable evaluation state')
            result = subprocess.run(command, cwd=workspace, capture_output=True)
            self.assertNotEqual(0, result.returncode, 'fixture alone is insufficient')
            (workspace / '.scratch').mkdir()
            routes = {'foreign': 'blocked', 'non_overlap': 'screened-baseline',
                      'identical': 'no-op', 'unknown': 'blocked',
                      'material': 'stakeholder-replan', 'stale': 'blocked',
                      'ambiguous_write': 'reconcile-before-retry'}
            artifact = workspace / '.scratch/assessment.json'
            artifact.write_text(json.dumps(routes))
            self.assertEqual(0, subprocess.run(command, cwd=workspace, capture_output=True).returncode)
            routes['material'] = 'amendment'
            artifact.write_text(json.dumps(routes))
            self.assertNotEqual(0, subprocess.run(command, cwd=workspace, capture_output=True).returncode)

    def test_prior_receipt_cannot_replace_a_predeclared_result(self):
        p, t = fixture()
        replace_payload(p, t, {'result_candidate': 'f' * 40, 'expected_head': 'f' * 40})
        prior = copy.deepcopy(p['effective'])
        second = copy.deepcopy(p['amendments'][0])
        second['url'] += '-2'
        p['amendments'].append(second)
        replace_payload(p, t, {'sequence': 2, 'previous': prior,
            'old_base': 'b' * 40, 'new_base': 'd' * 40, 'candidate': 'e' * 40,
            'expected_head': 'e' * 40, 'result_candidate': None}, 1)
        t['base'], t['head'] = 'd' * 40, 'e' * 40
        t['prior_results'] = {prior['url']: {'effective': prior, 'base': 'b' * 40,
            'candidate': 'e' * 40, 'starting_candidate': 'c' * 40,
            'pr': t['pr'], 'owner': t['owner']}}
        self.assertTrue(validate_effective_contract(p, t))

    def test_source_identity_cannot_extend_v1_semantics(self):
        p, t = fixture()
        source = dict(t['source'], permission='new')
        replace_payload(p, t, {'source': source})
        t['source'] = source
        self.assertTrue(validate_effective_contract(p, t))


if __name__ == '__main__':
    unittest.main()
