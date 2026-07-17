#!/usr/bin/env python3
"""
THUMB DRIVE EXHIBIT ORGANIZER — CR-2018-03023 — Keith A. King
==============================================================
Run this on your own computer (Windows, Mac, or Linux).
It will:
  1. Ask where your thumb drive is
  2. Ask you to locate each exhibit file
  3. Copy everything into labeled folders
  4. Generate a clickable INDEX.html that opens in any browser

Requirements: Python 3.7+ (no extra installs needed)
To run: double-click this file OR open terminal and type:
        python exhibit_thumbdrive_builder.py
"""

import os
import sys
import shutil
import textwrap
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# ── EXHIBIT DEFINITIONS ────────────────────────────────────────────────────────
EXHIBITS = [
    {
        "id": "EXH-A",
        "folder": "EXH-A_CAD_Dispatch_Log",
        "title": "BPD CAD Log — Incident 18-060430",
        "filename": "EXH-A_CAD_Dispatch_Log.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds I, II, III",
        "proves": (
            "Farrar didn't arrive until 12:56 PM — 56 min AFTER signing warrant at 12:00 PM. "
            "Davis Road stop was NEVER dispatched."
        ),
        "status": "READY",
        "special_note": None,
    },
    {
        "id": "EXH-B",
        "folder": "EXH-B_Discovery_Packet",
        "title": "2018 Initial Discovery Packet",
        "filename": "EXH-B_2018_Initial_Discovery_Packet.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds I, II",
        "proves": (
            "Witness statements cited in warrant affidavit are marked "
            "'DOES NOT EXIST' on the State's own checklist. "
            "ALSO CONTAINS: Police reports (EXH-D, pp. 3–12) and "
            "TruNarc field test (EXH-H)."
        ),
        "status": "READY",
        "special_note": (
            "EXH-D (Haskell + Perry police reports) and EXH-H (TruNarc INCONCLUSIVE) "
            "are on pages 3–12 of this PDF. No separate file needed."
        ),
    },
    {
        "id": "EXH-C",
        "folder": "EXH-C_AAG_Anton_Letter",
        "title": "AAG Anton Admission — 'Inadvertent Error'",
        "filename": "EXH-C_AAG_Anton_Nov2025_Letter.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds I, V, VI",
        "proves": (
            "State admitted all 3 Class A Aggravated charges were an "
            "'inadvertent error' — charges were legally impossible under "
            "17-A M.R.S. § 1105-A(1)(C-1)."
        ),
        "status": "READY",
        "special_note": None,
    },
    {
        "id": "EXH-D",
        "folder": "EXH-D_Police_Reports",
        "title": "Police Reports — Haskell + Perry",
        "filename": "SEE_EXH-B_PAGES_3-12.txt",
        "ext_filter": None,
        "grounds": "Grounds I, III, V",
        "proves": (
            "Haskell report: NO drugs found in vehicle. "
            "Perry report: holster ONLY in bedroom — no firearm nexus. "
            "Destroys 'in furtherance of' element under § 1105-A(1)(C-1)."
        ),
        "status": "IN_EXH_B",
        "special_note": (
            "Located inside EXH-B (the big discovery PDF), pages 3–12. "
            "Open EXH-B and look at pages 3 through 12 for both reports."
        ),
    },
    {
        "id": "EXH-E",
        "folder": "EXH-E_Dashcam_Video",
        "title": "BPD Dashcam Video — Aug 2, 2018",
        "filename": "EXH-E_Haskell_Dashcam_Aug2_2018.mp4",
        "ext_filter": [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*"),
        ],
        "grounds": "Grounds II, III, IV",
        "proves": (
            "Withheld 5.5 years — released Feb 21, 2024 via FOAA. "
            "ON VIDEO: No infraction stated. Handcuffed transport (Bailey). "
            "Warrant refused twice. Key entry. Amanda Ross strip search."
        ),
        "status": "READY",
        "special_note": "VIDEO FILE — will play directly in browser via the INDEX.html video player.",
    },
    {
        "id": "EXH-F",
        "folder": "EXH-F_BHA_Key_Log",
        "title": "BHA Master Key Log — No Aug 2 Entry",
        "filename": "EXH-F_BHA_Master_Key_Log.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds III, VI",
        "proves": (
            "NO key authorized to BPD on or around August 2, 2018. "
            "Officer had key in pocket — visible on video (EXH-E). "
            "Entry was warrantless under the 4th Amendment."
        ),
        "status": "READY",
        "special_note": None,
    },
    {
        "id": "EXH-G",
        "folder": "EXH-G_Billing_Vouchers",
        "title": "Public Defense Billing Vouchers",
        "filename": "EXH-G_Billing_Vouchers_All_Attorneys.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds IV, VI",
        "proves": (
            "All 4 attorneys billed for video review — then told Keith "
            "the video didn't exist. Zero suppression motions filed. "
            "Establishes IAC (Ground IV)."
        ),
        "status": "READY",
        "special_note": None,
    },
    {
        "id": "EXH-H",
        "folder": "EXH-H_TruNarc_Test",
        "title": "TruNarc Field Test — INCONCLUSIVE",
        "filename": "SEE_EXH-B_FOR_TRUNARC.txt",
        "ext_filter": None,
        "grounds": "Grounds I, V, VI",
        "proves": (
            "TruNarc field test result was INCONCLUSIVE. "
            "No confirmatory lab analysis ever done. "
            "'In fact heroin' charge had no scientific basis."
        ),
        "status": "IN_EXH_B",
        "special_note": (
            "Located inside EXH-B. Search the discovery PDF for 'TruNarc'. "
            "The test page showing INCONCLUSIVE is in that packet."
        ),
    },
    {
        "id": "EXH-I",
        "folder": "EXH-I_CAD_Log_Radio",
        "title": "CAD/Radio Logs — Davis Road Never Dispatched",
        "filename": "EXH-I_CAD_Radio_Log.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds II, III",
        "proves": (
            "Davis Road traffic stop NEVER appeared in dispatch or radio logs. "
            "Officers used personal cell phones. Off-book pretextual stop. "
            "Farrar was not present at the Davis Road stop."
        ),
        "status": "READY",
        "special_note": None,
    },
    {
        "id": "EXH-J",
        "folder": "EXH-J_Drug_Schedule_2018",
        "title": "2018 Maine Drug Schedule (Gabapentin NOT Listed)",
        "filename": "EXH-J_Maine_Drug_Schedule_2018.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Ground VII — AUTOMATIC DISMISSAL",
        "proves": (
            "Gabapentin was NOT on Maine's controlled substance schedule in 2018. "
            "It was added October 15, 2019 (Me. PL 2019, ch. 487). "
            "Charging gabapentin under the 2018 schedule = Ex Post Facto violation."
        ),
        "status": "PENDING",
        "special_note": (
            "PRINT FROM: legislature.maine.gov → Title 17-A → Section 1102 (Schedule Z). "
            "Print the pre-October 2019 version. Save or scan as PDF."
        ),
    },
    {
        "id": "EXH-K",
        "folder": "EXH-K_Mental_Health_Eval",
        "title": "Mental Health Evaluation + July 29, 2021 Court Order",
        "filename": "EXH-K_Mental_Health_Eval_and_Court_Order.pdf",
        "ext_filter": [("PDF files", "*.pdf"), ("All files", "*.*")],
        "grounds": "Grounds V, VI",
        "proves": (
            "July 29, 2021 court ORDER required medical stabilization BEFORE any plea. "
            "9 diagnoses including Bipolar Disorder and Panic Disorder. "
            "Keith was unmedicated at the surprise September 2021 plea — "
            "violating the court's own order. Plea void ab initio."
        ),
        "status": "PENDING",
        "special_note": (
            "CALL (207) 561-2300 — Penobscot County Superior Court clerk. "
            "Request all court orders from docket CR-2018-03023 dated July 29, 2021. "
            "Also request mental health evaluation records from the court-ordered evaluation."
        ),
    },
]

