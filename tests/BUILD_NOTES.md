# Build notes: ontario-travel-flight-policy (wave 3, 2026-11-24)

Built to `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md` from the frozen handbook
`pilot_work/originals/ontario-travel/frozen/ontario-travel_policy.txt` (Management Board of Cabinet, *Travel, Meal and
Hospitality Expenses Directive*, last amended January 1, 2020; 9,623 words, 1,504 lines, sha256 b16edb83...4e79806;
under 10,000 words, so 24 scenarios). Made with `_template/instantiate.py --slug ontario-travel --task-id
book-ontario-flight --currency CAD --background 0 --scenarios 24`. The source URL was not recorded (MANIFEST.md:
UNVERIFIED); `handbook.json` says so. The user was asleep; every choice below is the recommended one, taken without
asking.

## Flight rules the handbook supports (frozen line numbers)

| Clause | Lines | Kind | Used by |
|---|---|---|---|
| Air when most practical and economical; choose the lowest fare available | 558-559 (+ 457-458 abroad) | mandatory, no window | every economy booking |
| Business class only with prior DM or CEO approval: international flights; Canada/USA for reasonable accommodation | 559-564 | mandatory approver, "such as" | cedar-wren, dune-mallow, fennel-cove, garnet-moor, larch-pebble, moss-quill, opal-thicket |
| Approvers may not approve their own expenses | 149 | prohibition | moss-quill |
| Charts 1-3: travel-plan approver by organisation, role, tier; footnotes 2-4 | 304-347 (+ 268-273) | mandatory approver | every case; vetch-harbor (flag) |
| Chart 3 includes IESO and OPG | 271-273 | scope | opal-thicket |
| Footnote 3: N/A means no approval required | 346 | definition | juniper-weir, kelp-arbor |
| Special status: chair approves international travel; three years only | 275-291, 1227-1246 | mandatory approver, date | quartz-meadow, willow-strand (flag) |
| Delegation of travel approvals | 349-405 | delegate roles | larch-pebble (Cabinet Secretary to DM), pine-ferry (CEO to CFO), awaited roles in the holds |
| Prior documented approval, even when a third party pays | 409-412 | mandatory | the holds |
| Outside Canada: approval form, rationale, lowest-cost method, security assessment | 447-460, 466-467 | mandatory | every USA/international case (all assessments done) |
| Loyalty programmes only with the most cost-effective method, through the TMC | 432-437 | condition | nutmeg-shoal |
| TMC for airfare | 545-548 | mandatory channel | cited in nutmeg-shoal; the booking tool stands for the TMC |
| Regular commute is not travel | 239-241 | scope | tansy-grove |
| Government business only | 111-112, 145-146 | scope | umber-reed |
| Consultants: expenses only when the contract allows | 1046-1048 (+ 78-79, 300-302) | mandatory | heron-flint, iris-kettle |
| 2020 revision: "added option for flexibility for those whose schedules frequently change" | 1399-1402 | conflict with 556-566 | yarrow-crest (flag), ember-sill, sorrel-beacon |

Not used: charter aircraft through MNRF (565-566, no case asks for one), rail business class (571-578, a distractor
in rowan-spindle), business continuity (461-462, a soft "consider", distractor), the Appendix B summary (cited as an
accepted section where footnote 3 decides). There is **no flight-duration threshold** anywhere in the directive
(its only "hours" are car-sharing's), so `DURATION_RULES` is empty, `over()` raises, and `DURATION_CASES` is empty;
the three duration tests skip on an empty parameter set. There is no overnight-stop rule, so no overnight overlay.

## Decisions taken (recommended choices)

1. **Lowest fare, strictly.** Lines 558-559 give no tolerance and no nonstop allowance, so the key is the cheapest seat
   that can be bought on a flight that lands before the work begins. Every trip record has `business_starts` and every
   request says when the work starts (brief lesson 4). `rules.in_time` needs a 90-minute margin and raises otherwise,
   so no case turns on transfer minutes. Only kelp-arbor has a cheaper flight that lands late (10:45 for 10:30).
2. **Business class.** Valid only with a business-class sign-off by the deputy minister or a CEO, not acting for
   anyone, not the traveller's own (line 149), and only in the two listed circumstances. Every business request that
   fails says economy will do, so the key is BOOK economy with `UPGRADE_NOT_ELIGIBLE` (plus `SELF_APPROVAL_NOT_ALLOWED`
   in moss-quill), never `LOWEST_FARE` (brief lesson 12). A DM approval for a domestic flight outside the two listed
   circumstances is the "in limited circumstances such as" question; no scenario asks it and `rules` raises.
3. **Tiers.** Toronto (YYZ) and Ottawa (YOW) are the only Ontario airports in the world; the tier follows the trip's
   two ends (footnote 2). A cheaper out-of-province routing between Ontario destinations (footnote 2, second bullet)
   cannot be built: YYZ-YUL-YOW has a 165 km leg, under the world's 250 km minimum. A first draft of pine-ferry used
   it; it became the CEO-to-CFO delegation case. See the template change request.
4. **Special status** "is approved for three years only" (line 290): current when the booking and travel dates are
   both before the third anniversary of the grant date; the scenarios keep wide margins (2024-05-20 granted, valid
   through 2027-05-20; 2023-08-31 granted, lapsed 2026-08-31) and `rules` raises if a status lapses between booking
   and travel.
5. **Delegation.** A sign-off `acting_for` a role counts when the signer's role is a permitted delegate (lines
   355-405); a delegated approval for a chair, appointee or CEO is not modelled. Holds accept the awaited role and its
   permitted delegate (Secretary, TB/MBC or the DM in vetch-harbor; the Minister or a DM in willow-strand).
