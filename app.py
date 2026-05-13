"""
Legal Video Analyzer — Flask Web Application

Runs as a local web server. Navigate to http://127.0.0.1:5000 in your browser.

Features:
  • Case management (create, view, update, organize)
  • Upload police video evidence
  • Analyze video with Claude AI (literally watches the footage)
  • Metadata analysis for tampering/red flags
  • Win probability estimation
  • Document generation (motions, complaints, demands)
  • Case notes — persistent memory, never auto-reset
"""

import os
import threading
import json
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_file, abort
)

from config import config
import database as db
from data.housing_facts import seed_housing_data
from data.pcr_facts import seed_pcr_data
from analyzers.video_analyzer import analyze_video
from analyzers.metadata_analyzer import analyze_metadata, format_metadata_for_display
from analyzers.legal_analyzer import analyze_case_legal_posture
from analyzers.document_generator import (
    generate_document, DOCUMENT_TITLES
)

# ── App setup ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER

# Create all required directories
for d in [config.UPLOAD_FOLDER, config.CASES_FOLDER,
          config.DOCUMENTS_FOLDER, config.EXPORTS_FOLDER]:
    Path(d).mkdir(parents=True, exist_ok=True)

# Initialize database on startup
db.init_db()
seed_housing_data()
seed_pcr_data()

# ── Allowed file extensions ───────────────────────────────────────────────────
VIDEO_EXTENSIONS = {
    "mp4", "avi", "mov", "mkv", "wmv", "flv", "webm",
    "m4v", "mpg", "mpeg", "3gp", "ts", "mts", "m2ts",
}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in VIDEO_EXTENSIONS


# ── Context processors ────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        "now": datetime.utcnow(),
        "app_version": "1.0.0",
        "api_configured": config.is_configured,
        "api_provider": config.api_provider,
    }


# ── Routes: Dashboard ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    cases = db.list_cases()
    # Enrich with stats
    enriched = []
    for case in cases:
        violations = db.get_case_violations(case["id"])
        analyses = db.list_analyses(case["id"])
        evidence = db.list_evidence(case["id"])
        win_pct = None
        for a in analyses:
            if a.get("status") == "complete" and a.get("win_probability"):
                win_pct = f"{a['win_probability'] * 100:.1f}%"
                break
        enriched.append({
            **case,
            "violation_count": len(violations),
            "evidence_count": len(evidence),
            "analysis_count": len(analyses),
            "win_probability_pct": win_pct,
        })
    return render_template("index.html", cases=enriched)


# ── Routes: Case creation ─────────────────────────────────────────────────────

@app.route("/case/new", methods=["GET"])
def new_case_form():
    return render_template("new_case.html")


@app.route("/case/create", methods=["POST"])
def create_case():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Case name is required.", "error")
        return redirect(url_for("new_case_form"))

    case = db.create_case(
        name=name,
        case_number=request.form.get("case_number", "").strip(),
        defendant_name=request.form.get("defendant_name", "").strip(),
        incident_date=request.form.get("incident_date", "").strip() or None,
        arrest_date=request.form.get("arrest_date", "").strip() or None,
        court=request.form.get("court", "").strip(),
        county=request.form.get("county", "").strip(),
        charge=request.form.get("charge", "").strip(),
        description=request.form.get("description", "").strip(),
    )
    flash(f'Case "{name}" created successfully.', "success")
    return redirect(url_for("case_detail", case_id=case["id"]))


# ── Routes: Case detail ───────────────────────────────────────────────────────