# ── HTML INDEX TEMPLATE ────────────────────────────────────────────────────────

def build_index_html(exhibit_file_map: dict, drive_path: Path) -> str:
    """Generate the INDEX.html content for the thumb drive."""

    def status_badge(ex):
        s = ex["status"]
        if s == "READY":
            return '<span class="badge ready">READY</span>'
        elif s == "IN_EXH_B":
            return '<span class="badge partial">INSIDE EXH-B</span>'
        else:
            return '<span class="badge pending">PENDING</span>'

    def exhibit_card(ex):
        fmap = exhibit_file_map.get(ex["id"])
        if ex["status"] == "IN_EXH_B":
            link_html = (
                '<p class="file-note">📁 '
                + ex["special_note"]
                + "</p>"
            )
        elif fmap:
            rel = fmap
            ext = Path(rel).suffix.lower()
            if ext in (".mp4", ".avi", ".mov", ".mkv", ".wmv"):
                link_html = f"""
                <div class="video-wrap">
                  <video controls preload="metadata">
                    <source src="{rel}" type="video/mp4">
                    <p>Your browser does not support HTML5 video.
                       <a href="{rel}">Click here to open the video file directly.</a></p>
                  </video>
                  <p class="file-note">📁 File: {rel}</p>
                </div>"""
            else:
                link_html = f'<a class="open-btn" href="{rel}" target="_blank">📄 Open {ex["id"]}</a>'
                if ex.get("special_note") and ex["status"] == "READY":
                    link_html += f'<p class="note">{ex["special_note"]}</p>'
        else:
            if ex.get("special_note"):
                link_html = f'<p class="file-note pending-note">⚠️ {ex["special_note"]}</p>'
            else:
                link_html = '<p class="file-note pending-note">⚠️ File not yet obtained. See notes above.</p>'

        return f"""
      <div class="card {"card-pending" if ex["status"] == "PENDING" else ""}">
        <div class="card-header">
          <span class="exh-id">{ex["id"]}</span>
          {status_badge(ex)}
          <span class="grounds">{ex["grounds"]}</span>
        </div>
        <h3>{ex["title"]}</h3>
        <p class="proves"><strong>PROVES:</strong> {ex["proves"]}</p>
        {link_html}
      </div>"""

    cards = "\n".join(exhibit_card(ex) for ex in EXHIBITS)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EXHIBIT INDEX — CR-2018-03023 — Keith A. King</title>
