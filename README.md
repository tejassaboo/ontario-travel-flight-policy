# Ontario Travel Directive Flight Booking

**Source of the handbook:** https://files.ontario.ca/tbs-travel-directive-en-2019-11-28.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with the Government of Ontario.** The handbook is the Management Board of Cabinet's *Travel, Meal
and Hospitality Expenses Directive* (issued November 2004, last amended January 1, 2020), a public provincial
government directive, bundled verbatim for research. Its source URL was not recorded when it was downloaded
(`pilot_work/originals/MANIFEST.md`): confirm the public URL before publishing.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the directive: it reads the
trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or **FLAG_FOR_APPROVAL** with the
offer, cabin, reason, approver and directive section. A deterministic Python verifier, with no LLM, rebuilds the
offers and the directive's answer itself and checks every field. Built from the original-handbook template
(`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 9,623 words, 1,504 lines, sha256 `b16edb83...4e79806`, equal to
`pilot_work/originals/ontario-travel/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule.
Under stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy`
switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system
prompt: `harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant
to run with `query: instructions+input`, so a selector sees the traveller's request.

**What decides a booking.** Air travel when it is the most practical and economical way, at the lowest fare
available (lines 558-559, with no fare window or nonstop allowance); business class only with the deputy minister's
or CEO's prior approval, on international flights or for a reasonable accommodation within Canada and the USA (lines
559-564); who approves the travel plan, by organisation (ministry, Commission public body, other agency or
organisation), role and destination tier (Charts 1-3, lines 304-347), with special status (lines 275-291,
1227-1246) and written delegation (lines 349-405); no self-approval (line 149); no regular commute (lines 239-241);
consultants only when their contract allows (lines 1046-1048). **No flight-length rule**: nothing turns on how long a
flight is, so `rules.DURATION_RULES` is empty. Every trip record says when the work at the destination begins.

**Size.** At 1.33 tokens a word the handbook alone is about 12,800 tokens (about 16,800 at 4 characters a token).
Under `full` the first call carries about 14,600 input tokens (handbook, task instructions about 280, tool and
submit schemas about 1,500, the request), and later calls about 15,700-16,700 as tool results accumulate. A run
makes 3 calls (`get_trip`, `search_flights`, `submit`): about 47,000 input tokens, under the hosted cap of 65,536
(about 55,000 at 4 characters a token), with room for one repeated search. Every case pins one one-way search.

