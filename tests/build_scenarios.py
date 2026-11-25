"""Writes the Ontario travel directive scenario JSON files (an authoring aid, not a test; the JSON files are the
truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (a colleague's flight) are read from the shared world, so they
match what search_flights lists. Expected answers are hand-written here; tests/test_scenarios.py checks them
against rules.solve.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
LOWEST = keep(558, 559, "Air travel is permitted when it is the most practical and economical way to travel. Choose "
              "the lowest fare available when purchasing a ticket.", "air when practical and economical; the lowest fare")
BUSINESS = keep(559, 564, None, "business class only with the deputy minister's or CEO's prior approval: international "
                "flights, or Canada/USA flights for a reasonable accommodation")
TMC = keep(545, 548, None, "airfare is booked through the government's travel management company")
CHART_ONE = keep(306, 315, None, "Chart 1: who approves a ministry's travel plans, by role and destination")
CHART_TWO = keep(317, 328, None, "Chart 2: who approves a Commission public body's travel plans")
CHART_THREE = keep(330, 341, None, "Chart 3: who approves other agencies' and organizations' travel plans")
WITHIN_NOTE = keep(343, 345, None, "within Ontario includes Ottawa and a cheaper routing outside the province")
NO_APPROVAL = keep(346, 346, "3 Given the level of responsibility, no approvals are required.",
                   "footnote 3: N/A means no approval is required")
CHART_THREE_SCOPE = keep(271, 273, None, "Chart 3 includes the electricity system operator and Ontario Power Generation")
SPECIAL = keep(277, 291, None, "special status lets the chair approve international travel; three years only")
SPECIAL_LEVELS = keep(1233, 1246, None, "with special status the chair approves international travel by staff")
DELEGATE = keep(367, 381, None, "the Secretary of the Cabinet may delegate to a deputy minister for their ministry")
PRIOR = keep(409, 412, None, "prior documented approval for travel")
ABROAD = keep(447, 460, None, "travel outside Canada: prior approval, lowest-cost method, security assessment")
SECURITY = keep(466, 467, "When travelling outside Canada, including the USA, a prior assessment of physical and cyber "
                "security is required.", "a security assessment before any trip outside Canada")
SELF = keep(144, 149, None, "approvers may not approve their own expenses")
COMMUTE = keep(239, 241, None, "a regular commute is not travel and is not reimbursable")
GOV_BUSINESS = keep(111, 112, None, "only legitimate expenses in the course of government business are reimbursed")
NECESSARY = keep(145, 146, None, "approval only for expenses necessarily incurred in government business")
CONTRACT = keep(1046, 1048, None, "a contractor's expenses only when the contract allows for them")
CONSULTANTS_COVERED = keep(78, 79, None, "the directive applies to consultants and contractors")
TRAVEL_NOT_EXPENSE = keep(300, 302, None, "footnote 1: the chart approves travel, not the expenses of it")
LOYALTY = keep(432, 437, None, "loyalty programmes only with the most cost-effective method, through the TMC")
REVISION = keep(1399, 1402, None, "the 2020 revision: lowest fare as the standard, an option for flexibility for "
                "those whose schedules frequently change")
DIRECTION = keep(1064, 1064, "seeking timely direction when there are questions of application.",
                 "managers seek direction on questions of application")

# ----- nearby clauses that must not change the answer -----
RAIL_TEAM = aside(571, 574, "the need to work with a team", "a reason for business class on rail, not air")
CONTINUITY = aside(461, 462, "When planning any travel, consider business continuity",
                   "a consideration (should senior people travel together), not a fare rule")
CHANGES = aside(417, 420, "If there is a change in your itinerary, you should:", "how changes are made, not which fare")
CHARTER = aside(565, 566, "In some cases, ministry employees may need to use government-owned and charter aircraft.",
                "charter aircraft are not asked for")
CAR_SHARE = aside(634, 635, "Car-sharing, through the government's vendor of record, can be used if a vehicle is",
                  "car-sharing hours are not a flight rule")
THIRD_PARTY = aside(411, 412, "Note that prior approval is required even in situations where expenses are covered by a "
                    "third party.", "no third party pays here")
REGULAR_JOB = aside(244, 245, "There are some jobs where frequent travel is a requirement",
                    "a job with frequent travel does not change the fare rule")
CEO_DELEGATE = keep(396, 405, None, "the CEO may delegate travel approval to the CFO, not for direct reports")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "traveller_role": "EMPLOYEE", "organization": "",
        "organization_kind": "MINISTRY", "special_status_granted_on": "", "contract_covers_travel_costs": False,
        "home_city": "Toronto", "workplace_city": "Toronto", "origin": "YYZ", "destination": "", "travel_date": "",
        "return_date": "", "booking_date": "", "business_starts": "", "purpose": "", "purpose_kind": "MEETING",
        "requested_cabin": "ECONOMY", "requested_airline": "", "requested_flight": "", "wants_changeable_fare": False,
        "schedule_often_changes": False, "health_need_on_file": "", "security_review_done": False, "sign_offs": [],
        "travelling_with": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def sign(role, name, title, covers, subject="TRAVEL_PLAN", acting_for="NONE"):
    return {"role": role, "name": name, "title": title, "subject": subject, "acting_for": acting_for, "covers": covers}


def offer(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins),
            "reason_codes": sorted(reasons), "approvers": sorted(approvers), "clauses": sorted(clauses),
            "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=0, name="main"):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    if isinstance(searches, dict):
        searches = [searches]
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


# Accepted sections.
AIR = ["AIR_TRAVEL", "TRANSPORTATION"]
APPROVALS = ["APPROVALS_FOR_TRAVEL", "APPROVAL_FOR_TRAVEL_PLANS"]
ABROAD_SECTIONS = ["SECURITY_ASSESSMENT", "TRAVELLING_OUTSIDE_CANADA"]
SPECIAL_SECTIONS = ["APPENDIX_SPECIAL_STATUS", "SPECIAL_STATUS"]
MIN_CH = APPROVALS + ["CHART_MINISTRIES"]
COM_CH = APPROVALS + ["CHART_COMMISSION_PUBLIC_BODIES"]
OTH_CH = APPROVALS + ["CHART_OTHER_AGENCIES"]
LOW = ["LOWEST_FARE"]

# Shared people and organisations.
MINISTRY_ECON = "Ministry of Economic Development and Trade"
MINISTRY_LAB = "Ministry of Labour and Workplace Safety"
MINISTRY_AGRI = "Ministry of Agriculture and Food"
MINISTRY_MUN = "Ministry of Municipal Affairs"
HEARINGS = "Provincial Land and Licensing Hearings Commission (a Commission public body)"
SEC_TB_SIGN = sign("SECRETARY_TB_MBC", "Helen Okafor", "Secretary, Treasury Board/Management Board of Cabinet",
                   "Approves the travel plan, on the form for travel within Canada and the USA")
CAB_SIGN = sign("CABINET_SECRETARY", "Gordon Achebe", "Secretary of the Cabinet",
                "Approves the international travel plan, on the international travel form")

# ===== easy (5) =====

scenario(
    "alder-quay", "easy", [],
    "I need to fly Toronto to Ottawa on December 9th for the interministerial working group, which starts at nine the "
    "next morning. My manager has signed off on the trip.",
    trip(traveller_name="Nadia Petrov", traveller_title="Policy Analyst", organization=MINISTRY_MUN,
         destination="YOW", travel_date="2026-12-09", booking_date="2026-11-25", business_starts="2026-12-10 09:00",
         purpose="Interministerial working group on housing data in Ottawa",
         sign_offs=[sign("MANAGER_SUPERVISOR", "Priya Raman", "Manager, Housing Policy Unit",
                         "Approves the trip to Ottawa")]),
    search("YYZ", "YOW", "2026-12-09", {
        "morning": {"carrier": "AC", "depart": "07:00", "minutes": [65]},
        "midday": {"carrier": "WS", "depart": "10:15", "minutes": [65]},
        "evening": {"carrier": "AC", "depart": "17:30", "minutes": [65]},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 31800),
        offer("morning-business", "morning", "BUSINESS", 58800),
        offer("midday-economy", "midday", "ECONOMY", 24900),
        offer("evening-economy", "evening", "ECONOMY", 27600),
    ]),
    expected("BOOK", ["midday-economy"], ["ECONOMY"], LOW, ["MANAGER_SUPERVISOR", "NONE"], AIR + MIN_CH),
    [LOWEST, CHART_ONE, WITHIN_NOTE],
    "A ministry employee within Ontario: the manager/supervisor approves the travel plan (Chart 1, lines 306-315), "
    "and that approval is on file. Lines 558-559: the lowest fare available, WestJet at $249.")

scenario(
    "birch-lantern", "easy", [],
    "Please book me Toronto to Chicago on January 13th for the Great Lakes trade conference, which opens at nine the "
    "next morning. The Secretary of Treasury Board has approved the trip and the security assessment is done.",
    trip(traveller_name="Marcus Feld", traveller_title="Senior Trade Analyst", organization=MINISTRY_ECON,
         destination="ORD", travel_date="2027-01-13", booking_date="2026-12-01", business_starts="2027-01-14 09:00",
         purpose="Great Lakes trade conference in Chicago", purpose_kind="CONFERENCE", security_review_done=True,
         sign_offs=[SEC_TB_SIGN]),
    search("YYZ", "ORD", "2027-01-13", {
        "early": {"carrier": "AC", "depart": "07:10"},
        "united": {"carrier": "UA", "depart": "09:40"},
        "afternoon": {"carrier": "AC", "depart": "13:15"},
    }, [
        offer("early-economy", "early", "ECONOMY", 33500, seats=False),
        offer("united-economy", "united", "ECONOMY", 36800),
        offer("afternoon-economy", "afternoon", "ECONOMY", 39200),
    ]),
    expected("BOOK", ["united-economy"], ["ECONOMY"], LOW, ["NONE", "SECRETARY_TB_MBC"],
             AIR + MIN_CH + ABROAD_SECTIONS),
    [LOWEST, CHART_ONE, SECURITY],
    "A ministry employee to the USA: Chart 1 gives the Secretary, TB/MBC, whose approval is on file; the security "
    "assessment is done (lines 466-467). The 07:10 seat at $335 is sold out, so the lowest fare available is United "
    "at $368 (lines 558-559).")

scenario(
    "cedar-wren", "easy", ["dearer_option"],
    "Toronto to Vancouver on February 3rd for the licensing hearings, which start at nine the next morning. Because of "
    "my spinal condition my physician says I can't sit upright in economy that long; our CEO approved business class "
    "for me in advance. Business class, please.",
    trip(traveller_name="Olivia Brandt", traveller_title="Senior Hearing Officer", organization=HEARINGS,
         organization_kind="COMMISSION_PUBLIC_BODY", destination="YVR", travel_date="2027-02-03",
         booking_date="2026-12-07", business_starts="2027-02-04 09:00",
         purpose="Licensing hearings in Vancouver", purpose_kind="MEETING", requested_cabin="BUSINESS",
         health_need_on_file="Chronic spinal condition: the physician's note says she must be able to lie back on "
                             "flights over two hours",
         sign_offs=[
             sign("CEO", "Daniel Mercer", "Chief Executive Officer, " + HEARINGS, "Approves the trip to Vancouver"),
             sign("CEO", "Daniel Mercer", "Chief Executive Officer, " + HEARINGS,
                  "Approves business class on this trip because of the documented spinal condition",
                  subject="BUSINESS_CLASS"),
         ]),
    search("YYZ", "YVR", "2027-02-03", {
        "aircanada": {"carrier": "AC", "depart": "08:00"},
        "westjet": {"carrier": "WS", "depart": "10:30"},
        "noon": {"carrier": "AC", "depart": "12:15"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 48900),
        offer("aircanada-business", "aircanada", "BUSINESS", 189000),
        offer("westjet-economy", "westjet", "ECONOMY", 45500),
        offer("westjet-business", "westjet", "BUSINESS", 171000),
        offer("noon-economy", "noon", "ECONOMY", 52000),
        offer("noon-business", "noon", "BUSINESS", 205000),
    ]),
    expected("BOOK", ["westjet-business"], ["BUSINESS"], ["BUSINESS_CLASS_APPROVED", "MEDICAL_NEED"], ["CEO", "NONE"],
             AIR + COM_CH),
    [BUSINESS, CHART_TWO],
    "Lines 559-564: business class with the CEO's prior approval on a flight within Canada for a reasonable "
    "accommodation (health reasons). The CEO also approves the travel plan of a Commission public body employee "
    "travelling outside Ontario within Canada (Chart 2). The lowest business fare: WestJet at $1,710.")

scenario(
    "dune-mallow", "easy", ["upgrade_not_taken", "multi_leg"],
    "Toronto to Vancouver on February 10th for the municipal finance forum, which opens at nine the next morning. "
    "Business class if the policy allows it; otherwise economy is fine, I just have to be there.",
    trip(traveller_name="Kevin Osei", traveller_title="Program Manager", organization=MINISTRY_MUN,
         destination="YVR", travel_date="2027-02-10", booking_date="2026-12-08", business_starts="2027-02-11 09:00",
         purpose="Municipal finance forum in Vancouver", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
         sign_offs=[SEC_TB_SIGN]),
    search("YYZ", "YVR", "2027-02-10", {
        "aircanada": {"carrier": "AC", "depart": "07:45"},
        "calgary": {"carrier": "WS", "via": ["YYC"], "depart": "09:00", "layovers": [70]},
        "midday": {"carrier": "AC", "depart": "11:30"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 51500),
        offer("aircanada-business", "aircanada", "BUSINESS", 198000),
        offer("calgary-economy", "calgary", "ECONOMY", 44800),
        offer("midday-economy", "midday", "ECONOMY", 49900),
        offer("midday-business", "midday", "BUSINESS", 187000),
    ]),
    expected("BOOK", ["calgary-economy"], ["ECONOMY"], ["UPGRADE_NOT_ELIGIBLE"], ["NONE", "SECRETARY_TB_MBC"],
             AIR + MIN_CH),
    [BUSINESS, LOWEST, CHART_ONE],
    "Lines 559-564: business class must have the deputy minister's or CEO's prior approval; none is on file, and a "
    "flight within Canada with no accommodation need is not one of the listed circumstances. The traveller accepts "
    "economy: the lowest fare is WestJet via Calgary at $448, landing the same afternoon (lines 558-559).")

scenario(
    "ember-sill", "easy", [],
    "I'm a workplace inspector and my inspection schedule moves around constantly, so I need a fare I can change. "
    "Ottawa to Toronto on December 15th; the inspections start at eight the next morning. My manager approved it.",
    trip(traveller_name="Luc Tremblay", traveller_title="Workplace Inspector", organization=MINISTRY_LAB,
         home_city="Ottawa", workplace_city="Ottawa", origin="YOW", destination="YYZ", travel_date="2026-12-15",
         booking_date="2026-11-30", business_starts="2026-12-16 08:00",
         purpose="Construction site inspections in Toronto", purpose_kind="INSPECTION", wants_changeable_fare=True,
         schedule_often_changes=True,
         sign_offs=[sign("MANAGER_SUPERVISOR", "Grace Liu", "Manager, Eastern Region Inspections",
                         "Approves the inspection trip to Toronto")]),
    search("YOW", "YYZ", "2026-12-15", {
        "morning": {"carrier": "AC", "depart": "07:00", "minutes": [65]},
        "noon": {"carrier": "WS", "depart": "12:30", "minutes": [65]},
        "evening": {"carrier": "AC", "depart": "18:00", "minutes": [65]},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 21900, seats=False),
        offer("morning-flex", "morning", "ECONOMY", 33400, refundable=True),
        offer("noon-economy", "noon", "ECONOMY", 23900, seats=False),
        offer("noon-flex", "noon", "ECONOMY", 31800, refundable=True),
        offer("evening-flex", "evening", "ECONOMY", 35500, refundable=True),
    ]),
    expected("BOOK", ["noon-flex"], ["ECONOMY"], LOW, ["MANAGER_SUPERVISOR", "NONE"],
             AIR + MIN_CH + ["APPENDIX_REVISIONS"]),
    [LOWEST, CHART_ONE, WITHIN_NOTE],
    "Every non-changeable seat is sold out, so the lowest fare available (lines 558-559) is WestJet's changeable fare "
    "at $318. Whatever the 2020 flexibility note (lines 1399-1402) means, the traveller gets a changeable fare. Within "
    "Ontario: the manager's approval is on file (Chart 1).",
    distractors=[aside(1399, 1402, "added option for flexibility for those whose schedules frequently change",
                       "both readings give the same seat here")])

# ===== boundary twins (6) =====

LONDON_FLIGHTS = {
    "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "16:40", "layovers": [95]},
    "aircanada": {"carrier": "AC", "depart": "18:30"},
    "british": {"carrier": "BA", "depart": "21:00"},
}
LONDON_OFFERS = [
    offer("frankfurt-economy", "frankfurt", "ECONOMY", 86400),
    offer("aircanada-economy", "aircanada", "ECONOMY", 98000),
    offer("aircanada-business", "aircanada", "BUSINESS", 412000),
    offer("british-economy", "british", "ECONOMY", 91500),
    offer("british-business", "british", "BUSINESS", 389000),
]
DM_ECON = "Deputy Minister, " + MINISTRY_ECON
ADM_ECON = "Assistant Deputy Minister, International Trade Division, " + MINISTRY_ECON


def london_trip(signer_role, signer_name, signer_title):
    return trip(traveller_name="Amara Nwosu", traveller_title="Director, Trade Policy", organization=MINISTRY_ECON,
                destination="LHR", travel_date="2027-01-24", booking_date="2026-12-02",
                business_starts="2027-01-26 09:00", purpose="UK-Canada trade summit in London",
                purpose_kind="NEGOTIATION", requested_cabin="BUSINESS", security_review_done=True,
                sign_offs=[CAB_SIGN, sign(signer_role, signer_name, signer_title,
                                          "Approves business class for the flight to London", subject="BUSINESS_CLASS")])


scenario(
    "fennel-cove", "boundary_twin", ["dearer_option"],
    "Toronto to London on January 24th for the trade summit, which opens on the 26th. The deputy minister approved "
    "business class for me in advance. Please book business; if that isn't enough, book what the policy allows. I "
    "have to be at the summit.",
    london_trip("DEPUTY_MINISTER", "Raymond Cho", DM_ECON),
    search("YYZ", "LHR", "2027-01-24", LONDON_FLIGHTS, LONDON_OFFERS),
    expected("BOOK", ["british-business"], ["BUSINESS"], ["BUSINESS_CLASS_APPROVED", "INTERNATIONAL_LONG_FLIGHT"],
             ["CABINET_SECRETARY", "DEPUTY_MINISTER", "NONE"], AIR + MIN_CH + ABROAD_SECTIONS),
    [BUSINESS, CHART_ONE, ABROAD],
    "An international flight with the deputy minister's prior approval of business class (lines 559-562); the travel "
    "plan is approved by the Secretary of the Cabinet (Chart 1). The lowest business fare: British Airways at $3,890.",
    twin_of="garnet-moor", twin_fact="business class approved by the deputy minister, or by an assistant deputy minister")

scenario(
    "garnet-moor", "boundary_twin", ["upgrade_not_taken", "multi_leg"],
    "Toronto to London on January 24th for the trade summit, which opens on the 26th. My assistant deputy minister "
    "approved business class for me in advance. Please book business; if that isn't enough, book what the policy "
    "allows. I have to be at the summit.",
    london_trip("ASSISTANT_DEPUTY_MINISTER", "Sofia Marchetti", ADM_ECON),
    search("YYZ", "LHR", "2027-01-24", LONDON_FLIGHTS, LONDON_OFFERS),
    expected("BOOK", ["frankfurt-economy"], ["ECONOMY"], ["UPGRADE_NOT_ELIGIBLE"], ["CABINET_SECRETARY", "NONE"],
             AIR + MIN_CH + ABROAD_SECTIONS),
    [BUSINESS, LOWEST, CHART_ONE, ABROAD],
    "Business class 'must have prior approval by the deputy minister or CEO' (lines 559-560); the assistant deputy "
    "minister's approval is not that. The traveller accepts what the policy allows: the lowest fare, Lufthansa via "
    "Frankfurt at $864, landing the day before the summit (lines 558-559; line 457-458: the lowest cost method "
    "abroad).",
    twin_of="fennel-cove", twin_fact="business class approved by the deputy minister, or by an assistant deputy minister")

HALIFAX_FLIGHTS = {
    "montreal": {"carrier": "AC", "via": ["YUL"], "depart": "07:30", "layovers": [65]},
    "nonstop": {"carrier": "AC", "depart": "09:10"},
    "westjet": {"carrier": "WS", "depart": "14:20"},
}
HALIFAX_OFFERS = [
    offer("montreal-economy", "montreal", "ECONOMY", 39800),
    offer("nonstop-economy", "nonstop", "ECONOMY", 46200),
    offer("westjet-economy", "westjet", "ECONOMY", 43300),
]


def halifax_trip(covered):
    return trip(traveller_name="Ethan Clarke", traveller_title="Contract hearing transcription specialist",
                traveller_role="CONSULTANT", organization=HEARINGS, organization_kind="COMMISSION_PUBLIC_BODY",
                contract_covers_travel_costs=covered, destination="YHZ", travel_date="2027-01-27",
                booking_date="2026-12-03", business_starts="2027-01-28 09:00",
                purpose="Transcribing the Atlantic licensing hearings in Halifax",
                sign_offs=[sign("CEO", "Daniel Mercer", "Chief Executive Officer, " + HEARINGS,
                                "Approves the consultant's trip to Halifax")])


scenario(
    "heron-flint", "boundary_twin", ["multi_leg"],
    "I'm a contractor to the hearings commission. My contract covers my travel costs, and the CEO approved this trip. "
    "Please book Toronto to Halifax on January 27th on the commission's account; the hearings start at nine the next "
    "morning.",
    halifax_trip(True),
    search("YYZ", "YHZ", "2027-01-27", HALIFAX_FLIGHTS, HALIFAX_OFFERS),
    expected("BOOK", ["montreal-economy"], ["ECONOMY"], LOW, ["CEO", "NONE"], AIR + COM_CH),
    [LOWEST, CHART_TWO, CONTRACT],
    "A consultant to a Commission public body travelling outside Ontario within Canada: the CEO approves (Chart 2), "
    "and the contract allows travel costs (lines 1046-1048). The lowest fare: Air Canada via Montreal at $398.",
    twin_of="iris-kettle", twin_fact="the contract covers travel costs, or does not")

scenario(
    "iris-kettle", "boundary_twin", ["outside_air_section"],
    "I'm a contractor to the hearings commission. My contract covers my fees only, not travel costs, but the CEO "
    "approved this trip. Please book Toronto to Halifax on January 27th on the commission's account; the hearings "
    "start at nine the next morning.",
    halifax_trip(False),
    search("YYZ", "YHZ", "2027-01-27", HALIFAX_FLIGHTS, HALIFAX_OFFERS),
    expected("REFUSE", [], ["NONE"], ["CONTRACT_EXCLUDES_TRAVEL_COSTS", "OUTSIDE_POLICY_SCOPE"], ["CEO", "NONE"],
             ["CONSULTANTS_AND_CONTRACTORS"]),
    [CONTRACT, CONSULTANTS_COVERED, TRAVEL_NOT_EXPENSE],
    "Lines 1046-1048: a consultant or contractor can claim expenses only when the contract specifically allows for "
    "it, and this one does not cover travel. Footnote 1 (lines 300-302): the CEO's approval of the travel is not an "
    "approval of its expenses. The commission buys no ticket.",
    twin_of="heron-flint", twin_fact="the contract covers travel costs, or does not")

OTTAWA_DM_FLIGHTS = {
    "early": {"carrier": "AC", "depart": "06:45", "minutes": [65]},
    "westjet": {"carrier": "WS", "depart": "09:40", "minutes": [65]},
}
OTTAWA_DM_OFFERS = [
    offer("early-economy", "early", "ECONOMY", 34600),
    offer("early-business", "early", "BUSINESS", 61000),
    offer("westjet-economy", "westjet", "ECONOMY", 26800),
]


def ottawa_dm_trip(starts):
    return trip(traveller_name="Catherine Doyle", traveller_title="Deputy Minister", traveller_role="DEPUTY_MINISTER",
                organization=MINISTRY_AGRI, destination="YOW", travel_date="2027-02-16", booking_date="2026-12-09",
                business_starts=starts, purpose="Federal-provincial committee of agriculture deputies in Ottawa")


scenario(
    "juniper-weir", "boundary_twin", ["outside_air_section"],
    "Please book me Toronto to Ottawa on February 16th, in the morning; the federal-provincial committee meets at "
    "2 p.m. that day.",
    ottawa_dm_trip("2027-02-16 14:00"),
    search("YYZ", "YOW", "2027-02-16", OTTAWA_DM_FLIGHTS, OTTAWA_DM_OFFERS),
    expected("BOOK", ["westjet-economy"], ["ECONOMY"], LOW, ["NONE"], AIR + MIN_CH + ["APPENDIX_APPROVAL_SUMMARY"]),
    [LOWEST, CHART_ONE, NO_APPROVAL],
    "A deputy minister travelling within Ontario needs no approval (Chart 1, N/A, footnote 3 at line 346). The WestJet "
    "flight lands at 10:45, in time for 2 p.m.: the lowest fare, $268 (lines 558-559).",
    twin_of="kelp-arbor", twin_fact="the committee meets at 14:00 or at 10:30")

scenario(
    "kelp-arbor", "boundary_twin", ["dearer_option", "outside_air_section"],
    "Please book me Toronto to Ottawa on February 16th, in the morning; the federal-provincial committee meets at "
    "10:30 a.m. that day.",
    ottawa_dm_trip("2027-02-16 10:30"),
    search("YYZ", "YOW", "2027-02-16", OTTAWA_DM_FLIGHTS, OTTAWA_DM_OFFERS),
    expected("BOOK", ["early-economy"], ["ECONOMY"], ["ARRIVES_AFTER_BUSINESS_STARTS", "LOWEST_FARE"], ["NONE"],
             AIR + MIN_CH + ["APPENDIX_APPROVAL_SUMMARY"]),
    [LOWEST, CHART_ONE, NO_APPROVAL],
    "No approval is needed (footnote 3). The cheaper WestJet flight lands at 10:45, after the 10:30 meeting starts, so "
    "it is not a practical way to get there (line 558); the lowest fare that arrives in time is the 06:45 Air Canada "
    "economy seat at $346.",
    twin_of="juniper-weir", twin_fact="the committee meets at 14:00 or at 10:30")

# ===== multi-rule (4) =====

scenario(
    "larch-pebble", "multi_rule", ["dearer_option"],
    "Toronto to Frankfurt on February 21st for the agri-food export fair, which opens on the 23rd. The deputy minister "
    "approved the trip and business class for me. Business class, please.",
    trip(traveller_name="Hiroshi Tanaka", traveller_title="Senior Director, Agri-Food Exports",
         organization=MINISTRY_AGRI, destination="FRA", travel_date="2027-02-21", booking_date="2026-12-10",
         business_starts="2027-02-23 09:00", purpose="Agri-food export fair in Frankfurt", purpose_kind="CONFERENCE",
         requested_cabin="BUSINESS", security_review_done=True,
         sign_offs=[
             sign("DEPUTY_MINISTER", "Catherine Doyle", "Deputy Minister, " + MINISTRY_AGRI,
                  "Approves the international travel plan, on the international travel form, under the Secretary of "
                  "the Cabinet's written delegation of international travel approvals for this ministry",
                  acting_for="CABINET_SECRETARY"),
             sign("DEPUTY_MINISTER", "Catherine Doyle", "Deputy Minister, " + MINISTRY_AGRI,
                  "Approves business class for the flight to Frankfurt", subject="BUSINESS_CLASS"),
         ]),
    search("YYZ", "FRA", "2027-02-21", {
        "lufthansa": {"carrier": "LH", "depart": "18:15"},
        "aircanada": {"carrier": "AC", "depart": "21:40"},
    }, [
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 84000),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 338000),
        offer("aircanada-economy", "aircanada", "ECONOMY", 89000),
        offer("aircanada-business", "aircanada", "BUSINESS", 352000),
    ]),
    expected("BOOK", ["lufthansa-business"], ["BUSINESS"], ["BUSINESS_CLASS_APPROVED", "INTERNATIONAL_LONG_FLIGHT"],
             ["CABINET_SECRETARY", "DEPUTY_MINISTER", "NONE"],
             AIR + MIN_CH + ABROAD_SECTIONS + ["DELEGATION_OF_AUTHORITY"]),
    [BUSINESS, CHART_ONE, DELEGATE, ABROAD],
    "International travel by a ministry employee is approved by the Secretary of the Cabinet (Chart 1), who may "
    "delegate it to a deputy minister for their ministry in writing (lines 367-381); the deputy minister signed under "
    "that delegation. The deputy minister also approved business class on an international flight (lines 559-562). "
    "The lowest business fare: Lufthansa at $3,380.")

scenario(
    "moss-quill", "multi_rule", ["upgrade_not_taken", "multi_leg", "outside_air_section"],
    "Toronto to London on March 7th for the cultural agencies forum on the 9th. As CEO I've approved business class "
    "for myself. Book business; if that isn't enough, book what the policy allows. I have to be at the forum.",
    trip(traveller_name="Isabelle Fontaine", traveller_title="Chief Executive Officer", traveller_role="CEO",
         organization="Provincial Arts and Heritage Grants Commission (a Commission public body)",
         organization_kind="COMMISSION_PUBLIC_BODY", destination="LHR", travel_date="2027-03-07",
         booking_date="2026-12-04", business_starts="2027-03-09 09:00",
         purpose="International cultural agencies forum in London", purpose_kind="CONFERENCE",
         requested_cabin="BUSINESS", security_review_done=True,
         sign_offs=[CAB_SIGN,
                    sign("CEO", "Isabelle Fontaine", "Chief Executive Officer, Provincial Arts and Heritage Grants "
                         "Commission", "Approves business class for the flight to London", subject="BUSINESS_CLASS")]),
    search("YYZ", "LHR", "2027-03-07", {
        "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "17:10", "layovers": [85]},
        "aircanada": {"carrier": "AC", "depart": "19:00"},
        "british": {"carrier": "BA", "depart": "21:30"},
    }, [
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 87900),
        offer("aircanada-economy", "aircanada", "ECONOMY", 94000),
        offer("aircanada-business", "aircanada", "BUSINESS", 401000),
        offer("british-economy", "british", "ECONOMY", 90500),
        offer("british-business", "british", "BUSINESS", 386000),
    ]),
    expected("BOOK", ["amsterdam-economy"], ["ECONOMY"], ["SELF_APPROVAL_NOT_ALLOWED", "UPGRADE_NOT_ELIGIBLE"],
             ["CABINET_SECRETARY", "NONE"], AIR + COM_CH + ABROAD_SECTIONS + ["GENERAL_REQUIREMENTS"]),
    [BUSINESS, SELF, CHART_TWO, ABROAD],
    "Business class needs the deputy minister's or CEO's prior approval (lines 559-562), but the traveller is the CEO "
    "and approvers may not approve their own expenses (line 149). The Secretary of the Cabinet approved the travel "
    "plan of a Commission public body's CEO abroad (Chart 2). The traveller accepts what the policy allows: the "
    "lowest fare, KLM via Amsterdam at $879.")

scenario(
    "nutmeg-shoal", "multi_rule", [],
    "Please put me on Air Canada so I keep collecting Aeroplan points; if that isn't allowed, book what the policy "
    "allows. Toronto to Calgary on January 11th for the regulators' meeting at nine the next morning. The CEO approved "
    "the trip.",
    trip(traveller_name="Rebecca Hall", traveller_title="Licensing Coordinator", organization=HEARINGS,
         organization_kind="COMMISSION_PUBLIC_BODY", destination="YYC", travel_date="2027-01-11",
         booking_date="2026-11-26", business_starts="2027-01-12 09:00",
         purpose="National licensing regulators' meeting in Calgary", requested_airline="Air Canada",
         sign_offs=[sign("CEO", "Daniel Mercer", "Chief Executive Officer, " + HEARINGS,
                         "Approves the trip to Calgary")]),
    search("YYZ", "YYC", "2027-01-11", {
        "morning": {"carrier": "AC", "depart": "08:20"},
        "westjet": {"carrier": "WS", "depart": "10:05"},
        "afternoon": {"carrier": "AC", "depart": "14:40"},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 45900),
        offer("westjet-economy", "westjet", "ECONOMY", 38700),
        offer("afternoon-economy", "afternoon", "ECONOMY", 42100),
    ]),
    expected("BOOK", ["westjet-economy"], ["ECONOMY"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE"], ["CEO", "NONE"],
             AIR + COM_CH + ["BEFORE_TRAVELLING"]),
    [LOWEST, LOYALTY, CHART_TWO, TMC],
    "Lines 432-437: loyalty programmes are allowed only when the most cost-effective method of travel is chosen; lines "
    "558-559: the lowest fare. Air Canada's cheapest is $421; WestJet is $387. The CEO approved the trip (Chart 2).")

scenario(
    "opal-thicket", "multi_rule", ["dearer_option"],
    "Toronto to London on February 14th for the reactor safety workshop, which opens on the 16th. The Minister of "
    "Energy approved the trip and our CEO approved business class for me. Business class, please.",
    trip(traveller_name="Samuel Adeyemi", traveller_title="Senior Nuclear Safety Engineer",
         organization="Ontario Power Generation Inc.", organization_kind="ELECTRICITY_ORGANIZATION", destination="LHR",
         travel_date="2027-02-14", booking_date="2026-12-01", business_starts="2027-02-16 09:00",
         purpose="International reactor safety workshop in London", purpose_kind="TRAINING", requested_cabin="BUSINESS",
         security_review_done=True,
         sign_offs=[
             sign("MINISTER", "Hon. Patricia Wong", "Minister of Energy", "Approves the international travel plan"),
             sign("CEO", "Martin Keller", "President and Chief Executive Officer, Ontario Power Generation Inc.",
                  "Approves business class for the flight to London", subject="BUSINESS_CLASS"),
         ]),
    search("YYZ", "LHR", "2027-02-14", {
        "aircanada": {"carrier": "AC", "depart": "18:30"},
        "british": {"carrier": "BA", "depart": "20:45"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 96500),
        offer("aircanada-business", "aircanada", "BUSINESS", 405000),
        offer("british-economy", "british", "ECONOMY", 92800),
        offer("british-business", "british", "BUSINESS", 392000),
    ]),
    expected("BOOK", ["british-business"], ["BUSINESS"], ["BUSINESS_CLASS_APPROVED", "INTERNATIONAL_LONG_FLIGHT"],
             ["CEO", "MINISTER", "NONE"], AIR + OTH_CH + ABROAD_SECTIONS),
    [BUSINESS, CHART_THREE, CHART_THREE_SCOPE, ABROAD],
    "Ontario Power Generation is under Chart 3 (lines 271-273): an employee's international travel is approved by the "
    "Minister, and that approval is on file. Business class on an international flight with the CEO's prior approval "
    "(lines 559-562). The lowest business fare: British Airways at $3,920.")

# ===== hidden clause (2) =====

scenario(
    "pine-ferry", "hidden_clause", [],
    "Toronto to Edmonton on January 6th for the licensing hearings at nine the next morning. Our CFO approved the trip "
    "under the CEO's delegation.",
    trip(traveller_name="Daniel Kim", traveller_title="Case Analyst", organization=HEARINGS,
         organization_kind="COMMISSION_PUBLIC_BODY", destination="YEG", travel_date="2027-01-06",
         booking_date="2026-11-27", business_starts="2027-01-07 09:00", purpose="Licensing hearings in Edmonton",
         sign_offs=[sign("CFO", "Laura Bennett", "Chief Financial Officer, " + HEARINGS,
                         "Approves the trip to Edmonton under the CEO's written delegation of travel approvals for staff "
                         "who do not report to the CEO", acting_for="CEO")]),
    search("YYZ", "YEG", "2027-01-06", {
        "aircanada": {"carrier": "AC", "depart": "08:00"},
        "westjet": {"carrier": "WS", "depart": "09:15"},
        "evening": {"carrier": "AC", "depart": "16:50"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 46800),
        offer("westjet-economy", "westjet", "ECONOMY", 41900),
        offer("westjet-business", "westjet", "BUSINESS", 154000),
        offer("evening-economy", "evening", "ECONOMY", 44300),
    ]),
    expected("BOOK", ["westjet-economy"], ["ECONOMY"], LOW, ["CEO", "CFO", "NONE"],
             AIR + COM_CH + ["DELEGATION_OF_AUTHORITY"]),
    [LOWEST, CHART_TWO, CEO_DELEGATE],
    "A Commission public body employee travelling outside Ontario within Canada needs the CEO's approval (Chart 2). The "
    "CEO may delegate it to the CFO, but not for direct reports (lines 396-405); the CFO signed under that written "
    "delegation for a case analyst. The lowest fare: WestJet at $419 (lines 558-559).")

scenario(
    "quartz-meadow", "hidden_clause", ["date_arithmetic", "outside_air_section"],
    "Toronto to Paris on March 2nd for the international film market, which opens on the 4th. Our chair approved the "
    "trip under the agency's special status. The security assessment is done.",
    trip(traveller_name="Chloe Martin", traveller_title="International Sales Manager",
         organization="Provincial Film and Screen Investment Agency (a provincial agency whose staff are not public "
                      "servants)",
         organization_kind="OTHER_PROVINCIAL_AGENCY", special_status_granted_on="2024-05-20", destination="CDG",
         travel_date="2027-03-02", booking_date="2026-12-07", business_starts="2027-03-04 09:00",
         purpose="International film market in Paris", purpose_kind="CONFERENCE", security_review_done=True,
         sign_offs=[sign("CHAIR", "Victor Lalonde", "Chair, Provincial Film and Screen Investment Agency",
                         "Approves the international travel plan under the agency's special status")]),
    search("YYZ", "CDG", "2027-03-02", {
        "aircanada": {"carrier": "AC", "depart": "17:45"},
        "airfrance": {"carrier": "AF", "depart": "19:30"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 91200),
        offer("airfrance-economy", "airfrance", "ECONOMY", 87600),
        offer("airfrance-business", "airfrance", "BUSINESS", 361000),
    ]),
    expected("BOOK", ["airfrance-economy"], ["ECONOMY"], LOW, ["CHAIR", "NONE"],
             AIR + OTH_CH + ABROAD_SECTIONS + SPECIAL_SECTIONS),
    [LOWEST, SPECIAL, SPECIAL_LEVELS, ABROAD],
    "Chart 3 would send an agency employee's international travel to the Minister, but with special status the chair "
    "approves it (lines 277-282, 1233-1246). Special status lasts three years (line 290): granted 2024-05-20, it runs "
    "to 2027-05-20, past both today and the flight. The lowest fare: Air France at $876.")

# ===== distractors (2) =====

HALIFAX_TEAM = search("YYZ", "YHZ", "2027-02-08", {
    "director": {"carrier": "AC", "depart": "07:30"},
    "westjet": {"carrier": "WS", "depart": "09:50"},
    "afternoon": {"carrier": "AC", "depart": "13:00"},
}, [
    offer("director-economy", "director", "ECONOMY", 47800),
    offer("westjet-economy", "westjet", "ECONOMY", 39900),
    offer("afternoon-economy", "afternoon", "ECONOMY", 44100),
])
DIRECTOR_FLIGHT = first_flight("rowan-spindle", HALIFAX_TEAM, "director-economy")

scenario(
    "rowan-spindle", "distractor", ["multi_traveller"],
    f"My director is already booked on {DIRECTOR_FLIGHT} from Toronto to Halifax on February 8th. Please put me on the "
    "same flight so we can prepare together; if that isn't allowed, book what the policy allows. The fisheries "
    "consultation starts at nine the next morning.",
    trip(traveller_name="Emily Sato", traveller_title="Senior Policy Analyst", organization=MINISTRY_AGRI,
         destination="YHZ", travel_date="2027-02-08", booking_date="2026-12-09", business_starts="2027-02-09 09:00",
         purpose="Interprovincial fisheries consultation in Halifax", requested_flight=DIRECTOR_FLIGHT,
         sign_offs=[SEC_TB_SIGN],
         travelling_with=[{"name": "Mark Delaney", "title": "Director, Fisheries Policy",
                           "flight_number": DIRECTOR_FLIGHT, "date": "2027-02-08", "cabin": "ECONOMY"}]),
    HALIFAX_TEAM,
    expected("BOOK", ["westjet-economy"], ["ECONOMY"], ["COST_SAVINGS", "LOWEST_FARE"], ["NONE", "SECRETARY_TB_MBC"],
             AIR + MIN_CH),
    [LOWEST, CHART_ONE],
    "Lines 558-559: the lowest fare available is WestJet at $399; the director's Air Canada flight is $478. Wanting to "
    "work together is a reason for business class on rail (line 574), not for a dearer flight, and business continuity "
    "(lines 461-462) only asks whether senior people should travel together. The Secretary, TB/MBC approved the trip "
    "(Chart 1).",
    distractors=[RAIL_TEAM, CONTINUITY])

scenario(
    "sorrel-beacon", "distractor", [],
    "Toronto to Winnipeg on January 19th for the hearings, which start at nine the next morning. Could you get me a "
    "refundable fare, just in case plans shift? The CEO approved the trip.",
    trip(traveller_name="Aaron Fischer", traveller_title="Case Manager", organization=HEARINGS,
         organization_kind="COMMISSION_PUBLIC_BODY", destination="YWG", travel_date="2027-01-19",
         booking_date="2026-11-30", business_starts="2027-01-20 09:00", purpose="Licensing hearings in Winnipeg",
         wants_changeable_fare=True,
         sign_offs=[sign("CEO", "Daniel Mercer", "Chief Executive Officer, " + HEARINGS,
                         "Approves the trip to Winnipeg")]),
    search("YYZ", "YWG", "2027-01-19", {
        "aircanada": {"carrier": "AC", "depart": "08:10"},
        "westjet": {"carrier": "WS", "depart": "11:25"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 41800),
        offer("aircanada-flex", "aircanada", "ECONOMY", 56900, refundable=True),
        offer("westjet-economy", "westjet", "ECONOMY", 37500),
        offer("westjet-flex", "westjet", "ECONOMY", 51200, refundable=True),
    ]),
    expected("BOOK", ["westjet-economy"], ["ECONOMY"], ["LOWEST_FARE", "REFUNDABLE_FARE_NOT_ALLOWED"], ["CEO", "NONE"],
             AIR + COM_CH),
    [LOWEST, CHART_TWO],
    "Lines 558-559: the lowest fare available, WestJet's non-refundable $375. The 2020 flexibility note (lines "
    "1399-1402) is for those whose schedules frequently change; this traveller's does not, and itinerary changes "
    "(lines 417-420) are made through the travel management company. The CEO approved the trip (Chart 2).",
    distractors=[aside(1399, 1402, "added option for flexibility for those whose schedules frequently change",
                       "the traveller's schedule does not frequently change"), CHANGES])

# ===== refusals (2) =====

scenario(
    "tansy-grove", "refusal", ["outside_air_section"],
    "I live in Ottawa and my job is at the ministry's Toronto head office. Please book my usual Monday morning flight "
    "to the office on December 7th; I'm due in at ten.",
    trip(traveller_name="Jonathan Reyes", traveller_title="Senior Economist", organization=MINISTRY_ECON,
         home_city="Ottawa", workplace_city="Toronto", origin="YOW", destination="YYZ", travel_date="2026-12-07",
         booking_date="2026-11-25", business_starts="2026-12-07 10:00",
         purpose="A regular working week at his own office in Toronto", purpose_kind="REGULAR_OFFICE_DAY"),
    search("YOW", "YYZ", "2026-12-07", {
        "early": {"carrier": "AC", "depart": "06:30", "minutes": [65]},
        "westjet": {"carrier": "WS", "depart": "07:15", "minutes": [65]},
    }, [
        offer("early-economy", "early", "ECONOMY", 24800),
        offer("westjet-economy", "westjet", "ECONOMY", 22600),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED", "REGULAR_COMMUTE"],
             ["NONE"], ["TRAVEL"]),
    [COMMUTE],
    "Lines 239-241: travel does not refer to a person's regular commute to work, and its expenses are not "
    "reimbursable. Flying from home to his own regular workplace is that commute; the ministry buys no ticket.",
    distractors=[REGULAR_JOB])

scenario(
    "umber-reed", "refusal", ["personal_travel"],
    "The housing conference in Vancouver on January 29th has been cancelled, but I'd still like to fly out on the 28th "
    "as planned; my sister lives there and I'll take a few vacation days. The trip was already approved, so please "
    "book it.",
    trip(traveller_name="Hannah Wright", traveller_title="Housing Policy Advisor", organization=MINISTRY_MUN,
         destination="YVR", travel_date="2027-01-28", booking_date="2026-12-02", business_starts="2027-01-29 09:00",
         purpose="Visit to her sister in Vancouver while on vacation; the housing conference she was approved to attend "
                 "is cancelled", purpose_kind="PERSONAL_VISIT",
         sign_offs=[sign("SECRETARY_TB_MBC", "Helen Okafor", "Secretary, Treasury Board/Management Board of Cabinet",
                         "Approved the travel plan for the housing conference, now cancelled")]),
    search("YYZ", "YVR", "2027-01-28", {
        "aircanada": {"carrier": "AC", "depart": "08:30"},
        "westjet": {"carrier": "WS", "depart": "11:00"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 50200),
        offer("westjet-economy", "westjet", "ECONOMY", 46700),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             ["NONE", "SECRETARY_TB_MBC"], ["GENERAL_REQUIREMENTS", "PRINCIPLES", "TRAVEL"]),
    [GOV_BUSINESS, NECESSARY, COMMUTE],
    "Lines 111-112: only legitimate expenses incurred in the course of government business are reimbursed; lines "
    "145-146: approval only for expenses necessarily incurred in government business; line 239: the directive applies "
    "when travel is required. With the conference cancelled the trip is personal, and the earlier approval was for "
    "the conference. The ministry buys no ticket.")

# ===== flags (3) =====

scenario(
    "vetch-harbor", "flag", ["approval_required", "outside_air_section"],
    "Toronto to Boston on January 20th for the northeast transit planning summit, which opens at nine the next "
    "morning. My manager approved the trip last week and the security assessment is done, so please go ahead and "
    "book.",
    trip(traveller_name="Priyanka Shah", traveller_title="Transit Planning Analyst", organization=MINISTRY_MUN,
         destination="BOS", travel_date="2027-01-20", booking_date="2026-12-03", business_starts="2027-01-21 09:00",
         purpose="Northeast transit planning summit in Boston", purpose_kind="CONFERENCE", security_review_done=True,
         sign_offs=[sign("MANAGER_SUPERVISOR", "Tom Ellis", "Manager, Transit Policy", "Approves the trip to Boston")]),
    search("YYZ", "BOS", "2027-01-20", {
        "aircanada": {"carrier": "AC", "depart": "08:05"},
        "jetblue": {"carrier": "B6", "depart": "11:20"},
        "evening": {"carrier": "AC", "depart": "16:40"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 40100),
        offer("jetblue-economy", "jetblue", "ECONOMY", 35600),
        offer("evening-economy", "evening", "ECONOMY", 37900),
    ]),
    expected("FLAG_FOR_APPROVAL", ["jetblue-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED", "TRAVEL_APPROVAL_LEVEL"],
             ["DEPUTY_MINISTER", "SECRETARY_TB_MBC"], MIN_CH + ABROAD_SECTIONS + ["BEFORE_TRAVELLING"]),
    [CHART_ONE, PRIOR, ABROAD],
    "A ministry employee travelling outside Ontario within Canada and the USA needs the Secretary, TB/MBC's approval "
    "(Chart 1), or that of the deputy minister under its written delegation (lines 382-390); a manager's approval "
    "covers only travel within Ontario. Lines 409-412 and 447-452: prior documented approval. Hold the lowest fare, "
    "JetBlue at $356, for that approval. Approval required, not 'no compliant offer'.",
    flag_twins=["alder-quay", "birch-lantern"],
    ambiguity="none: the Secretary, TB/MBC's approval is required and missing; the text is clear")

scenario(
    "willow-strand", "flag", ["approval_required", "date_arithmetic", "month_end", "outside_air_section"],
    "Toronto to Paris on March 9th for the European co-production meetings, which open on the 11th. Our chair "
    "approved the trip under the agency's special status, and the security assessment is done. Please book it.",
    trip(traveller_name="Gabriel Roy", traveller_title="Co-production Manager",
         organization="Provincial Music and Media Export Agency (a provincial agency whose staff are not public "
                      "servants)",
         organization_kind="OTHER_PROVINCIAL_AGENCY", special_status_granted_on="2023-08-31", destination="CDG",
         travel_date="2027-03-09", booking_date="2026-12-08", business_starts="2027-03-11 09:00",
         purpose="European co-production meetings in Paris", purpose_kind="NEGOTIATION", security_review_done=True,
         sign_offs=[sign("CHAIR", "Monique Gagnon", "Chair, Provincial Music and Media Export Agency",
                         "Approves the international travel plan under the agency's special status")]),
    search("YYZ", "CDG", "2027-03-09", {
        "aircanada": {"carrier": "AC", "depart": "17:45"},
        "airfrance": {"carrier": "AF", "depart": "19:30"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 90400),
        offer("airfrance-economy", "airfrance", "ECONOMY", 88300),
    ]),
    expected("FLAG_FOR_APPROVAL", ["airfrance-economy"], ["ECONOMY"],
             ["APPROVAL_REQUIRED", "SPECIAL_STATUS_LAPSED", "TRAVEL_APPROVAL_LEVEL"], ["DEPUTY_MINISTER", "MINISTER"],
             OTH_CH + ABROAD_SECTIONS + SPECIAL_SECTIONS + ["BEFORE_TRAVELLING"]),
    [SPECIAL, SPECIAL_LEVELS, CHART_THREE, PRIOR],
    "Special status 'is approved for three years only' (line 290): granted 2023-08-31, it lapsed on 2026-08-31, before "
    "today. Without it, Chart 3 sends an agency employee's international travel to the Minister (or a deputy minister "
    "under the Minister's delegation, lines 360-366). The chair's approval does not stand in. Hold the lowest fare, Air "
    "France at $883, for the Minister's approval.",
    flag_twins=["quartz-meadow", "opal-thicket"],
    ambiguity="none: the Minister's approval is required and missing once special status has lapsed; the text is clear")

scenario(
    "yarrow-crest", "flag", ["unclear_phrase"],
    "I'm a workplace inspector and my schedule changes all the time, so I need a fare I can change. Toronto to Ottawa "
    "on December 14th; the inspections start at eight the next morning. My manager approved it.",
    trip(traveller_name="Sandra Okonkwo", traveller_title="Workplace Inspector", organization=MINISTRY_LAB,
         destination="YOW", travel_date="2026-12-14", booking_date="2026-11-26", business_starts="2026-12-15 08:00",
         purpose="Factory inspections in Ottawa", purpose_kind="INSPECTION", wants_changeable_fare=True,
         schedule_often_changes=True,
         sign_offs=[sign("MANAGER_SUPERVISOR", "Grace Liu", "Manager, Eastern Region Inspections",
                         "Approves the inspection trip to Ottawa")]),
    search("YYZ", "YOW", "2026-12-14", {
        "morning": {"carrier": "AC", "depart": "07:00", "minutes": [65]},
        "afternoon": {"carrier": "WS", "depart": "13:20", "minutes": [65]},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 25400),
        offer("morning-flex", "morning", "ECONOMY", 36800, refundable=True),
        offer("afternoon-economy", "afternoon", "ECONOMY", 22700),
        offer("afternoon-flex", "afternoon", "ECONOMY", 33900, refundable=True),
    ]),
    expected("FLAG_FOR_APPROVAL", ["afternoon-economy", "afternoon-flex"], ["ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], ["MANAGER_SUPERVISOR", "NOT_NAMED"],
             AIR + ["APPENDIX_REVISIONS"],
             phrase="added option for flexibility for those whose schedules frequently change"),
    [LOWEST, REVISION, DIRECTION],
    "The Air Travel text (lines 558-559) says to choose the lowest fare available, with no exception. Appendix C (lines "
    "1399-1402) says the 2020 revision of Airplane and Train 'added option for flexibility for those whose schedules "
    "frequently change', and this inspector's schedule does. Whether the directive lets them buy a changeable fare "
    "($339) above the lowest ($227) is open: hold either. No role is named; the manager seeks direction on questions "
    "of application (line 1064).",
    flag_twins=["ember-sill", "sorrel-beacon"],
    ambiguity={"phrase": "added option for flexibility for those whose schedules frequently change",
               "readings": [("the 2020 revision gave travellers whose schedules frequently change the option of a "
                             "flexible fare: book the cheapest changeable fare"),
                            ("the operative Air Travel text has no such option and says to choose the lowest fare "
                             "available: book the lowest, non-changeable fare")]})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