@app.route("/case/<case_id>")
def case_detail(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)

    evidence_list = db.list_evidence(case_id)
    analyses = db.list_analyses(case_id)
    violations = db.get_case_violations(case_id)
    notes = db.get_notes(case_id)
    documents = db.list_documents(case_id)

    # Latest completed analysis for summary
    latest_analysis = None
    for a in analyses:
        if a.get("status") == "complete":
            latest_analysis = db.get_analysis(a["id"])
            break

    # Legal posture
    metadata_findings = []
    for ev in evidence_list:
        metadata_findings.extend(db.get_metadata_findings(ev["id"]))

    legal_posture = analyze_case_legal_posture(violations, metadata_findings, case)

    # Violation stats
    critical = [v for v in violations if v.get("severity", 0) >= 9]
    serious = [v for v in violations if 7 <= v.get("severity", 0) < 9]
    illegal_count = sum(1 for v in violations if v.get("is_illegal"))

    return render_template(
        "case_detail.html",
        case=case,
        evidence_list=evidence_list,
        analyses=analyses,
        violations=violations,
        critical_violations=critical,
        serious_violations=serious,
        illegal_count=illegal_count,
        notes=notes,
        documents=documents,
        latest_analysis=latest_analysis,
        legal_posture=legal_posture,
        document_types=DOCUMENT_TITLES,
    )


@app.route("/case/<case_id>/edit", methods=["GET", "POST"])
def edit_case(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)
    if request.method == "POST":
        db.update_case(
            case_id,
            name=request.form.get("name", case["name"]).strip(),
            case_number=request.form.get("case_number", "").strip(),
            defendant_name=request.form.get("defendant_name", "").strip(),
            incident_date=request.form.get("incident_date", "").strip() or None,
            arrest_date=request.form.get("arrest_date", "").strip() or None,
            court=request.form.get("court", "").strip(),
            county=request.form.get("county", "").strip(),
            charge=request.form.get("charge", "").strip(),
            description=request.form.get("description", "").strip(),
        )
        flash("Case updated.", "success")
        return redirect(url_for("case_detail", case_id=case_id))
    return render_template("new_case.html", case=case, editing=True)


@app.route("/case/<case_id>/delete", methods=["POST"])
def delete_case(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)
    # Confirm via form field
    confirm = request.form.get("confirm_delete", "")
    if confirm != case.get("name", ""):
        flash("Deletion cancelled — case name did not match.", "error")
        return redirect(url_for("case_detail", case_id=case_id))
    db.delete_case(case_id)
    flash(f'Case "{case["name"]}" permanently deleted.', "warning")
    return redirect(url_for("index"))


# ── Routes: Evidence upload ───────────────────────────────────────────────────

