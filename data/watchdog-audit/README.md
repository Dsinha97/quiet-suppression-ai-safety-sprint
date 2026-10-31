# Text-free watchdog audit data

This release contains per-read observations for the original-provider runs represented in the cross-model analysis, the five seed-0 Modal watchdogs, two seed-1 repeats, and four API-runner watchdogs. It covers the six-arm precedent and harder sets only. The Gemma-written-case experiment, pipeline trajectories, and other pilots are not included; the repository still cannot rebuild every report table. Original-provider inputs differed from the archived exported inputs. Their historical user hashes are retained, and the exported-input hash field is blank for those reads.

`observations.csv` contains one row per saved read, including the historical flag and suspicion score. `item` identifies a condition, record and trajectory repeat; `draw` is the per-prompt output sample. Seed 0 for Modal denotes the documented default, rather than a seed field recorded in those output files. API seed is blank. Missing flags remain in denominators and count as not flagged, matching the published analysis. Model labels and item IDs are identifiers, not complaint text. Historical labels are not independently validated. Refusal status was not independently coded for this release; do not interpret absent flags as measured false-positive performance.

`prompt-hash-sidecar.csv` maps each archived exported prompt to its original stored user hash and the full SHA-256 of its archived user string encoded as UTF-8. The first 16 hex characters of the latter differ from the stored value for 228/324 precedent and 18/147 harder-set rows. Historical result files inherited the stored field. For the API and Modal runs, a join on prompt set, arm and item matched stored user and system hashes and labels in all included result files. Original-provider records retain their recorded hashes; where a sidecar key exists, the original user hash matches the stored source hash. The sidecar exported-text hash is not attributed to those reads. This join does not independently prove the exact bytes transmitted in each call; it links observations to the documented frozen inputs. The complete frozen files have SHA-256 values `4c899ab6610963c8f949840b4e93140de7553f68de47a32fe2f8d0d777c5958a` (precedent) and `8d57485b6593ff2c60f4399b57a56e75841fee71c916809b2acd4efe8472efea` (harder), matching the report. Case text and model responses are excluded.

Rebuild counts and descriptive read-level Wilson intervals without model calls:

```sh
python experiments/grievance-pilots/rebuild_watchdog_audit.py > watchdog-counts.csv
```

Intervals treat reads as independent and do not account for repeated draws and shared complaints. They are descriptive, not evidence of significance or generalization to new complaints. This release does not repair the absence of held-out, human-checked labels.

Original-provider precedent rows exclude the initial C2 cases, following the published cross-model analysis. Some arms have fewer saved reads: Nemotron has 285 harder-set reads, while the Opus and Sol precedent runs cover arm C only. The analysis reports saved reads, with missing flags counted as not flagged; it does not reconstruct failed calls.


## Recomputed historical hashes

All 18,633 rows now include `recomputed_user_sha256`, `recomputed_system_sha256`, `input_hash_provenance`, and `prompt_file_sha256`. Original-provider user strings were reconstructed from archived trajectories using the historical formatting, with all recorded 16-character user-hash prefixes matching. `archived_user_sha256` remains blank for those rows to distinguish them from scrubbed exported text. The reconstructed strings are not included in this release. Exported-run recomputed hashes come from the archived JSONL strings; the stored system hashes, user source hashes and labels were checked when joining the observations. `prompt_file_sha256` identifies the frozen exported file for API/Modal rows and is blank for originals. Hashing is UTF-8 with no whitespace normalization.

To repeat the historical correction with private inputs:

```text
python experiments/grievance-pilots/recompute_historical_hashes.py --trajectory-dir /path/to/trajectories --prompt-dir /path/to/frozen-prompts --output observations-recomputed.csv
```

Historical reconstruction and archived-input joins do not prove the bytes a provider received. The revised API and Modal runners compute fresh full hashes from the exact system and user strings before the call, preserve legacy user hashes as `source_user_sha`, and record the full prompt-file hash. A mismatching supplied full hash raises. Existing historical output directories cannot be silently overwritten; the API runner rejects legacy or mismatched input hashes on resume, and the Modal runner requires an empty output folder. Use a new suffix for fresh runs. No historical raw output or frozen input file was modified.

An empty `flag` cell is a missing parsed flag, not an affirmative or a negative decision. Analyses retain it in the denominator and count only `True` as flagged, following the submitted convention. No historical labels are replaced with the later human record judgments.

Run `python experiments/grievance-pilots/test_watchdog_release.py` for offline checks of input hashes and row identity, plus the 13-model interval criterion. The tests invoke no provider or GPU service.
