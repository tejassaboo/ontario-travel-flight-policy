"""The answer key's rules for the Ontario Travel, Meal and Hospitality Expenses Directive (Management Board of
Cabinet, last amended January 1, 2020), as exact integer code. Byte-identical in src/plugin/rules.py and
verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The rules, by line:

- Lines 558-559 (Air Travel): air when it is the most practical and economical way; "Choose the lowest fare
  available when purchasing a ticket". There is no fare window and no nonstop allowance: the key is the
  cheapest seat that can be bought on a flight landing before the work at the destination begins (every
  scenario states when that is; a flight that lands after it is not a practical way to get there).
- Lines 559-564: business class "must have prior approval by the deputy minister or CEO, in limited
  circumstances such as" international flights, or flights within Canada and the USA for a reasonable
  accommodation (e.g. health reasons). Line 149: approvers may not approve their own expenses. A business
  request without a valid prior approval gets the lowest economy fare (every such request says economy will
  do). A domestic approval for a reason outside the two listed is the "such as" question; no scenario asks it.
- Lines 304-347 (Charts 1-3 and footnotes 2-4): who approves the travel plan, by organisation, role and
  destination tier (within Ontario, outside Ontario within Canada and the USA, international). Footnote 2:
  within Ontario includes the National Capital Region and an out-of-province routing that is more economical
  between provincial destinations (so the tier follows the trip's two ends). Footnote 3: N/A, no approval.
- Lines 275-291 and 1227-1246 (special status): an agency or organisation with special status has its
  international travel approved by the chair (the chair's own by the Minister; the chair may delegate staff
  approvals to the CEO). "Special status is approved for three years only" (line 290).
- Lines 349-405 (delegation): the Secretary of the Cabinet may delegate to a deputy minister for their
  ministry or to the Secretary of TB/MBC; the Secretary of TB/MBC to the deputy minister; a minister, for
  others than chairs and appointees, to deputy ministers; a CEO to the CFO.
- Lines 409-412, 447-460: prior documented approval; outside Canada, the right approval and a security
  assessment (every outside-Canada record holds a completed one).
- Lines 239-241: a regular commute is not travel. Lines 105-112 and 145-146: only government business.
  Lines 1046-1048: a consultant's or contractor's expenses only when their contract allows for them.
- Lines 1399-1402 (Appendix C, revisions of January 1, 2020): "added option for flexibility for those whose
  schedules frequently change" for airplane and train, while the Air Travel text itself (lines 556-566) holds
  no such option. For a traveller whose schedule often changes who asks for a changeable fare dearer than the
  lowest one, the directive is unclear (one flag scenario).

The handbook has no flight-duration threshold, so DURATION_RULES is empty and over() raises for any name.

Approvers (template SYNC_NOTES rule 4'): a BOOK whose travel approval (and business-class approval) is on file
accepts each of those roles and NONE; a refusal accepts NONE and any sign-off on file (rule 4(b)); a hold
accepts only the awaited roles (with the role's permitted delegate). A sign-off whose invalidity is the point
of the case (an assistant deputy minister's or the traveller's own business-class approval, a chair's approval
after special status lapsed) is not accepted for its giver.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    Decision,
    OrganizationKind,
    Purpose,
    ReasonCode,
    SignOffSubject,
    TravellerRole,
)

from .world import day_number, utc_minute, utc_offset

HANDBOOK = "Ontario Travel, Meal and Hospitality Expenses Directive, last amended January 1, 2020"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.PURPOSE: "1.0 PURPOSE",
    Clause.APPLICATION_AND_SCOPE: "1.1 Application and Scope",
    Clause.PRINCIPLES: "2.1 Principles",
    Clause.BEST_PRACTICES: "2.2 Best Practices",
    Clause.GENERAL_REQUIREMENTS: "3.0 REQUIREMENTS - GENERAL",
    Clause.ACCOUNTABILITY_FRAMEWORK: "4.0 ACCOUNTABILITY FRAMEWORK",
    Clause.MANAGERIAL_DISCRETION: "4.1 Managerial Discretion",
    Clause.TRAVEL: "5.0 TRAVEL",
    Clause.REGULAR_PART_OF_JOB: "5.1 When Travel is a Regular Part of the Job",
    Clause.OCCASIONAL_TRAVEL: "5.2 When Travel Occurs Occasionally",
    Clause.APPROVALS_FOR_TRAVEL: "5.3 Approvals for Travel",
    Clause.SPECIAL_STATUS: "Special Status for International Travel",
    Clause.APPROVAL_FOR_TRAVEL_PLANS: "Approval for Travel Plans",
    Clause.CHART_MINISTRIES: "Level of Approval Required in Ministries",
    Clause.CHART_COMMISSION_PUBLIC_BODIES: "Level of Approval Required in Provincial Agencies whose Employees are Appointed",
    Clause.CHART_OTHER_AGENCIES: "Level of Approval Required in Provincial Agencies/Organizations whose Employees",
    Clause.DELEGATION_OF_AUTHORITY: "5.4 Delegation of Authority for Travel Approvals",
    Clause.BEFORE_TRAVELLING: "5.5 Before Travelling",
    Clause.TRAVELLING_OUTSIDE_CANADA: "Travelling Outside Canada",
    Clause.SECURITY_ASSESSMENT: "Security Assessment",
    Clause.TRANSPORTATION: "5.6 Transportation - How to Get There",
    Clause.AIR_TRAVEL: "Air Travel",
    Clause.RAIL_TRAVEL: "Rail Travel",
    Clause.ROAD_TRAVEL: "Road Travel",
    Clause.ACCOMMODATION: "5.7 Accommodation",
    Clause.INCIDENTAL_EXPENSES: "5.8 Incidental Expenses",
    Clause.MEALS: "6.0 MEALS",
    Clause.HOSPITALITY: "7.0 HOSPITALITY",
    Clause.CONSULTANTS_AND_CONTRACTORS: "8.0 EXPENSES FOR CONSULTANTS AND OTHER CONTRACTORS",
    Clause.RESPONSIBILITIES: "9.0 RESPONSIBILITIES",
    Clause.DEFINITIONS: "10.0 DEFINITIONS",
    Clause.APPENDIX_SPECIAL_STATUS: "11.1 Appendix A: Requesting Special Status for International Travel and/or",
    Clause.APPENDIX_APPROVAL_SUMMARY: "11.2 Appendix B: Summary of Approval Authority",
    Clause.APPENDIX_REVISIONS: "11.3 Appendix C: Revisions to the Travel, Meal and Hospitality Expenses",
}

# The handbook has no flight-duration threshold (its only "hours" are car-sharing's, line 635).
DURATION_RULES = ()

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# The world's airports in Ontario (Toronto; Ottawa, in the National Capital Region, footnote 2 at line 344).
ONTARIO = ("YYZ", "YOW")
CANADA_USA = ("CA", "US")
WITHIN, CANADA_OR_USA, INTERNATIONAL = "within Ontario", "outside Ontario, within Canada and the USA", "international"
# A flight must land at least this long before the work starts to count as in time (and every late one lands
# after the start), so that no scenario turns on minutes of airport transfer.
ARRIVAL_MARGIN_MINUTES = 90
# Line 290: "Special status is approved for three years only."
SPECIAL_STATUS_YEARS = 3

M, A = Approver.MANAGER_SUPERVISOR, Approver.CONTRACT_MANAGER
SEC_TB, CAB, MIN = Approver.SECRETARY_TB_MBC, Approver.CABINET_SECRETARY, Approver.MINISTER
CHAIR, CEO = Approver.CHAIR, Approver.CEO
R = TravellerRole
# Charts 1-3 (lines 306-341): (within Ontario, outside Ontario within Canada and the USA, international);
# None is N/A ("Given the level of responsibility, no approvals are required", footnote 3, line 346).
MINISTRY_CHART = {R.DEPUTY_MINISTER: (None, SEC_TB, CAB), R.EMPLOYEE: (M, SEC_TB, CAB), R.CONSULTANT: (A, SEC_TB, CAB)}
COMMISSION_CHART = {R.CHAIR: (None, None, MIN), R.APPOINTEE: (CHAIR, CHAIR, MIN), R.CEO: (None, None, CAB),
                    R.EMPLOYEE: (M, CEO, CAB), R.CONSULTANT: (A, CEO, CAB)}
OTHER_CHART = {R.CHAIR: (None, None, MIN), R.APPOINTEE: (CHAIR, CHAIR, MIN), R.CEO: (None, None, MIN),
               R.EMPLOYEE: (M, CEO, MIN), R.CONSULTANT: (A, CEO, MIN)}
CHARTS = {
    OrganizationKind.MINISTRY: (MINISTRY_CHART, Clause.CHART_MINISTRIES),
    OrganizationKind.COMMISSION_PUBLIC_BODY: (COMMISSION_CHART, Clause.CHART_COMMISSION_PUBLIC_BODIES),
    OrganizationKind.OTHER_PROVINCIAL_AGENCY: (OTHER_CHART, Clause.CHART_OTHER_AGENCIES),
    # Lines 271-273: Chart 3 "includes the Independent Electricity System Operator and Ontario Power Generation".
    OrganizationKind.ELECTRICITY_ORGANIZATION: (OTHER_CHART, Clause.CHART_OTHER_AGENCIES),
}
# Lines 1241-1246: approval levels for international travel once special status is granted.
SPECIAL_CHART = {R.CHAIR: MIN, R.APPOINTEE: CHAIR, R.CEO: CHAIR, R.EMPLOYEE: CHAIR, R.CONSULTANT: CHAIR}
# Lines 355-405 (and 1236-1238): whom each approver may delegate travel approval to.
DELEGATES = {CAB: (Approver.DEPUTY_MINISTER, SEC_TB), SEC_TB: (Approver.DEPUTY_MINISTER,),
             MIN: (Approver.DEPUTY_MINISTER,), CEO: (Approver.CFO,)}
# Lines 559-560: business class "must have prior approval by the deputy minister or CEO".
BUSINESS_APPROVERS = (Approver.DEPUTY_MINISTER, Approver.CEO)

FLEX_PHRASE = "added option for flexibility for those whose schedules frequently change"
UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]

AIR = [Clause.AIR_TRAVEL, Clause.TRANSPORTATION]
APPROVAL_CLAUSES = [Clause.APPROVALS_FOR_TRAVEL, Clause.APPROVAL_FOR_TRAVEL_PLANS]
ABROAD_CLAUSES = [Clause.TRAVELLING_OUTSIDE_CANADA, Clause.SECURITY_ASSESSMENT]


def over(rule, offer):
    """The duration hook: this handbook has no duration threshold, so every name is unknown."""
    raise ValueError(f"unknown duration rule {rule!r}: the directive sets no flight-duration limit")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def one(offers, what):
    if len(offers) != 1:
        raise ValueError(f"{what}: {len(offers)} offers tie or none is listed; not modelled")
    return offers[0]


def on_route(trip, offers):
    return [offer for offer in offers if offer.segments[0].origin == trip.origin.code
            and offer.segments[-1].destination == trip.destination.code
            and offer.segments[0].depart_local[:10] == trip.travel_date]


def start_utc(trip):
    """The minute (UTC) the work at the destination begins."""
    return utc_minute(trip.business_starts) - utc_offset(trip.destination.code)


def in_time(trip, offers):
    """The offers landing in time for the work, and whether any listed seat lands after it starts."""
    start = start_utc(trip)
    timely, late = [], False
    for offer in offers:
        landing = utc_minute(offer.segments[-1].arrive_utc)
        if landing + ARRIVAL_MARGIN_MINUTES <= start:
            timely.append(offer)
        elif landing > start:
            late = True
        else:
            raise ValueError(f"{offer.offer_id} lands less than {ARRIVAL_MARGIN_MINUTES} minutes before the work starts")
    return timely, late


def tier(trip):
    """Footnote 2 (lines 343-345): the tier follows the trip's two ends, whatever the routing between them."""
    if trip.origin.code not in ONTARIO:
        raise ValueError("a trip that does not start in Ontario is not modelled")
    if trip.destination.code in ONTARIO:
        return WITHIN
    return CANADA_OR_USA if trip.destination.country in CANADA_USA else INTERNATIONAL