@app.route("/case/<case_id>/upload", methods=["POST"])
def upload_evidence(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)

    if "video_file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("case_detail", case_id=case_id))

    file = request.files["video_file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("case_detail", case_id=case_id))

    if not allowed_file(file.filename):
        flash(f"File type not supported. Supported types: {', '.join(sorted(VIDEO_EXTENSIONS))}", "error")
        return redirect(url_for("case_detail", case_id=case_id))

    # Save file
    original_name = file.filename
    safe_name = secure_filename(file.filename)
    case_upload_dir = Path(config.UPLOAD_FOLDER) / case_id
    case_upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = str(case_upload_dir / safe_name)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else "unknown"

    evidence = db.add_evidence(
        case_id=case_id,
        file_path=file_path,
        file_type=ext,
        original_name=original_name,
        file_size=file_size,
    )

    flash(f'Evidence "{original_name}" uploaded. Run analysis to examine it.', "success")
    return redirect(url_for("case_detail", case_id=case_id))


# ── Routes: Analysis ──────────────────────────────────────────────────────────

@app.route("/case/<case_id>/analyze/<evidence_id>", methods=["POST"])
def start_analysis(case_id, evidence_id):
    if not config.is_configured:
        flash(
            "No API key configured. Add ANTHROPIC_API_KEY or OPENROUTER_API_KEY to your .env file.",
            "error"
        )
        return redirect(url_for("case_detail", case_id=case_id))

    evidence = db.get_evidence(evidence_id)
    if not evidence or evidence["case_id"] != case_id:
        abort(404)

    case = db.get_case(case_id)
    incident_date = case.get("incident_date") if case else None

    # Create analysis record
    analysis = db.create_analysis(case_id, evidence_id, "full")
    analysis_id = analysis["id"]

    # Run metadata analysis immediately (fast)
    try:
        meta_result = analyze_metadata(
            evidence_id=evidence_id,
            case_id=case_id,
            video_path=evidence["file_path"],
            incident_date=incident_date,
        )
        flash(
            f"Metadata analyzed: {meta_result.get('red_flag_count', 0)} red flags found.",
            "info"
        )
    except Exception as e:
        flash(f"Metadata analysis warning: {e}", "warning")

    # Run video analysis in background thread
    def run_analysis():
        try:
            analyze_video(
                analysis_id=analysis_id,
                evidence_id=evidence_id,
                case_id=case_id,
                video_path=evidence["file_path"],
                incident_date=incident_date,
                interval=config.VIDEO_FRAME_INTERVAL,
            )
            # Mark evidence as analyzed
            conn = db.get_db()
            try:
                conn.execute("UPDATE evidence SET analyzed=1 WHERE id=?", (evidence_id,))
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:
            db.update_analysis(analysis_id, status="failed", error_message=str(exc))

    thread = threading.Thread(target=run_analysis, daemon=True)
    thread.start()

    flash(
        "Video analysis started! This runs in the background — "
        "refresh the page or check the status below. Large videos may take several minutes.",
        "success"
    )
    return redirect(url_for("analysis_status", case_id=case_id, analysis_id=analysis_id))


@app.route("/case/<case_id>/analysis/<analysis_id>")
def analysis_status(case_id, analysis_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)
    analysis = db.get_analysis(analysis_id)
    if not analysis or analysis["case_id"] != case_id:
        abort(404)

    violations = db.get_violations(analysis_id)
    evidence = db.get_evidence(analysis["evidence_id"])
    metadata_findings = db.get_metadata_findings(analysis["evidence_id"]) if evidence else []
    meta_display = []
    if evidence:
        from analyzers.metadata_analyzer import extract_metadata, format_metadata_for_display
        raw_meta = extract_metadata(evidence["file_path"])
        if "error" not in raw_meta:
            meta_display = format_metadata_for_display({
                **raw_meta.get("format", {}),
                "streams": raw_meta.get("streams", []),
                "filesystem": {},
            })

    return render_template(
        "analysis.html",
        case=case,
        analysis=analysis,
        violations=violations,
        evidence=evidence,
        metadata_findings=metadata_findings,
        meta_display=meta_display,
    )


# ── Routes: API (AJAX polling) ────────────────────────────────────────────────

@app.route("/api/analysis/<analysis_id>/status")
def api_analysis_status(analysis_id):
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "status": analysis.get("status"),
        "progress": analysis.get("progress", 0),
        "violation_count": len(db.get_violations(analysis_id)),
        "win_probability": analysis.get("win_probability"),
        "error_message": analysis.get("error_message"),
    })


@app.route("/api/case/<case_id>/violations")
def api_violations(case_id):
    violations = db.get_case_violations(case_id)
    return jsonify(violations)


# ── Routes: Notes ─────────────────────────────────────────────────────────────

@app.route("/case/<case_id>/note", methods=["POST"])
def add_note(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)
    note_text = request.form.get("note", "").strip()
    if note_text:
        db.add_note(case_id, note_text)
        flash("Note saved.", "success")
    return redirect(url_for("case_detail", case_id=case_id) + "#notes")


# ── Routes: Documents ─────────────────────────────────────────────────────────

@app.route("/case/<case_id>/documents/generate", methods=["POST"])
def generate_doc(case_id):
    case = db.get_case(case_id)
    if not case:
        abort(404)

    doc_type = request.form.get("doc_type", "")
    if not doc_type:
        flash("No document type selected.", "error")
        return redirect(url_for("case_detail", case_id=case_id))

    result = generate_document(case_id, doc_type)
    if "error" in result:
        flash(f"Document generation failed: {result['error']}", "error")
    else:
        flash(f'Document "{result["title"]}" generated successfully.', "success")

    return redirect(url_for("case_detail", case_id=case_id) + "#documents")


