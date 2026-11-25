# Validation notes: ontario-travel-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/ontario-travel-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head b5395e2. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

23/24 valid (95.8%), mean field score 0.979, **easy 5/5**. By category: boundary_twin 6/6, distractor 2/2, easy 5/5, flag 2/3, hidden_clause 2/2, multi_rule 4/4, refusal 2/2.
$0.00167 billed per run, 16,949 prompt tokens per call, 4.00 calls per run;
0 of 24 runs would exceed the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| yarrow-crest | flag | BOOK WestJet changeable fare ($339), LOWEST_FARE; key FLAG | model slip | "The policy (Air Travel, and the Appendix C revision note) allows flexibility for those whose schedules frequently change." It took Appendix C's revision note (lines 1399-1402) as an operative rule and never weighed the Air Travel text (lines 558-559: choose the lowest fare available, with no exception). The twins ember-sill and sorrel-beacon passed. |

## Fixes

None. The one failure is a model slip; no key was widened and no record changed.

## Q2

Unchanged: the always-cheapest agent passes **10/24 (42%)**. This is above the ~40% guide; it was set by the audit (`MAX_PASS_ALWAYS_LOWEST = 10`) and nothing in this run changes it. Flagged for the lead.

## Re-score at the head (stored answers)

23/24 (no key changed). No re-run is required.

## Checks (at the notes commit)

`uv run pytest -q` (196 passed, 3 skipped), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical `rules.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