<style>
  :root {{
    --navy: #0f2744;
    --navy-mid: #1a3a5c;
    --gold: #c9a84c;
    --cream: #f4f0e6;
    --text: #1a1a1a;
    --card-bg: #ffffff;
    --border: #d5cfc0;
    --ready: #1a6b3c;
    --ready-bg: #d4edda;
    --partial: #856404;
    --partial-bg: #fff3cd;
    --pending: #842029;
    --pending-bg: #f8d7da;
    --link: #0c3d6e;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    background: var(--cream);
    color: var(--text);
    line-height: 1.5;
  }}
  header {{
    background: var(--navy);
    color: #fff;
    padding: 0;
    border-bottom: 4px solid var(--gold);
  }}
  .header-inner {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 32px;
  }}
  .case-label {{
    font-family: 'Courier New', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  header h1 {{
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 4px;
  }}
  .header-meta {{
    display: flex;
    gap: 32px;
    margin-top: 12px;
    flex-wrap: wrap;
  }}
  .meta-item {{
    font-size: 12px;
    color: #a8c0d4;
    font-family: 'Courier New', monospace;
  }}
  .meta-item strong {{ color: #e0e8f0; }}
  .print-warning {{
    background: #7a1c1c;
    border-left: 5px solid #ff6b6b;
    color: #fff;
    padding: 12px 32px;
    font-size: 13px;
    font-family: 'Courier New', monospace;
  }}
  main {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 28px 24px;
  }}
  .section-title {{
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--navy-mid);
    font-family: 'Courier New', monospace;
    border-bottom: 2px solid var(--navy-mid);
    padding-bottom: 6px;
    margin: 28px 0 16px;
  }}
  .docs-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }}
  .doc-link {{
    display: block;
    background: var(--navy-mid);
    color: #fff;
    text-decoration: none;
    padding: 14px 16px;
    border-radius: 4px;
    font-size: 13px;
    transition: background 0.15s;
  }}
  .doc-link:hover {{ background: #0f2744; }}
  .doc-link .doc-icon {{ font-size: 18px; display: block; margin-bottom: 6px; }}
  .doc-link .doc-label {{ font-weight: bold; font-family: 'Courier New', monospace; font-size: 11px; }}
  .doc-link .doc-title {{ font-size: 12px; color: #c8d8e8; margin-top: 4px; }}
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
    gap: 16px;
  }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}
  .card-pending {{
    border-left: 5px solid #c0392b;
    background: #fff8f8;
  }}
  .card-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }}
  .exh-id {{
    font-family: 'Courier New', monospace;
    font-size: 13px;
    font-weight: bold;
    color: var(--navy);
    background: #e8eef5;
    padding: 2px 8px;
    border-radius: 3px;
  }}
  .badge {{
    font-size: 10px;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 3px;
    text-transform: uppercase;
  }}
  .badge.ready {{ background: var(--ready-bg); color: var(--ready); }}
  .badge.partial {{ background: var(--partial-bg); color: var(--partial); }}
  .badge.pending {{ background: var(--pending-bg); color: var(--pending); }}
  .grounds {{
    font-size: 11px;
    font-family: 'Courier New', monospace;
    color: #666;
    margin-left: auto;
  }}
  .card h3 {{
    font-size: 15px;
    color: var(--navy);
    margin-bottom: 6px;
    line-height: 1.3;
  }}
  .proves {{
    font-size: 12.5px;
    color: #3a3a3a;
    margin-bottom: 12px;
    line-height: 1.5;
  }}
  .open-btn {{
    display: inline-block;
    background: var(--navy);
    color: #fff;
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'Courier New', monospace;
  }}
  .open-btn:hover {{ background: var(--navy-mid); }}
  .file-note {{
    font-size: 12px;
    font-family: 'Courier New', monospace;
    background: #f0f4f8;
    border-left: 3px solid #aaa;
    padding: 8px 12px;
    margin-top: 8px;
    line-height: 1.5;
    color: #444;
  }}
  .pending-note {{
    background: #fff3f3;
    border-left-color: #c0392b;
    color: #7a1c1c;
  }}
  .note {{
    font-size: 11.5px;
    font-family: 'Courier New', monospace;
    color: #555;
    margin-top: 8px;
    padding: 6px 8px;
    background: #f5f5f5;
    border-radius: 3px;
  }}
  .video-wrap video {{
    width: 100%;
    max-width: 100%;
    border-radius: 4px;
    background: #000;
    margin-bottom: 8px;
  }}
  footer {{
    background: var(--navy);
    color: #8fa8be;
    text-align: center;
    padding: 20px;
    font-size: 12px;
    font-family: 'Courier New', monospace;
    margin-top: 40px;
    border-top: 4px solid var(--gold);
  }}
  @media (max-width: 600px) {{
    .cards {{ grid-template-columns: 1fr; }}
    .header-inner {{ padding: 16px; }}
  }}
  @media print {{
    .video-wrap video {{ display: none; }}
    .open-btn {{ color: var(--navy); border: 1px solid var(--navy); }}
  }}
