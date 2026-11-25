"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-ontario-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    BUSINESS_CLASS_APPROVED = "BUSINESS_CLASS_APPROVED"
    SELF_APPROVAL_NOT_ALLOWED = "SELF_APPROVAL_NOT_ALLOWED"
    CONTRACT_EXCLUDES_TRAVEL_COSTS = "CONTRACT_EXCLUDES_TRAVEL_COSTS"
    REGULAR_COMMUTE = "REGULAR_COMMUTE"
    ARRIVES_AFTER_BUSINESS_STARTS = "ARRIVES_AFTER_BUSINESS_STARTS"
    SPECIAL_STATUS_LAPSED = "SPECIAL_STATUS_LAPSED"
    TRAVEL_APPROVAL_LEVEL = "TRAVEL_APPROVAL_LEVEL"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    TRAVEL_PACKAGE_NOT_ITEMIZED = "TRAVEL_PACKAGE_NOT_ITEMIZED"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: Ontario Travel, Meal and Hospitality Expenses Directive (last amended January 1, 2020).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    ALDER_QUAY = "alder-quay"
    BIRCH_LANTERN = "birch-lantern"
    CEDAR_WREN = "cedar-wren"
    DUNE_MALLOW = "dune-mallow"
    EMBER_SILL = "ember-sill"
    FENNEL_COVE = "fennel-cove"
    GARNET_MOOR = "garnet-moor"
    HERON_FLINT = "heron-flint"
    IRIS_KETTLE = "iris-kettle"
    JUNIPER_WEIR = "juniper-weir"
    KELP_ARBOR = "kelp-arbor"
    LARCH_PEBBLE = "larch-pebble"
    MOSS_QUILL = "moss-quill"
    NUTMEG_SHOAL = "nutmeg-shoal"
    OPAL_THICKET = "opal-thicket"
    PINE_FERRY = "pine-ferry"
    QUARTZ_MEADOW = "quartz-meadow"
    ROWAN_SPINDLE = "rowan-spindle"
    SORREL_BEACON = "sorrel-beacon"
    TANSY_GROVE = "tansy-grove"
    UMBER_REED = "umber-reed"
    VETCH_HARBOR = "vetch-harbor"
    WILLOW_STRAND = "willow-strand"
    YARROW_CREST = "yarrow-crest"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    MANAGER_SUPERVISOR = "MANAGER_SUPERVISOR"
    CONTRACT_MANAGER = "CONTRACT_MANAGER"
    ASSISTANT_DEPUTY_MINISTER = "ASSISTANT_DEPUTY_MINISTER"
    DEPUTY_MINISTER = "DEPUTY_MINISTER"
    SECRETARY_TB_MBC = "SECRETARY_TB_MBC"
    CABINET_SECRETARY = "CABINET_SECRETARY"
    MINISTER = "MINISTER"
    CHAIR = "CHAIR"
    CEO = "CEO"
    CFO = "CFO"
    TREASURY_BOARD = "TREASURY_BOARD"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    TRAVEL_COORDINATOR = "TRAVEL_COORDINATOR"
    FINANCE_DIRECTOR = "FINANCE_DIRECTOR"


class Clause(Enum):
    """The handbook's sections, by heading."""

    PURPOSE = "PURPOSE"
    APPLICATION_AND_SCOPE = "APPLICATION_AND_SCOPE"
    PRINCIPLES = "PRINCIPLES"
    BEST_PRACTICES = "BEST_PRACTICES"
    GENERAL_REQUIREMENTS = "GENERAL_REQUIREMENTS"
    ACCOUNTABILITY_FRAMEWORK = "ACCOUNTABILITY_FRAMEWORK"
    MANAGERIAL_DISCRETION = "MANAGERIAL_DISCRETION"
    TRAVEL = "TRAVEL"
    REGULAR_PART_OF_JOB = "REGULAR_PART_OF_JOB"
    OCCASIONAL_TRAVEL = "OCCASIONAL_TRAVEL"
    APPROVALS_FOR_TRAVEL = "APPROVALS_FOR_TRAVEL"
    SPECIAL_STATUS = "SPECIAL_STATUS"
    APPROVAL_FOR_TRAVEL_PLANS = "APPROVAL_FOR_TRAVEL_PLANS"
    CHART_MINISTRIES = "CHART_MINISTRIES"
    CHART_COMMISSION_PUBLIC_BODIES = "CHART_COMMISSION_PUBLIC_BODIES"
    CHART_OTHER_AGENCIES = "CHART_OTHER_AGENCIES"
    DELEGATION_OF_AUTHORITY = "DELEGATION_OF_AUTHORITY"
    BEFORE_TRAVELLING = "BEFORE_TRAVELLING"
    TRAVELLING_OUTSIDE_CANADA = "TRAVELLING_OUTSIDE_CANADA"
    SECURITY_ASSESSMENT = "SECURITY_ASSESSMENT"
    TRANSPORTATION = "TRANSPORTATION"
    AIR_TRAVEL = "AIR_TRAVEL"
    RAIL_TRAVEL = "RAIL_TRAVEL"
    ROAD_TRAVEL = "ROAD_TRAVEL"
    ACCOMMODATION = "ACCOMMODATION"
    INCIDENTAL_EXPENSES = "INCIDENTAL_EXPENSES"
    MEALS = "MEALS"
    HOSPITALITY = "HOSPITALITY"
    CONSULTANTS_AND_CONTRACTORS = "CONSULTANTS_AND_CONTRACTORS"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    DEFINITIONS = "DEFINITIONS"
    APPENDIX_SPECIAL_STATUS = "APPENDIX_SPECIAL_STATUS"
    APPENDIX_APPROVAL_SUMMARY = "APPENDIX_APPROVAL_SUMMARY"
    APPENDIX_REVISIONS = "APPENDIX_REVISIONS"


