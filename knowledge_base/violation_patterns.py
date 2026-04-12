"""
Known police misconduct and rights-violation patterns to look for in video footage.
Each pattern includes what to observe visually, what it may indicate legally,
and how to rate its severity.
"""

from typing import List, Dict


VIOLATION_PATTERNS: List[Dict] = [

    # ── Miranda / Interrogation ────────────────────────────────────────────────
    {
        "id": "P001",
        "name": "Miranda Warning Not Given Before Questioning",
        "category": "miranda",
        "visual_cues": [
            "Officer asks questions about crime before reading Miranda",
            "Person appears restrained (handcuffed/in patrol car) and is being questioned",
            "No visible reading from Miranda card or recitation of rights",
            "Officer says 'you don't have to talk to me' informally but proceeds to question",
        ],
        "legal_basis": ["MIRANDA_RIGHTS", "US_CONST_5A", "US_CONST_6A"],
        "severity_range": (8, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "recommended_action": "File Motion to Suppress all statements made during custodial interrogation.",
    },
    {
        "id": "P002",
        "name": "Questioning Continued After Rights Invoked",
        "category": "miranda",
        "visual_cues": [
            "Person says 'I want a lawyer' and officer continues asking questions",
            "Person says 'I am not answering' and officer continues",
            "Person says 'I want to remain silent' and interrogation resumes",
        ],
        "legal_basis": ["MIRANDA_RIGHTS", "US_CONST_5A"],
        "severity_range": (9, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "recommended_action": "File Motion to Suppress all post-invocation statements. Report to DOJ Civil Rights Division.",
    },

    # ── Search and Seizure ────────────────────────────────────────────────────
    {
        "id": "P003",
        "name": "Warrantless Vehicle Search Without Exception",
        "category": "search_seizure",
        "visual_cues": [
            "Officer opens car door without consent",
            "Officer reaches into vehicle without warrant being presented",
            "Officer searches trunk, glove box, or under seats",
            "No written warrant document visible",
            "No apparent exigent circumstances (no safety threat visible)",
        ],
        "legal_basis": ["US_CONST_4A", "ME_CONST_ART1_SEC5", "ME_15_1091"],
        "severity_range": (7, 9),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Exceptions: consent (must be voluntary), inventory search after lawful arrest, plain view, exigent circumstances.",
        "recommended_action": "File Motion to Suppress all evidence obtained from vehicle search.",
    },
    {
        "id": "P004",
        "name": "Traffic Stop Extended Beyond Lawful Purpose",
        "category": "search_seizure",
        "visual_cues": [
            "Officer returns to car with license/registration (stop purpose completed) and continues detention",
            "Dog sniff or additional questioning begins after documents checked",
            "Stop extends visibly beyond time needed to write a ticket",
            "Officer calling for backup during a routine stop with no threat",
        ],
        "legal_basis": ["US_CONST_4A", "ME_29A_2104"],
        "severity_range": (6, 8),
        "is_illegal": True,
        "is_red_flag": True,
        "key_cases": ["Rodriguez v. United States, 575 U.S. 348 (2015)"],
        "recommended_action": "Move to suppress all evidence obtained after the unlawful extension.",
    },
    {
        "id": "P005",
        "name": "Search of Person Without Arrest or Consent",
        "category": "search_seizure",
        "visual_cues": [
            "Officer pats down or searches pockets without placing person under arrest",
            "Officer removes items from pockets without visible consent",
            "No safety threat evident to justify Terry stop pat-down",
        ],
        "legal_basis": ["US_CONST_4A", "ME_CONST_ART1_SEC5"],
        "severity_range": (7, 9),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Terry stop permits limited pat-down for weapons only if articulable safety concern.",
    },

    # ── Excessive Force ───────────────────────────────────────────────────────
    {
        "id": "P006",
        "name": "Excessive Force Against Compliant Subject",
        "category": "excessive_force",
        "visual_cues": [
            "Subject has hands up, is not resisting, but force continues",
            "Person is on ground compliant and officer strikes them",
            "Handcuffed person is struck, kneed, or kicked",
            "Multiple officers restraining unresisting subject",
            "Use of taser/OC spray on clearly compliant person",
        ],
        "legal_basis": ["US_CONST_4A", "US_CONST_8A", "ME_17A_107", "GRAHAM_STANDARD"],
        "severity_range": (8, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "recommended_action": "Document injuries. File civil complaint under 42 U.S.C. §1983 and Maine Civil Rights Act.",
    },
    {
        "id": "P007",
        "name": "Choke Hold or Neck Restraint",
        "category": "excessive_force",
        "visual_cues": [
            "Officer grabs subject's neck/throat area",
            "Officer places arm across throat in restraint",
            "Subject appears to be having difficulty breathing",
        ],
        "legal_basis": ["US_CONST_4A", "ME_17A_107"],
        "severity_range": (9, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Many Maine agencies have prohibited this. Check agency policy. Post-George Floyd legislation may apply.",
    },
    {
        "id": "P008",
        "name": "Failure to Intervene in Excessive Force",
        "category": "excessive_force",
        "visual_cues": [
            "One officer using excessive force while others watch and do nothing",
            "No officer attempts to stop a colleague's use of force",
        ],
        "legal_basis": ["ME_17A_107"],
        "severity_range": (7, 9),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Duty-to-intervene added to Maine law in 2021 (LD 1884). Applies to incidents after June 29, 2021.",
    },

    # ── Unlawful Arrest / Detention ────────────────────────────────────────────
    {
        "id": "P009",
        "name": "Arrest Without Probable Cause",
        "category": "arrest",
        "visual_cues": [
            "Person is handcuffed for minor activity with no evident crime",
            "Officer cannot articulate or explain reason for arrest at scene",
            "Arrest appears retaliatory (person recorded police, complained, etc.)",
        ],
        "legal_basis": ["US_CONST_4A", "ME_15_823"],
        "severity_range": (7, 9),
        "is_illegal": True,
        "is_red_flag": True,
        "recommended_action": "Challenge probable cause at arraignment. File suppression motion.",
    },
    {
        "id": "P010",
        "name": "Prolonged Detention Without Charges",
        "category": "detention",
        "visual_cues": [
            "Person in custody in patrol car for extended time",
            "No Miranda, no charges explained, no booking evident",
        ],
        "legal_basis": ["US_CONST_4A", "US_CONST_6A", "ME_15_821"],
        "severity_range": (6, 8),
        "is_red_flag": True,
    },
    {
        "id": "P011",
        "name": "Arrest / Retaliation for Recording Police",
        "category": "first_amendment",
        "visual_cues": [
            "Person is filming/recording police",
            "Officer orders person to stop recording",
            "Officer arrests or detains person after or during recording",
            "Officer takes phone or camera from person filming",
        ],
        "legal_basis": ["US_CONST_4A", "ME_15_709"],
        "severity_range": (7, 9),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "1st Circuit has held there is a First Amendment right to record police in public.",
    },

    # ── Officer Identification / Procedure ────────────────────────────────────
    {
        "id": "P012",
        "name": "Officer Refuses to Identify / No Badge Visible",
        "category": "procedure",
        "visual_cues": [
            "Officer's badge not visible or covered",
            "Officer refuses to give name or badge number when asked",
            "Officer in plain clothes with no identification shown before force",
        ],
        "legal_basis": ["ME_25_2803B"],
        "severity_range": (5, 7),
        "is_red_flag": True,
    },
    {
        "id": "P013",
        "name": "Body Camera Not Activated During Required Contact",
        "category": "body_camera",
        "visual_cues": [
            "Officer interacts with public but body camera light not on",
            "Video starts mid-interaction (missing the beginning)",
            "Officer is seen turning off or covering camera",
        ],
        "legal_basis": ["ME_25_2803B"],
        "severity_range": (6, 8),
        "is_red_flag": True,
        "notes": "Post-2021 Maine law requires activation during specified contacts. Creates adverse inference.",
    },
    {
        "id": "P014",
        "name": "Dashcam Audio or Video Disabled During Stop",
        "category": "body_camera",
        "visual_cues": [
            "Video cuts out during critical moments",
            "Audio muted or missing during encounter",
            "Camera position changed to avoid capturing action",
        ],
        "legal_basis": ["ME_25_2803B", "ME_17A_453"],
        "severity_range": (7, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Intentional deactivation during arrest may constitute evidence tampering.",
    },

    # ── Racial Profiling / Discrimination ─────────────────────────────────────
    {
        "id": "P015",
        "name": "Apparent Racial Profiling Stop",
        "category": "discrimination",
        "visual_cues": [
            "Stop of minority driver/pedestrian with no visible traffic violation",
            "Officer questions race/ethnicity of occupants",
            "Pattern visible: stops of similar demographic without apparent cause",
        ],
        "legal_basis": ["US_CONST_14A", "ME_5_4551", "ME_29A_2104"],
        "severity_range": (7, 10),
        "is_illegal": True,
        "is_red_flag": True,
    },

    # ── Evidence / Documentation ───────────────────────────────────────────────
    {
        "id": "P016",
        "name": "Evidence Handling Irregularities",
        "category": "evidence",
        "visual_cues": [
            "Officer handles evidence without gloves",
            "Evidence placed in unmarked/unsecured container",
            "No documentation or photography of evidence at scene",
            "Officer moves or disturbs items before photographing",
        ],
        "legal_basis": ["ME_17A_453"],
        "severity_range": (5, 8),
        "is_red_flag": True,
        "recommended_action": "Challenge chain of custody at trial. Request evidence log in discovery.",
    },
    {
        "id": "P017",
        "name": "Coercive or Threatening Statements by Officer",
        "category": "coercion",
        "visual_cues": [
            "Officer threatens consequences to get cooperation",
            "Officer makes promises in exchange for statements",
            "Officer raises voice aggressively, uses profanity, or demeans subject",
        ],
        "legal_basis": ["US_CONST_5A", "MIRANDA_RIGHTS"],
        "severity_range": (6, 9),
        "is_red_flag": True,
    },
    {
        "id": "P018",
        "name": "Search or Entry Into Residence Without Warrant",
        "category": "search_seizure",
        "visual_cues": [
            "Officers enter a home without showing a warrant",
            "Door forced open without consent visible",
            "Officers inside residence before any emergency visible",
        ],
        "legal_basis": ["US_CONST_4A", "ME_CONST_ART1_SEC5", "ME_15_1091"],
        "severity_range": (9, 10),
        "is_illegal": True,
        "is_red_flag": True,
        "notes": "Home is highest-protected area — warrantless entry presumptively unreasonable. Exceptions: exigent circumstances, consent.",
    },
]


MISCONDUCT_PATTERNS: List[Dict] = [
    {
        "id": "M001",
        "name": "Planting Evidence",
        "indicators": [
            "Officer reaches into area not visible and item appears",
            "Item found in location suspect was nowhere near",
            "Officer's hand seen at suspicious location before 'discovery'",
        ],
        "laws": ["ME_17A_453", "US_18_1519"],
        "severity": 10,
        "is_illegal": True,
    },
    {
        "id": "M002",
        "name": "False Arrest / Pretextual Stop",
        "indicators": [
            "Officer invents or inflates reason for stop on camera",
            "Stated reason for arrest inconsistent with observable facts",
        ],
        "laws": ["ME_15_823", "US_CONST_4A"],
        "severity": 9,
        "is_illegal": True,
    },
    {
        "id": "M003",
        "name": "Coordinated Misconduct / Cover Story",
        "indicators": [
            "Officers huddle away from cameras before writing reports",
            "Officers give identical word-for-word accounts",
            "Officers confer before making statements without documenting",
        ],
        "laws": ["US_42_1985", "ME_17A_451", "ME_17A_452"],
        "severity": 10,
        "is_illegal": True,
    },
    {
        "id": "M004",
        "name": "Retaliation for Complaint or Lawsuit",
        "indicators": [
            "Officer's conduct changes negatively after learning of complaint",
            "Pattern of stops targeting the same person",
        ],
        "laws": ["US_42_1983", "ME_MCRA_4681"],
        "severity": 9,
        "is_illegal": True,
    },
]


# Metadata red flags (for use by metadata analyzer)
METADATA_RED_FLAGS = [
    {
        "key": "editing_software",
        "description": "Video edited with commercial software before disclosure",
        "keywords": ["Adobe Premiere", "Final Cut", "DaVinci Resolve", "iMovie", "Vegas Pro",
                     "Camtasia", "Handbrake", "ffmpeg"],
        "severity": 9,
        "law": "ME_17A_453",
        "note": "Presence of editing software metadata suggests the video may have been altered after recording.",
    },
    {
        "key": "timestamp_gap",
        "description": "Gap between file creation time and video timestamp",
        "severity": 7,
        "law": "ME_17A_453",
        "note": "Large discrepancy between file creation date and video content timestamps may indicate tampering.",
    },
    {
        "key": "missing_gps",
        "description": "GPS metadata absent from body camera / dashcam footage",
        "severity": 5,
        "law": "ME_25_2803B",
        "note": "Modern dashcams and body cameras typically record GPS. Missing GPS may indicate data was stripped.",
    },
    {
        "key": "codec_mismatch",
        "description": "Video codec inconsistent with recording device specifications",
        "severity": 6,
        "law": "ME_17A_453",
        "note": "If the codec is not standard for the stated recording device, the file may have been transcoded/edited.",
    },
    {
        "key": "file_modified_after_creation",
        "description": "File modification date is after the file creation date",
        "severity": 6,
        "law": "ME_17A_453",
        "note": "Modification after creation can indicate editing or re-encoding.",
    },
    {
        "key": "missing_audio",
        "description": "No audio track in a video that should have audio",
        "severity": 7,
        "law": "ME_25_2803B",
        "note": "Body cameras and dashcams always record audio. Missing audio suggests it was stripped or camera was muted.",
    },
    {
        "key": "short_duration",
        "description": "Video is unusually short or appears truncated",
        "severity": 6,
        "law": "ME_25_2803B",
        "note": "If incident extended longer than the video, footage may have been withheld or deleted.",
    },
    {
        "key": "discontinuous_timestamps",
        "description": "Internal video timestamps are discontinuous (jump or reset)",
        "severity": 8,
        "law": "ME_17A_453",
        "note": "Timestamp jumps within the video file indicate frames or segments were removed.",
    },
]