@app.route("/case/<case_id>/documents/<doc_id>/download")
def download_document(case_id, doc_id):
    doc = db.get_document(doc_id)
    if not doc or doc["case_id"] != case_id:
        abort(404)
    file_path = doc["file_path"]
    if not os.path.exists(file_path):
        flash("Document file not found on disk.", "error")
        return redirect(url_for("case_detail", case_id=case_id))
    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path),
    )


# ── Routes: Housing Dashboard ─────────────────────────────────────────────────
# MHRC H25-0389 / H25-0395 — BHA (Bangor Housing Authority) — FHA federal track

@app.route("/housing")
def housing_dashboard():
    from datetime import date
    today = date.today()
    evidence = db.housing_list_evidence()
    emails = db.housing_list_emails()
    denial_changes = db.housing_list_denial_changes()
    deadlines = db.housing_list_deadlines()

    # Compute days remaining for each deadline
    for dl in deadlines:
        try:
            dl_date = date.fromisoformat(dl["deadline_date"])
            dl["days_remaining"] = (dl_date - today).days
        except Exception:
            dl["days_remaining"] = None

    flagged = [e for e in evidence if e.get("flagged")]
    missing_emails = [em for em in emails if em.get("missing")]
    categories = sorted({e["category"] for e in evidence if e.get("category")})

    return render_template(
        "housing_dashboard.html",
        evidence=evidence,
        emails=emails,
        denial_changes=denial_changes,
        deadlines=deadlines,
        flagged=flagged,
        missing_emails=missing_emails,
        categories=categories,
        today=today.isoformat(),
    )


@app.route("/housing/evidence/add", methods=["POST"])
def housing_add_evidence():
    db.housing_add_evidence(
        event_date=request.form.get("event_date", ""),
        category=request.form.get("category", "fact"),
        title=request.form.get("title", "").strip(),
        description=request.form.get("description", "").strip(),
        source=request.form.get("source", "").strip(),
        exhibit_label=request.form.get("exhibit_label", "").strip(),
        verified=1 if request.form.get("verified") else 0,
        flagged=1 if request.form.get("flagged") else 0,
        flag_reason=request.form.get("flag_reason", "").strip(),
    )
    flash("Evidence entry added.", "success")
    return redirect(url_for("housing_dashboard") + "#evidence")


@app.route("/housing/evidence/<eid>/delete", methods=["POST"])
def housing_delete_evidence(eid):
    db.housing_delete_evidence(eid)
    flash("Entry deleted.", "info")
    return redirect(url_for("housing_dashboard") + "#evidence")


@app.route("/housing/email/add", methods=["POST"])
def housing_add_email():
    db.housing_add_email(
        sent_date=request.form.get("sent_date", ""),
        sender=request.form.get("sender", "").strip(),
        recipient=request.form.get("recipient", "").strip(),
        subject=request.form.get("subject", "").strip(),
        summary=request.form.get("summary", "").strip(),
        exhibit_label=request.form.get("exhibit_label", "").strip(),
        produced=1 if request.form.get("produced") else 0,
        missing=1 if request.form.get("missing") else 0,
        notes=request.form.get("notes", "").strip(),
    )
    flash("Email record added.", "success")
    return redirect(url_for("housing_dashboard") + "#emails")


@app.route("/housing/email/<eid>/delete", methods=["POST"])
def housing_delete_email(eid):
    db.housing_delete_email(eid)
    flash("Email record deleted.", "info")
    return redirect(url_for("housing_dashboard") + "#emails")


@app.route("/housing/denial/add", methods=["POST"])
def housing_add_denial():
    db.housing_add_denial_change(
        change_date=request.form.get("change_date", ""),
        reason_before=request.form.get("reason_before", "").strip(),
        reason_after=request.form.get("reason_after", "").strip(),
        source_document=request.form.get("source_document", "").strip(),
        significance=request.form.get("significance", "").strip(),
    )
    flash("Denial reason change recorded.", "success")
    return redirect(url_for("housing_dashboard") + "#denials")


