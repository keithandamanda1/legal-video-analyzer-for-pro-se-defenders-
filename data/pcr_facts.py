"""
Seed data for PCR Petition Organizer — CR-2018-03023
Call seed_pcr_data() once at startup if the table is empty.
"""
import database as db


# ── Evidence by ground ────────────────────────────────────────────────────────

PCR_EVIDENCE_SEED = [
    # GROUND 1 — Involuntary Plea
    {
        "event_date": "2021-09-21",
        "category": "plea",
        "ground_number": 1,
        "title": "Surprise plea at mental-health hearing — not calendared as plea",
        "description": (
            "The September 21, 2021 hearing was calendared as a mental-health/medication "
            "check-in. AAG Jason Horn arrived with a plea offer and a 30-minute ultimatum. "
            "Petitioner was unmedicated and in documented mental health crisis (Bipolar "
            "Disorder, Panic Attack Disorder)."
        ),
        "source": "Docket sheet; hearing transcript; medical records",
        "exhibit_label": "Exhibit A",
        "law_reference": "Boykin v. Alabama, 395 U.S. 238 (1969); M.R.U. Crim. P. 11(b)(3)",
        "status": "documented",
    },
    {
        "event_date": "2021-09-21",
        "category": "plea",
        "ground_number": 1,
        "title": "Prior court order required medical stabilization before plea",
        "description": (
            "A prior court order explicitly required medical stabilization before any "
            "plea could be entered. This order was ignored at the September 21 hearing. "
            "No disability accommodation was sought or offered."
        ),
        "source": "Prior court order (on file); docket",
        "exhibit_label": "Exhibit A-2",
        "law_reference": "ADA Title II; M.R.U. Crim. P. 11(b)(3)",
        "status": "documented",
    },
    {
        "event_date": "2021-09-21",
        "category": "plea",
        "ground_number": 1,
        "title": "4-year mandatory minimum threat used to coerce plea",
        "description": (
            "AAG Horn threatened a 4-year mandatory minimum if the plea offer was "
            "refused. Petitioner, unmedicated and without adequate time to consult "
            "with counsel, accepted. No adequate explanation of rights being waived "
            "was provided."
        ),
        "source": "Plea colloquy transcript; counsel records",
        "exhibit_label": "Exhibit A-3",
        "law_reference": "Brady v. United States, 397 U.S. 742 (1970)",
        "status": "needed",
    },
    {
        "event_date": "2021-09-21",
        "category": "plea",
        "ground_number": 1,
        "title": "Factual basis for 'in fact heroin' never established at plea",
        "description": (
            "The TruNarc field test returned 'INCONCLUSIVE.' No confirmatory laboratory "
            "test was completed. The plea's factual basis for 'in fact heroin' was "
            "never scientifically established. The court accepted the plea without "
            "requiring confirmation of the chemical identity."
        ),
        "source": "TruNarc field test report; crime lab records (requested)",
        "exhibit_label": "Exhibit C",
        "law_reference": "State v. Searles; M.R.U. Crim. P. 11(b)(3)",
        "status": "missing",
    },

    # GROUND 2 — Ineffective Assistance of Counsel
    {
        "event_date": "2018-08-02",
        "category": "stop",
        "ground_number": 2,
        "title": "No suppression motion filed — pretextual, unrecorded traffic stop",
        "description": (
            "The August 2, 2018 traffic stop was never logged in dispatch or radio. "
            "No articulable basis was stated on dashcam. Counsel filed no motion to "
            "suppress under Rodriguez v. United States (no prolonged stop justification) "
            "or the Maine Constitution."
        ),
        "source": "Dashcam video (released 2/21/24); CAD/dispatch records",
        "exhibit_label": "Exhibit D",
        "law_reference": "Rodriguez v. United States, 575 U.S. 348 (2015); U.S. Const. amend. IV",
        "status": "obtained",
    },
    {
        "event_date": "2018-08-02",
        "category": "stop",
        "ground_number": 2,
        "title": "No motion filed — off-site transport/detention without warrant authority",
        "description": (
            "Petitioner was handcuffed and transported from Davis Road to his residence "
            "before any warrant existed. The search warrant application was signed "
            "approximately 2 hours AFTER the traffic stop. Counsel filed no Bailey motion."
        ),
        "source": "Dashcam video; warrant application timestamp records",
        "exhibit_label": "Exhibit D-2",
        "law_reference": "Bailey v. United States, 568 U.S. 186 (2013)",
        "status": "obtained",
    },
    {
        "event_date": "2018-08-02",
        "category": "stop",
        "ground_number": 2,
        "title": "No Franks challenge — nonexistent/contradictory witness statements in warrant",
        "description": (
            "The search warrant affidavit cited 'witness statements' that either do not "
            "exist or are internally contradictory. Counsel filed no Franks challenge "
            "to the affidavit. A successful Franks challenge would have invalidated "
            "the warrant and suppressed all downstream evidence."
        ),
        "source": "Warrant affidavit; investigative records",
        "exhibit_label": "Exhibit E",
        "law_reference": "Franks v. Delaware, 438 U.S. 154 (1978)",
        "status": "needed",
    },
    {
        "event_date": "2018-08-07",
        "category": "phone",
        "ground_number": 2,
        "title": "No motion filed — phone seized despite explicit warrant exclusion",
        "description": (
            "The August 2 search warrant contained an explicit exclusionary clause "
            "prohibiting seizure of cellular phones. Officers seized Petitioner's phone "
            "anyway. Counsel filed no motion to suppress or return the phone under "
            "the warrant's own terms."
        ),
        "source": "Search warrant (explicit exclusion clause); evidence log",
        "exhibit_label": "Exhibit F",
        "law_reference": "U.S. Const. amend. IV; Wong Sun v. United States, 371 U.S. 471 (1963)",
        "status": "obtained",
    },
    {
        "event_date": "2019-10-15",
        "category": "chain_of_custody",
        "ground_number": 2,
        "title": "No motion to dismiss gabapentin charge — not scheduled until October 2019",
        "description": (
            "Gabapentin was not a scheduled controlled substance in Maine on "
            "August 2, 2018. It was added to Schedule W by Me. PL 2019, ch. 487, "
            "effective October 15, 2019. The charge was legally impossible. "
            "Counsel failed to file any motion to dismiss on ex post facto grounds."
        ),
        "source": "Me. PL 2019, ch. 487; Maine statute history",
        "exhibit_label": "Exhibit G",
        "law_reference": "U.S. Const. art. I, § 10 (Ex Post Facto Clause); Me. PL 2019 ch. 487",
        "status": "documented",
    },

    # GROUND 3 — Brady/Giglio/Napue
    {
        "event_date": "2018-08-02",
        "category": "brady",
        "ground_number": 3,
        "title": "TruNarc 'INCONCLUSIVE' result withheld / misrepresented",
        "description": (
            "The TruNarc handheld spectrometer test on the alleged heroin returned "
            "'INCONCLUSIVE.' This exculpatory result was withheld from defense and "
            "never disclosed. The prosecution charged 'in fact heroin' with no "
            "scientific basis. No confirmatory GC-MS or lab test was completed."
        ),
        "source": "TruNarc field test report; crime lab request (pending)",
        "exhibit_label": "Exhibit C",
        "law_reference": "Brady v. Maryland, 373 U.S. 83 (1963); Giglio v. United States, 405 U.S. 150 (1972)",
        "status": "documented",
    },
    {
        "event_date": "2024-02-21",
        "category": "brady",
        "ground_number": 3,
        "title": "Dashcam footage withheld 5.5 years — released February 21, 2024",
        "description": (
            "Full dashcam footage was withheld for 5.5 years after the August 2, 2018 "
            "arrest. Released February 21, 2024 following Petitioner's FOAA/Rule 16 "
            "demands. The footage shows: no traffic infraction articulated, no warrant "
            "shown at apartment door, officers produced a key from their pocket."
        ),
        "source": "Dashcam video (released 2/21/24); BPD FOAA response",
        "exhibit_label": "Exhibit D",
        "law_reference": "Brady v. Maryland; Me. R.U. Crim. P. 16",
        "status": "obtained",
    },
    {
        "event_date": "2024-02-21",
        "category": "brady",
        "ground_number": 3,
        "title": "Dashcam metadata stripped — date, time, GPS, officer ID removed",
        "description": (
            "The produced dashcam footage is missing all embedded metadata: date, "
            "time, GPS coordinates, and officer ID fields have been stripped. "
            "Native file format audit logs and hash values have not been produced. "
            "This constitutes evidence of tampering and ongoing Brady non-compliance."
        ),
        "source": "Produced dashcam file (metadata analysis); Brady request",
        "exhibit_label": "Exhibit D-3",
        "law_reference": "Brady v. Maryland; 18 U.S.C. § 1519 (evidence tampering)",
        "status": "documented",
    },
    {
        "event_date": "2018-08-02",
        "category": "brady",
        "ground_number": 3,
        "title": "Amanda Ross phone seizure — DA falsely denied phone was taken",
        "description": (
            "The DA stated Amanda Ross's phone was never taken. Forensic extraction "
            "records prove the phone was extracted and held for approximately 45 days "
            "without any warrant. 1,000+ calls and 350+ private photos were extracted "
            "from multiple devices; private materials subsequently appeared online."
        ),
        "source": "Forensic extraction records; DA statements; evidence logs",
        "exhibit_label": "Exhibit F-2",
        "law_reference": "Brady v. Maryland; Napue v. Illinois, 360 U.S. 264 (1959)",
        "status": "documented",
    },
    {
        "event_date": "2025-10-05",
        "category": "brady",
        "ground_number": 3,
        "title": "AAG Stuver conflict of interest — DHHS/CPS overlap never disclosed",
        "description": (
            "Confirmation on October 5, 2025: AAG Janice Stuver previously represented "
            "DHHS/CPS in a related family matter involving Petitioner while this criminal "
            "case was pending — a direct conflict of interest that was never disclosed "
            "to defense counsel or the court."
        ),
        "source": "CPS case records; AAG assignment records; October 5, 2025 confirmation",
        "exhibit_label": "Exhibit I",
        "law_reference": "Giglio v. United States; Maine Rules of Professional Conduct 1.7, 1.9",
        "status": "documented",
    },

    # GROUND 4 — Fourth Amendment
    {
        "event_date": "2018-08-02",
        "category": "stop",
        "ground_number": 4,
        "title": "Stop — warrant signed 2 hours AFTER traffic stop",
        "description": (
            "The search warrant application was signed approximately 2 hours after "
            "the traffic stop. The entire initial detention was warrantless. "
            "The stop was never logged in dispatch or radio — an off-book stop "
            "with no contemporaneous record."
        ),
        "source": "Warrant application timestamp; dispatch/CAD records; dashcam",
        "exhibit_label": "Exhibit D",
        "law_reference": "U.S. Const. amend. IV; Terry v. Ohio, 392 U.S. 1 (1968)",
        "status": "obtained",
    },
    {
        "event_date": "2018-08-02",
        "category": "stop",
        "ground_number": 4,
        "title": "BHA Master Key Log — ZERO entry for August 2, 2018",
        "description": (
            "BHA Master Key Log (MHRC Exhibit B, produced October 2025) contains "
            "ZERO entry for August 2, 2018. No key was officially checked out. "
            "Officers obtained Petitioner's master key entirely outside the official "
            "checkout system — a covert, unauthorized handoff. Residential entry "
            "violated 4th Amendment, 24 C.F.R. § 966.4(d)(3), and 5 M.R.S. § 4582."
        ),
        "source": "BHA Master Key Log (Exhibit B); PCR affidavit December 2025",
        "exhibit_label": "Exhibit B",
        "law_reference": "U.S. Const. amend. IV; Bailey v. United States; 24 C.F.R. § 966.4(d)(3)",
        "status": "obtained",
    },
    {
        "event_date": "2018-08-02",
        "category": "phone",
        "ground_number": 4,
        "title": "Phone seized despite explicit warrant exclusion — tainted fruit",
        "description": (
            "Officers seized Petitioner's phone despite the explicit exclusionary clause "
            "in the warrant. The phone was held August 2–7 without a warrant. "
            "A second warrant (August 7) was obtained to search the already-illegally-"
            "seized phone — this second warrant is tainted fruit under Wong Sun."
        ),
        "source": "Search warrant (exclusion clause); evidence log; second warrant",
        "exhibit_label": "Exhibit F",
        "law_reference": "Wong Sun v. United States, 371 U.S. 471 (1963)",
        "status": "obtained",
    },

    # GROUND 5 — Gabapentin Ex Post Facto
    {
        "event_date": "2018-08-02",
        "category": "chain_of_custody",
        "ground_number": 5,
        "title": "Gabapentin charged as controlled substance — not scheduled until Oct 15, 2019",
        "description": (
            "Gabapentin was charged as a controlled substance for August 2, 2018 conduct. "
            "Gabapentin was NOT scheduled in Maine until Me. PL 2019, ch. 487, "
            "effective October 15, 2019 — more than one year AFTER the arrest. "
            "The charge was legally impossible. Conviction on this count is void."
        ),
        "source": "Me. PL 2019, ch. 487; Maine statute history; charging document",
        "exhibit_label": "Exhibit G",
        "law_reference": "U.S. Const. art. I, § 10; Me. Const. art. I, § 11",
        "status": "documented",
    },

    # GROUND 6 — Coercive Pretrial Conditions
    {
        "event_date": "2018-08-02",
        "category": "plea",
        "ground_number": 6,
        "title": "$100,000 cash-only bail — no property bond, no ankle monitoring",
        "description": (
            "First-time, non-violent, disabled defendant with $370 cash, no passport, "
            "lifelong Bangor ties. Parents offered $450K home + 45 acres + ankle monitoring "
            "— all denied. Cash-only bail of $100,000 was constitutionally disproportionate "
            "and effectively punitive pretrial detention."
        ),
        "source": "Bail hearing transcript; parents' property records",
        "exhibit_label": "Exhibit J",
        "law_reference": "U.S. Const. amend. VIII; Stack v. Boyle, 342 U.S. 1 (1951)",
        "status": "documented",
    },
    {
        "event_date": "2018-08-02",
        "category": "plea",
        "ground_number": 6,
        "title": "Medication denied for 42 days of detention",
        "description": (
            "Petitioner's prescribed medications for Bipolar Disorder and Panic Attack "
            "Disorder were denied for 42 days of pretrial detention. This created the "
            "medicated-impaired state that made the surprise plea involuntary."
        ),
        "source": "Medical records; detention facility records",
        "exhibit_label": "Exhibit K",
        "law_reference": "Washington v. Harper, 494 U.S. 210 (1990); Estelle v. Gamble",
        "status": "needed",
    },

    # GROUND 7 — Equitable Tolling / Newly Discovered Evidence
    {
        "event_date": "2024-02-21",
        "category": "newly_discovered",
        "ground_number": 7,
        "title": "Dashcam released 5.5 years post-arrest — triggers newly discovered evidence pathway",
        "description": (
            "Dashcam video released February 21, 2024 — 5.5 years after the August 2, "
            "2018 arrest. This is a key newly discovered evidence predicate for "
            "15 M.R.S. § 2128-B. Active stonewalling by BHA, BPD, and state agencies "
            "for 7+ years constitutes fraudulent concealment tolling under 14 M.R.S. § 859."
        ),
        "source": "BPD FOAA response; dashcam video",
        "exhibit_label": "Exhibit D",
        "law_reference": "15 M.R.S. § 2128-B; 14 M.R.S. § 859",
        "status": "obtained",
    },
    {
        "event_date": "2025-12-17",
        "category": "newly_discovered",
        "ground_number": 7,
        "title": "AAG Stuver admission: Aggravated Class A charges were 'inadvertent error'",
        "description": (
            "December 17, 2025: Former AAG Janice Stuver formally admitted the "
            "Aggravated Class A charges were based on an 'inadvertent error' regarding "
            "the location of evidence. This admission was not available at the time of "
            "plea and constitutes newly discovered evidence under § 2128-B."
        ),
        "source": "AAG Stuver written admission, December 17, 2025",
        "exhibit_label": "Exhibit M",
        "law_reference": "15 M.R.S. § 2128-B; Kyles v. Whitley, 514 U.S. 419 (1995)",
        "status": "obtained",
    },
    {
        "event_date": "2025-10-01",
        "category": "newly_discovered",
        "ground_number": 7,
        "title": "BHA Key Log produced — ZERO entry for 8/2/18 confirms off-book key handoff",
        "description": (
            "BHA Master Key Log (October 2025) contains no entry for August 2, 2018. "
            "Confirms officers used Petitioner's master key entirely outside the official "
            "checkout system. Not available at time of plea (produced 7 years later)."
        ),
        "source": "BHA Master Key Log (MHRC Exhibit B)",
        "exhibit_label": "Exhibit B",
        "law_reference": "15 M.R.S. § 2128-B",
        "status": "obtained",
    },
    {
        "event_date": "2025-10-05",
        "category": "newly_discovered",
        "ground_number": 7,
        "title": "HUD FOIA records — inter-agency suppression of Petitioner's records requests",
        "description": (
            "HUD FOIA records (October 2025) reveal coordination between HUD Boston "
            "Region (Norman/Karki) and BHA to suppress Petitioner's records requests. "
            "These records were obtained through multi-year FOIA litigation and "
            "represent newly discovered evidence unavailable at time of plea."
        ),
        "source": "HUD FOIA response",
        "exhibit_label": "Exhibit L",
        "law_reference": "15 M.R.S. § 2128-B; 14 M.R.S. § 859 (fraudulent concealment)",
        "status": "obtained",
    },
    {
        "event_date": "2018-08-02",
        "category": "chain_of_custody",
        "ground_number": 3,
        "title": "Evidence held 18 hours by Officer Gastia in unrecorded location",
        "description": (
            "Evidence was held by Officer Gastia in an unrecorded location for "
            "approximately 18 hours overnight before being logged into the evidence "
            "system. This 18-24 hour custody gap breaks chain of custody and raises "
            "serious integrity questions about the physical evidence."
        ),
        "source": "Evidence log; property room records; Officer Gastia reports",
        "exhibit_label": "Exhibit N",
        "law_reference": "Me. R. Evid. 901; Brady v. Maryland",
        "status": "needed",
    },
]


