"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "ontario-travel" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. The directive has no rule on
# overnight stops, so no overnight scenario is required; its one rule on colleagues travelling together (business
# continuity, lines 461-462) is a soft "consider", tested by a distractor.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "ontario", "ottawa", "toronto", "montreal", "minister", "deputy", "secretary", "cabinet", "treasury", "board",
    "chair", "ceo", "cfo", "appointee", "consultant", "contractor", "contract", "manager", "supervisor", "agency",
    "commission", "ministry", "status", "special", "delegation", "delegate", "approval", "approved", "business",
    "economy", "flexible", "flex", "refundable", "change", "commute", "office", "workplace", "personal", "family",
    "vacation", "health", "medical", "accommodation", "security", "international", "canada", "usa", "abroad",
    "lowest", "cheap", "fare", "airline", "loyalty", "points", "aeroplan", "colleague", "team", "late", "early",
    "hearing", "own", "self", "expired", "lapsed", "valid", "power", "hydro", "electricity",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.TravellerRole, contract.OrganizationKind, contract.Purpose, contract.SignOffSubject]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section).
MAX_PASS_ALWAYS_FLAG = 1
MAX_PASS_ALWAYS_LOWEST = 10

# The directive sets no flight-duration threshold (rules.DURATION_RULES is empty), so there are no cases.
DURATION_CASES = []
