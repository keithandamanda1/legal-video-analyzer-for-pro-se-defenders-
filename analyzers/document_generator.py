"""
Legal document generator.

Generates ready-to-file legal documents for pro se defendants in Maine.
Outputs both .docx (Word) and plain-text formats.

Documents generated:
  1. Evidence Preservation Demand Letter
  2. Brady/Giglio Discovery Demand
  3. FOAA (Freedom of Access Act) Request
  4. Motion to Suppress Evidence (4th Amendment)
  5. Motion to Suppress Statements (Miranda)
  6. Civil Rights Complaint (42 U.S.C. §1983 / Maine Civil Rights Act)
  7. Adverse Inference Motion (Spoliation)
  8. Full Case Analysis Report
  9. Incident Timeline
"""

import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import config
import database as db


# ── Word document helper ──────────────────────────────────────────────────────

def _make_docx(title: str, sections: List[Dict], output_path: str) -> str:
    """
    Create a Word document from a list of sections.
    Each section: {"heading": str or None, "text": str, "style": "normal"|"bold"|"center"}
    Returns the output path.
    """
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        doc.core_properties.author = "Legal Video Analyzer — Pro Se Defense Tool"

        # Title
        heading = doc.add_heading(title, level=0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        for section in sections:
            h = section.get("heading")
            text = section.get("text", "")
            style = section.get("style", "normal")

            if h:
                doc.add_heading(h, level=2)

            if text:
                para = doc.add_paragraph(text)
                if style == "bold":
                    for run in para.runs:
                        run.bold = True
                elif style == "center":
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.save(output_path)
        return output_path
    except ImportError:
        # Fallback: write plain text file
        txt_path = output_path.replace(".docx", ".txt")
        _make_txt(title, sections, txt_path)
        return txt_path


def _make_txt(title: str, sections: List[Dict], output_path: str) -> str:
    """Plain text fallback."""
    lines = [title, "=" * len(title), ""]
    for section in sections:
        h = section.get("heading")
        text = section.get("text", "")
        if h:
            lines.extend([h, "-" * len(h)])
        if text:
            lines.append(text)
        lines.append("")
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    return output_path


def _save_doc(case_id: str, doc_type: str, title: str, filename: str, content_sections: List[Dict]) -> Dict:
    """Save a document to disk and record it in the database."""
    doc_dir = Path(config.DOCUMENTS_FOLDER) / case_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(doc_dir / filename)
    final_path = _make_docx(title, content_sections, output_path)
    doc_id = db.save_document(case_id, doc_type, title, final_path)
    return {"id": doc_id, "path": final_path, "title": title, "type": doc_type}


# ── Date/header helpers ───────────────────────────────────────────────────────

def _today() -> str:
    return date.today().strftime("%B %d, %Y")


def _case_header(case: Dict) -> str:
    defendant = case.get("defendant_name") or "[DEFENDANT NAME]"
    case_num = case.get("case_number") or "[CASE NUMBER]"
    court = case.get("court") or "[COURT NAME]"
    county = case.get("county") or "[COUNTY]"
    charge = case.get("charge") or "[CHARGE]"
    return (
        f"STATE OF MAINE\n"
        f"{county.upper()} COUNTY\n\n"
        f"STATE OF MAINE,\n    Plaintiff,\n\n"
        f"v.\n\n"
        f"{defendant.upper()},\n    Defendant.\n\n"
        f"Docket No.: {case_num}\n"
        f"Court: {court}\n"
        f"Charge: {charge}"
    )


def _pro_se_footer(defendant: str) -> str:
    return (
        f"Respectfully submitted,\n\n"
        f"{'_' * 40}\n"
        f"{defendant or '[DEFENDANT NAME]'}\n"
        f"Pro Se Defendant\n"
        f"[Your Address]\n"
        f"[City, State ZIP]\n"
        f"[Phone Number]\n\n"
        f"Date: {_today()}\n\n"
        f"CERTIFICATE OF SERVICE\n"
        f"I hereby certify that on {_today()}, I served a copy of the foregoing upon "
        f"the prosecutor by [first class mail / hand delivery / electronic filing] to "
        f"the address on record.\n\n"
        f"{'_' * 40}\n"
        f"{defendant or '[DEFENDANT NAME]'}"
    )


# ── 1. Evidence Preservation Demand ──────────────────────────────────────────

def generate_preservation_demand(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    title = "EVIDENCE PRESERVATION DEMAND LETTER"
    sections = [
        {"text": _today()},
        {"text": (
            f"TO: [District Attorney / Prosecutor Name]\n"
            f"[Office Address]\n"
            f"[City, ME ZIP]\n\n"
            f"RE: State v. {defendant}, Docket No. {case.get('case_number') or '[NUMBER]'}\n"
            f"    FORMAL DEMAND FOR PRESERVATION OF ALL EVIDENCE"
        )},
        {"heading": "DEMAND FOR PRESERVATION", "text": (
            f"I, {defendant}, the defendant in the above-referenced matter, hereby "
            f"formally demand that you, and all law enforcement agencies and personnel "
            f"involved in this case, IMMEDIATELY preserve ALL evidence related to this matter, "
            f"including but not limited to:"
        )},
        {"text": (
            "1. ALL dashcam video footage from all patrol vehicles at the scene or involved in the incident;\n"
            "2. ALL body-worn camera footage from all officers at the scene;\n"
            "3. ALL audio recordings including dispatch recordings, radio communications, and 911 calls;\n"
            "4. ALL original, unedited, uncompressed video/audio files in their native formats;\n"
            "5. ALL metadata associated with video/audio files;\n"
            "6. ALL written incident reports, supplemental reports, and field notes;\n"
            "7. ALL evidence collected at the scene, including chain of custody documentation;\n"
            "8. Personnel files and disciplinary records of all officers involved;\n"
            "9. ALL communications (text, email, radio) related to this incident;\n"
            "10. Any exculpatory evidence as required by Brady v. Maryland, 373 U.S. 83 (1963)."
        )},
        {"heading": "LEGAL BASIS", "text": (
            "Failure to preserve evidence constitutes spoliation and may entitle the defense to "
            "sanctions, dismissal, or an adverse inference instruction. See Brady v. Maryland, 373 U.S. 83 (1963); "
            "25 M.R.S.A. §2803-B (Maine law enforcement recording requirements). "
            "Under Maine Rules of Criminal Procedure, the State has an ongoing duty to disclose "
            "all exculpatory and impeachment material."
        )},
        {"heading": "NOTICE", "text": (
            "This letter constitutes formal notice that any destruction, alteration, or failure to "
            "preserve the above evidence will be brought to the court's attention and will be the "
            "subject of an appropriate motion for sanctions, adverse inference, or dismissal."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "preservation_demand", title,
                     "evidence_preservation_demand.docx", sections)


# ── 2. Brady/Giglio Discovery Demand ─────────────────────────────────────────

def generate_brady_request(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    title = "DEFENDANT'S BRADY/GIGLIO DISCOVERY REQUEST"
    sections = [
        {"style": "center", "text": "STATE OF MAINE\nSUPERIOR / DISTRICT COURT"},
        {"text": _case_header(case)},
        {"heading": "MOTION AND DEMAND FOR EXCULPATORY EVIDENCE", "text": (
            f"NOW COMES the Defendant, {defendant}, pro se, and pursuant to Brady v. Maryland, "
            f"373 U.S. 83 (1963); Giglio v. United States, 405 U.S. 150 (1972); "
            f"Kyles v. Whitley, 514 U.S. 419 (1995); and Maine Rules of Criminal Procedure, "
            f"Rule 16, respectfully requests immediate disclosure of all exculpatory, "
            f"favorable, and impeachment evidence in the possession of the prosecution and "
            f"all law enforcement agencies."
        )},
        {"heading": "ITEMS DEMANDED", "text": (
            "1. ALL video/audio recordings of the incident, including original unedited files;\n"
            "2. ALL exculpatory evidence, including evidence that contradicts the prosecution's theory;\n"
            "3. Complete disciplinary and complaint history of all officers involved;\n"
            "4. Records of any prior Brady/Giglio violations by the officers involved;\n"
            "5. Any evidence of inconsistencies in officers' statements;\n"
            "6. Any deals, agreements, or consideration provided to witnesses;\n"
            "7. All scientific tests, reports, and lab results, including those unfavorable to prosecution;\n"
            "8. All 911 calls, dispatch logs, and radio communications;\n"
            "9. GPS data and routing records for police vehicles;\n"
            "10. Any evidence of racial profiling or selective enforcement;\n"
            "11. The officers' complete training records relevant to this incident."
        )},
        {"heading": "LEGAL STANDARD", "text": (
            "The prosecution's Brady obligation extends to all material evidence in the hands "
            "of law enforcement. See Kyles v. Whitley, 514 U.S. 419, 437 (1995). "
            "Evidence is material if there is a 'reasonable probability' of a different result "
            "had it been disclosed. Strickler v. Greene, 527 U.S. 263 (1999). "
            "Failure to comply is grounds for dismissal or new trial."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "brady_request", title, "brady_giglio_request.docx", sections)


# ── 3. FOAA Request ───────────────────────────────────────────────────────────

def generate_foaa_request(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    incident_date = case.get("incident_date") or "[DATE OF INCIDENT]"
    title = "MAINE FREEDOM OF ACCESS ACT (FOAA) REQUEST"
    sections = [
        {"text": _today()},
        {"text": (
            "TO: Records Custodian\n"
            "[Police Department Name]\n"
            "[Address]\n"
            "[City, ME ZIP]\n\n"
            "RE: Freedom of Access Act Request — 1 M.R.S.A. §408-A\n"
            f"    Incident Date: {incident_date}"
        )},
        {"heading": "FOAA REQUEST", "text": (
            f"Pursuant to the Maine Freedom of Access Act, 1 M.R.S.A. §401 et seq., "
            f"I, {defendant}, hereby request copies of the following public records related "
            f"to the incident on {incident_date}:"
        )},
        {"text": (
            "1. All dashcam video recordings from all police vehicles at the scene;\n"
            "2. All body-worn camera recordings from all officers at the scene;\n"
            "3. All incident reports and supplemental reports;\n"
            "4. All dispatch logs and CAD records;\n"
            "5. All 911 call recordings;\n"
            "6. Radio communication recordings related to this incident;\n"
            "7. Arrest report(s) and booking records;\n"
            "8. Any use-of-force reports filed in connection with this incident;\n"
            "9. The department's written policies for use of force, body cameras, and dashcams;\n"
            "10. The officer's training records related to use of force and camera operation."
        )},
        {"heading": "LEGAL BASIS & TIMELINE", "text": (
            "Under 1 M.R.S.A. §408-A, public records must be provided within 5 business days "
            "or the agency must acknowledge the request and provide a timeline. "
            "Please notify me within 5 days if any items are withheld and state the specific "
            "statutory exemption being claimed for each withheld item, as required by law. "
            "I am willing to pay reasonable duplication costs up to $[AMOUNT] without prior "
            "approval. Please waive fees for records that cost $5 or less."
        )},
        {"text": (
            f"Name: {defendant}\n"
            f"Address: [Your Address]\n"
            f"Phone: [Your Phone]\n"
            f"Date: {_today()}"
        )},
    ]

    return _save_doc(case_id, "foaa_request", title, "foaa_records_request.docx", sections)


# ── 4. Motion to Suppress (4th Amendment) ────────────────────────────────────

def generate_motion_to_suppress(case_id: str, analysis_id: Optional[str] = None) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    violations = db.get_case_violations(case_id)
    search_violations = [v for v in violations
                         if "search" in (v.get("violation_type") or "").lower()
                         or "seizure" in (v.get("violation_type") or "").lower()]

    # Build violation facts section
    facts_text = ""
    if search_violations:
        facts_text = "The following specific violations were documented in the video analysis:\n\n"
        for v in search_violations[:5]:
            facts_text += (
                f"• At timestamp {v.get('timestamp_label', 'N/A')}: "
                f"{v.get('description', 'Undescribed violation')} "
                f"[{v.get('law_reference', '')}]\n"
            )
    else:
        facts_text = (
            "On [DATE], at approximately [TIME], officers [conducted a search/seized evidence/stopped "
            "defendant] at [LOCATION] without a warrant and without any applicable exception to "
            "the warrant requirement."
        )

    title = "DEFENDANT'S MOTION TO SUPPRESS EVIDENCE"
    sections = [
        {"style": "center", "text": "STATE OF MAINE\nSUPERIOR / DISTRICT COURT"},
        {"text": _case_header(case)},
        {"heading": "MOTION TO SUPPRESS ILLEGALLY OBTAINED EVIDENCE", "text": (
            f"NOW COMES the Defendant, {defendant}, pro se, and respectfully moves this "
            f"Honorable Court to suppress all evidence obtained as a result of an unlawful "
            f"search and seizure in violation of the Fourth Amendment to the United States "
            f"Constitution and Article I, Section 5 of the Maine Constitution."
        )},
        {"heading": "STATEMENT OF FACTS", "text": facts_text},
        {"heading": "LEGAL ARGUMENT", "text": (
            "I. THE WARRANTLESS SEARCH VIOLATED THE FOURTH AMENDMENT\n\n"
            "The Fourth Amendment prohibits 'unreasonable searches and seizures' and requires "
            "that warrants issue only upon 'probable cause.' U.S. Const. amend. IV. "
            "A warrantless search is presumptively unreasonable. Katz v. United States, 389 U.S. 347 (1967). "
            "The burden is on the State to demonstrate that a recognized exception applies.\n\n"
            "II. THE EVIDENCE MUST BE SUPPRESSED — EXCLUSIONARY RULE\n\n"
            "Evidence obtained in violation of the Fourth Amendment must be suppressed "
            "under the exclusionary rule. Mapp v. Ohio, 367 U.S. 643 (1961). "
            "All evidence derived from the illegal search — 'fruit of the poisonous tree' — "
            "is also inadmissible. Wong Sun v. United States, 371 U.S. 471 (1963).\n\n"
            "III. MAINE CONSTITUTIONAL PROTECTION\n\n"
            "Article I, Section 5 of the Maine Constitution independently prohibits "
            "unreasonable searches and seizures and is interpreted no more narrowly than "
            "the Fourth Amendment. State v. Boyington, 2015 ME 101."
        )},
        {"heading": "RELIEF REQUESTED", "text": (
            "WHEREFORE, Defendant respectfully requests that this Court:\n"
            "1. Suppress all evidence obtained from the illegal search;\n"
            "2. Suppress all evidence derived from the illegal search (fruit of the poisonous tree);\n"
            "3. Grant a hearing on this Motion;\n"
            "4. Grant any other relief the Court deems just and proper."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "motion_to_suppress", title, "motion_to_suppress.docx", sections)


# ── 5. Motion to Suppress Statements (Miranda) ───────────────────────────────

def generate_motion_to_suppress_statements(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    violations = db.get_case_violations(case_id)
    miranda_violations = [v for v in violations
                          if "miranda" in (v.get("violation_type") or "").lower()]

    facts_text = ""
    if miranda_violations:
        facts_text = "The video analysis documented the following Miranda-related violations:\n\n"
        for v in miranda_violations[:5]:
            facts_text += (
                f"• {v.get('timestamp_label', 'N/A')}: {v.get('description', '')}\n"
            )
    else:
        facts_text = (
            "On [DATE], officers questioned the Defendant while in custody without first "
            "advising the Defendant of Miranda rights, or questioning continued after "
            "the Defendant invoked the right to remain silent or requested counsel."
        )

    title = "MOTION TO SUPPRESS STATEMENTS (MIRANDA VIOLATION)"
    sections = [
        {"style": "center", "text": "STATE OF MAINE"},
        {"text": _case_header(case)},
        {"heading": "MOTION TO SUPPRESS DEFENDANT'S STATEMENTS", "text": (
            f"NOW COMES the Defendant, {defendant}, pro se, and moves to suppress all "
            f"statements made during custodial interrogation as obtained in violation of "
            f"the Fifth and Sixth Amendments and Miranda v. Arizona, 384 U.S. 436 (1966)."
        )},
        {"heading": "STATEMENT OF FACTS", "text": facts_text},
        {"heading": "LEGAL ARGUMENT", "text": (
            "I. MIRANDA WARNINGS WERE REQUIRED\n\n"
            "Miranda warnings are required prior to any custodial interrogation. "
            "Miranda v. Arizona, 384 U.S. 436 (1966). Custody is determined by whether "
            "a reasonable person would feel free to leave. Thompson v. Keohane, 516 U.S. 99 (1995). "
            "Interrogation includes express questioning and its 'functional equivalent.' "
            "Rhode Island v. Innis, 446 U.S. 291 (1980).\n\n"
            "II. STATEMENTS MUST BE SUPPRESSED\n\n"
            "Statements obtained without Miranda warnings in a custodial context are "
            "inadmissible in the prosecution's case-in-chief. Miranda, 384 U.S. at 479. "
            "Once a defendant invokes the right to silence, all interrogation must cease "
            "'scrupulously.' Michigan v. Mosley, 423 U.S. 96 (1975). Once counsel is "
            "invoked, questioning may not resume unless defendant initiates. "
            "Edwards v. Arizona, 451 U.S. 477 (1981).\n\n"
            "III. MAINE PROTECTION\n\n"
            "Maine Constitution Art. I §6 prohibits compelling any person to give "
            "evidence against themselves."
        )},
        {"heading": "RELIEF REQUESTED", "text": (
            "Defendant requests suppression of all statements made during the custodial "
            "interrogation, a hearing on this Motion, and all other relief deemed just."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "motion_to_suppress_statements", title,
                     "motion_suppress_miranda.docx", sections)


# ── 6. Civil Rights Complaint ─────────────────────────────────────────────────

def generate_civil_rights_complaint(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    violations = db.get_case_violations(case_id)

    facts = "\n".join(
        f"• {v.get('timestamp_label', '')}: {v.get('description', '')} "
        f"[{v.get('law_reference', '')}]"
        for v in violations[:8] if v.get("is_illegal")
    ) or "See video analysis attached."

    title = "CIVIL RIGHTS COMPLAINT — 42 U.S.C. §1983 / MAINE CIVIL RIGHTS ACT"
    sections = [
        {"style": "center", "text": "UNITED STATES DISTRICT COURT\nDISTRICT OF MAINE"},
        {"text": (
            f"{defendant.upper()},\n    Plaintiff,\n\n"
            f"v.\n\n"
            f"[OFFICER FULL NAME], individually and in his/her official capacity;\n"
            f"[DEPARTMENT NAME];\n"
            f"[MUNICIPALITY NAME],\n    Defendants.\n\n"
            f"Civil Action No.: ____________"
        )},
        {"heading": "COMPLAINT FOR CIVIL RIGHTS VIOLATIONS", "text": (
            f"Plaintiff {defendant}, proceeding pro se, brings this action pursuant to "
            f"42 U.S.C. §1983 and the Maine Civil Rights Act, 5 M.R.S.A. §4681 et seq., "
            f"for deprivation of rights secured by the United States and Maine Constitutions."
        )},
        {"heading": "JURISDICTION AND VENUE", "text": (
            "This Court has jurisdiction under 28 U.S.C. §§1331, 1343(a)(3). "
            "Venue is proper in this district under 28 U.S.C. §1391(b)."
        )},
        {"heading": "STATEMENT OF FACTS", "text": facts},
        {"heading": "CLAIMS FOR RELIEF", "text": (
            "COUNT I — 42 U.S.C. §1983 — VIOLATION OF 4th AMENDMENT\n"
            "Defendants, acting under color of state law, violated Plaintiff's right to be "
            "free from unreasonable search and seizure.\n\n"
            "COUNT II — 42 U.S.C. §1983 — EXCESSIVE FORCE\n"
            "Defendants used force that was not objectively reasonable under Graham v. Connor, "
            "490 U.S. 386 (1989), violating Plaintiff's 4th Amendment rights.\n\n"
            "COUNT III — MAINE CIVIL RIGHTS ACT (5 M.R.S.A. §4681)\n"
            "Defendants, by physical force or threat, interfered with Plaintiff's rights "
            "secured by the U.S. and Maine Constitutions.\n\n"
            "COUNT IV — MUNICIPAL LIABILITY (MONELL)\n"
            "The constitutional violations resulted from the municipality's official policy, "
            "custom, or practice. Monell v. Dept. of Social Services, 436 U.S. 658 (1978)."
        )},
        {"heading": "RELIEF REQUESTED", "text": (
            "Plaintiff requests: compensatory damages; punitive damages against individual "
            "officers; injunctive relief; attorney's fees under 42 U.S.C. §1988; "
            "and all other relief the Court deems just."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "civil_rights_complaint", title,
                     "civil_rights_complaint_1983.docx", sections)


# ── 7. Adverse Inference Motion ───────────────────────────────────────────────

def generate_adverse_inference_motion(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    defendant = case.get("defendant_name") or "[YOUR NAME]"
    title = "MOTION FOR ADVERSE INFERENCE INSTRUCTION (SPOLIATION OF EVIDENCE)"
    sections = [
        {"style": "center", "text": "STATE OF MAINE"},
        {"text": _case_header(case)},
        {"heading": "MOTION FOR ADVERSE INFERENCE — DESTRUCTION/ALTERATION OF EVIDENCE", "text": (
            f"NOW COMES the Defendant, {defendant}, pro se, and moves this Court to issue "
            f"an adverse inference instruction based on the State's failure to preserve, "
            f"or alteration of, material video evidence."
        )},
        {"heading": "GROUNDS", "text": (
            "1. The video evidence produced by the State contains metadata indicating it was "
            "processed through video editing software after recording, suggesting alteration.\n\n"
            "2. The video is missing audio, which should be present given the recording equipment used.\n\n"
            "3. The video duration is inconsistent with the full duration of the recorded encounter.\n\n"
            "4. Officers failed to activate body-worn cameras as required by 25 M.R.S.A. §2803-B.\n\n"
            "5. The State has failed to provide the original, unedited footage despite demand."
        )},
        {"heading": "LEGAL ARGUMENT", "text": (
            "The prosecution has a constitutional obligation to preserve material evidence. "
            "Brady v. Maryland, 373 U.S. 83 (1963). Where the State fails to preserve "
            "potentially exculpatory evidence, an adverse inference may be appropriate. "
            "The appropriate remedy is an instruction that the missing/altered evidence "
            "would have been favorable to the defense. "
            "Maine courts recognize spoliation remedies when bad faith or negligent destruction occurs."
        )},
        {"heading": "RELIEF REQUESTED", "text": (
            "Defendant requests: (1) an adverse inference jury instruction; "
            "(2) alternatively, suppression of the altered/incomplete video; "
            "(3) dismissal of charges if the full, unaltered footage cannot be produced; "
            "(4) a hearing on this Motion."
        )},
        {"text": _pro_se_footer(defendant)},
    ]

    return _save_doc(case_id, "adverse_inference_motion", title,
                     "adverse_inference_motion.docx", sections)


# ── 8. Case Analysis Report ───────────────────────────────────────────────────

def generate_case_report(case_id: str) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    violations = db.get_case_violations(case_id)
    analyses = db.list_analyses(case_id)
    evidence_list = db.list_evidence(case_id)
    notes = db.get_notes(case_id)

    # Get win probability from most recent completed analysis
    win_pct = "N/A"
    for a in analyses:
        if a.get("status") == "complete" and a.get("win_probability"):
            win_pct = f"{a['win_probability'] * 100:.1f}%"
            break

    violation_text = "\n".join(
        f"[{v.get('severity', 0)}/10] {v.get('timestamp_label', '')}: "
        f"{v.get('description', '')} — {v.get('law_reference', '')}"
        for v in violations
    ) or "No violations recorded yet."

    evidence_text = "\n".join(
        f"• {e.get('original_name', e.get('file_path', ''))}: "
        f"{e.get('file_type', 'unknown')} "
        f"({'analyzed' if e.get('analyzed') else 'not yet analyzed'})"
        for e in evidence_list
    ) or "No evidence uploaded."

    title = f"CASE ANALYSIS REPORT — {case.get('name', 'Unnamed Case')}"
    sections = [
        {"heading": "CASE INFORMATION", "text": (
            f"Case Name: {case.get('name', 'N/A')}\n"
            f"Defendant: {case.get('defendant_name', 'N/A')}\n"
            f"Case Number: {case.get('case_number', 'N/A')}\n"
            f"Court: {case.get('court', 'N/A')}\n"
            f"Charge: {case.get('charge', 'N/A')}\n"
            f"Incident Date: {case.get('incident_date', 'N/A')}\n"
            f"Report Generated: {_today()}"
        )},
        {"heading": "ANALYSIS SUMMARY", "text": (
            f"Total Violations Found: {len(violations)}\n"
            f"Critical (Severity 9-10): {sum(1 for v in violations if v.get('severity', 0) >= 9)}\n"
            f"Serious (Severity 7-8): {sum(1 for v in violations if 7 <= v.get('severity', 0) < 9)}\n"
            f"Estimated Win Probability: {win_pct}\n\n"
            f"DISCLAIMER: Win probability is an AI estimate and NOT legal advice."
        )},
        {"heading": "VIOLATIONS DOCUMENTED", "text": violation_text},
        {"heading": "EVIDENCE INVENTORY", "text": evidence_text},
        {"heading": "CASE NOTES", "text": (
            "\n".join(f"[{n.get('created_at', '')}] {n.get('note', '')}" for n in notes)
            or "No notes recorded."
        )},
        {"heading": "RECOMMENDED ACTIONS", "text": (
            "1. File Evidence Preservation Demand immediately\n"
            "2. File Brady/Giglio discovery demand\n"
            "3. File FOAA request for all records\n"
            "4. File Motion to Suppress (if 4th Amendment violations documented)\n"
            "5. File Motion to Suppress Statements (if Miranda violations documented)\n"
            "6. Contact Maine Legal Services: 1-800-750-5353 (free legal help)\n"
            "7. Contact Pine Tree Legal Assistance: 207-774-8211\n"
            "8. Contact Maine ACLU (civil rights cases): 207-774-5444"
        )},
    ]

    return _save_doc(case_id, "case_report", title, "case_analysis_report.docx", sections)


# ── 9. Incident Timeline ──────────────────────────────────────────────────────

def generate_timeline(case_id: str, analysis_id: Optional[str] = None) -> Dict:
    case = db.get_case(case_id)
    if not case:
        return {"error": "Case not found"}

    violations = db.get_case_violations(case_id)
    sorted_violations = sorted(violations, key=lambda v: v.get("timestamp_secs") or 0)

    timeline_text = ""
    for v in sorted_violations:
        ts = v.get("timestamp_label", "??:??:??")
        severity = v.get("severity", 0)
        flag = "[ILLEGAL]" if v.get("is_illegal") else "[RED FLAG]" if v.get("is_red_flag") else "[NOTE]"
        timeline_text += (
            f"\n{ts}  {flag} Severity {severity}/10\n"
            f"  Description: {v.get('description', 'N/A')}\n"
            f"  Law: {v.get('law_reference', 'N/A')}\n"
            f"  Recommendation: {v.get('recommendation', 'N/A')}\n"
        )

    title = f"INCIDENT TIMELINE — {case.get('name', 'Unnamed Case')}"
    sections = [
        {"heading": "CASE INFORMATION", "text": (
            f"Case: {case.get('name')}\n"
            f"Defendant: {case.get('defendant_name', 'N/A')}\n"
            f"Incident Date: {case.get('incident_date', 'N/A')}\n"
            f"Generated: {_today()}"
        )},
        {"heading": "CHRONOLOGICAL EVENT TIMELINE", "text": (
            timeline_text or "No violation timeline data available yet. Run video analysis first."
        )},
        {"heading": "HOW TO USE THIS TIMELINE", "text": (
            "This timeline can be used in court to show the chronological sequence of events "
            "as documented by the video evidence. Each entry includes the exact timestamp, "
            "the nature of the violation, and the applicable law. "
            "Reference specific timestamps when cross-examining officers."
        )},
    ]

    return _save_doc(case_id, "timeline", title, "incident_timeline.docx", sections)


# ── Master generator ──────────────────────────────────────────────────────────

DOCUMENT_GENERATORS = {
    "preservation_demand": generate_preservation_demand,
    "brady_request": generate_brady_request,
    "foaa_request": generate_foaa_request,
    "motion_to_suppress": generate_motion_to_suppress,
    "motion_to_suppress_statements": generate_motion_to_suppress_statements,
    "civil_rights_complaint": generate_civil_rights_complaint,
    "adverse_inference_motion": generate_adverse_inference_motion,
    "case_report": generate_case_report,
    "timeline": generate_timeline,
}

DOCUMENT_TITLES = {
    "preservation_demand": "Evidence Preservation Demand Letter",
    "brady_request": "Brady/Giglio Discovery Demand",
    "foaa_request": "FOAA Public Records Request",
    "motion_to_suppress": "Motion to Suppress Evidence (4th Amendment)",
    "motion_to_suppress_statements": "Motion to Suppress Statements (Miranda)",
    "civil_rights_complaint": "Civil Rights Complaint (42 U.S.C. §1983)",
    "adverse_inference_motion": "Motion for Adverse Inference (Spoliation)",
    "case_report": "Full Case Analysis Report",
    "timeline": "Incident Timeline",
}


def generate_document(case_id: str, doc_type: str) -> Dict:
    """Generate a document by type. Returns {id, path, title, type} or {error: ...}."""
    gen = DOCUMENT_GENERATORS.get(doc_type)
    if not gen:
        return {"error": f"Unknown document type: {doc_type}"}
    return gen(case_id)
