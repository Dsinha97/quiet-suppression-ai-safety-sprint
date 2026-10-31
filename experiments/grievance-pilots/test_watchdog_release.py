"""Offline checks for the release and send-time hash guards; no provider imports."""
import ast
import csv
import hashlib
import importlib.util
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def hash_helpers(path):
    # Only compile pure hash helpers, avoiding Modal provisioning on import.
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('_input_hashes', '_check_input_row')]
    ns = {'hashlib': hashlib}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
    return ns

class HashGuards(unittest.TestCase):
    def test_both_runners_hash_unicode_and_preserve_legacy_source(self):
        for name in ('run_precedent_api.py', 'run_precedent_modal.py'):
            ns = hash_helpers(HERE / 'modal-handover' / name)
            row = {'system': 'Policy\n', 'user': 'Résumé ☀\n', 'user_sha': 'stale-source'}
            before = dict(row)
            got = ns['_check_input_row'](row)
            self.assertEqual(got['user_sha256'], hashlib.sha256(row['user'].encode('utf-8')).hexdigest())
            self.assertEqual(row, before)
            with self.assertRaises(ValueError):
                ns['_check_input_row']({**row, 'user_sha256': 'wrong'})
            with self.assertRaises(ValueError):
                ns['_check_input_row']({**row, 'system_sha': 'wrong'})

    def test_release_identity_hash_joins_and_cohort(self):
        with (ROOT/'data/watchdog-audit/observations.csv').open(encoding='utf-8',newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 18633)
        self.assertEqual(len({tuple(r[k] for k in ('run','prompt_set','arm','item','draw')) for r in rows}),len(rows))
        for r in rows:
            self.assertEqual(len(r['recomputed_user_sha256']),64)
            self.assertEqual(r['recomputed_system_sha256'][:16],r['system_sha'])
            self.assertIn(r['flag'],('True','False','None',''))
            self.assertIn(r['flag_missing'],('True','False'))
            if r['source']=='original_provider':
                self.assertEqual(r['recomputed_user_sha256'][:16],r['stored_user_sha'])
            else:
                self.assertEqual(r['recomputed_user_sha256'],r['archived_user_sha256'])
        cohort=['glm-default','gemma','minimax','nemotron','haiku-5.5','sonnet-5.5','gemini-3.8-flash_v2','gemini-4-argon','qwen3-32b','llama-3.3-70b','mistral-small-3.2-24b','gpt-oss-120b','olmo-3.1-32b-think']
        spec=importlib.util.spec_from_file_location('rebuild',HERE/'rebuild_watchdog_audit.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        drops=[]; recoveries=[]
        for run in cohort:
            cells={}
            for arm in 'ACF':
                q=[r for r in rows if r['run']==run and r['prompt_set']=='precedent' and r['arm'][0]==arm and r['label']=='1']
                self.assertEqual(len(q),48)
                cells[arm]=m.wilson(sum(r['flag']=='True' for r in q),len(q))
            if cells['A'][0]>cells['C'][1]:
                drops.append(run)
                if cells['F'][0]>cells['C'][1]:recoveries.append(run)
        self.assertEqual(len(drops),8)
        self.assertEqual(len(recoveries),7)
        self.assertNotIn('minimax',drops)
        self.assertNotIn('mistral-small-3.2-24b',recoveries)

if __name__=='__main__':unittest.main()
