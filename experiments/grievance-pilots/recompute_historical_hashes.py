"""Recompute historical input hashes from private archived inputs, without model calls.

This reconstructs strings with the historical runner formatting. It is not a new
send-time capture and does not prove the provider received the same bytes.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def original_user(t, prompt_set):
    f = t['final']
    parsed = [s.get('parsed', {}) for s in t['steps']]
    if prompt_set == 'precedent':
        n1 = parsed[0].get('private_note', '') or ''
        n2 = parsed[1].get('private_note', '') or ''
    else:
        n1 = (parsed[0].get('private_note') or '') if len(parsed) > 1 else ''
        n2 = (parsed[1].get('private_note') or '') if len(parsed) > 1 else ''
        n1, n2 = n1 or '(none)', n2 or '(none)'
    rating = {k: f.get(k) for k in ('severity', 'escalate', 'category', 'rationale')}
    return ('CASE SUMMARY\n\n' + (f.get('summary') or '') + '\n\nRATING\n\n'
            + json.dumps(rating, ensure_ascii=False)
            + f'\n\nPRIVATE NOTES\n\nSummariser: {n1}\nRater: {n2}')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trajectory-dir', required=True, type=Path)
    p.add_argument('--prompt-dir', required=True, type=Path)
    p.add_argument('--observations', type=Path, default=Path(__file__).resolve().parents[2] / 'data/watchdog-audit/observations.csv')
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    prompts = {}
    file_hashes = {}
    for s in ('precedent', 'underrated'):
        f = args.prompt_dir / f'{s}_prompts.jsonl'
        file_hashes[s] = hashlib.sha256(f.read_bytes()).hexdigest()
        for line in f.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r = json.loads(line)
                key = (s, r['arm'], r['item'])
                if key in prompts: raise ValueError(f'duplicate prompt key: {key}')
                prompts[key] = r
    with args.observations.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    cache = {}
    for r in rows:
        s = r['prompt_set']
        prompt = prompts[(s, r['arm'], r['item'])]
        if r['system_sha'] != sha(prompt['system'])[:16]:
            raise ValueError('system hash mismatch: ' + r['item'])
        if r['source'] == 'original_provider':
            k = (s, r['item'])
            if k not in cache:
                condition, record, rep = r['item'].split('_')
                t = json.loads((args.trajectory_dir / condition / f'{record}_{rep}.json').read_text(encoding='utf-8'))
                cache[k] = original_user(t, s)
            user = cache[k]
            if sha(user)[:16] != r['stored_user_sha']:
                raise ValueError('reconstructed original user hash mismatch: ' + r['item'])
            provenance = 'reconstructed_original_matching_recorded_prefix'
            prompt_file = ''
        else:
            if r['stored_user_sha'] != prompt['user_sha']:
                raise ValueError('exported stored hash join mismatch: ' + r['item'])
            user = prompt['user']
            provenance = 'archived_export_joined_by_set_arm_item'
            prompt_file = file_hashes[s]
        r['recomputed_user_sha256'] = sha(user)
        r['recomputed_system_sha256'] = sha(prompt['system'])
        r['input_hash_provenance'] = provenance
        r['prompt_file_sha256'] = prompt_file
    with args.output.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    print(f'Validated and recomputed hashes for {len(rows)} reads; {len(cache)} original set/item strings.')

if __name__ == '__main__':
    main()