PCR_CONTRADICTIONS_SEED = [
    {
        "contradiction_date": "2018-08-02",
        "ground_number": 3,
        "item_a_label": "TruNarc Field Test Result",
        "item_a_text": "TruNarc handheld test result: 'INCONCLUSIVE' — no identification of substance.",
        "item_b_label": "Criminal Charging Language",
        "item_b_text": "'In fact heroin' — affirmative factual assertion in charging document and plea colloquy.",
        "significance": "CRITICAL Brady/Giglio violation. The charging language is directly contradicted by the only scientific test performed. No confirmatory GC-MS test was ever run.",
        "law_reference": "Brady v. Maryland, 373 U.S. 83 (1963); Giglio v. United States, 405 U.S. 150 (1972)",
        "resolution_needed": "Obtain complete crime lab packet including all TruNarc printouts, bench notes, chain of custody for the substance, and evidence that any confirmatory test was or was not performed.",
    },
    {
        "contradiction_date": "2018-08-02",
        "ground_number": 4,
        "item_a_label": "Warrant Application Timestamp",
        "item_a_text": "Search warrant application signed approximately 2 hours AFTER the traffic stop and initial detention.",
        "item_b_label": "Legal Authority for Initial Stop/Detention",
        "item_b_text": "Officers claimed to have legal authority to stop, detain, and transport Petitioner to his residence.",
        "significance": "The entire initial detention — including transport to the residence, entry, and initial search — was warrantless. No emergency exception was claimed or documented.",
        "law_reference": "Bailey v. United States, 568 U.S. 186 (2013); U.S. Const. amend. IV",
        "resolution_needed": "Obtain warrant application with timestamp; compare to dashcam timestamp (stripped but recoverable from file metadata); obtain dispatch/CAD logs for August 2, 2018.",
    },
    {
        "contradiction_date": "2018-08-02",
        "ground_number": 4,
        "item_a_label": "BHA Master Key Log (Exhibit B)",
        "item_a_text": "BHA Master Key Log for August 2, 2018 contains ZERO entry. No key was officially checked out for the date of the search.",
        "item_b_label": "Officers' Implied Authority to Enter",
        "item_b_text": "Officers entered Petitioner's residence using a key they produced from their pocket — implying an authorized key handoff through proper channels.",
        "significance": "The absence of any log entry IS the evidence of an unauthorized, off-book key arrangement. Entry without consent, warrant, or officially-checked-out key is a Fourth Amendment violation.",
        "law_reference": "U.S. Const. amend. IV; 24 C.F.R. § 966.4(d)(3); 5 M.R.S. § 4582",
        "resolution_needed": "BHA Key Log already obtained (MHRC Exhibit B). Cross-reference with dashcam footage showing officers producing key. Subpoena BHA records for any alternative key authorization document.",
    },
    {
        "contradiction_date": "2018-08-02",
        "ground_number": 2,
        "item_a_label": "Search Warrant — Explicit Phone Exclusion",
        "item_a_text": "Search warrant contained an explicit exclusionary clause prohibiting seizure of cellular phones.",
        "item_b_label": "Actual Conduct — Phone Seized",
        "item_b_text": "Officers seized Petitioner's phone on August 2, 2018 and held it August 2–7 without any warrant authority. A second warrant was obtained August 7 to search the already-illegally-held phone.",
        "significance": "The phone seizure violated the warrant's own express terms. All phone evidence is tainted fruit. The August 7 second warrant cannot purge the taint of the initial illegal seizure.",
        "law_reference": "Wong Sun v. United States, 371 U.S. 471 (1963); U.S. Const. amend. IV",
        "resolution_needed": "Obtain: (1) original August 2 warrant with exclusion clause; (2) evidence log showing phone check-in date; (3) August 7 warrant; (4) forensic extraction report and chain of custody.",
    },
    {
        "contradiction_date": "2018-08-02",
        "ground_number": 5,
        "item_a_label": "Gabapentin Scheduling Date in Maine",
        "item_a_text": "Gabapentin added to Schedule W by Me. PL 2019, ch. 487, effective October 15, 2019.",
        "item_b_label": "Gabapentin Charge Conduct Date",
        "item_b_text": "Gabapentin charged as a controlled substance for conduct on August 2, 2018 — more than 14 months before it was scheduled.",
        "significance": "This is a legally impossible charge. It violates the Ex Post Facto Clause. The conviction on this count is void ab initio and must be dismissed regardless of other relief.",
        "law_reference": "U.S. Const. art. I, § 10; Me. PL 2019, ch. 487",
        "resolution_needed": "Statutory history already documented. Need: charging document confirming gabapentin count; plea colloquy confirming count was included in plea.",
    },
    {
        "contradiction_date": "2018-09-01",
        "ground_number": 3,
        "item_a_label": "DA Statement re: Amanda Ross Phone",
        "item_a_text": "District Attorney stated Amanda Ross's phone was never taken by law enforcement.",
        "item_b_label": "Forensic Extraction Records",
        "item_b_text": "Forensic extraction records prove Amanda Ross's phone was extracted and held approximately 45 days without any warrant. 350+ private photos and 1,000+ calls extracted.",
        "significance": "The DA's statement constitutes a Napue violation — knowing presentation of false information to the court. Private materials subsequently appeared on the internet, compounding the harm.",
        "law_reference": "Napue v. Illinois, 360 U.S. 264 (1959); Brady v. Maryland",
        "resolution_needed": "Obtain forensic extraction report for Amanda Ross phone; cross-reference with DA statements; document timeline of when materials appeared online.",
    },
    {
        "contradiction_date": "2021-09-21",
        "ground_number": 1,
        "item_a_label": "Court Docket — Hearing Purpose",
        "item_a_text": "September 21, 2021 hearing was calendared as a mental-health/medication check-in, NOT a plea hearing.",
        "item_b_label": "Actual Event at Hearing",
        "item_b_text": "AAG Horn arrived with a plea offer, 30-minute ultimatum, and 4-year mandatory minimum threat. Plea was entered that day.",
        "significance": "Petitioner had no notice that the hearing would involve a plea. No time to prepare, consult, or seek accommodations. This alone establishes involuntariness under Boykin.",
        "law_reference": "Boykin v. Alabama, 395 U.S. 238 (1969); M.R.U. Crim. P. 11",
        "resolution_needed": "Obtain: (1) court docket entry showing hearing type as mental-health review; (2) hearing transcript; (3) any pre-hearing communications between counsel and AAG Horn.",
    },
    {
        "contradiction_date": "2025-12-17",
        "ground_number": 3,
        "item_a_label": "Original Aggravated Class A Charge",
        "item_a_text": "Aggravated Class A drug trafficking charges filed, carrying mandatory minimum sentences.",
        "item_b_label": "AAG Stuver Admission (12/17/2025)",
        "item_b_text": "Former AAG Stuver admitted Aggravated Class A charges were based on 'inadvertent error' regarding the location of evidence.",
        "significance": "If the aggravated charges were error, the 4-year mandatory minimum threat used to coerce the plea was illegitimate. The plea was induced by a threat that had no valid basis.",
        "law_reference": "Brady v. United States; Giglio; Ferrara v. United States, 456 F.3d 278 (1st Cir. 2006)",
        "resolution_needed": "Obtain AAG Stuver's written admission in full; obtain evidence location records that reveal the 'error'; document when prosecution knew or should have known.",
    },
]


