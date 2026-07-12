#!/usr/bin/env python3
"""
EXHIBIT ASSEMBLER — CR-2018-03023 — Keith A. King
==========================================================
Run this program on your own computer to collect your
exhibit files, rename them correctly (EXH-A through EXH-K),
and package them into a single zip file ready to file.

Requirements: Python 3.7+ (already installed on most computers)
To run:  double-click this file  OR  open a terminal and type:
         python exhibit_assembler.py
"""

import os
import sys
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# ── EXHIBIT DEFINITIONS ────────────────────────────────────────────────────────
EXHIBITS = [
    {
        "id": "EXH-A",
        "title": "BPD CAD Log — Incident 18-060430",
        "description": (
            "Bangor Police Department Computer-Aided Dispatch Log\n"
            "for Incident 18-060430, with chain of custody.\n\n"
            "PROVES: Farrar didn't arrive until 12:56 PM — 56 min AFTER\n"
            "signing warrant at 12:00 PM. Davis Road stop never dispatched."
        ),
        "source": "Received January 2026 via second FOAA to BPD",
        "grounds": "Grounds I, II, III",
        "file_keyword": ["CAD", "18-060430", "dispatch", "incident"],
    },
    {
        "id": "EXH-B",
        "title": "2018 Initial Discovery Checklist",
        "description": (
            "State's original 2018 discovery checklist.\n\n"
            "PROVES: Witness statements cited in warrant affidavit\n"
            "are marked 'DOES NOT EXIST' on State's own checklist."
        ),
        "source": "Original case discovery file",
        "grounds": "Grounds I, II",
        "file_keyword": ["discovery", "checklist", "witness"],
    },
    {
        "id": "EXH-C",
        "title": "Board of Overseers Response — GCF #25-222",
        "description": (
            "Maine Board of Overseers response (April 2026)\n"
            "containing AAG Jason D. Anton's written admission.\n\n"
            "PROVES: State admitted all 3 Class A Aggravated charges\n"
            "were an 'inadvertent error' — charges were legally impossible."
        ),
        "source": "Maine Board of Overseers of the Bar — April 2026",
        "grounds": "Grounds I, V, VI",
        "file_keyword": ["overseers", "GCF", "Anton", "25-222"],
    },
    {
        "id": "EXH-D",
        "title": "Police Reports — Incident 18-060430 (Haskell + Perry)",
        "description": (
            "BPD incident reports — Haskell and Perry reports.\n\n"
            "PROVES: Haskell = NO drugs in vehicle.\n"
            "Perry = holster only in bedroom.\n"
            "= No 'in furtherance of' nexus under 17-A M.R.S. § 1105-A(1)(C-1)."
        ),
        "source": "BPD Incident 18-060430 official reports",
        "grounds": "Grounds I, III, V",
        "file_keyword": ["Haskell", "Perry", "police report", "incident report"],
    },
    {
        "id": "EXH-E",
        "title": "Cruiser / Body Camera Video Footage",
        "description": (
            "BPD dashcam/body cam video from August 2, 2018.\n"
            "Withheld 5.5 years — released Feb 21, 2024 via FOAA.\n\n"
            "ON VIDEO: No infraction stated. Handcuffed transport (Bailey).\n"
            "Warrant refused twice. Key entry. Amanda Ross strip search.\n"
            "NOTE: Video file may be large (MP4, AVI, MOV, etc.)"
        ),
        "source": "FOAA to BPD — Released February 21, 2024",
        "grounds": "Grounds II, III, IV (IAC)",
        "file_keyword": ["dashcam", "cruiser", "video", "bodycam", "footage"],
    },
    {
        "id": "EXH-F",
        "title": "BHA Master Key Log",
        "description": (
            "Bangor Housing Authority Master Key Log\n"
            "for 33 Bald Mountain Drive.\n\n"
            "PROVES: NO key authorized to BPD on/around Aug 2, 2018.\n"
            "Officer had key in pocket — ON VIDEO (EXH-E).\n"
            "Entry was warrantless under 4th Amendment."
        ),
        "source": "BHA — Produced October 2025 via MHRC discovery",
        "grounds": "Grounds III, VI",
        "file_keyword": ["BHA", "master key", "key log", "housing authority"],
    },
    {
        "id": "EXH-G",
        "title": "State Public Defense Billing Vouchers (All 4 Attorneys)",
        "description": (
            "Billing vouchers for Harris, Johnson, Willey, and Bart\n"
            "from State Public Defense Services.\n\n"
            "PROVES: All 4 attorneys billed for video review — then\n"
            "told you the video didn't exist. Zero suppression motions."
        ),
        "source": "Brochu, Audit Director, State Public Defense Services — August 2024",
        "grounds": "Grounds IV, VI",
        "file_keyword": ["billing", "voucher", "Harris", "Willey", "Bart", "public defense"],
    },
    {
        "id": "EXH-H",
        "title": "TruNarc Field Test Results — INCONCLUSIVE",
        "description": (
            "BPD TruNarc field test results for substance at\n"
            "33 Bald Mountain Drive, August 2, 2018.\n\n"
            "PROVES: Test result was INCONCLUSIVE.\n"
            "No confirmatory lab analysis ever done.\n"
            "'In fact heroin' charge had no scientific basis."
        ),
        "source": "BPD evidence records / original case file",
        "grounds": "Grounds I, V, VI",
        "file_keyword": ["TruNarc", "field test", "heroin", "inconclusive", "drug test"],
    },
    {
        "id": "EXH-I",
        "title": "CAD / Radio Logs — Davis Road Stop Never Dispatched",
        "description": (
            "BPD CAD and radio transmission logs for August 2, 2018.\n\n"
            "PROVES: Davis Road traffic stop NEVER appeared in dispatch\n"
            "or radio logs. Officers used personal cell phones.\n"
            "Off-book pretextual stop. Farrar not present at Davis Rd."
        ),
        "source": "Second FOAA to BPD — Received January 2026",
        "grounds": "Grounds II, III",
        "file_keyword": ["radio log", "CAD log", "Davis Road", "dispatch", "radio"],
    },
    {
        "id": "EXH-J",
        "title": "2018 Maine Drug Schedule (Gabapentin Not Listed)",
        "description": (
            "Maine controlled substance schedule as of August 2, 2018.\n\n"
            "PROVES: Gabapentin was NOT on Maine's schedule in 2018.\n"
            "It wasn't added until October 15, 2019 (Me. PL 2019, ch. 487).\n"
            "Gabapentin charge = Ex Post Facto violation. Auto-dismissal."
        ),
        "source": "Maine Legislature — pre-October 2019 drug schedule",
        "grounds": "Ground VII (AUTOMATIC DISMISSAL)",
        "file_keyword": ["gabapentin", "drug schedule", "Schedule Z", "Maine schedule"],
    },
    {
        "id": "EXH-K",
        "title": "Mental Health Evaluation Records (9 Diagnoses + Court Order)",
        "description": (
            "Court-ordered mental health evaluation records.\n\n"
            "PROVES: (1) July 29, 2021 court ORDER requiring medical\n"
            "stabilization BEFORE any plea.\n"
            "(2) 9 diagnoses including Bipolar Disorder, Panic Disorder.\n"
            "(3) You were unmedicated at the surprise Sept 2021 plea —\n"
            "violating the court's own order."
        ),
        "source": "Court-ordered evaluation; court docket (July 29, 2021 order)",
        "grounds": "Grounds V, VI",
        "file_keyword": ["mental health", "evaluation", "bipolar", "diagnosis", "court order"],
    },
]