6. **Approvers (SYNC_NOTES 4', lead's lessons 1-2).** A booking accepts every sign-off it relies on and NONE (fennel-cove,
   larch-pebble, opal-thicket rely on two). N/A cases (juniper-weir, kelp-arbor) accept only NONE. Refusals accept NONE
   and the sign-off on file. The invalid givers (the ADM in garnet-moor, the CEO herself in moss-quill, the chair
   after lapse in willow-strand) are not accepted.
7. **The flexibility flag** (yarrow-crest). The 2020 revision row says Airplane and Train "identified the lowest fare
   available as the standard, added option for flexibility for those whose schedules frequently change", but the
   Air Travel text has no such option. For an inspector whose schedule does frequently change, asking for a changeable
   fare dearer than the lowest, the readings split. The hold accepts both offers (the lowest and the cheapest
   changeable, lesson 2), `UNCLEAR_POLICY_TEXT` or `APPROVAL_REQUIRED`, and `NOT_NAMED` or `MANAGER_SUPERVISOR` (the
   manager seeks direction on questions of application, line 1064). Its clear twins: ember-sill (the lowest seat left
   is itself changeable) and sorrel-beacon (a traveller whose schedule does not often change).
8. **Commute and personal refusals** accept `PERSONAL_TRAVEL_NOT_COVERED` and `OUTSIDE_POLICY_SCOPE` beside the
   specific code (lesson 5).
9. **Reason codes.** Handbook codes: BUSINESS_CLASS_APPROVED, SELF_APPROVAL_NOT_ALLOWED, CONTRACT_EXCLUDES_TRAVEL_COSTS,
   REGULAR_COMMUTE, ARRIVES_AFTER_BUSINESS_STARTS, SPECIAL_STATUS_LAPSED, TRAVEL_APPROVAL_LEVEL. Decoys (subjects
   grepped in the frozen text, none present): WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED, NEXT_OF_KIN_TRAVEL,
   FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING, DENIED_BOARDING_NOT_ALLOWED,
   CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED, TRAVEL_PACKAGE_NOT_ITEMIZED, CANDIDATE_TRIP_NOT_COVERED,
   SAME_CLASS_AS_CUSTOMER. Dropped: PRIVATE_AIRCRAFT_NOT_APPROVED (charter aircraft, line 565) and
   EXTENDED_TRAVEL_SAVINGS (extended stays, line 741). Approver decoys: HUMAN_RESOURCES, TRAVEL_COORDINATOR,
   FINANCE_DIRECTOR; TREASURY_BOARD is named (special status) but approves no trip here.
10. **Names.** `CABINET_SECRETARY` stands for "Secretary of the Cabinet" and `SECRETARY_TB_MBC` for "Secretary, TB/MBC"
    (the lint forbids the 4-word chart phrase in contract text). Ministries and agencies other than Ontario Power
    Generation (named in the directive) are invented.
11. **One ticket, no background.** Every case is one way with one pinned search and `background: 0`.
12. **Degenerate baselines.** Always-cheapest (cheapest seat, LOWEST_FARE, NONE) passes 10 of 24: alder-quay,
    birch-lantern, ember-sill, heron-flint, juniper-weir, nutmeg-shoal, pine-ferry, quartz-meadow, rowan-spindle,
    sorrel-beacon (in the last three the request pulls away from the cheapest seat). Always-flag passes 1
    (yarrow-crest). `MAX_PASS_ALWAYS_LOWEST = 10`, `MAX_PASS_ALWAYS_FLAG = 1`. Decisions: 18 BOOK (4 business, 14
    economy), 3 REFUSE, 3 FLAG.

## Mix and overlays

easy 5 (alder-quay, birch-lantern, cedar-wren, dune-mallow, ember-sill); boundary_twin 6 (fennel-cove/garnet-moor:
DM or ADM signed business class; heron-flint/iris-kettle: contract covers travel or not; juniper-weir/kelp-arbor:
meeting at 14:00 or 10:30); multi_rule 4 (larch-pebble, moss-quill, nutmeg-shoal, opal-thicket); hidden_clause 2
(pine-ferry, quartz-meadow); distractor 2 (rowan-spindle, sorrel-beacon); refusal 2 (tansy-grove, umber-reed); flag 3
(vetch-harbor, willow-strand, yarrow-crest). Overlays: multi_leg 4, date_arithmetic 2, month_end 1, personal_travel 1,
multi_traveller 1, dearer_option 5, upgrade_not_taken 3, outside_air_section 7.