def special_status(trip):
    """True when the agency's special status for international travel is current on the booking and travel
    dates; False when it lapsed before both or was never granted (line 290: three years only)."""
    granted = trip.special_status_granted_on
    if not granted:
        return False
    if trip.organization_kind == OrganizationKind.MINISTRY:
        raise ValueError("a ministry with special status is not modelled")
    ends = f"{int(granted[:4]) + SPECIAL_STATUS_YEARS}{granted[4:]}"
    current = {day_number(day) < day_number(ends) for day in (trip.booking_date, trip.travel_date)}
    if len(current) != 1 or day_number(granted) > day_number(trip.booking_date):
        raise ValueError("special status that lapses between booking and travel is not modelled")
    return current.pop()


def required_approver(trip):
    """The role that approves this travel plan (None: no approval required) and the sections that say so."""
    chart, chart_clause = CHARTS[trip.organization_kind]
    where = tier(trip)
    clauses = [*APPROVAL_CLAUSES, chart_clause]
    if where == INTERNATIONAL and trip.organization_kind != OrganizationKind.MINISTRY and special_status(trip):
        return SPECIAL_CHART[trip.traveller_role], [*clauses, Clause.SPECIAL_STATUS, Clause.APPENDIX_SPECIAL_STATUS]
    row = chart.get(trip.traveller_role)
    if row is None:
        raise ValueError(f"{trip.traveller_role} has no row in the chart for {trip.organization_kind}")
    return row[(WITHIN, CANADA_OR_USA, INTERNATIONAL).index(where)], clauses