</style>
</head>
<body>

<header>
  <div class="print-warning">
    ⚠️ CONFIDENTIAL — ATTORNEY-CLIENT PRIVILEGE — Keith A. King v. State of Maine — FOR COURT USE ONLY
  </div>
  <div class="header-inner">
    <div class="case-label">Penobscot County Unified Criminal Docket</div>
    <h1>EXHIBIT INDEX — STATE v. KEITH A. KING</h1>
    <div class="header-meta">
      <div class="meta-item"><strong>Docket:</strong> PENCD-CR-2018-03023</div>
      <div class="meta-item"><strong>Court:</strong> Penobscot County — 78 Exchange St, Bangor ME 04401</div>
      <div class="meta-item"><strong>Petitioner:</strong> Keith A. King (Pro Se)</div>
      <div class="meta-item"><strong>Filing:</strong> Post-Conviction Review — 15 M.R.S. §§ 2121–2130-A</div>
    </div>
  </div>
</header>

<main>

  <div class="section-title">Core Documents — Print and File These</div>
  <div class="docs-grid">
    <a class="doc-link" href="DOCUMENTS/PCR_CORRECTED_FINAL_CR-2018-03023.html" target="_blank">
      <span class="doc-icon">📋</span>
      <span class="doc-label">PCR PETITION</span>
      <span class="doc-title">Post-Conviction Review Petition (corrected final)</span>
    </a>
    <a class="doc-link" href="DOCUMENTS/CR140_FILLED_King.pdf" target="_blank">
      <span class="doc-icon">📄</span>
      <span class="doc-label">CR-140 FORM</span>
      <span class="doc-title">Post-Conviction Review Form — filled out</span>
    </a>
    <a class="doc-link" href="DOCUMENTS/CR032_FILLED_King.pdf" target="_blank">
      <span class="doc-icon">📄</span>
      <span class="doc-label">CR-032 FORM</span>
      <span class="doc-title">Financial Disclosure Form — filled out</span>
    </a>
    <a class="doc-link" href="DOCUMENTS/EXHIBIT_ORGANIZER_CR-2018-03023.html" target="_blank">
      <span class="doc-icon">🗂</span>
      <span class="doc-label">EXHIBIT DIVIDERS</span>
      <span class="doc-title">Print divider pages for exhibit packet binder</span>
    </a>
  </div>

  <div class="section-title">Exhibit Packet — EXH-A through EXH-K</div>
  <div class="cards">
{cards}
  </div>

