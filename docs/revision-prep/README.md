# Revision preparation

The submitted report is unchanged. `WATCHDOG-TABLES.md` contains the local reconstruction of watchdog counts, descriptive read-level Wilson intervals, in-sample ROC summaries, and private-trajectory F1 counts. `TABLE-INVENTORY.md` maps report tables to source analyses and identifies outstanding items. `analysis-*.txt` are saved aggregate-only analysis outputs from the local raw files.

To rebuild the watchdog portion without private files, run `python docs/revision-prep/build_watchdog_tables.py`. This writes `WATCHDOG-TABLES.regenerated.md`. F1 requires `QUIET_SUPPRESSION_TRAJECTORIES` to name the private C2–C5 trajectory directory. The other pilot analyses require private raw files and the commands in the inventory. The original local script and data live outside this checkout; do not treat these results as a complete public reproduction of every table.

The retrospective and candidate human decisions are in `data/human-review/`. They have not been used to recalculate the submitted findings. The new candidate set is not a frozen or completed held-out evaluation. Inspect its disclosure before publishing this branch.
