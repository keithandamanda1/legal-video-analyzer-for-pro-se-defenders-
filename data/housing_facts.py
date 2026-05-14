"""
Seed data for Housing Case Dashboard — MHRC H25-0389 / H25-0395
Call seed_housing_data() once at startup if the table is empty.
"""
import database as db


HOUSING_EVIDENCE_SEED = [
    # ── Chronological verified facts ──────────────────────────────────────────
    {
        "event_date": "2024-09-03",
        "category": "fact",
        "title": "Apartment offered to Petitioner",
        "description": (
            "BHA/Perkins offered Petitioner the apartment on September 3, 2024. "
            "Offer was made BEFORE any background check was initiated — "
            "establishing that the screening order was reversed from policy."
        ),
        "source": "Lease offer letter / BHA records",
        "exhibit_label": "Exhibit A",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "Offer preceded background check — reversal of required order",
    },
    {
        "event_date": "2024-09-03",
        "category": "fact",
        "title": "Background check run AFTER denial — critical sequence violation",
        "description": (
            "BHA ran a background check on Petitioner AFTER the denial decision "
            "had already been made. This inverts the required sequence under "
            "24 C.F.R. § 966.4 and BHA's own Admissions and Continued Occupancy "
            "Policy (ACOP). Pre-texted denial: the outcome was fixed before screening."
        ),
        "source": "BHA ACOP; background check timestamp records",
        "exhibit_label": "Exhibit B",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "CRITICAL: background check post-dates denial — pretextual denial",
    },
    {
        "event_date": "2024-10-01",
        "category": "denial",
        "title": "Initial denial issued — stated reason #1",
        "description": (
            "BHA issued its initial denial letter. Stated reason was [criminal history]. "
            "No individualized assessment was conducted as required by HUD guidance "
            "(HUD Notice PIH 2015-19 and April 2016 HUD Criminal History Guidance)."
        ),
        "source": "BHA Denial Letter #1",
        "exhibit_label": "Exhibit C",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "No individualized assessment; blanket criminal-history bar violates FHA",
    },
    {
        "event_date": "2025-01-15",
        "category": "foaa",
        "title": "FOAA records request submitted to BHA",
        "description": (
            "Petitioner submitted a formal FOAA (Freedom of Access to Information Act, "
            "1 M.R.S. § 408-A) request to BHA for all records related to the denial, "
            "application file, screening notes, and communications with Knox/Perkins."
        ),
        "source": "FOAA Request Letter",
        "exhibit_label": "Exhibit D",
        "verified": 1,
        "flagged": 0,
        "flag_reason": "",
    },
    {
        "event_date": "2025-01-15",
        "category": "foaa",
        "title": "FOAA response MISSING — Knox-Perkins screening emails not produced",
        "description": (
            "BHA did not produce internal emails between Knox and Perkins discussing "
            "the denial decision. These emails were specifically requested and are "
            "responsive to the FOAA request. Non-production may constitute willful "
            "withholding under 1 M.R.S. § 408-A(8)."
        ),
        "source": "FOAA response (incomplete); identified gap in production",
        "exhibit_label": "Exhibit E",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "MISSING: Knox-Perkins internal emails — potential willful withholding",
    },
    {
        "event_date": "2025-02-01",
        "category": "document",
        "title": "MHRC Complaint H25-0389 filed",
        "description": (
            "Petitioner filed MHRC Complaint H25-0389 alleging housing discrimination "
            "under the Maine Human Rights Act (5 M.R.S. § 4582) and Fair Housing Act "
            "(42 U.S.C. § 3604). Complaint includes FHA familial status, disability, "
            "and retaliation grounds."
        ),
        "source": "MHRC filing record",
        "exhibit_label": "Exhibit F",
        "verified": 1,
        "flagged": 0,
        "flag_reason": "",
    },
    {
        "event_date": "2025-02-01",
        "category": "document",
        "title": "MHRC Complaint H25-0395 filed",
        "description": (
            "Related MHRC Complaint H25-0395 filed contemporaneously. Addresses "
            "overlapping conduct and parties. Cross-referenced with H25-0389."
        ),
        "source": "MHRC filing record",
        "exhibit_label": "Exhibit G",
        "verified": 1,
        "flagged": 0,
        "flag_reason": "",
    },
    {
        "event_date": "2025-04-28",
        "category": "fact",
        "title": "MHRC Day-180 extension window CLOSED",
        "description": (
            "The 180-day window during which Petitioner could request an extension of "
            "MHRC proceedings closed on April 28, 2026. MHRC must now complete its "
            "investigation or Petitioner may request a right-to-sue letter to proceed "
            "in federal court under the FHA."
        ),
        "source": "MHRC case docket; 5 M.R.S. § 4612",
        "exhibit_label": "",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "Deadline: must monitor MHRC for right-to-sue or dismissal",
    },
    {
        "event_date": "2025-10-01",
        "category": "document",
        "title": "BHA Master Key Log produced (MHRC Exhibit B)",
        "description": (
            "BHA Master Key Log produced in response to MHRC discovery. Log shows "
            "ZERO entry for August 2, 2018 — corroborating PCR petition claim of "
            "an off-book key handoff. Cross-reference: PCR Ground 4 (Fourth Amendment)."
        ),
        "source": "BHA Key Log (MHRC Exhibit B)",
        "exhibit_label": "Exhibit H",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "Cross-matter evidence: also supports PCR Ground 4",
    },
    {
        "event_date": "2025-10-15",
        "category": "document",
        "title": "HUD FOIA response — inter-agency cover-up emails (Exhibit L)",
        "description": (
            "HUD FOIA records reveal internal emails showing HUD officials "
            "Kara E. Norman and Richa Karki (Boston Regional Office) coordinated "
            "with BHA counsel 'Bethany' and BrHA Director Perkins to ignore "
            "Petitioner's records requests — an inter-agency cover-up. "
            "These emails are Exhibit L to the MHRC complaint."
        ),
        "source": "HUD FOIA response",
        "exhibit_label": "Exhibit L",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "CRITICAL: HUD Boston Region coordinated suppression of records requests",
    },
    {
        "event_date": "2025-12-17",
        "category": "testimony",
        "title": "AAG Stuver admits Aggravated Class A charges were 'inadvertent error'",
        "description": (
            "Former AAG Janice Stuver formally admitted the Aggravated Class A "
            "charges were based on an 'inadvertent error' regarding the location "
            "of evidence. This admission is cross-material to both the PCR petition "
            "and the housing case (shows pattern of government error/misconduct)."
        ),
        "source": "AAG Stuver written admission, December 17, 2025",
        "exhibit_label": "Exhibit M",
        "verified": 1,
        "flagged": 1,
        "flag_reason": "Cross-matter: admission of prosecutorial error supports PCR and housing bias narrative",
    },
]


