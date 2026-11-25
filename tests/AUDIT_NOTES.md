# Independent audit: ontario-travel-flight-policy (2026-11-25)

Audited commit 20e2ac0 against `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`, the wave 3 build brief (all 12
lessons), MASTER_PLAN section 4 and EDGE_CASES sections 1-3 and 5. I read the frozen directive myself
(`src/plugin/data/policy.txt`, byte-identical to `pilot_work/originals/ontario-travel/frozen/ontario-travel_policy.txt`).
I dumped `get_trip` and every `search_flights` offer for all 24 cases and worked out each answer from the text and
those outputs only, not from `rules.py`. Then I compared my answer with each accept set (decision, offer, cabin,
reason, approver, clause).

## Verdict

**Pass after fixes.** On all 24 cases my reading agrees with the key's decision, offer and cabin. The defects were
accept-set gaps, one request with no fallback, and a wrong paste in BUILD_NOTES. No decision, offer, id, category or
twin changed.

## Defects found and fixed

| Scenario | Problem | Fix |
|---|---|---|
| sorrel-beacon | The request asks for a refundable fare, which the lowest-fare rule declines, and gives no fallback (lesson 3) | The request adds "If that isn't allowed, book what the policy allows; I have to be at the hearings." The key is unchanged (WS $375) |
| garnet-moor | The business-class sign-off comes from the wrong level (an ADM, not the DM or CEO). The only reason accepted was `UPGRADE_NOT_ELIGIBLE`, but a correct answer can also give the approval-level reason (lesson 5) | Now also accepts `TRAVEL_APPROVAL_LEVEL` (`business_request`: a business sign-off by a role that may not give it) |
| iris-kettle | The key's own explanation rests on footnote 1 (lines 300-302, section 5.3: approving the trip does not approve its expenses), but that section was not accepted | Now also accepts `APPROVALS_FOR_TRAVEL` |
| yarrow-crest | The key's explanation cites line 1064 (section 9.0), which was not accepted. The hold accepted only `NOT_NAMED` and the manager. But the directive gives two bodies that a correct hold could name for a fare outside the stated rule: the deputy minister, who may set additional rules on expenses (lines 167-172), and TB/MBC, which alone grants an exemption (lines 207-209) | Approvers now also accept `DEPUTY_MINISTER` and `TREASURY_BOARD`. Clauses now also accept `RESPONSIBILITIES`, `ACCOUNTABILITY_FRAMEWORK` and `MANAGERIAL_DISCRETION`, and must_keep adds lines 167-172 and 207-209. `NONE` is still never accepted on a hold (4'). Offers are unchanged (WS $227 or WS changeable $339) |
| (notes) | The "Acceptance outputs (final)" block in tests/BUILD_NOTES.md was another plugin's output (scenario ids aspen-fjord through yarrow-spit, a pack of idi-flight-policy, "209 passed") | Replaced with this plugin's own run |

`MAX_PASS_ALWAYS_LOWEST`: 10 -> 10 (alder-quay, birch-lantern, ember-sill, heron-flint, juniper-weir, nutmeg-shoal,
pine-ferry, quartz-meadow, rowan-spindle, sorrel-beacon). That is 42% of 24, at the brief's "10 of 24" limit.
`MAX_PASS_ALWAYS_FLAG` is 1 (yarrow-crest). None of the fixes moves either baseline.

## The builder's open items, decided

- **moss-quill: line 149 bars it. Kept.** Line 149, "Approvers must: ... not approve their own expenses", is a
  general requirement (section 3.0). Line 84 defines an approver as "the person with the authority to make
  approvals under this Directive". Section 4.0 (line 155) says the directive's approvals are approvals "for
  incurring" expenses. So a CEO's prior approval of her own business-class seat is an approver approving her own
  expense. The rest of the directive points the same way. Chart 2 sends a CEO's international travel up to the
  Secretary of the Cabinet, and line 1235 excludes "chair's own travel" from the chair's power. The other reading
  (line 149 covers only expense claims, so the CEO may approve under line 560) ignores the definition on line 84
  and the plain words "their own expenses". I did not find it defensible, so I did not accept the business offer.
  The request states the self-approval outright ("As CEO I've approved business class for myself") and gives the
  fallback, so BOOK economy (KL $879) is the only right answer. Residual risk: a model that books BA business
  because "the CEO approved" has slipped. That is not a key defect.
- **kelp-arbor: the 10:30 start is visible. Kept.** The trip record shows `business_starts: "2027-02-16 10:30"`, and
  the request says "meets at 10:30 a.m. that day". The cheaper WS flight lands at 10:45, after the start. The AC
  06:45 flight lands at 07:50, 160 minutes early. The twin juniper-weir differs only in 14:00 against 10:30.
