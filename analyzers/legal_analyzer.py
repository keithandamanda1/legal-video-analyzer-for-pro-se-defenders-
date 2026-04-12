"""
Legal analyzer — takes violations from the video analyzer and metadata analyzer,
matches them to specific Maine and federal laws, generates legal strategy advice,
and computes an updated win probability incorporating all evidence.
"""

from typing import Dict, List, Optional
from knowledge_base.maine_laws import get_maine_laws_for_date
from knowledge_base.federal_laws import FEDERAL_LAWS
from knowledge_base.violation_patterns import VIOLATION_PATTERNS


def analyze_case_legal_posture(
    violations: List[Dict],
    metadata_findings: List[Dict],
    case_info: Dict,
) -> Dict:
    """
    Full legal analysis of a case.

    Parameters
    ----------
    violations      : from database.get_case_violations()
    metadata_findings : from database.get_metadata_findings() (all evidence)
    case_info       : case dict from database.get_case()

    Returns
    -------
    dict with keys: applicable_laws, motions_available, legal_theories,
                    win_probability, recommendations, action_items
    """
    incident_date = case_info.get("incident_date")
    maine_laws = get_maine_laws_for_date(incident_date or "2000-01-01")

    # ── Determine which laws are directly triggered ───────────────────────────
    triggered_law_ids = set()
    for v in violations:
        vtype = v.get("violation_type", "")
        for law in maine_laws:
            if vtype in law.get("violations", []):
                triggered_law_ids.add(law["id"])
        for law in FEDERAL_LAWS:
            if vtype in law.get("violations", []):
                triggered_law_ids.add(law["id"])

    applicable_laws = [
        law for law in (maine_laws + FEDERAL_LAWS)
        if law["id"] in triggered_law_ids
    ]

    # ── Identify available motions ────────────────────────────────────────────
    motions = _identify_motions(violations, metadata_findings, incident_date)

    # ── Build legal theories ──────────────────────────────────────────────────
    theories = _build_legal_theories(violations, metadata_findings)

    # ── Action items ──────────────────────────────────────────────────────────
    action_items = _build_action_items(violations, metadata_findings, case_info)

    # ── Win probability (full case assessment) ────────────────────────────────
    win_prob = _full_win_probability(violations, metadata_findings, motions)

    return {
        "applicable_laws": applicable_laws,
        "motions_available": motions,
        "legal_theories": theories,
        "win_probability": win_prob,
        "action_items": action_items,
        "recommendations": action_items,  # alias for template compatibility
    }


# ── Motion identification ─────────────────────────────────────────────────────