HOUSING_EMAILS_SEED = [
    {
        "sent_date": "2024-09-03",
        "sender": "BHA / Perkins",
        "recipient": "Knox",
        "subject": "Re: King application — unit offer",
        "summary": "Internal coordination email re: apartment offer to Petitioner — REQUESTED but NOT PRODUCED in FOAA response.",
        "exhibit_label": "Exhibit E-1",
        "produced": 0,
        "missing": 1,
        "notes": "Critical gap: this email would show whether denial decision preceded the offer or vice versa.",
    },
    {
        "sent_date": "2024-09-10",
        "sender": "Knox",
        "recipient": "Perkins",
        "subject": "Re: King — background check results",
        "summary": "Internal email re: background check results and denial rationale — REQUESTED but NOT PRODUCED.",
        "exhibit_label": "Exhibit E-2",
        "produced": 0,
        "missing": 1,
        "notes": "Timing of this email relative to denial letter will prove pre-texted denial.",
    },
    {
        "sent_date": "2025-01-20",
        "sender": "BHA Counsel Bethany",
        "recipient": "HUD Boston (Norman/Karki)",
        "subject": "Re: King FOAA request — handling",
        "summary": "Email produced via HUD FOIA showing BHA counsel and HUD coordinating response to Petitioner's records request. Exhibit L.",
        "exhibit_label": "Exhibit L-1",
        "produced": 1,
        "missing": 0,
        "notes": "Produced via HUD FOIA. Shows inter-agency coordination to obstruct records access.",
    },
    {
        "sent_date": "2025-01-22",
        "sender": "Kara E. Norman (HUD Boston)",
        "recipient": "Richa Karki (HUD Boston)",
        "subject": "King complaint — BHA coordination",
        "summary": "HUD internal email (Exhibit L) — Norman and Karki discussing how to handle King's complaint in coordination with BHA.",
        "exhibit_label": "Exhibit L-2",
        "produced": 1,
        "missing": 0,
        "notes": "Key evidence of HUD Boston Region acting as advocate for BHA rather than neutral investigator.",
    },
]


