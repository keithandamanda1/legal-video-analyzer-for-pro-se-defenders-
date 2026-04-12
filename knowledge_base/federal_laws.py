"""
Federal laws and constitutional provisions relevant to police misconduct cases.
All section text is from official U.S. government sources.
"""

from typing import List, Dict


FEDERAL_LAWS: List[Dict] = [

    # ── Constitutional Amendments ─────────────────────────────────────────────
    {
        "id": "US_CONST_4A",
        "title": "4th Amendment — Unreasonable Searches and Seizures",
        "category": "constitutional",
        "effective_date": "1791-12-15",
        "full_text": (
            "The right of the people to be secure in their persons, houses, papers, and "
            "effects, against unreasonable searches and seizures, shall not be violated, and "
            "no Warrants shall issue, but upon probable cause, supported by Oath or "
            "affirmation, and particularly describing the place to be searched, and the "
            "persons or things to be seized."
        ),
        "violations": [
            "warrantless_search", "illegal_seizure", "no_probable_cause",
            "illegal_search", "illegal_vehicle_search", "unreasonable_stop"
        ],
        "severity_base": 9,
        "key_cases": [
            "Terry v. Ohio, 392 U.S. 1 (1968) — stop and frisk requires reasonable articulable suspicion",
            "Mapp v. Ohio, 367 U.S. 643 (1961) — exclusionary rule applies to states",
            "Katz v. United States, 389 U.S. 347 (1967) — reasonable expectation of privacy test",
            "Rodriguez v. United States, 575 U.S. 348 (2015) — traffic stop cannot be extended beyond its purpose",
            "Utah v. Strieff, 579 U.S. 232 (2016) — attenuation doctrine limits exclusion in some cases",
        ],
        "remedy": "Motion to Suppress — fruit of the poisonous tree doctrine (Wong Sun v. United States)",
    },
    {
        "id": "US_CONST_5A",
        "title": "5th Amendment — Self-Incrimination & Due Process",
        "category": "constitutional",
        "effective_date": "1791-12-15",
        "full_text": (
            "No person shall be held to answer for a capital, or otherwise infamous crime, "
            "unless on a presentment or indictment of a Grand Jury, except in cases arising "
            "in the land or naval forces, or in the Militia, when in actual service in time "
            "of War or public danger; nor shall any person be subject for the same offence "
            "to be twice put in jeopardy of life or limb; nor shall be compelled in any "
            "criminal case to be a witness against himself, nor be deprived of life, liberty, "
            "or property, without due process of law."
        ),
        "violations": [
            "self_incrimination_compelled", "coerced_confession", "double_jeopardy",
            "due_process_violation", "miranda_violation"
        ],
        "severity_base": 9,
        "key_cases": [
            "Miranda v. Arizona, 384 U.S. 436 (1966) — warnings required before custodial interrogation",
            "Berkemer v. McCarty, 468 U.S. 420 (1984) — Miranda applies to traffic stop arrests",
            "Colorado v. Connelly, 479 U.S. 157 (1986) — voluntariness standard for confessions",
        ],
        "remedy": "Suppression of any statements made; Motion to Dismiss if coercion shown.",
    },
    {
        "id": "US_CONST_6A",
        "title": "6th Amendment — Right to Counsel & Fair Trial",
        "category": "constitutional",
        "effective_date": "1791-12-15",
        "full_text": (
            "In all criminal prosecutions, the accused shall enjoy the right to a speedy "
            "and public trial, by an impartial jury of the State and district wherein the "
            "crime shall have been committed; to be informed of the nature and cause of the "
            "accusation; to be confronted with the witnesses against him; to have compulsory "
            "process for obtaining witnesses in his favor, and to have the Assistance of "
            "Counsel for his defence."
        ),
        "violations": [
            "right_to_counsel_denied", "right_to_counsel_delayed", "speedy_trial_violation",
            "right_to_counsel_not_invoked_respected"
        ],
        "severity_base": 9,
        "key_cases": [
            "Gideon v. Wainwright, 372 U.S. 335 (1963) — right to counsel applies to states",
            "Massiah v. United States, 377 U.S. 201 (1964) — 6th Am. right attaches at indictment",
            "Barker v. Wingo, 407 U.S. 514 (1972) — speedy trial balancing test",
        ],
        "remedy": "Motion to Dismiss; suppression of post-invocation statements.",
    },
    {
        "id": "US_CONST_8A",
        "title": "8th Amendment — Cruel and Unusual Punishment / Excessive Force",
        "category": "constitutional",
        "effective_date": "1791-12-15",
        "full_text": (
            "Excessive bail shall not be required, nor excessive fines imposed, nor cruel "
            "and unusual punishments inflicted."
        ),
        "violations": [
            "excessive_force_in_custody", "cruel_treatment", "excessive_bail",
            "punishment_before_conviction"
        ],
        "severity_base": 8,
        "key_cases": [
            "Hudson v. McMillian, 503 U.S. 1 (1992) — 8th Am. protects against excessive force by officers against prisoners",
            "Graham v. Connor, 490 U.S. 386 (1989) — pre-conviction excessive force analyzed under 4th Am. 'objective reasonableness'",
        ],
        "notes": "Pre-conviction excessive force is analyzed under the 4th Amendment (Graham v. Connor).",
    },
    {
        "id": "US_CONST_14A",
        "title": "14th Amendment — Equal Protection & Due Process",
        "category": "constitutional",
        "effective_date": "1868-07-09",
        "full_text": (
            "All persons born or naturalized in the United States, and subject to the "
            "jurisdiction thereof, are citizens of the United States and of the State wherein "
            "they reside. No State shall make or enforce any law which shall abridge the "
            "privileges or immunities of citizens of the United States; nor shall any State "
            "deprive any person of life, liberty, or property, without due process of law; "
            "nor deny to any person within its jurisdiction the equal protection of the laws."
        ),
        "violations": [
            "equal_protection_violation", "racial_profiling", "discriminatory_policing",
            "selective_enforcement", "due_process_violation"
        ],
        "severity_base": 9,
        "key_cases": [
            "Washington v. Davis, 426 U.S. 229 (1976) — discriminatory intent required for equal protection claim",
            "Village of Arlington Heights v. Metropolitan Housing Dev. Corp., 429 U.S. 252 (1977) — factors for proving discriminatory intent",
        ],
    },

    # ── Federal Civil Rights Statutes ─────────────────────────────────────────
    {
        "id": "US_42_1983",
        "title": "42 U.S.C. §1983 — Civil Action for Deprivation of Rights",
        "category": "civil_rights",
        "effective_date": "1871-04-20",
        "full_text": (
            "Every person who, under color of any statute, ordinance, regulation, custom, "
            "or usage, of any State or Territory or the District of Columbia, subjects, or "
            "causes to be subjected, any citizen of the United States or other person within "
            "the jurisdiction thereof to the deprivation of any rights, privileges, or "
            "immunities secured by the Constitution and laws, shall be liable to the party "
            "injured in an action at law, suit in equity, or other proper proceeding for "
            "redress."
        ),
        "violations": ["civil_rights_violation", "constitutional_violation_by_officer"],
        "severity_base": 9,
        "notes": (
            "Primary vehicle for suing officers individually. Qualified immunity is a defense "
            "but does not protect clearly established rights violations. "
            "Monell v. Dept. of Social Services, 436 U.S. 658 (1978): municipalities can be "
            "sued under §1983 for policy/custom/practice that causes constitutional violation."
        ),
        "key_cases": [
            "Monroe v. Pape, 365 U.S. 167 (1961) — §1983 applies to police misconduct",
            "Monell v. Dept. of Social Services, 436 U.S. 658 (1978) — municipal liability",
            "Pearson v. Callahan, 555 U.S. 223 (2009) — qualified immunity standard",
            "Harlow v. Fitzgerald, 457 U.S. 800 (1982) — objective test for qualified immunity",
        ],
    },
    {
        "id": "US_42_1985",
        "title": "42 U.S.C. §1985(3) — Conspiracy to Interfere with Civil Rights",
        "category": "civil_rights",
        "effective_date": "1871-04-20",
        "full_text": (
            "If two or more persons in any State or Territory conspire... for the purpose "
            "of depriving, either directly or indirectly, any person or class of persons of "
            "the equal protection of the laws, or of equal privileges and immunities under "
            "the laws... the party so injured or deprived may have an action for the recovery "
            "of damages occasioned by such injury or deprivation, against any one or more of "
            "the conspirators."
        ),
        "violations": ["conspiracy_to_violate_rights", "coordinated_misconduct"],
        "severity_base": 9,
        "notes": "Requires class-based animus (race, etc.) unlike Maine MCRA.",
    },
    {
        "id": "US_18_242",
        "title": "18 U.S.C. §242 — Criminal Deprivation of Rights Under Color of Law",
        "category": "civil_rights",
        "effective_date": "1866-04-09",
        "full_text": (
            "Whoever, under color of any law, statute, ordinance, regulation, or custom, "
            "willfully subjects any person in any State, Territory, Commonwealth, Possession, "
            "or District to the deprivation of any rights, privileges, or immunities secured "
            "or protected by the Constitution or laws of the United States... shall be fined "
            "under this title or imprisoned not more than one year, or both; and if bodily "
            "injury results from the acts committed in violation of this section... shall be "
            "fined under this title or imprisoned not more than ten years, or both."
        ),
        "violations": ["willful_civil_rights_violation"],
        "severity_base": 10,
        "notes": "Federal criminal statute — can be reported to FBI, U.S. Attorney, or DOJ Civil Rights Division.",
    },
    {
        "id": "US_18_1519",
        "title": "18 U.S.C. §1519 — Destruction/Falsification of Records in Federal Investigation",
        "category": "evidence",
        "effective_date": "2002-07-30",
        "full_text": (
            "Whoever knowingly alters, destroys, mutilates, conceals, covers up, falsifies, "
            "or makes a false entry in any record, document, or tangible object with the "
            "intent to impede, obstruct, or influence the investigation or proper "
            "administration of any matter within the jurisdiction of any department or agency "
            "of the United States... shall be fined under this title, imprisoned not more "
            "than 20 years, or both."
        ),
        "violations": ["evidence_tampering", "video_tampering", "record_falsification"],
        "severity_base": 10,
        "notes": "Applies when there is a federal nexus. 20-year maximum.",
    },

    # ── Miranda Rights ────────────────────────────────────────────────────────
    {
        "id": "MIRANDA_RIGHTS",
        "title": "Miranda Warning Requirements (Miranda v. Arizona, 384 U.S. 436 (1966))",
        "category": "miranda",
        "effective_date": "1966-06-13",
        "full_text": (
            "Prior to any custodial interrogation, a person must be informed: "
            "(1) You have the right to remain silent. "
            "(2) Anything you say can and will be used against you in a court of law. "
            "(3) You have the right to an attorney. "
            "(4) If you cannot afford an attorney, one will be appointed for you. "
            "Custodial interrogation means questioning initiated by law enforcement officers "
            "after a person has been taken into custody or otherwise deprived of their "
            "freedom of action in any significant way. "
            "Invocation of the right to remain silent or the right to counsel must be "
            "scrupulously honored — all questioning must cease immediately upon invocation."
        ),
        "violations": [
            "miranda_warning_not_given", "questioning_after_invocation",
            "failure_to_honor_invocation", "custodial_interrogation_without_warning"
        ],
        "severity_base": 9,
        "key_cases": [
            "Miranda v. Arizona, 384 U.S. 436 (1966)",
            "Berkemer v. McCarty, 468 U.S. 420 (1984) — applies at traffic stop if in custody",
            "Rhode Island v. Innis, 446 U.S. 291 (1980) — definition of interrogation",
            "Michigan v. Mosley, 423 U.S. 96 (1975) — must scrupulously honor right to silence",
            "Edwards v. Arizona, 451 U.S. 477 (1981) — must cease questioning when counsel invoked",
        ],
        "remedy": "Suppression of all statements made during un-Mirandized custodial interrogation.",
    },

    # ── Brady Disclosure ──────────────────────────────────────────────────────
    {
        "id": "BRADY_RULE",
        "title": "Brady v. Maryland, 373 U.S. 83 (1963) — Exculpatory Evidence Disclosure",
        "category": "evidence",
        "effective_date": "1963-05-13",
        "full_text": (
            "The prosecution must disclose to the defense all material exculpatory evidence "
            "in its possession or accessible to it (including evidence held by law enforcement). "
            "Evidence is 'material' if there is a reasonable probability that, had the evidence "
            "been disclosed to the defense, the result of the proceeding would have been different. "
            "Brady material includes: evidence undermining witness credibility (Giglio), "
            "evidence establishing a defense, evidence contradicting police reports, "
            "video footage, police personnel records with misconduct history."
        ),
        "violations": [
            "brady_violation", "failure_to_disclose_exculpatory_evidence",
            "suppression_of_evidence", "giglio_violation"
        ],
        "severity_base": 10,
        "key_cases": [
            "Brady v. Maryland, 373 U.S. 83 (1963)",
            "Giglio v. United States, 405 U.S. 150 (1972) — impeachment evidence required",
            "Kyles v. Whitley, 514 U.S. 419 (1995) — prosecution must learn of police evidence",
            "Strickler v. Greene, 527 U.S. 263 (1999) — materiality standard",
        ],
        "notes": "Video footage of the incident is Brady material. Request it immediately in writing.",
    },

    # ── Excessive Force Standard ──────────────────────────────────────────────
    {
        "id": "GRAHAM_STANDARD",
        "title": "Graham v. Connor — Objective Reasonableness Test for Excessive Force",
        "category": "use_of_force",
        "effective_date": "1989-05-15",
        "full_text": (
            "Determining whether force used by police was excessive requires objective "
            "reasonableness analysis under the 4th Amendment. Relevant factors: "
            "(1) The severity of the crime at issue; "
            "(2) Whether the suspect poses an immediate threat to the safety of officers or others; "
            "(3) Whether the suspect is actively resisting arrest or attempting to evade by flight. "
            "The 'reasonableness' inquiry is objective — judged from the perspective of a "
            "reasonable officer on the scene, not in hindsight. The calculus of reasonableness "
            "must embody allowance for the fact that police officers are often forced to make "
            "split-second judgments."
        ),
        "violations": ["excessive_force", "unjustified_force"],
        "severity_base": 8,
        "key_cases": [
            "Graham v. Connor, 490 U.S. 386 (1989)",
            "Tennessee v. Garner, 471 U.S. 1 (1985) — deadly force against fleeing felon",
        ],
    },
]
