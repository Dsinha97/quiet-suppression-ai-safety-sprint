"""Rebuild descriptive watchdog counts from the text-free audit release."""
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/watchdog-audit/observations.csv'

def wilson(k, n):
    z = 1.96
    p = k / n
    d = 1 + z*z/n
    c = p + z*z/(2*n)
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (100*(c-h)/d, 100*(c+h)/d)

def main():
    cells = defaultdict(lambda: [0, 0, 0, 0, 0])
    seen = set()
    with DATA.open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            ident = tuple(row[k] for k in ('run','prompt_set','arm','item','draw'))
            if ident in seen: raise ValueError(f'duplicate read: {ident}')
            seen.add(ident)
            c = cells[(row['run'], row['prompt_set'], row['arm'])]
            label = int(row['label']); flag = row['flag'] == 'True'
            if label == 1: c[0] += flag; c[1] += 1
            elif label == 0: c[2] += flag; c[3] += 1
            else: raise ValueError(f'unknown label: {label}')
            c[4] += row['flag_missing'] == 'True'
    print('run,prompt_set,arm,suppression_flagged,suppression_n,wilson_low_pct,wilson_high_pct,benign_flagged,benign_n,missing_all')
    for (run, prompt_set, arm), (k,n,b,bn,missing) in sorted(cells.items()):
        lo, hi = wilson(k,n)
        print(f'{run},{prompt_set},{arm},{k},{n},{lo:.2f},{hi:.2f},{b},{bn},{missing}')
if __name__ == '__main__': main()
