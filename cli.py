#!/usr/bin/env python3
"""
Legal Video Analyzer — Interactive CLI
Use this when running in a cloud environment where the web UI isn't accessible.
Run: python3 cli.py
"""
import os
import sys
import json
import textwrap
from pathlib import Path
from datetime import datetime

# Ensure we're in the project directory
os.chdir(Path(__file__).parent)

from config import config
import database as db
from analyzers.metadata_analyzer import analyze_metadata, format_metadata_for_display
from analyzers.legal_analyzer import analyze_case_legal_posture
from analyzers.document_generator import generate_document, DOCUMENT_TITLES


# ── Display helpers ───────────────────────────────────────────────────────────

def hr(char="─", width=60):
    print(char * width)

def header(title):
    print()
    hr("═")
    print(f"  {title}")
    hr("═")

def section(title):
    print()
    hr()
    print(f"  {title}")
    hr()

def success(msg): print(f"\n  ✓  {msg}")
def warn(msg):    print(f"\n  ⚠  {msg}")
def error(msg):   print(f"\n  ✗  {msg}")
def info(msg):    print(f"\n  ℹ  {msg}")

def wrap(text, indent=4):
    for line in textwrap.wrap(text, width=72, initial_indent=" "*indent,
                               subsequent_indent=" "*indent):
        print(line)

def severity_label(s):
    s = int(s or 0)
    if s >= 9: return f"[CRITICAL {s}/10]"
    if s >= 7: return f"[SERIOUS  {s}/10]"
    if s >= 5: return f"[MODERATE {s}/10]"
    return f"[MINOR    {s}/10]"

def menu(title, options):
    """Show a numbered menu and return the chosen key."""
    print(f"\n  {title}")
    for i, (key, label) in enumerate(options, 1):
        print(f"    {i}) {label}")
    print(f"    0) Back / Cancel")
    while True:
        choice = input("\n  Choice: ").strip()
        if choice == "0":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except ValueError:
            pass
        print("  Invalid choice, try again.")

def prompt(label, default=None):
    if default:
        val = input(f"  {label} [{default}]: ").strip()
        return val or default
    return input(f"  {label}: ").strip()


# ── Case management ───────────────────────────────────────────────────────────

def list_cases_menu():
    cases = db.list_cases()
    if not cases:
        warn("No cases yet. Create one first.")
        return None
    print()
    for i, c in enumerate(cases, 1):
        violations = db.get_case_violations(c["id"])
        print(f"  {i}) {c['name']}")
        print(f"       Charge: {c.get('charge','—')}  |  "
              f"Violations: {len(violations)}  |  "
              f"Status: {c.get('status','active')}")
    print("  0) Back")
    while True:
        choice = input("\n  Select case: ").strip()
        if choice == "0": return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(cases):
                return cases[idx]
        except ValueError:
            pass


def create_case_flow():
    header("CREATE NEW CASE")
    print("  Enter your case information. Press Enter to skip optional fields.\n")

    name = prompt("Case name (required)")
    if not name:
        error("Case name is required.")
        return

    case = db.create_case(
        name=name,
        defendant_name=prompt("Your full name (defendant)"),
        case_number=prompt("Court docket/case number (optional)"),
        charge=prompt("Charge(s) (e.g. OUI, Disorderly Conduct)"),
        court=prompt("Court name (e.g. Maine District Court Portland)"),
        county=prompt("County"),
        incident_date=prompt("Incident date (YYYY-MM-DD)") or None,
        arrest_date=prompt("Arrest date (YYYY-MM-DD, if different)") or None,
        description=prompt("Brief description of what happened (optional)"),
    )
    success(f'Case created: "{name}"  ID: {case["id"][:8]}…')
    return case