HOUSING_DENIAL_CHANGES_SEED = [
    {
        "change_date": "2024-10-01",
        "reason_before": "(None — initial denial)",
        "reason_after": "Criminal history — unspecified conviction(s)",
        "source_document": "BHA Denial Letter #1",
        "significance": "Initial stated reason. No individualized assessment provided. Blanket bar.",
    },
    {
        "change_date": "2024-11-15",
        "reason_before": "Criminal history — unspecified conviction(s)",
        "reason_after": "Criminal history AND alleged lease violations at prior tenancy",
        "source_document": "BHA Response to MHRC inquiry",
        "significance": "Reason shifted to add a second ground AFTER complaint was filed — post-hoc rationalization.",
    },
    {
        "change_date": "2025-03-01",
        "reason_before": "Criminal history AND alleged lease violations at prior tenancy",
        "reason_after": "Safety concerns for other residents (unspecified)",
        "source_document": "BHA MHRC position statement",
        "significance": "Third different reason. Pattern of shifting rationale = pretext under McDonnell Douglas framework.",
    },
]


HOUSING_DEADLINES_SEED = [
    {
        "deadline_date": "2026-04-28",
        "label": "MHRC Day-180 Extension Window — CLOSED",
        "description": "The 180-day period within which MHRC must act or Petitioner may request right-to-sue. This window has closed.",
        "authority": "5 M.R.S. § 4612",
        "critical": 1,
        "met": 1,
    },
    {
        "deadline_date": "2026-09-26",
        "label": "FHA Federal Filing Deadline — HARD STOP",
        "description": (
            "Federal Fair Housing Act (42 U.S.C. § 3613) requires civil action to be "
            "filed within two years of the discriminatory act. This is the hard federal "
            "deadline. Do NOT rely on MHRC tolling without confirming with Pine Tree Legal."
        ),
        "authority": "42 U.S.C. § 3613(a)(1)(A)",
        "critical": 1,
        "met": 0,
    },
    {
        "deadline_date": "2026-07-01",
        "label": "Target: Retain counsel or file pro se federal complaint",
        "description": (
            "To meet the September 26 FHA deadline with adequate preparation time, "
            "Petitioner should retain counsel or commit to pro se federal filing by July 1, 2026. "
            "Contact Pine Tree Legal Assistance immediately."
        ),
        "authority": "Internal planning deadline",
        "critical": 1,
        "met": 0,
    },
    {
        "deadline_date": "2026-06-01",
        "label": "Request MHRC right-to-sue letter if no determination",
        "description": (
            "If MHRC has not issued a finding by June 1, request a right-to-sue letter "
            "to preserve federal court access. This allows filing in federal district court "
            "independently of the MHRC outcome."
        ),
        "authority": "42 U.S.C. § 3613; 5 M.R.S. § 4613",
        "critical": 1,
        "met": 0,
    },
    {
        "deadline_date": "2026-05-20",
        "label": "Pine Tree Legal consultation",
        "description": "Schedule consultation with Pine Tree Legal Assistance re: FHA federal complaint and MHRC status.",
        "authority": "Self-imposed",
        "critical": 0,
        "met": 0,
    },
]


def seed_housing_data() -> None:
    if db.housing_seeded():
        return

    for ev in HOUSING_EVIDENCE_SEED:
        db.housing_add_evidence(**ev)

    for em in HOUSING_EMAILS_SEED:
        db.housing_add_email(**em)

    for dc in HOUSING_DENIAL_CHANGES_SEED:
        db.housing_add_denial_change(**dc)

    for dl in HOUSING_DEADLINES_SEED:
        db.housing_add_deadline(**dl)