class TravellerRole(Enum):
    DEPUTY_MINISTER = "DEPUTY_MINISTER"
    CHAIR = "CHAIR"
    APPOINTEE = "APPOINTEE"
    CEO = "CEO"
    EMPLOYEE = "EMPLOYEE"
    CONSULTANT = "CONSULTANT"


class OrganizationKind(Enum):
    MINISTRY = "MINISTRY"
    COMMISSION_PUBLIC_BODY = "COMMISSION_PUBLIC_BODY"
    OTHER_PROVINCIAL_AGENCY = "OTHER_PROVINCIAL_AGENCY"
    ELECTRICITY_ORGANIZATION = "ELECTRICITY_ORGANIZATION"


class Purpose(Enum):
    MEETING = "MEETING"
    CONFERENCE = "CONFERENCE"
    TRAINING = "TRAINING"
    INSPECTION = "INSPECTION"
    NEGOTIATION = "NEGOTIATION"
    REGULAR_OFFICE_DAY = "REGULAR_OFFICE_DAY"
    PERSONAL_VISIT = "PERSONAL_VISIT"


class SignOffSubject(Enum):
    TRAVEL_PLAN = "TRAVEL_PLAN"
    BUSINESS_CLASS = "BUSINESS_CLASS"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role"]
    name: Annotated[str, "Their name"]
    title: Annotated[str, "Their job title and organisation"]
    subject: Annotated[SignOffSubject, "What they signed: the trip itself, or a business class seat on it"]
    acting_for: Annotated[Approver, "The role whose power the signer used under a written assignment of it to them; NONE when they signed in their own right"]
    covers: Annotated[str, "What the sign-off says, in plain words"]


@dataclass
class Colleague(Output):
    name: Annotated[str, "The colleague's name"]
    title: Annotated[str, "Their job title"]
    flight_number: Annotated[str, "The flight they are already ticketed on, as search_flights lists it"]
    date: Annotated[str, "That flight's local departure date, YYYY-MM-DD"]
    cabin: Annotated[Cabin, "The cabin they are ticketed in"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title"]
    traveller_role: Annotated[TravellerRole, "What the traveller is to the organisation: its deputy minister, chair, an appointee, its chief executive, an employee, or a consultant or contractor"]
    organization: Annotated[str, "The ministry, provincial agency or organisation the traveller works for or under contract to"]
    organization_kind: Annotated[OrganizationKind, "MINISTRY; COMMISSION_PUBLIC_BODY for a provincial agency whose staff are public servants appointed under the provincial public service statute; OTHER_PROVINCIAL_AGENCY for a provincial agency whose staff are not; ELECTRICITY_ORGANIZATION for the province's electricity system operator or its power generation company"]
    special_status_granted_on: Annotated[str, "For an agency or organisation, the day cabinet's board granted it special status to have its international trips approved by its chair, YYYY-MM-DD; empty when it was never granted"]
    contract_covers_travel_costs: Annotated[bool, "For a consultant or contractor, whether their contract says the organisation pays their travel costs; false for everyone else"]
    home_city: Annotated[str, "Where the traveller lives"]
    workplace_city: Annotated[str, "Where the traveller's job is based"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    return_date: Annotated[str, "For a round trip bought as one fare, the day to fly back, YYYY-MM-DD; empty for one way"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    business_starts: Annotated[str, "When the work at the destination begins: YYYY-MM-DD HH:MM, local time there"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    requested_airline: Annotated[str, "The airline the traveller asks for, as search_flights names airlines; empty when none"]
    requested_flight: Annotated[str, "A flight number the traveller asks to be on, as search_flights lists it; empty when none"]
    wants_changeable_fare: Annotated[bool, "Whether the traveller asks for a fare that can be refunded or changed without a fee"]
    schedule_often_changes: Annotated[bool, "Whether the traveller's job is one whose trips are often moved at short notice"]
    health_need_on_file: Annotated[str, "A health or accessibility need of the traveller, documented by a physician and on file, that affects how they can fly; empty when none"]
    security_review_done: Annotated[bool, "Whether a review of the destination's physical and online safety risks was completed before today"]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file for this trip, each given in writing before today"]
    travelling_with: Annotated[list[Colleague], "Colleagues on the same trip who are already ticketed; empty when none"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