def view_case(case):
    header(f"CASE: {case['name']}")
    violations = db.get_case_violations(case["id"])
    evidence_list = db.list_evidence(case["id"])
    analyses = db.list_analyses(case["id"])
    notes = db.get_notes(case["id"])
    docs = db.list_documents(case["id"])

    # Info
    print(f"  Defendant:     {case.get('defendant_name','—')}")
    print(f"  Case Number:   {case.get('case_number','—')}")
    print(f"  Charge:        {case.get('charge','—')}")
    print(f"  Court:         {case.get('court','—')}")
    print(f"  Incident Date: {case.get('incident_date','—')}")
    print(f"  Evidence:      {len(evidence_list)} file(s)")
    print(f"  Violations:    {len(violations)} documented")
    print(f"  Documents:     {len(docs)} generated")

    # Win probability from latest analysis
    for a in analyses:
        if a.get("status") == "complete" and a.get("win_probability"):
            pct = a["win_probability"] * 100
            print(f"\n  ★ ESTIMATED WIN PROBABILITY: {pct:.1f}%")
            print("    (AI estimate only — NOT legal advice)")
            break

    while True:
        action = menu("Case actions:", [
            ("violations",  f"View violations ({len(violations)} found)"),
            ("analyze",     "Analyze a video file"),
            ("metadata",    "Check video metadata for tampering"),
            ("documents",   "Generate legal documents"),
            ("notes",       f"View / add notes ({len(notes)} notes)"),
            ("legal",       "View legal strategy & motions"),
        ])
        if action is None: break
        elif action == "violations":  show_violations(case)
        elif action == "analyze":     analyze_flow(case)
        elif action == "metadata":    metadata_flow(case)
        elif action == "documents":   documents_flow(case)
        elif action == "notes":       notes_flow(case)
        elif action == "legal":       legal_flow(case)


def show_violations(case):
    violations = db.get_case_violations(case["id"])
    if not violations:
        info("No violations documented yet. Run video analysis first.")
        return

    section(f"VIOLATIONS — {case['name']}")
    illegal = [v for v in violations if v.get("is_illegal")]
    flags   = [v for v in violations if v.get("is_red_flag") and not v.get("is_illegal")]

    print(f"  Total: {len(violations)}  |  Illegal: {len(illegal)}  |  Red Flags: {len(flags)}")
    print()

    for v in violations:
        label = severity_label(v.get("severity", 0))
        ts    = v.get("timestamp_label", "??:??:??")
        flag  = " [ILLEGAL]" if v.get("is_illegal") else " [RED FLAG]" if v.get("is_red_flag") else ""
        print(f"  {label}{flag}  @{ts}")
        wrap(v.get("description", "No description"), 6)
        if v.get("law_reference"):
            print(f"      Law: {v['law_reference']}")
        if v.get("recommendation"):
            print(f"      ➤  {v['recommendation']}")
        print()

    input("  Press Enter to continue…")