def _identify_motions(violations, metadata_findings, incident_date) -> List[Dict]:
    motions = []
    vtypes = {v.get("violation_type", "") for v in violations}
    meta_flags = {f.get("flag", "") for f in metadata_findings}

    # Motion to Suppress — illegal search/seizure
    search_types = {t for t in vtypes if "search" in t or "seizure" in t or "stop" in t}
    if search_types:
        motions.append({
            "motion_type": "motion_to_suppress",
            "title": "Motion to Suppress Evidence (Illegal Search/Seizure)",
            "basis": "4th Amendment to U.S. Constitution; Maine Constitution Art. I §5",
            "strength": "strong",
            "description": (
                "Evidence obtained through an unlawful search or seizure must be suppressed "
                "under the exclusionary rule (Mapp v. Ohio). If the video shows a warrantless "
                "search without a valid exception, all evidence from that search can be thrown out."
            ),
            "key_cases": ["Mapp v. Ohio, 367 U.S. 643 (1961)", "Wong Sun v. United States, 371 U.S. 471 (1963)"],
        })

    # Motion to Suppress — Miranda violation
    miranda_types = {t for t in vtypes if "miranda" in t or "questioning" in t}
    if miranda_types:
        motions.append({
            "motion_type": "motion_to_suppress_statements",
            "title": "Motion to Suppress Statements (Miranda Violation)",
            "basis": "5th & 6th Amendments; Miranda v. Arizona, 384 U.S. 436 (1966)",
            "strength": "very strong",
            "description": (
                "Any statements made by the defendant during custodial interrogation without "
                "Miranda warnings, or after invoking the right to silence or counsel, must be "
                "suppressed and cannot be used by the prosecution."
            ),
            "key_cases": [
                "Miranda v. Arizona, 384 U.S. 436 (1966)",
                "Edwards v. Arizona, 451 U.S. 477 (1981)",
            ],
        })

    # Motion to Dismiss — constitutional violations
    serious_violations = [v for v in violations if v.get("severity", 0) >= 8]
    if len(serious_violations) >= 2:
        motions.append({
            "motion_type": "motion_to_dismiss",
            "title": "Motion to Dismiss for Constitutional Violations",
            "basis": "Due Process — 5th and 14th Amendments",
            "strength": "moderate",
            "description": (
                "Where multiple serious constitutional violations exist, a motion to dismiss "
                "for outrageous government conduct or due process violations may succeed. "
                "This is a high bar but is supported by the documented violations found."
            ),
            "key_cases": ["United States v. Russell, 411 U.S. 423 (1973)"],
        })

    # Adverse inference motion — camera issues
    if "missing_audio" in meta_flags or "body_cam_not_activated" in vtypes or "editing_software" in meta_flags:
        motions.append({
            "motion_type": "adverse_inference_motion",
            "title": "Motion for Adverse Inference (Spoliation of Evidence)",
            "basis": "25 M.R.S.A. §2803-B; Brady v. Maryland; Maine Evidence Rule 404",
            "strength": "strong if tampering shown",
            "description": (
                "When police fail to preserve, activate, or provide required camera footage, "
                "or when metadata shows the video was edited, the court may instruct the jury "
                "to assume the missing/altered footage would have been favorable to the defense."
            ),
            "key_cases": [
                "Brady v. Maryland, 373 U.S. 83 (1963)",
                "Strickler v. Greene, 527 U.S. 263 (1999)",
            ],
        })

    # Civil rights claim (42 U.S.C. §1983)
    civil_types = {"excessive_force", "arrest_without_probable_cause",
                   "illegal_search", "civil_rights_violation"}
    if vtypes & civil_types:
        motions.append({
            "motion_type": "civil_rights_complaint_1983",
            "title": "Civil Rights Complaint — 42 U.S.C. §1983",
            "basis": "42 U.S.C. §1983; 5 M.R.S.A. §4681 (Maine Civil Rights Act)",
            "strength": "depends on qualified immunity analysis",
            "description": (
                "Officers may be sued individually for constitutional violations under §1983. "
                "The municipality may also be liable if violations stem from policy or practice "
                "(Monell). Maine's Civil Rights Act provides additional protection without "
                "requiring proof of racial animus."
            ),
            "key_cases": [
                "Monroe v. Pape, 365 U.S. 167 (1961)",
                "Monell v. Dept. of Social Services, 436 U.S. 658 (1978)",
            ],
        })

    # Brady motion
    motions.append({
        "motion_type": "brady_request",
        "title": "Brady/Giglio Demand for Exculpatory Evidence",
        "basis": "Brady v. Maryland, 373 U.S. 83 (1963); Giglio v. United States, 405 U.S. 150 (1972)",
        "strength": "always file this motion",
        "description": (
            "Demand ALL exculpatory evidence in the prosecution's possession, including: "
            "all video footage (unedited originals), officer disciplinary records, "
            "prior complaints against the officer(s), any evidence undermining the state's case."
        ),
        "key_cases": ["Brady v. Maryland, 373 U.S. 83 (1963)"],
    })

    return motions


# ── Legal theory builder ──────────────────────────────────────────────────────

def _build_legal_theories(violations, metadata_findings) -> List[Dict]:
    theories = []
    vtypes = {v.get("violation_type", "") for v in violations}

    if any("search" in t or "seizure" in t for t in vtypes):
        theories.append({
            "theory": "Fruit of the Poisonous Tree",
            "explanation": (
                "Under Wong Sun v. United States, evidence derived from an illegal search is "
                "inadmissible. If the stop, arrest, or search was unconstitutional, ALL evidence "
                "that flows from it — contraband found, statements made, further evidence "
                "discovered — must be suppressed."
            ),
            "applicable_violations": [v for v in violations if "search" in (v.get("violation_type") or "")],
        })

    if any("miranda" in t for t in vtypes):
        theories.append({
            "theory": "Miranda Exclusionary Rule",
            "explanation": (
                "Statements obtained without Miranda warnings in a custodial context, or "
                "after the right to silence or counsel was invoked, are per se inadmissible. "
                "The prosecution cannot use them in its case-in-chief."
            ),
            "applicable_violations": [v for v in violations if "miranda" in (v.get("violation_type") or "")],
        })

    if any(f.get("flag") in ("editing_software", "discontinuous_timestamps", "timestamp_gap")
           for f in metadata_findings):
        theories.append({
            "theory": "Chain of Custody / Spoliation",
            "explanation": (
                "The metadata shows potential alteration of the video evidence. Under Maine "
                "evidence rules and federal principles, tampered evidence has a compromised "
                "chain of custody. Request the original raw footage, all editing history, "
                "and file a motion for adverse inference or dismissal if originals are unavailable."
            ),
            "applicable_violations": [],
        })

    if any("force" in t for t in vtypes):
        theories.append({
            "theory": "Excessive Force (Graham v. Connor)",
            "explanation": (
                "Under Graham v. Connor, force must be 'objectively reasonable' considering: "
                "(1) severity of the alleged crime, (2) whether subject posed immediate safety "
                "threat, (3) whether subject was actively resisting. If none of these factors "
                "justify the force shown on video, a §1983 civil rights claim is viable."
            ),
            "applicable_violations": [v for v in violations if "force" in (v.get("violation_type") or "")],
        })

    return theories