def travel_sign_offs(trip, needed):
    """The valid travel-plan sign-offs on file for the needed role: the role itself, or its delegate acting for
    it in writing (lines 349-405). Returns (roles to accept, extra sections)."""
    roles, clauses = [], []
    for record in trip.sign_offs:
        if record.subject != SignOffSubject.TRAVEL_PLAN:
            continue
        if record.name == trip.traveller_name:
            raise ValueError("a traveller approving their own travel plan is not modelled")
        if record.acting_for == Approver.NONE and record.role == needed:
            roles.append(record.role)
        elif record.acting_for == needed and record.role in DELEGATES.get(needed, ()):
            if trip.traveller_role in (R.CHAIR, R.APPOINTEE, R.CEO):
                raise ValueError("a delegated approval for a chair, appointee or CEO is not modelled")
            roles += [record.role, needed]
            clauses.append(Clause.DELEGATION_OF_AUTHORITY)
    return roles, clauses


def awaited(needed):
    return [needed, *DELEGATES.get(needed, ())]


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its searches: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.return_date:
        raise ValueError("a round-trip ticket is not modelled")
    on_file = [record.role for record in trip.sign_offs]
    unused = [Approver.NONE, *on_file]
    if trip.purpose_kind == Purpose.REGULAR_OFFICE_DAY:
        if trip.destination.city != trip.workplace_city or trip.home_city == trip.workplace_city:
            raise ValueError("a regular office day must take the traveller from home to their own workplace")
        return answer(Decision.REFUSE, [], [ReasonCode.REGULAR_COMMUTE, ReasonCode.OUTSIDE_POLICY_SCOPE,
                                            ReasonCode.PERSONAL_TRAVEL_NOT_COVERED], unused, [Clause.TRAVEL],
                      "Lines 239-241: travel does not refer to a person's regular commute to work, and expenses "
                      "related to it are not reimbursable. The flight takes the traveller from home to their own "
                      "regular workplace; the government buys no ticket.")
    if trip.purpose_kind == Purpose.PERSONAL_VISIT:
        return answer(Decision.REFUSE, [], [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      unused, [Clause.TRAVEL, Clause.PRINCIPLES, Clause.GENERAL_REQUIREMENTS],
                      "Lines 111-112 and 145-146: only expenses incurred in the course of government business are "
                      "reimbursed or approved, and line 239: the directive applies when travel is required. The "
                      "business reason is gone and the trip is personal; the government buys no ticket.")
    if trip.traveller_role == R.CONSULTANT and not trip.contract_covers_travel_costs:
        return answer(Decision.REFUSE, [], [ReasonCode.CONTRACT_EXCLUDES_TRAVEL_COSTS, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      unused, [Clause.CONSULTANTS_AND_CONTRACTORS, Clause.APPROVALS_FOR_TRAVEL],
                      "Lines 1046-1048: a consultant or contractor can claim expenses allowable under the directive "
                      "only when their contract specifically allows for it; this contract does not cover travel "
                      "costs, and footnote 1 (lines 300-302) says the travel approval is not an approval of "
                      "expenses. The organisation buys no ticket.")
    if trip.traveller_role != R.CONSULTANT and trip.contract_covers_travel_costs:
        raise ValueError("only a consultant has a contract that covers travel costs")
    where = tier(trip)
    if where != WITHIN and trip.destination.country != "CA" and not trip.security_review_done:
        raise ValueError("a trip outside Canada without the security assessment is not modelled")
    seated = [offer for offer in on_route(trip, offers) if offer.seats_available]
    if any(offer.cabin not in (Cabin.ECONOMY, Cabin.BUSINESS) for offer in seated):
        raise ValueError("only economy and business seats are modelled")
    seated, late = in_time(trip, seated)
    economy = [offer for offer in seated if offer.cabin == Cabin.ECONOMY]
    needed, clauses = required_approver(trip)
    if where != WITHIN and trip.destination.country != "CA":
        clauses = [*clauses, *ABROAD_CLAUSES]
    if needed is None:
        if any(record.subject == SignOffSubject.TRAVEL_PLAN for record in trip.sign_offs):
            raise ValueError("a travel-plan sign-off where none is required is not modelled")
        roles, notes = [], [("footnote 3 (line 346): given the level of responsibility, no approval of the travel plan "
                            "is required")]
        clauses = [*clauses, Clause.APPENDIX_APPROVAL_SUMMARY]
    else:
        roles, extra = travel_sign_offs(trip, needed)
        clauses = [*clauses, *extra]
        notes = [(f"lines 304-347: the travel plan ({where}) is approved by the {needed.value}, and that approval is on "
                 "file")]
        if not roles:
            return hold_for_approval(trip, economy, needed, clauses)
    roles = [Approver.NONE, *roles]
    if trip.requested_cabin == Cabin.BUSINESS:
        return business_request(trip, seated, economy, roles, clauses, notes, where)
    if trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError("only economy and business requests are modelled")
    if any(record.subject == SignOffSubject.BUSINESS_CLASS for record in trip.sign_offs):
        raise ValueError("a business-class approval on an economy request is not modelled")
    return economy_request(trip, economy, late, roles, clauses, notes)


def hold_for_approval(trip, economy, needed, clauses):
    """Lines 304-347 and 409-412 (448-452 outside Canada): the travel plan needs the needed role's prior
    documented approval, and none valid is on file: hold the fare the directive would buy."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.wants_changeable_fare or trip.requested_airline:
        raise ValueError("a missing travel approval on anything but a plain economy request is not modelled")
    low = cheapest(economy)
    one(low, "held fare")
    reasons = [ReasonCode.APPROVAL_REQUIRED, ReasonCode.TRAVEL_APPROVAL_LEVEL]
    clauses = [*clauses, Clause.BEFORE_TRAVELLING]
    why = (f"Lines 304-347: this travel plan ({tier(trip)}) must be approved by the {needed.value} (or, under a "
           "written delegation of lines 349-405, its delegate), and lines 409-412 require that approval before the "
           "trip; the sign-off on file is from someone else.")
    if trip.special_status_granted_on:
        reasons.append(ReasonCode.SPECIAL_STATUS_LAPSED)
        clauses += [Clause.SPECIAL_STATUS, Clause.APPENDIX_SPECIAL_STATUS]
        why += (" Line 290: special status is approved for three years only; it was granted on "
                f"{trip.special_status_granted_on} and has lapsed, so the chair's approval no longer stands in for "
                "the chart's.")
    return answer(Decision.FLAG_FOR_APPROVAL, low, reasons, awaited(needed), clauses,
                  why + " Hold the lowest fare for that approval.")


def economy_request(trip, economy, late, roles, clauses, notes):
    """Lines 558-559: the lowest fare available, on a flight that lands before the work begins."""
    low = cheapest(economy)
    one(low, "lowest fare")
    chosen = low[0]
    reasons = [ReasonCode.LOWEST_FARE]
    clauses = [*AIR, *clauses]
    notes = ["lines 558-559: air is the practical and economical way, and the lowest fare available is chosen", *notes]
    if late:
        reasons.append(ReasonCode.ARRIVES_AFTER_BUSINESS_STARTS)
        notes.append("a cheaper seat lands after the work begins, so it is not a practical way to get there")
    if trip.wants_changeable_fare:
        return changeable(trip, economy, chosen, reasons, roles, clauses, notes)
    if trip.requested_airline:
        if chosen.carrier == trip.requested_airline:
            raise ValueError("an airline wish the lowest fare already meets is not modelled")
        # Lines 432-437 allow loyalty programmes only with the most cost-effective method of travel: the ground is
        # the lowest-fare rule itself, so LOWEST_FARE stays beside LOYALTY_PROGRAM_PREFERENCE.
        reasons.append(ReasonCode.LOYALTY_PROGRAM_PREFERENCE)
        clauses.append(Clause.BEFORE_TRAVELLING)
        notes.append("lines 432-437: loyalty programmes are permitted provided the most cost-effective method of travel "
                     "is chosen, through the travel management company")
    if trip.requested_flight:
        if trip.requested_flight in [segment.flight_number for segment in chosen.segments]:
            raise ValueError("a flight wish the lowest fare already meets is not modelled")
        reasons.append(ReasonCode.COST_SAVINGS)
        notes.append("the colleague's flight is dearer; nothing in the air rules lets a traveller pay more to sit with "
                     "a colleague (the team reason of lines 574 is for rail business class)")
    return answer(Decision.BOOK, low, reasons, roles, clauses, "; ".join(notes) + ".")


def changeable(trip, economy, chosen, reasons, roles, clauses, notes):
    """A changeable fare asked for. Lines 558-559: the lowest fare. Lines 1399-1402 record a 2020 'option for
    flexibility for those whose schedules frequently change' that the air text does not contain."""
    if trip.requested_airline or trip.requested_flight:
        raise ValueError("a changeable fare with another wish is not modelled")
    if chosen.refundable:
        if not trip.schedule_often_changes:
            raise ValueError("a refundable lowest fare for a traveller without changing schedules is not modelled")
        return answer(Decision.BOOK, [chosen], reasons, roles, [*clauses, Clause.APPENDIX_REVISIONS],
                      "; ".join(notes) + "; the lowest fare that can be bought is itself changeable, so every reading "
                      "gives the traveller the flexible fare they ask for.")
    if not trip.schedule_often_changes:
        return answer(Decision.BOOK, [chosen], [*reasons, ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED], roles, clauses,
                      "; ".join(notes) + "; the traveller's schedule is not one that frequently changes, so the 2020 "
                      "flexibility note of lines 1399-1402 does not reach them, and the lower non-changeable fare is "
                      "bought.")
    flexible = cheapest([offer for offer in economy if offer.refundable])
    one(flexible, "cheapest changeable fare")
    # No role is named for the option. A hold may also name the deputy minister, who may set additional rules on
    # expenses (lines 167-172), or TB/MBC, the only body that grants an exemption from the directive (lines 207-209).
    approvers = [Approver.NOT_NAMED, Approver.DEPUTY_MINISTER, Approver.TREASURY_BOARD,
                 *[role for role in roles if role == Approver.MANAGER_SUPERVISOR]]
    return answer(Decision.FLAG_FOR_APPROVAL, [chosen, *flexible], UNCLEAR_REASONS, approvers,
                  [*AIR, Clause.APPENDIX_REVISIONS, Clause.RESPONSIBILITIES, Clause.ACCOUNTABILITY_FRAMEWORK,
                   Clause.MANAGERIAL_DISCRETION],
                  "Lines 558-559 say to choose the lowest fare available, with no exception; Appendix C (lines "
                  "1399-1402) says the 2020 revision of Airplane and Train identified the lowest fare as the standard "
                  "and 'added option for flexibility for those whose schedules frequently change'. The traveller's "
                  "schedule does change often. Whether the directive gives them a changeable fare dearer than the "
                  "lowest is open: hold the lowest fare or the cheapest changeable fare. No role is named; the "
                  "manager seeks direction on questions of application (line 1064); the deputy minister may set "
                  "additional rules (lines 167-172) and only TB/MBC grants an exemption (lines 207-209).",
                  phrase=FLEX_PHRASE)


def business_request(trip, seated, economy, roles, clauses, notes, where):
    """Lines 559-564 and line 149: business class only with the deputy minister's or CEO's prior approval, for an
    international flight or for a reasonable accommodation within Canada and the USA."""
    if trip.wants_changeable_fare or trip.requested_airline or trip.requested_flight:
        raise ValueError("a business request with another wish is not modelled")
    approvals = [record for record in trip.sign_offs if record.subject == SignOffSubject.BUSINESS_CLASS]
    if len(approvals) > 1:
        raise ValueError("several business-class sign-offs are not modelled")
    circumstance = where == INTERNATIONAL or bool(trip.health_need_on_file)
    record = approvals[0] if approvals else None
    own = record is not None and record.name == trip.traveller_name
    valid = record is not None and record.role in BUSINESS_APPROVERS and record.acting_for == Approver.NONE and not own
    if valid and not circumstance:
        raise ValueError("a business approval outside the listed circumstances ('such as') is not modelled")
    if valid:
        business = cheapest([offer for offer in seated if offer.cabin == Cabin.BUSINESS])
        one(business, "cheapest business fare")
        reasons = [ReasonCode.BUSINESS_CLASS_APPROVED]
        if where == INTERNATIONAL:
            if trip.health_need_on_file:
                raise ValueError("an international business request with a health need is not modelled")
            reasons.append(ReasonCode.INTERNATIONAL_LONG_FLIGHT)
            why = "an international flight"
        else:
            reasons.append(ReasonCode.MEDICAL_NEED)
            why = "a flight within Canada and the USA for a reasonable accommodation (a documented health need)"
        return answer(Decision.BOOK, business, reasons, [*roles, record.role], [*AIR, *clauses],
                      f"Lines 559-564: business class with the prior approval of the {record.role.value}, on {why}; "
                      f"the lowest business fare that lands in time; " + "; ".join(notes) + ".")
    low = cheapest(economy)
    one(low, "lowest economy fare")
    reasons = [ReasonCode.UPGRADE_NOT_ELIGIBLE]
    extra = []
    if own:
        reasons.append(ReasonCode.SELF_APPROVAL_NOT_ALLOWED)
        extra.append(Clause.GENERAL_REQUIREMENTS)
        why = "the business-class approval on file is the traveller's own, and line 149 says approvers may not " \
              "approve their own expenses"
    elif record is not None:
        # The sign-off is at the wrong level, so a reason naming the approval level is also right.
        reasons.append(ReasonCode.TRAVEL_APPROVAL_LEVEL)
        why = f"the business-class approval on file is from the {record.role.value}, not the deputy minister or CEO"
    elif circumstance:
        why = "no deputy minister's or CEO's prior approval of business class is on file"
    else:
        why = "the flight is within Canada and the USA with no accommodation need, and no prior approval is on file"
    return answer(Decision.BOOK, low, reasons, roles, [*AIR, *extra, *clauses],
                  f"Lines 559-564: business class must have the deputy minister's or CEO's prior approval; {why}. The "
                  "traveller accepts economy otherwise: the lowest economy fare (lines 558-559); " + "; ".join(notes) + ".")