def analyze_flow(case):
    section("ANALYZE VIDEO FILE")
    print("  Enter the full path to the video file.")
    print("  Example: /home/user/dashcam.mp4")
    print()
    video_path = prompt("Video file path")

    if not video_path or not Path(video_path).exists():
        error(f"File not found: {video_path}")
        return

    if not config.is_configured:
        error("No API key configured. Add ANTHROPIC_API_KEY to .env")
        return

    # Register evidence
    file_size = Path(video_path).stat().st_size
    ext = video_path.rsplit(".", 1)[-1].lower() if "." in video_path else "video"
    evidence = db.add_evidence(
        case_id=case["id"],
        file_path=video_path,
        file_type=ext,
        original_name=Path(video_path).name,
        file_size=file_size,
    )

    print()
    info("Starting analysis. The AI will watch every frame of the video.")
    info("This runs synchronously here — large videos may take several minutes.")
    info("You will see progress updates as it runs.")
    print()

    analysis = db.create_analysis(case["id"], evidence["id"], "full")

    # Progress callback for CLI
    last_phase = [None]
    def progress(done, total, phase):
        if phase != last_phase[0]:
            last_phase[0] = phase
            label = {"extracting_frames": "Extracting frames…",
                     "analyzing_frames":  "AI watching frames…"}.get(phase, phase)
            print(f"\n  [{label}]", end="", flush=True)
        print(".", end="", flush=True)

    try:
        from analyzers.video_analyzer import analyze_video
        result = analyze_video(
            analysis_id=analysis["id"],
            evidence_id=evidence["id"],
            case_id=case["id"],
            video_path=video_path,
            incident_date=case.get("incident_date"),
            progress_callback=progress,
        )
        print()

        if "error" in result:
            error(f"Analysis failed: {result['error']}")
            return

        section("ANALYSIS COMPLETE")
        print(f"  Frames watched:    {result.get('total_frames_analyzed', 0)}")
        print(f"  Violations found:  {result.get('total_violations_found', 0)}")
        print(f"  Illegal acts:      {result.get('illegal_violations', 0)}")
        print(f"  Red flags:         {result.get('red_flags', 0)}")
        print(f"  Miranda concern:   {'YES' if result.get('miranda_concern') else 'No'}")
        print(f"  Camera issues:     {'YES' if result.get('camera_issues_detected') else 'No'}")
        print()
        pct = result.get("win_probability", 0) * 100
        print(f"  ★ ESTIMATED WIN PROBABILITY: {pct:.1f}%")
        print("    (AI estimate only — NOT legal advice)")
        print()
        print("  Recommendations:")
        for rec in result.get("recommendations", [])[:5]:
            wrap(f"• {rec}", 4)

        input("\n  Press Enter to continue…")

    except Exception as exc:
        print()
        error(f"Analysis error: {exc}")


def metadata_flow(case):
    section("VIDEO METADATA ANALYSIS")
    print("  Check video file metadata for signs of tampering, missing audio,")
    print("  editing software, timestamp anomalies, and other red flags.\n")

    evidence_list = db.list_evidence(case["id"])
    if evidence_list:
        print("  Registered evidence files:")
        for i, ev in enumerate(evidence_list, 1):
            print(f"    {i}) {ev.get('original_name', ev['file_path'])}")
        print()
        video_path = prompt("Full path to video file (or press Enter to use #1)")
        if not video_path and evidence_list:
            video_path = evidence_list[0]["file_path"]
    else:
        video_path = prompt("Full path to video file")

    if not video_path or not Path(video_path).exists():
        error(f"File not found: {video_path}")
        return

    evidence = db.add_evidence(
        case_id=case["id"],
        file_path=video_path,
        file_type=video_path.rsplit(".", 1)[-1].lower() if "." in video_path else "video",
        original_name=Path(video_path).name,
        file_size=Path(video_path).stat().st_size,
    )

    info("Running metadata analysis…")
    result = analyze_metadata(
        evidence_id=evidence["id"],
        case_id=case["id"],
        video_path=video_path,
        incident_date=case.get("incident_date"),
    )

    if "error" in result:
        error(result["error"])
        return

    section("METADATA RESULTS")
    meta = result.get("metadata", {})
    duration = meta.get("duration_seconds", 0)
    h, r = divmod(int(duration), 3600)
    m, s = divmod(r, 60)
    print(f"  Format:       {meta.get('format_name','—')}")
    print(f"  Duration:     {h:02d}:{m:02d}:{s:02d}")
    print(f"  File size:    {meta.get('file_size_bytes',0)/1048576:.1f} MB")
    print(f"  Encoder:      {meta.get('encoder') or 'NOT FOUND'}")
    print(f"  Created:      {meta.get('creation_time') or 'NOT FOUND'}")
    fs = meta.get("filesystem", {})
    print(f"  Modified:     {fs.get('fs_modified','—')}")

    findings = result.get("findings", [])
    red_flags = result.get("red_flag_count", 0)
    critical  = result.get("critical_flag_count", 0)

    print()
    print(f"  Red flags found: {red_flags}  |  Critical: {critical}")

    if findings:
        print()
        print("  FLAGS:")
        for f in findings:
            sev = f.get("severity", 0)
            print(f"\n  [{sev}/10] {f.get('flag','').upper().replace('_',' ')}")
            wrap(f.get("note", f.get("value", "")), 6)
            if f.get("law"):
                print(f"      Law: {f['law']}")
    else:
        print("\n  No significant metadata red flags detected.")

    input("\n  Press Enter to continue…")