@app.route("/housing/deadline/add", methods=["POST"])
def housing_add_deadline():
    db.housing_add_deadline(
        deadline_date=request.form.get("deadline_date", ""),
        label=request.form.get("label", "").strip(),
        description=request.form.get("description", "").strip(),
        authority=request.form.get("authority", "").strip(),
        critical=1 if request.form.get("critical") else 0,
        met=1 if request.form.get("met") else 0,
    )
    flash("Deadline added.", "success")
    return redirect(url_for("housing_dashboard") + "#deadlines")


@app.route("/housing/note/add", methods=["POST"])
def housing_add_note():
    note = request.form.get("note", "").strip()
    if note:
        db.pcr_add_note(note, ground_num=None, author="Housing Case")
        flash("Note saved.", "success")
    return redirect(url_for("housing_dashboard") + "#notes")


# ── Routes: PCR Petition Organizer ───────────────────────────────────────────
# CR-2018-03023 — 15 M.R.S. §§ 2121-2132

PCR_GROUNDS = {
    1: "Involuntary Plea — Boykin / M.R.U. Crim. P. 11(b)(3)",
    2: "Ineffective Assistance of Counsel — Strickland / Hill / Lafler",
    3: "Brady / Giglio / Napue Violations",
    4: "Fourth Amendment — Unlawful Stop, Search, and Seizure",
    5: "Legally Impossible Gabapentin Charge (Ex Post Facto)",
    6: "Coercive Pretrial Conditions — Plea Involuntariness Context",
    7: "Equitable Tolling / Newly Discovered Evidence — 15 M.R.S. § 2128-B",
}


@app.route("/pcr")
def pcr_organizer():
    ground_filter = request.args.get("ground", type=int)
    evidence = db.pcr_list_evidence(ground_filter)
    contradictions = db.pcr_list_contradictions(ground_filter)
    exhibits = db.pcr_list_exhibits()
    notes = db.pcr_list_notes()

    obtained_count = sum(1 for ex in exhibits if ex.get("obtained"))
    missing_count = sum(1 for ex in exhibits if not ex.get("obtained"))
    filed_count = sum(1 for ex in exhibits if ex.get("filed"))

    missing_evidence = [e for e in evidence if e.get("status") in ("missing", "needed")]

    return render_template(
        "pcr_organizer.html",
        evidence=evidence,
        contradictions=contradictions,
        exhibits=exhibits,
        notes=notes,
        grounds=PCR_GROUNDS,
        ground_filter=ground_filter,
        obtained_count=obtained_count,
        missing_count=missing_count,
        filed_count=filed_count,
        missing_evidence=missing_evidence,
        categories=["stop", "chain_of_custody", "phone", "plea",
                    "newly_discovered", "brady"],
        statuses=["documented", "obtained", "missing", "needed"],
    )


@app.route("/pcr/evidence/add", methods=["POST"])
def pcr_add_evidence():
    db.pcr_add_evidence(
        event_date=request.form.get("event_date", ""),
        category=request.form.get("category", ""),
        ground_number=int(request.form.get("ground_number", 0) or 0),
        title=request.form.get("title", "").strip(),
        description=request.form.get("description", "").strip(),
        source=request.form.get("source", "").strip(),
        exhibit_label=request.form.get("exhibit_label", "").strip(),
        law_reference=request.form.get("law_reference", "").strip(),
        status=request.form.get("status", "documented"),
    )
    flash("Evidence entry added.", "success")
    return redirect(url_for("pcr_organizer") + "#evidence")


@app.route("/pcr/evidence/<eid>/delete", methods=["POST"])
def pcr_delete_evidence(eid):
    db.pcr_delete_evidence(eid)
    flash("Entry deleted.", "info")
    return redirect(url_for("pcr_organizer") + "#evidence")