# ── Action items ──────────────────────────────────────────────────────────────

def _build_action_items(violations, metadata_findings, case_info) -> List[Dict]:
    items = []
    vtypes = {v.get("violation_type", "") for v in violations}
    meta_flags = {f.get("flag", "") for f in metadata_findings}
    charge = case_info.get("charge", "")

    # Always-file items
    items.append({
        "priority": "URGENT",
        "action": "Send written evidence preservation demand to prosecutor AND police department TODAY",
        "reason": "Failure to preserve evidence can result in sanctions, but only if you formally demanded it first.",
        "document_type": "preservation_demand",
    })
    items.append({
        "priority": "URGENT",
        "action": "File Brady/Giglio demand for all exculpatory evidence and officer disciplinary records",
        "reason": "Brady material includes ALL videos (unedited), officer complaints, and contradictory reports.",
        "document_type": "brady_request",
    })
    items.append({
        "priority": "HIGH",
        "action": "File public records request (FOAA) for all dashcam/body cam footage, dispatch logs, incident reports",
        "reason": "Maine Freedom of Access Act (1 M.R.S.A. §401) gives you the right to these records.",
        "document_type": "foaa_request",
    })

    if any("search" in t or "seizure" in t for t in vtypes):
        items.append({
            "priority": "HIGH",
            "action": "File Motion to Suppress evidence obtained from illegal search/seizure",
            "reason": "4th Amendment exclusionary rule — illegally obtained evidence must be suppressed.",
            "document_type": "motion_to_suppress",
        })

    if any("miranda" in t for t in vtypes):
        items.append({
            "priority": "HIGH",
            "action": "File Motion to Suppress all statements (Miranda violation)",
            "reason": "Statements during custodial interrogation without Miranda warning are inadmissible.",
            "document_type": "motion_to_suppress_statements",
        })

    if "editing_software" in meta_flags or "discontinuous_timestamps" in meta_flags:
        items.append({
            "priority": "HIGH",
            "action": "File Motion for Adverse Inference — video appears to have been edited",
            "reason": "Metadata shows editing software was used. Request original raw footage immediately.",
            "document_type": "adverse_inference_motion",
        })

    if any("force" in t for t in vtypes):
        items.append({
            "priority": "HIGH",
            "action": "Document and photograph all injuries; seek medical examination to document injuries on record",
            "reason": "Medical documentation is essential evidence for excessive force claims.",
            "document_type": None,
        })
        items.append({
            "priority": "MEDIUM",
            "action": "File complaint with Maine Attorney General's office regarding excessive force",
            "reason": "AG office investigates law enforcement misconduct in Maine.",
            "document_type": "ag_complaint",
        })

    items.append({
        "priority": "MEDIUM",
        "action": "Contact Maine Legal Services (1-800-750-5353) or Pine Tree Legal Assistance (207-774-8211)",
        "reason": "Free legal help for those who cannot afford attorneys in Maine.",
        "document_type": None,
    })
    items.append({
        "priority": "MEDIUM",
        "action": "Contact the Maine ACLU if civil rights violations are documented (207-774-5444)",
        "reason": "ACLU of Maine takes cases involving police misconduct and civil rights violations.",
        "document_type": None,
    })

    return items


# ── Win probability (case-level) ──────────────────────────────────────────────

def _full_win_probability(violations, metadata_findings, motions) -> Dict:
    base = 0.28
    factors = []

    # Score motions
    motion_values = {
        "very strong": 0.15,
        "strong": 0.10,
        "moderate": 0.07,
        "depends on qualified immunity analysis": 0.05,
        "always file this motion": 0.03,
    }
    for m in motions:
        strength = m.get("strength", "")
        boost = motion_values.get(strength, 0.03)
        base += boost
        factors.append({
            "factor": m["title"],
            "impact": f"+{boost*100:.0f}%",
            "confidence": strength,
        })

    # Score violations by severity
    for v in violations:
        sev = v.get("severity", 0)
        conf = v.get("confidence", "low")
        cmult = {"high": 1.0, "medium": 0.7, "low": 0.35}.get(conf, 0.35)
        boost = max(0, (sev - 4)) * 0.015 * cmult
        if boost > 0:
            base += boost

    # Score metadata red flags
    for f in metadata_findings:
        sev = f.get("severity", 0)
        if sev >= 7:
            boost = 0.08
            base += boost
            factors.append({
                "factor": f"Metadata red flag: {f.get('key', 'unknown')}",
                "impact": f"+{boost*100:.0f}%",
                "confidence": "medium",
            })

    prob = round(min(base, 0.93), 4)
    return {
        "probability": prob,
        "percentage": f"{prob*100:.1f}%",
        "factors": factors,
        "disclaimer": (
            "AI estimate only — NOT legal advice. Actual outcomes depend on judge, "
            "prosecutor, jury, witness credibility, and many factors beyond this analysis. "
            "For free Maine legal help: Pine Tree Legal Assistance 207-774-8211."
        ),
    }