def documents_flow(case):
    section("GENERATE LEGAL DOCUMENTS")
    print("  Documents are saved to: data/documents/")
    print()

    options = [(k, v) for k, v in DOCUMENT_TITLES.items()]
    doc_type = menu("Select document to generate:", options)
    if doc_type is None:
        return

    info(f"Generating: {DOCUMENT_TITLES[doc_type]}…")
    result = generate_document(case["id"], doc_type)

    if "error" in result:
        error(result["error"])
    else:
        success(f"Document generated!")
        print(f"  Title: {result['title']}")
        print(f"  File:  {result['path']}")
        print()
        info("Copy the file path above to open/print the document.")

    input("\n  Press Enter to continue…")


def notes_flow(case):
    section("CASE NOTES")
    notes = db.get_notes(case["id"])

    if notes:
        for n in notes:
            ts = n.get("created_at", "")[:16]
            print(f"\n  [{ts}]")
            wrap(n["note"], 4)
    else:
        print("  No notes yet.")

    print()
    add = input("  Add a note? (y/N): ").strip().lower()
    if add == "y":
        note_text = input("  Note: ").strip()
        if note_text:
            db.add_note(case["id"], note_text)
            success("Note saved.")


def legal_flow(case):
    section("LEGAL STRATEGY")
    violations = db.get_case_violations(case["id"])
    evidence_list = db.list_evidence(case["id"])
    meta_findings = []
    for ev in evidence_list:
        meta_findings.extend(db.get_metadata_findings(ev["id"]))

    posture = analyze_case_legal_posture(violations, meta_findings, case)

    # Win probability
    wp = posture.get("win_probability", {})
    if wp.get("probability"):
        pct = wp["probability"] * 100
        print(f"\n  ★ WIN PROBABILITY: {pct:.1f}%")

    # Motions
    motions = posture.get("motions_available", [])
    if motions:
        print(f"\n  AVAILABLE MOTIONS ({len(motions)}):")
        for m in motions:
            strength = m.get("strength", "")
            print(f"\n  • {m['title']}")
            print(f"    Strength: {strength}")
            print(f"    Basis: {m.get('basis','')}")
            wrap(m.get("description","")[:300], 4)

    # Action items
    actions = posture.get("action_items", [])
    if actions:
        print(f"\n  ACTION ITEMS:")
        for a in actions:
            priority = a.get("priority", "")
            print(f"\n  [{priority}] {a['action']}")
            if a.get("reason"):
                wrap(a["reason"], 4)

    print()
    print(f"  {wp.get('disclaimer','')}")
    input("\n  Press Enter to continue…")


# ── Main menu ─────────────────────────────────────────────────────────────────

def main():
    db.init_db()

    header("LEGAL VIDEO ANALYZER — Pro Se Defense Tool")
    print("  AI-powered police video analysis for self-represented defendants in Maine")
    print(f"  API: {config.api_provider.upper()} | Model: {config.active_model}")
    print()
    print("  Free legal help in Maine:")
    print("    Pine Tree Legal Assistance: 207-774-8211")
    print("    Maine Legal Services:       1-800-750-5353")
    print("    ACLU of Maine:              207-774-5444")

    while True:
        action = menu("MAIN MENU", [
            ("cases",  "View / open existing cases"),
            ("new",    "Create a new case"),
        ])
        if action is None:
            print("\n  Goodbye.\n")
            break
        elif action == "new":
            case = create_case_flow()
            if case:
                view_case(db.get_case(case["id"]))
        elif action == "cases":
            case = list_cases_menu()
            if case:
                view_case(case)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Exited.\n")
