# Response to the first Quiet Suppression review

Prepared 1 November 2026. The original submission remains at `docs/report/Quiet-Suppression-report.pdf`. The dated revision is in `docs/report/v2/`. The team agreed to publish v2 alongside the unchanged Apart submission. The judges’ access to later versions is not confirmed here.

| Review request | Revision and evidence |
|---|---|
| PDF intervals and MiniMax wording | Appendix I contains the 13-model A/C/F rates and Wilson intervals, with explicit drop and recovery columns. Section 4.3 distinguishes observed rate decreases from the non-overlap criterion. The eight drops are GLM, Gemma, Nemotron, Sonnet, Gemini 3.8 Flash API, Mistral, gpt-oss and OLMo. Seven meet the recovery criterion; Mistral does not. MiniMax does not meet the drop criterion. |
| Text-free observations and hash correction | `data/watchdog-audit/observations.csv` contains 18,633 saved reads. Every row has recomputed system and user hashes with provenance. Original strings were reconstructed from private cached trajectories and match all recorded user-hash prefixes; API/Modal strings come from the archived freezes joined by set, arm and item. The legacy source fields remain. Historical joins cannot retroactively supply send-time capture. Both runners now compute fresh hashes on the strings passed to the provider and record the prompt-file hash. |
| Pre-sprint numbers in the main text | Sections 4.1–4.3 identify the cached MiniMax and initial pressure, paraphrase and watchdog-position pilots as prior work. Tables 2, C1 and D1 also mark the relevant MiniMax columns. |
| Consistent conditions and lifecycle description | Table 1 now includes C1 and C6; C2 is the no-notes baseline and C3 the notes baseline. The lifecycle description consistently identifies seven agent roles with simulated site-manager and complainant roles. The previous nine-stage wording is removed. |
| Held-out labels and low-authority arm | Both remain future work. The retrospective eight-record human pass and the rated 12-case candidate pool are disclosed without claiming a completed held-out evaluation. H01–H12 have already been exposed on the public PR branch and are development or practice cases, retired from blind held-out use. A future test needs fresh cases and private ratings until the evaluation is frozen and run. No new model runs were launched. |

## Validation

The offline checks reproduce the eight-of-thirteen and seven-of-eight interval counts. All 18,633 historical observation rows retain their previous data fields unchanged; only provenance fields were added. Hash reconstruction checked every row. Duplicate identities and hash joins pass. Unicode hashing, rejection of inconsistent full hashes and preservation of legacy source fields are tested without importing provider services. Both runner modules compile.

The PDF was rebuilt with the retained Apart template, exported through Word and visually checked across 22 pages. The main report occupies pages 1–8, references begin on page 9, and 37 hyperlink annotations are present. The retained submission PDF was not overwritten. The v2 source and portable DOCX builder are included.

## Remaining boundaries

The original logs do not contain a historical send-time capture. The release identifies inputs from the available archives and matched original hashes, and states that limitation. Some other pilot tables and refusal details require private raw files; the table inventory lists that boundary. The released observations permit offline reconstruction of the covered watchdog tables, not every experiment in the report. The wider held-out evaluation requires a frozen protocol and future runs; it is outside this correction package.

The agreed publication plan is to publish v2 alongside the unchanged Apart submission. It does not depend on Apart confirming a submission-update policy. This branch remains prepared for review. Swarm design, labeling and dates are unchanged by this work.