PCR_EXHIBITS_SEED = [
    {
        "exhibit_label": "Exhibit A",
        "title": "September 21, 2021 Hearing Transcript",
        "description": "Full transcript of the surprise plea hearing, showing calendaring as mental-health review, AAG Horn's arrival, ultimatum, and plea colloquy.",
        "source": "Superior Court clerk",
        "ground_numbers": "1,2",
        "obtained": 0,
        "filed": 1,
        "notes": "REQUEST IMMEDIATELY from court clerk. Essential for Grounds 1 and 2.",
    },
    {
        "exhibit_label": "Exhibit B",
        "title": "BHA Master Key Log — August 2018",
        "description": "BHA Master Key Log showing ZERO entry for August 2, 2018. No key officially checked out. Produced via MHRC discovery October 2025.",
        "source": "BHA (via MHRC discovery)",
        "ground_numbers": "4,7",
        "obtained": 1,
        "filed": 1,
        "notes": "Already in hand. Cross-reference with dashcam footage of officers producing key.",
    },
    {
        "exhibit_label": "Exhibit C",
        "title": "TruNarc Field Test Report — 'INCONCLUSIVE'",
        "description": "TruNarc handheld spectrometer test result showing inconclusive identification for the alleged heroin. Central Brady violation.",
        "source": "BPD evidence/lab records",
        "ground_numbers": "1,2,3",
        "obtained": 0,
        "filed": 0,
        "notes": "REQUEST via Brady demand and Rule 16. Also request full crime lab packet: bench notes, chromatograms, instrument logs, chain of custody.",
    },
    {
        "exhibit_label": "Exhibit D",
        "title": "Dashcam Video — Released February 21, 2024",
        "description": "Dashcam footage released 5.5 years post-arrest. Shows: no traffic infraction articulated, no warrant shown, officers produced key from pocket, 3-hour detention in 90-degree heat.",
        "source": "BPD FOAA response",
        "ground_numbers": "2,3,4,7",
        "obtained": 1,
        "filed": 1,
        "notes": "Native files with metadata STILL MISSING. Request: native dashcam files with hash values, metadata, audit/export logs, officer ID data.",
    },
    {
        "exhibit_label": "Exhibit D-3",
        "title": "Dashcam Native Files + Audit Logs (MISSING)",
        "description": "Native dashcam file format with all embedded metadata intact: date, time, GPS, officer ID. Export/audit logs showing chain of custody of video file.",
        "source": "BPD evidence — NOT YET PRODUCED",
        "ground_numbers": "3,4",
        "obtained": 0,
        "filed": 0,
        "notes": "CRITICAL MISSING EVIDENCE. Metadata was stripped from produced version. Brady demand outstanding.",
    },
    {
        "exhibit_label": "Exhibit E",
        "title": "Search Warrant + Affidavit (August 2, 2018)",
        "description": "Original search warrant showing: (1) timestamp of signing (2 hours after stop), (2) explicit phone exclusion clause, (3) witness statement citations that are nonexistent or contradictory.",
        "source": "Penobscot County Superior Court file",
        "ground_numbers": "2,4",
        "obtained": 0,
        "filed": 0,
        "notes": "Obtain from court file. Cross-reference witness statement citations in affidavit with actual investigation records.",
    },
    {
        "exhibit_label": "Exhibit F",
        "title": "Phone Seizure Records — August 2–7, 2018",
        "description": "Evidence log showing phone check-in date; August 7 second warrant; forensic extraction report and chain of custody for Petitioner's phone.",
        "source": "BPD evidence log; court file",
        "ground_numbers": "2,3,4",
        "obtained": 0,
        "filed": 0,
        "notes": "Request via Brady demand. Confirm date phone entered evidence log vs. date of arrest.",
    },
    {
        "exhibit_label": "Exhibit F-2",
        "title": "Amanda Ross Phone Forensic Extraction Records",
        "description": "Forensic extraction records proving Amanda Ross's phone was extracted and held ~45 days without warrant. Contradicts DA statement that phone was never taken.",
        "source": "BPD forensic unit",
        "ground_numbers": "3",
        "obtained": 0,
        "filed": 0,
        "notes": "Brady demand outstanding. Also document timeline of private materials appearing online.",
    },
    {
        "exhibit_label": "Exhibit G",
        "title": "Gabapentin Scheduling History — Me. PL 2019, ch. 487",
        "description": "Maine legislative record showing gabapentin added to Schedule W effective October 15, 2019 — confirming it was not scheduled on August 2, 2018.",
        "source": "Maine Legislature; Maine Revised Statutes history",
        "ground_numbers": "2,5",
        "obtained": 1,
        "filed": 1,
        "notes": "Statutory history documented. Also need: charging document confirming gabapentin count.",
    },
    {
        "exhibit_label": "Exhibit I",
        "title": "AAG Stuver CPS Conflict Documentation",
        "description": "Records showing AAG Stuver represented DHHS/CPS in a related family matter while this criminal case was pending.",
        "source": "CPS case records; AAG assignment records; October 5, 2025 confirmation",
        "ground_numbers": "3,7",
        "obtained": 0,
        "filed": 0,
        "notes": "Request via Brady demand and public records request.",
    },
    {
        "exhibit_label": "Exhibit J",
        "title": "Bail Hearing Transcript + Parents' Property Records",
        "description": "Bail hearing transcript showing cash-only $100,000 bail, denial of property bond/ankle monitoring, and judicial comment re: 'drugs that are killing people.'",
        "source": "Superior Court clerk; Oxford County Registry of Deeds",
        "ground_numbers": "6",
        "obtained": 0,
        "filed": 0,
        "notes": "Judicial pre-verdict comment ('selling drugs that are killing people') should be in transcript.",
    },
    {
        "exhibit_label": "Exhibit L",
        "title": "HUD FOIA Response — Inter-Agency Cover-Up Emails",
        "description": "HUD internal emails showing Kara E. Norman and Richa Karki (HUD Boston Regional Office) coordinating with BHA counsel Bethany and BrHA Director Perkins to ignore Petitioner's records requests.",
        "source": "HUD FOIA response (October 2025)",
        "ground_numbers": "7",
        "obtained": 1,
        "filed": 1,
        "notes": "In hand. Shows pattern of institutional obstruction across agencies.",
    },
    {
        "exhibit_label": "Exhibit M",
        "title": "AAG Stuver Admission — 'Inadvertent Error' (December 17, 2025)",
        "description": "Written admission from former AAG Janice Stuver that the Aggravated Class A charges were based on an inadvertent error regarding the location of evidence.",
        "source": "AAG Stuver written admission",
        "ground_numbers": "1,3,7",
        "obtained": 1,
        "filed": 1,
        "notes": "In hand. Key newly discovered evidence. Undermines the coercive plea threat.",
    },
    {
        "exhibit_label": "Exhibit N",
        "title": "18-Hour Chain of Custody Gap — Officer Gastia",
        "description": "Evidence log showing gap in chain of custody: evidence held by Officer Gastia in unrecorded location for 18-24 hours before logging. Evidence of potential tampering.",
        "source": "BPD evidence log",
        "ground_numbers": "3",
        "obtained": 0,
        "filed": 0,
        "notes": "Request complete evidence log for all items seized August 2, 2018, with timestamps.",
    },
]


def seed_pcr_data() -> None:
    if db.pcr_seeded():
        return

    for ev in PCR_EVIDENCE_SEED:
        db.pcr_add_evidence(**ev)

    for co in PCR_CONTRADICTIONS_SEED:
        db.pcr_add_contradiction(**co)

    for ex in PCR_EXHIBITS_SEED:
        db.pcr_add_exhibit(**ex)