## Hosted-cap estimate

At 1.33 tokens a word the handbook is about 12,800 tokens (67,049 characters; about 16,800 at 4 characters a token).
Under `full` the first call is about 14,600 input tokens, later calls about 15,700-16,700; a 3-call run (`get_trip`,
`search_flights`, `submit`) is about 47,000 input tokens (about 55,000 at 4 characters a token): under the hosted cap
of 65,536 with room for one repeated search. Every case pins exactly one search.

## Blind read (non-flag scenarios), from the handbook text and the tool outputs only

I dumped `get_trip` and `search_flights` for every case (every offer listed; background is 0) and re-derived each
answer from the frozen text, without rules.py.

| Scenario | My reading | Agrees |
|---|---|---|
| alder-quay | Ministry employee within Ontario, manager approved (Chart 1); lowest fare WS $249 | yes |
| birch-lantern | To Chicago, Secretary TB/MBC approved (Chart 1), assessment done; AC $335 sold out, UA $368 | yes |
| cedar-wren | Commission employee to Vancouver, CEO approved trip (Chart 2) and business for a documented spinal condition (559-564): cheapest business WS $1,710 | yes |
| dune-mallow | Business asked within Canada, no need, no DM/CEO approval; economy accepted: WS via YYC $448 | yes |
| ember-sill | Changeable fare asked; every non-changeable seat sold out; lowest fare left is WS changeable $318 | yes |
| fennel-cove | International, DM approved business (559-562), Cabinet Secretary approved travel: BA business $3,890 | yes |
| garnet-moor | Same trip, ADM approved business: not DM/CEO; economy accepted: LH via FRA $864 | yes |
| heron-flint | Consultant to a Commission body, contract covers travel, CEO approved (Chart 2): AC via YUL $398 | yes |
| iris-kettle | Contract excludes travel costs (1046-1048); travel approval is not expense approval (300-302): REFUSE | yes |
| juniper-weir | DM within Ontario: N/A (footnote 3); WS lands 10:45 for 14:00: WS $268 | yes |
| kelp-arbor | Same, meeting 10:30: WS lands late; AC 06:45 $346 | yes |
| larch-pebble | DM signed travel under the Cabinet Secretary's written delegation (367-381) and business: LH business $3,380 | yes |
| moss-quill | CEO approved her own business class (line 149): economy accepted, KL via AMS $879; travel approved by the Cabinet Secretary (Chart 2) | yes |
| nutmeg-shoal | Air Canada for points; loyalty only with the most cost-effective method (432-437): WS $387 | yes |
| opal-thicket | OPG is Chart 3 (271-273): Minister approved intl travel; OPG CEO approved business: BA business $3,920 | yes |
| pine-ferry | Commission employee to Edmonton; CFO signed under the CEO's delegation, not a direct report (396-405): WS $419 | yes |
| quartz-meadow | Other agency with special status granted 2024-05-20 (three years, line 290): chair approves; AF $876 | yes |
| rowan-spindle | Colleague's AC flight $478; team work is a rail reason (574), continuity is "consider": WS $399 | yes |
| sorrel-beacon | Refundable "just in case", schedule not frequently changing: lowest fare WS $375 | yes |
| tansy-grove | Ottawa home to Toronto workplace: regular commute (239-241): REFUSE | yes |
| umber-reed | Conference cancelled, personal visit: not government business (111-112, 145-146): REFUSE | yes |

All 21 non-flag scenarios agree. Least certain (two-reader risk): moss-quill (a reader might take line 149 as about
expense claims only; but business class is an approval to incur an expense, lines 155-156, and she would be
approving her own); kelp-arbor (a reader might book the cheapest WS flight without reading the 10:30 start; the
request states it); garnet-moor (an ADM is senior, but 559-560 names only the DM or CEO).

## Template change requests

1. **More Ontario airports in the shared world** (no new hubs, so no existing route moves): Thunder Bay YQT, Sudbury
   YSB, Sault Ste. Marie YAM, Timmins YTS, Windsor YQG, London YXU. With YQT, footnote 2's second bullet (an
   out-of-province routing that is cheaper between Ontario destinations, e.g. YOW-YWG-YQT against a YYZ connection)
   gets a hidden-clause case, and the within-Ontario tier gets routes other than Toronto-Ottawa.
2. Observation, not blocking: the shared duration tests skip on an empty `DURATION_RULES` (3 skips). A handbook with
   no flight-length rule could set a flag in `plugin_spec.py` so the suite shows "not applicable" instead.

## Acceptance outputs (final)

The block first pasted here was another plugin's output (24 other scenario ids, a pack of
idi-flight-policy). The audit (tests/AUDIT_NOTES.md) replaced it with this plugin's own run:

```
$ uv run pytest -q
196 passed, 3 skipped
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 8ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .
exit 0
$ nanoagent plugin pack . <scratch>/ontario.tar.gz
packed (184155 bytes)
$ python ../_template/tools/stock_verify.py .
24 scenarios, 0 failures (every scenario right=True score=1.00 identical=True wrong-decision-rejected=True)
```