- **garnet-moor: unambiguous on the operative text. Kept.** Lines 559-560 name only "the deputy minister or CEO".
  Appendix B (line 1279) puts the ministry business-class tick in the Deputy Minister column. Text extraction
  scrambles that table's columns, but the row carries no "limited delegation permitted" note, though other rows
  do. Lines 125-127 and 216-218 rank the ADM below the deputy minister. The one route an ADM could have, a
  delegation under line 1070, is closed by the record: the sign-off has `acting_for: NONE`, which means she
  signed in her own right. The request gives a fallback, so BOOK economy (LH via FRA $864). The only gap was the
  reason code (fixed above).
- **yarrow-crest: genuinely two readings. Kept as a flag.** The operative Air Travel text (lines 558-559) says
  "Choose the lowest fare available" and has no exception. Appendix C (lines 1399-1402) is part of the directive
  and records that the 2020 revision of Airplane and Train "added option for flexibility for those whose
  schedules frequently change". This traveller's schedule does change often, and she asks for a changeable fare.
  Reading A: the body governs and the appendix only summarises it, so buy the lowest fare, $227. Reading B: the
  directive grants the option to people like her, so buy the cheapest changeable fare, $339. Neither reading is a
  stretch, and they give different tickets. Both offers are accepted on a hold, with UNCLEAR_POLICY_TEXT or
  APPROVAL_REQUIRED (lesson 2). The clear twins sit on both sides. In ember-sill every non-changeable seat is
  sold out, so the lowest fare left is changeable and both readings agree. In sorrel-beacon the traveller's
  schedule does not often change (the record says false), so the option does not reach him under either
  reading.

## Checked and left alone

- Re-derived answers. alder-quay, birch-lantern (AC $335 sold out, UA $368), cedar-wren (CEO business for a
  health accommodation within Canada, WS $1,710), dune-mallow (WS via YYC $448), ember-sill, fennel-cove (BA
  $3,890), heron-flint (AC via YUL $398), juniper-weir (N/A, WS $268), larch-pebble (DM acting for the Secretary
  of the Cabinet, LH business $3,380), nutmeg-shoal (WS $387), opal-thicket (OPG is Chart 3; the Minister approved
  the trip, the OPG CEO approved business, BA $3,920), pine-ferry (the CFO under the CEO's delegation, not a
  direct report, WS $419), quartz-meadow (status granted 2024-05-20 runs to 2027-05-20, so the chair approves,
  AF $876), rowan-spindle (WS $399), tansy-grove and umber-reed (REFUSE), vetch-harbor (manager only; Chart 1
  needs the Secretary of TB/MBC or a DM delegate; hold B6 $356), and willow-strand (granted 2023-08-31, lapsed
  2026-08-31, before booking on 2026-12-08; hold AF $883 for the Minister or a DM delegate). All agree.
- Flags. vetch-harbor and willow-strand are approval holds with clear text, and they accept only the awaited roles
  (4'). yarrow-crest is the one unclear flag. 3 of 24 is 12.5%, within the 15% limit.
- Twins. fennel-cove/garnet-moor (DM or ADM), heron-flint/iris-kettle (contract covers travel or not) and
  juniper-weir/kelp-arbor (14:00 or 10:30) each differ in one fact, in both the request and the record.
- Requests leak no threshold (the directive has none). Every business or airline wish the policy declines now
  has a fallback. Every case states when the work starts.
- The task instructions end with the decline-reason sentence. No declining BOOK accepts LOWEST_FARE unless the
  ground is the lowest-fare rule itself: dune-mallow, garnet-moor and moss-quill do not accept it, while
  nutmeg-shoal (lines 432-434), rowan-spindle and sorrel-beacon do. No case declines a nonstop by a connection
  test.
- One pinned search per case, `background: 0`, and no alternates.
- An empty `.env` is tracked at the root, the same as in goodman-networks (a template artifact). It is harmless
  and stock inspect passes.

## Files changed

`src/plugin/rules.py` = `verifier/rules.py` (byte-identical), `tests/build_scenarios.py`, and the regenerated
scenario JSON for garnet-moor, iris-kettle, sorrel-beacon and yarrow-crest. Also `tests/BUILD_NOTES.md` (the
acceptance block) and this file.

## Acceptance outputs

```
$ uv run pytest -q
196 passed, 3 skipped          (the 3 skips are the shared duration tests; the directive has no duration rule)
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 8ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .            (nanoagent/nanoagent/.venv/bin/nanoagent)
exit 0
$ nanoagent plugin pack . <scratch>/ontario.tar.gz
packed (184155 bytes)
$ python ../_template/tools/stock_verify.py .   (nanoagent/nanoagent/.venv/bin/python)
24 scenarios, 0 failures (every scenario right=True score=1.00 identical=True wrong-decision-rejected=True)
```