@app.route("/pcr/contradiction/add", methods=["POST"])
def pcr_add_contradiction():
    db.pcr_add_contradiction(
        contradiction_date=request.form.get("contradiction_date", ""),
        ground_number=int(request.form.get("ground_number", 0) or 0),
        item_a_label=request.form.get("item_a_label", "").strip(),
        item_a_text=request.form.get("item_a_text", "").strip(),
        item_b_label=request.form.get("item_b_label", "").strip(),
        item_b_text=request.form.get("item_b_text", "").strip(),
        significance=request.form.get("significance", "").strip(),
        law_reference=request.form.get("law_reference", "").strip(),
        resolution_needed=request.form.get("resolution_needed", "").strip(),
    )
    flash("Contradiction logged.", "success")
    return redirect(url_for("pcr_organizer") + "#contradictions")


@app.route("/pcr/contradiction/<cid>/delete", methods=["POST"])
def pcr_delete_contradiction(cid):
    db.pcr_delete_contradiction(cid)
    flash("Contradiction deleted.", "info")
    return redirect(url_for("pcr_organizer") + "#contradictions")


@app.route("/pcr/exhibit/add", methods=["POST"])
def pcr_add_exhibit():
    db.pcr_add_exhibit(
        exhibit_label=request.form.get("exhibit_label", "").strip(),
        title=request.form.get("title", "").strip(),
        description=request.form.get("description", "").strip(),
        source=request.form.get("source", "").strip(),
        ground_numbers=request.form.get("ground_numbers", "").strip(),
        obtained=1 if request.form.get("obtained") else 0,
        filed=1 if request.form.get("filed") else 0,
        notes=request.form.get("notes", "").strip(),
    )
    flash("Exhibit added to index.", "success")
    return redirect(url_for("pcr_organizer") + "#exhibits")


@app.route("/pcr/exhibit/<eid>/delete", methods=["POST"])
def pcr_delete_exhibit(eid):
    db.pcr_delete_exhibit(eid)
    flash("Exhibit deleted.", "info")
    return redirect(url_for("pcr_organizer") + "#exhibits")


@app.route("/pcr/note/add", methods=["POST"])
def pcr_add_note_route():
    note = request.form.get("note", "").strip()
    ground_num = request.form.get("ground_num", "")
    if note:
        db.pcr_add_note(note, ground_num=int(ground_num) if ground_num else None)
        flash("Note saved.", "success")
    return redirect(url_for("pcr_organizer") + "#notes")


@app.route("/pcr/exhibit-index.txt")
def pcr_exhibit_index():
    exhibits = db.pcr_list_exhibits()
    lines = [
        "EXHIBIT INDEX",
        "PETITION FOR POST-CONVICTION REVIEW",
        "Docket No. CR-2018-03023 — State of Maine",
        "Petitioner: Keith A. King",
        "=" * 70,
        "",
    ]
    for ex in exhibits:
        status = "OBTAINED" if ex.get("obtained") else "NEEDED"
        filed = " / FILED" if ex.get("filed") else ""
        lines.append(f"{ex['exhibit_label']}: {ex['title']}")
        lines.append(f"  Status: {status}{filed}")
        lines.append(f"  Source: {ex.get('source', '')}")
        if ex.get("ground_numbers"):
            lines.append(f"  Grounds: {ex['ground_numbers']}")
        if ex.get("description"):
            lines.append(f"  Description: {ex['description']}")
        if ex.get("notes"):
            lines.append(f"  Notes: {ex['notes']}")
        lines.append("")

    from flask import Response
    return Response("\n".join(lines), mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment; filename=exhibit-index-CR-2018-03023.txt"})


# ── Routes: Error handlers ────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found", code=404), 404


@app.errorhandler(413)
def too_large(e):
    flash("File too large. Maximum upload size is 4 GB.", "error")
    return redirect(url_for("index"))


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error=str(e), code=500), 500


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  LEGAL VIDEO ANALYZER — Pro Se Defense Tool")
    print("=" * 60)
    print(f"  Database: {config.DATABASE_PATH}")
    print(f"  Uploads:  {config.UPLOAD_FOLDER}")
    print(f"  API Key:  {'CONFIGURED' if config.ANTHROPIC_API_KEY else 'NOT SET — add to .env'}")
    print(f"\n  Open in browser: http://{config.HOST}:{config.PORT}")
    print("=" * 60 + "\n")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