</main>

<footer>
  Generated for Keith A. King — PENCD-CR-2018-03023<br>
  Penobscot County Unified Criminal Docket — Bangor, ME 04401<br>
  To file: 78 Exchange St, Bangor ME · Clerk: (207) 561-2300
</footer>

</body>
</html>
"""


# ── BUILDER GUI ────────────────────────────────────────────────────────────────

DOCS_TO_COPY = [
    ("PCR_CORRECTED_FINAL_CR-2018-03023.html", "PCR_CORRECTED_FINAL_CR-2018-03023.html"),
    ("CR140_FILLED_King.pdf", "CR140_FILLED_King.pdf"),
    ("CR032_FILLED_King.pdf", "CR032_FILLED_King.pdf"),
    ("EXHIBIT_ORGANIZER_CR-2018-03023.html", "EXHIBIT_ORGANIZER_CR-2018-03023.html"),
]


class ThumbDriveBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("THUMB DRIVE BUILDER — CR-2018-03023")
        self.geometry("800x640")
        self.configure(bg="#0f2744")
        self.resizable(True, True)

        self.drive_path = tk.StringVar()
        self.script_dir = Path(sys.argv[0]).parent.resolve()
        self.exhibit_files = {}  # id -> relative path on drive

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="THUMB DRIVE EXHIBIT ORGANIZER",
            bg="#0f2744", fg="#c9a84c",
            font=("Courier", 15, "bold"),
        ).pack(pady=(20, 2))
        tk.Label(
            self,
            text="CR-2018-03023 — Keith A. King",
            bg="#0f2744", fg="#a8c0d4",
            font=("Courier", 11),
        ).pack(pady=(0, 16))

        # Drive selector
        frame = tk.Frame(self, bg="#1a3a5c", padx=16, pady=12)
        frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(
            frame, text="STEP 1 — Select thumb drive destination folder:",
            bg="#1a3a5c", fg="#e0e8f0", font=("Courier", 10, "bold"),
        ).pack(anchor="w")
        row = tk.Frame(frame, bg="#1a3a5c")
        row.pack(fill="x", pady=6)
        tk.Entry(row, textvariable=self.drive_path, width=55,
                 font=("Courier", 10)).pack(side="left", padx=(0, 8))
        tk.Button(
            row, text="Browse…", command=self._choose_drive,
            bg="#c9a84c", fg="#0f2744", font=("Courier", 9, "bold"),
        ).pack(side="left")

        # Scroll area for exhibits
        tk.Label(
            self, text="STEP 2 — Locate each exhibit file:",
            bg="#0f2744", fg="#e0e8f0", font=("Courier", 10, "bold"),
        ).pack(anchor="w", padx=20, pady=(6, 2))

        canvas_frame = tk.Frame(self, bg="#0f2744")
        canvas_frame.pack(fill="both", expand=True, padx=20)
        canvas = tk.Canvas(canvas_frame, bg="#0f2744", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(canvas, bg="#0f2744")
        self.inner_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self.inner_id, width=e.width)
        )
        # Mouse wheel scroll
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.row_vars = {}
        for ex in EXHIBITS:
            self._add_exhibit_row(ex)

        # Build button
        tk.Button(
            self,
            text="BUILD THUMB DRIVE →",
            command=self._build_drive,
            bg="#c9a84c", fg="#0f2744",
            font=("Courier", 12, "bold"),
            padx=20, pady=8,
        ).pack(pady=14)

    def _add_exhibit_row(self, ex):
        row = tk.Frame(self.inner, bg="#1a3a5c", padx=10, pady=8)
        row.pack(fill="x", pady=3)

        # Status colors
        colors = {"READY": "#1a6b3c", "IN_EXH_B": "#856404", "PENDING": "#842029"}
        color = colors.get(ex["status"], "#555")

        left = tk.Frame(row, bg="#1a3a5c", width=200)
        left.pack(side="left", anchor="n", padx=(0, 10))
        left.pack_propagate(False)
        tk.Label(
            left, text=ex["id"],
            bg="#1a3a5c", fg="#c9a84c", font=("Courier", 11, "bold"),
        ).pack(anchor="w")
        short = textwrap.fill(ex["title"], 28)
        tk.Label(
            left, text=short,
            bg="#1a3a5c", fg="#a8c0d4", font=("Courier", 8),
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            left, text=ex["status"].replace("_", " "),
            bg=color, fg="white", font=("Courier", 8, "bold"),
            padx=4,
        ).pack(anchor="w", pady=3)

        right = tk.Frame(row, bg="#1a3a5c")
        right.pack(side="left", fill="x", expand=True)

        if ex["status"] == "IN_EXH_B":
            note = ex.get("special_note", "See EXH-B")
            msg = textwrap.fill(f"Contained in EXH-B. {note}", 60)
            tk.Label(
                right, text=msg,
                bg="#1a3a5c", fg="#cca300", font=("Courier", 8),
                justify="left",
            ).pack(anchor="w")
            self.row_vars[ex["id"]] = None
        elif ex["status"] == "PENDING":
            note = ex.get("special_note", "Not yet obtained.")
            msg = textwrap.fill(f"PENDING: {note}", 60)
            tk.Label(
                right, text=msg,
                bg="#1a3a5c", fg="#ff8888", font=("Courier", 8),
                justify="left",
            ).pack(anchor="w")
            self.row_vars[ex["id"]] = tk.StringVar(value="")
            tk.Button(
                right, text="Locate file (if you have it)…",
                command=lambda e=ex: self._locate_file(e),
                bg="#555", fg="white", font=("Courier", 8),
            ).pack(anchor="w", pady=3)
            lbl = tk.Label(right, textvariable=self.row_vars[ex["id"]],
                           bg="#1a3a5c", fg="#88ff88", font=("Courier", 8), justify="left")
            lbl.pack(anchor="w")
        else:
            # READY — allow file location
            self.row_vars[ex["id"]] = tk.StringVar(value="")
            # Check if file exists in same dir as script
            auto = self._auto_locate(ex)
            if auto:
                self.row_vars[ex["id"]].set(str(auto))
                tk.Label(
                    right, text="Auto-found in same folder",
                    bg="#1a3a5c", fg="#88cc88", font=("Courier", 8),
                ).pack(anchor="w")
            tk.Button(
                right, text="Locate file…",
                command=lambda e=ex: self._locate_file(e),
                bg="#1a3a5c", fg="#c9a84c", font=("Courier", 9, "bold"),
                relief="ridge",
            ).pack(anchor="w", pady=3)
            lbl = tk.Label(right, textvariable=self.row_vars[ex["id"]],
                           bg="#1a3a5c", fg="#88ff88", font=("Courier", 8),
                           justify="left", wraplength=480)
            lbl.pack(anchor="w")

    def _auto_locate(self, ex):
        """Look for exhibit files in same folder as this script."""
        keywords = [ex["id"].lower(), ex["id"].replace("-", "").lower()]
        for f in self.script_dir.iterdir():
            name = f.name.lower()
            if any(k in name for k in keywords) and f.suffix.lower() in (".pdf", ".mp4", ".avi", ".mov", ".mkv"):
                return f
        return None

    def _choose_drive(self):
        path = filedialog.askdirectory(title="Select Thumb Drive Destination")
        if path:
            self.drive_path.set(path)

    def _locate_file(self, ex):
        filters = ex.get("ext_filter") or [("All files", "*.*")]
        path = filedialog.askopenfilename(
            title=f"Locate {ex['id']} — {ex['title']}",
            filetypes=filters,
        )
        if path and ex["id"] in self.row_vars and self.row_vars[ex["id"]] is not None:
            self.row_vars[ex["id"]].set(path)

    def _build_drive(self):
        dest = self.drive_path.get().strip()
        if not dest:
            messagebox.showerror("No destination", "Please select a thumb drive folder first.")
            return

        dest_path = Path(dest)
        if not dest_path.exists():
            messagebox.showerror("Folder not found", f"Could not find: {dest}")
            return

        errors = []
        copied = []
        skipped = []

        # Create DOCUMENTS folder and copy core docs
        docs_dir = dest_path / "DOCUMENTS"
        docs_dir.mkdir(exist_ok=True)
        for src_name, dst_name in DOCS_TO_COPY:
            src = self.script_dir / src_name
            if src.exists():
                shutil.copy2(src, docs_dir / dst_name)
                copied.append(f"DOCUMENTS/{dst_name}")
            else:
                skipped.append(f"DOCUMENTS/{dst_name} — not found in script folder")

        # Process each exhibit
        exhibit_file_map = {}
        for ex in EXHIBITS:
            folder = dest_path / ex["folder"]
            folder.mkdir(exist_ok=True)

            if ex["status"] == "IN_EXH_B":
                # Write a note file
                note_path = folder / f"{ex['id']}_LOCATION_NOTE.txt"
                note_text = f"{ex['id']} — {ex['title']}\n{'='*60}\n\n{ex['special_note']}\n"
                note_path.write_text(note_text)
                copied.append(f"{ex['folder']}/ (note file)")
                # Don't include in HTML map (no file to link)
                continue

            var = self.row_vars.get(ex["id"])
            src_path = Path(var.get()) if (var and var.get()) else None

            if src_path and src_path.exists():
                dst_file = folder / ex["filename"]
                shutil.copy2(src_path, dst_file)
                rel_path = f"{ex['folder']}/{ex['filename']}"
                exhibit_file_map[ex["id"]] = rel_path
                copied.append(rel_path)
            else:
                # Write a placeholder note
                note_path = folder / f"{ex['id']}_PENDING.txt"
                note_text = (
                    f"{ex['id']} — {ex['title']}\n{'='*60}\n\n"
                    f"STATUS: PENDING — FILE NOT YET OBTAINED\n\n"
                )
                if ex.get("special_note"):
                    note_text += f"HOW TO OBTAIN:\n{ex['special_note']}\n"
                note_path.write_text(note_text)
                if ex["status"] == "READY":
                    skipped.append(f"{ex['folder']}/ — exhibit file not located")
                else:
                    skipped.append(f"{ex['folder']}/ — {ex['status']} (note file written)")

        # Write INDEX.html
        html = build_index_html(exhibit_file_map, dest_path)
        index_path = dest_path / "INDEX.html"
        index_path.write_text(html, encoding="utf-8")
        copied.append("INDEX.html")

        # Summary
        msg = f"THUMB DRIVE BUILT!\n\nDestination: {dest}\n\n"
        msg += f"FILES COPIED ({len(copied)}):\n"
        msg += "\n".join(f"  ✅ {c}" for c in copied)
        if skipped:
            msg += f"\n\nSKIPPED / PENDING ({len(skipped)}):\n"
            msg += "\n".join(f"  ⚠️  {s}" for s in skipped)
        msg += "\n\nOpen INDEX.html on the thumb drive to see everything."
        messagebox.showinfo("Done!", msg)


if __name__ == "__main__":
    app = ThumbDriveBuilder()
    app.mainloop()