# ── GLOBAL STATE ───────────────────────────────────────────────────────────────
selected_files = {}  # exhibit_id -> Path


# ── GUI ────────────────────────────────────────────────────────────────────────

class ExhibitAssembler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EXHIBIT ASSEMBLER — CR-2018-03023 — Keith A. King")
        self.geometry("900x700")
        self.configure(bg="#1a3a5c")
        self.resizable(True, True)

        self._build_header()
        self._build_exhibit_list()
        self._build_footer()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_header(self):
        hdr = tk.Frame(self, bg="#1a3a5c", pady=10)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="EXHIBIT ASSEMBLER — CR-2018-03023",
            font=("Arial", 16, "bold"),
            bg="#1a3a5c", fg="white"
        ).pack()

        tk.Label(
            hdr,
            text="State of Maine v. Keith A. King  |  PCR — 15 M.R.S. §§ 2121–2130-A",
            font=("Arial", 10),
            bg="#1a3a5c", fg="#aaccee"
        ).pack()

        tk.Label(
            hdr,
            text=(
                "For each exhibit below, click BROWSE to select your file.\n"
                "When all exhibits are selected, click CREATE ZIP FILE at the bottom."
            ),
            font=("Arial", 10),
            bg="#1a3a5c", fg="#ffffcc",
            pady=6
        ).pack()

    def _build_exhibit_list(self):
        # Scrollable frame
        outer = tk.Frame(self, bg="#1a3a5c")
        outer.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        canvas = tk.Canvas(outer, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas, bg="#f0f4f8")
        scroll_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(e):
            canvas.itemconfig(scroll_window, width=e.width)

        self.scroll_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mouse wheel scrolling
        def on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Build one row per exhibit
        self.status_labels = {}
        self.path_labels = {}

        for i, exh in enumerate(EXHIBITS):
            bg = "#ffffff" if i % 2 == 0 else "#eaf0f8"
            row = tk.Frame(self.scroll_frame, bg=bg, padx=10, pady=8)
            row.pack(fill="x", padx=2, pady=2)

            # Left: exhibit ID badge
            badge_bg = "#1a3a5c"
            tk.Label(
                row, text=exh["id"],
                font=("Courier", 11, "bold"),
                bg=badge_bg, fg="white",
                width=8, relief="raised", padx=4, pady=6
            ).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="ns")

            # Middle: title + description
            info = tk.Frame(row, bg=bg)
            info.grid(row=0, column=1, sticky="ew")

            tk.Label(
                info, text=exh["title"],
                font=("Arial", 10, "bold"),
                bg=bg, fg="#1a3a5c", anchor="w"
            ).pack(anchor="w")

            tk.Label(
                info,
                text=f"Grounds: {exh['grounds']}  |  {exh['source']}",
                font=("Arial", 8),
                bg=bg, fg="#555", anchor="w"
            ).pack(anchor="w")

            path_lbl = tk.Label(
                info, text="No file selected",
                font=("Arial", 9, "italic"),
                bg=bg, fg="#999", anchor="w", wraplength=500
            )
            path_lbl.pack(anchor="w")
            self.path_labels[exh["id"]] = path_lbl

            row.columnconfigure(1, weight=1)

            # Right: browse button + status
            btn_frame = tk.Frame(row, bg=bg)
            btn_frame.grid(row=0, column=2, padx=(10, 0), sticky="e")

            status_lbl = tk.Label(
                btn_frame, text="⬜ NEEDED",
                font=("Arial", 9, "bold"),
                bg=bg, fg="#cc0000"
            )
            status_lbl.pack()
            self.status_labels[exh["id"]] = status_lbl

            tk.Button(
                btn_frame,
                text="BROWSE",
                font=("Arial", 9, "bold"),
                bg="#1a3a5c", fg="white",
                activebackground="#2a5a8c",
                padx=10, pady=4,
                cursor="hand2",
                command=lambda e=exh: self.browse_file(e)
            ).pack(pady=(4, 0))

            tk.Button(
                btn_frame,
                text="Clear",
                font=("Arial", 8),
                bg="#eee", fg="#555",
                padx=4, pady=2,
                cursor="hand2",
                command=lambda eid=exh["id"]: self.clear_file(eid)
            ).pack(pady=(2, 0))

    def _build_footer(self):
        footer = tk.Frame(self, bg="#1a3a5c", pady=8)
        footer.pack(fill="x", side="bottom")

        self.progress_lbl = tk.Label(
            footer,
            text="0 of 11 exhibits selected",
            font=("Arial", 10),
            bg="#1a3a5c", fg="#aaccee"
        )
        self.progress_lbl.pack()

        self.zip_btn = tk.Button(
            footer,
            text="CREATE ZIP FILE",
            font=("Arial", 13, "bold"),
            bg="#00aa44", fg="white",
            activebackground="#008833",
            padx=20, pady=8,
            cursor="hand2",
            command=self.create_zip,
            state="disabled"
        )
        self.zip_btn.pack(pady=(4, 0))

        tk.Label(
            footer,
            text="You do NOT need all 11 files to create the zip — click CREATE ZIP FILE any time to package what you have.",
            font=("Arial", 9),
            bg="#1a3a5c", fg="#88aacc"
        ).pack(pady=(4, 0))

    def browse_file(self, exh):
        filetypes = [
            ("All files", "*.*"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx *.doc"),
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff"),
            ("Text files", "*.txt"),
        ]
        path = filedialog.askopenfilename(
            title=f"Select file for {exh['id']}: {exh['title']}",
            filetypes=filetypes
        )
        if path:
            selected_files[exh["id"]] = Path(path)
            self.path_labels[exh["id"]].config(text=f"✔ {Path(path).name}", fg="#006600")
            self.status_labels[exh["id"]].config(text="✅ SELECTED", fg="#006600")
            self._update_progress()

    def clear_file(self, exhibit_id):
        if exhibit_id in selected_files:
            del selected_files[exhibit_id]
        self.path_labels[exhibit_id].config(text="No file selected", fg="#999")
        self.status_labels[exhibit_id].config(text="⬜ NEEDED", fg="#cc0000")
        self._update_progress()

    def _update_progress(self):
        count = len(selected_files)
        self.progress_lbl.config(text=f"{count} of 11 exhibits selected")
        self.zip_btn.config(state="normal" if count > 0 else "disabled")

    def create_zip(self):
        if not selected_files:
            messagebox.showwarning("No files", "Please select at least one exhibit file first.")
            return

        # Ask where to save
        save_path = filedialog.asksaveasfilename(
            title="Save Exhibit Zip File",
            defaultextension=".zip",
            initialfile="EXHIBITS_CR-2018-03023.zip",
            filetypes=[("ZIP files", "*.zip")]
        )
        if not save_path:
            return

        # Build the zip
        try:
            missing = []
            included = []

            with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for exh in EXHIBITS:
                    eid = exh["id"]
                    if eid in selected_files:
                        src = selected_files[eid]
                        ext = src.suffix  # keep original file extension
                        # Filename format: EXH-A_BPD_CAD_Log.pdf (etc.)
                        safe_title = (
                            exh["title"]
                            .replace(" — ", "_")
                            .replace(" / ", "_")
                            .replace("/", "_")
                            .replace("(", "")
                            .replace(")", "")
                            .replace(",", "")
                            .replace(".", "")
                            .replace(" ", "_")
                            .replace("__", "_")
                            [:50]  # keep filenames reasonable length
                        )
                        zip_name = f"{eid}_{safe_title}{ext}"
                        zf.write(str(src), zip_name)
                        included.append(f"  ✔ {eid}: {zip_name}")
                    else:
                        missing.append(f"  ✘ {eid}: {exh['title']}")

                # Also include the exhibit organizer HTML if it's alongside this script
                script_dir = Path(__file__).parent
                organizer = script_dir / "EXHIBIT_ORGANIZER_CR-2018-03023.html"
                pcr = script_dir / "PCR_CORRECTED_FINAL_CR-2018-03023.html"

                if organizer.exists():
                    zf.write(str(organizer), "00_EXHIBIT_ORGANIZER_CR-2018-03023.html")
                    included.append("  ✔ Exhibit Organizer (cover sheets)")
                if pcr.exists():
                    zf.write(str(pcr), "00_PCR_CORRECTED_FINAL_CR-2018-03023.html")
                    included.append("  ✔ Corrected PCR Petition")

                # Write a README inside the zip
                readme_lines = [
                    "EXHIBIT PACKET — CR-2018-03023 — Keith A. King",
                    "=" * 55,
                    "State of Maine v. Keith A. King",
                    "Penobscot County Unified Criminal Docket",
                    "PCR — 15 M.R.S. §§ 2121-2130-A; § 2128-B",
                    "",
                    "FILES INCLUDED:",
                    *included,
                    "",
                    "NOT YET INCLUDED (files not selected):",
                    *(missing if missing else ["  (all exhibits selected)"]),
                    "",
                    "FILING REMINDERS:",
                    "  1. Confirm plea date from actual court docket",
                    "     (Sept. 20 vs. Sept. 21, 2021) — correct throughout PCR.",
                    "  2. Verify exhibit letters A-K match PCR body text.",
                    "  3. Include IFP (In Forma Pauperis) application.",
                    "  4. File at: Penobscot County Unified Criminal Docket",
                    "     97 Hammond Street, Bangor, ME 04401",
                    "",
                    "Generated: July 2026 | Pro Se Filing Packet",
                ]
                zf.writestr("README.txt", "\n".join(readme_lines))

            # Show summary
            summary = (
                f"ZIP FILE CREATED SUCCESSFULLY!\n\n"
                f"Saved to:\n{save_path}\n\n"
                f"INCLUDED ({len(included)} items):\n" + "\n".join(included)
            )
            if missing:
                summary += f"\n\nNOT YET INCLUDED ({len(missing)}):\n" + "\n".join(missing)
                summary += "\n\nYou can run this program again to add the missing files."

            messagebox.showinfo("ZIP Created", summary)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not create ZIP file:\n\n{e}\n\nMake sure you have permission to write to that folder."
            )

    def on_close(self):
        if selected_files:
            if not messagebox.askyesno(
                "Exit",
                "You have files selected but haven't created the ZIP yet. Exit anyway?"
            ):
                return
        self.destroy()


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    # Check Python version
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or newer is required.")
        print(f"Your version: {sys.version}")
        sys.exit(1)

    # Check tkinter
    try:
        import tkinter  # noqa
    except ImportError:
        print("ERROR: tkinter is not available.")
        print("On Linux: sudo apt install python3-tk")
        print("On Mac/Windows: reinstall Python from python.org")
        sys.exit(1)

    app = ExhibitAssembler()
    app.mainloop()


if __name__ == "__main__":
    main()