**Only Toronto and Ottawa.** The shared world has two Ontario airports (YYZ, YOW), so every within-Ontario case flies
between them, and the footnote-2 rule on a cheaper routing outside the province (lines 343-345) has no case:
Toronto-Montreal-Ottawa is under the world's shortest leg (`tests/BUILD_NOTES.md`, template change requests).

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list
  (codes for rules this directive lacks) plus `BUSINESS_CLASS_APPROVED`, `SELF_APPROVAL_NOT_ALLOWED`,
  `CONTRACT_EXCLUDES_TRAVEL_COSTS`, `REGULAR_COMMUTE`, `ARRIVES_AFTER_BUSINESS_STARTS`, `SPECIAL_STATUS_LAPSED` and
  `TRAVEL_APPROVAL_LEVEL`, and decoy codes from other handbooks' rules. Fares are in cents of Canadian dollars.
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Approvers** (template rule 4'): a booking accepts each sign-off on file that it relies on (the travel plan's
  approver, and the business-class approver) and `NONE`; a refusal accepts `NONE` and any sign-off on file; a hold
  accepts only the awaited role and its permitted delegate. A sign-off whose invalidity is the case (an assistant
  deputy minister's or the traveller's own business-class approval, a chair's approval after special status lapsed)
  is not accepted for its giver.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller asked
  for, the reason code gives why the request is declined. A refused business cabin (`dune-mallow`, `garnet-moor`,
  `moss-quill`) accepts only the codes naming the ground, not `LOWEST_FARE`. An airline, a colleague's flight or a
  refundable fare declined because a cheaper fare exists (`nutmeg-shoal`, `rowan-spindle`, `sorrel-beacon`) keeps
  `LOWEST_FARE` beside the specific code: the ground there is the lowest-fare rule itself.
- **No hidden facts:** no scenario has `answer_key_inputs`.
- **Decisions:** 18 BOOK (4 business, 14 economy), 3 REFUSE, 3 FLAG. The always-cheapest agent (cheapest seat,
  `LOWEST_FARE`, `NONE`) passes 10 of 24; in three of them the request pulls away from the cheapest seat. The
  always-flag agent passes 1.

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (frozen lines of must_keep) |
|---|---|---|---|---|---|
| `alder-quay` | easy | BOOK (midday-economy; ECONOMY) | LOWEST_FARE | MANAGER_SUPERVISOR or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (558-559, 306-315, 343-345) |
| `birch-lantern` | easy | BOOK (united-economy; ECONOMY) | LOWEST_FARE | NONE or SECRETARY_TB_MBC | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (558-559, 306-315, 466-467) |
| `cedar-wren` | easy | BOOK (westjet-business; BUSINESS) | BUSINESS_CLASS_APPROVED or MEDICAL_NEED | CEO or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_COMMISSION_PUBLIC_BODIES or TRANSPORTATION (559-564, 317-328) |
| `dune-mallow` | easy | BOOK (calgary-economy; ECONOMY) | UPGRADE_NOT_ELIGIBLE | NONE or SECRETARY_TB_MBC | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (559-564, 558-559, 306-315) |
| `ember-sill` | easy | BOOK (noon-flex; ECONOMY) | LOWEST_FARE | MANAGER_SUPERVISOR or NONE | AIR_TRAVEL or APPENDIX_REVISIONS or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (558-559, 306-315, 343-345) |
| `fennel-cove` | boundary_twin | BOOK (british-business; BUSINESS) | BUSINESS_CLASS_APPROVED or INTERNATIONAL_LONG_FLIGHT | CABINET_SECRETARY or DEPUTY_MINISTER or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (559-564, 306-315, 447-460) |
| `garnet-moor` | boundary_twin | BOOK (frankfurt-economy; ECONOMY) | UPGRADE_NOT_ELIGIBLE | CABINET_SECRETARY or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (559-564, 558-559, 306-315, 447-460) |
| `heron-flint` | boundary_twin | BOOK (montreal-economy; ECONOMY) | LOWEST_FARE | CEO or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_COMMISSION_PUBLIC_BODIES or TRANSPORTATION (558-559, 317-328, 1046-1048) |
| `iris-kettle` | boundary_twin | REFUSE (-; NONE) | CONTRACT_EXCLUDES_TRAVEL_COSTS or OUTSIDE_POLICY_SCOPE | CEO or NONE | CONSULTANTS_AND_CONTRACTORS (1046-1048, 78-79, 300-302) |
| `juniper-weir` | boundary_twin | BOOK (westjet-economy; ECONOMY) | LOWEST_FARE | NONE | AIR_TRAVEL or APPENDIX_APPROVAL_SUMMARY or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (558-559, 306-315, 346) |
| `kelp-arbor` | boundary_twin | BOOK (early-economy; ECONOMY) | ARRIVES_AFTER_BUSINESS_STARTS or LOWEST_FARE | NONE | AIR_TRAVEL or APPENDIX_APPROVAL_SUMMARY or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (558-559, 306-315, 346) |
| `larch-pebble` | multi_rule | BOOK (lufthansa-business; BUSINESS) | BUSINESS_CLASS_APPROVED or INTERNATIONAL_LONG_FLIGHT | CABINET_SECRETARY or DEPUTY_MINISTER or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or DELEGATION_OF_AUTHORITY or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (559-564, 306-315, 367-381, 447-460) |
| `moss-quill` | multi_rule | BOOK (amsterdam-economy; ECONOMY) | SELF_APPROVAL_NOT_ALLOWED or UPGRADE_NOT_ELIGIBLE | CABINET_SECRETARY or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_COMMISSION_PUBLIC_BODIES or GENERAL_REQUIREMENTS or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (559-564, 144-149, 317-328, 447-460) |
| `nutmeg-shoal` | multi_rule | BOOK (westjet-economy; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | CEO or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or BEFORE_TRAVELLING or CHART_COMMISSION_PUBLIC_BODIES or TRANSPORTATION (558-559, 432-437, 317-328, 545-548) |
| `opal-thicket` | multi_rule | BOOK (british-business; BUSINESS) | BUSINESS_CLASS_APPROVED or INTERNATIONAL_LONG_FLIGHT | CEO or MINISTER or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_OTHER_AGENCIES or SECURITY_ASSESSMENT or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (559-564, 330-341, 271-273, 447-460) |
| `pine-ferry` | hidden_clause | BOOK (westjet-economy; ECONOMY) | LOWEST_FARE | CEO or CFO or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_COMMISSION_PUBLIC_BODIES or DELEGATION_OF_AUTHORITY or TRANSPORTATION (558-559, 317-328, 396-405) |
| `quartz-meadow` | hidden_clause | BOOK (airfrance-economy; ECONOMY) | LOWEST_FARE | CHAIR or NONE | AIR_TRAVEL or APPENDIX_SPECIAL_STATUS or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_OTHER_AGENCIES or SECURITY_ASSESSMENT or SPECIAL_STATUS or TRANSPORTATION or TRAVELLING_OUTSIDE_CANADA (558-559, 277-291, 1233-1246, 447-460) |
| `rowan-spindle` | distractor | BOOK (westjet-economy; ECONOMY) | COST_SAVINGS or LOWEST_FARE | NONE or SECRETARY_TB_MBC | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_MINISTRIES or TRANSPORTATION (558-559, 306-315) |
| `sorrel-beacon` | distractor | BOOK (westjet-economy; ECONOMY) | LOWEST_FARE or REFUNDABLE_FARE_NOT_ALLOWED | CEO or NONE | AIR_TRAVEL or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or CHART_COMMISSION_PUBLIC_BODIES or TRANSPORTATION (558-559, 317-328) |
| `tansy-grove` | refusal | REFUSE (-; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED or REGULAR_COMMUTE | NONE | TRAVEL (239-241) |
| `umber-reed` | refusal | REFUSE (-; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE or SECRETARY_TB_MBC | GENERAL_REQUIREMENTS or PRINCIPLES or TRAVEL (111-112, 145-146, 239-241) |
| `vetch-harbor` | flag | FLAG_FOR_APPROVAL (jetblue-economy; ECONOMY) | APPROVAL_REQUIRED or TRAVEL_APPROVAL_LEVEL | DEPUTY_MINISTER or SECRETARY_TB_MBC | APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or BEFORE_TRAVELLING or CHART_MINISTRIES or SECURITY_ASSESSMENT or TRAVELLING_OUTSIDE_CANADA (306-315, 409-412, 447-460) |
| `willow-strand` | flag | FLAG_FOR_APPROVAL (airfrance-economy; ECONOMY) | APPROVAL_REQUIRED or SPECIAL_STATUS_LAPSED or TRAVEL_APPROVAL_LEVEL | DEPUTY_MINISTER or MINISTER | APPENDIX_SPECIAL_STATUS or APPROVALS_FOR_TRAVEL or APPROVAL_FOR_TRAVEL_PLANS or BEFORE_TRAVELLING or CHART_OTHER_AGENCIES or SECURITY_ASSESSMENT or SPECIAL_STATUS or TRAVELLING_OUTSIDE_CANADA (277-291, 1233-1246, 330-341, 409-412) |
| `yarrow-crest` | flag | FLAG_FOR_APPROVAL (afternoon-economy; afternoon-flex; ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | MANAGER_SUPERVISOR or NOT_NAMED | AIR_TRAVEL or APPENDIX_REVISIONS or TRANSPORTATION (558-559, 1399-1402, 1064) |

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, role and organisation, route, dates, when the work begins, purpose, requested cabin, airline, flight and fare type, sign-offs, colleagues already ticketed | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-ontario-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this directive's scenario ids, approvers, sections, seven reason
  codes, decoys and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  directive's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this directive's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: decisions taken during the build, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/ontario-travel-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
