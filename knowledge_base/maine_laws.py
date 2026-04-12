"""
Maine State Laws relevant to police conduct, civil rights, and criminal procedure.
Statutes include effective dates so analysis can be anchored to the correct law
version for the date of the incident.

Sources:
  Maine Revised Statutes (MRS) — legislature.maine.gov
  Maine Constitution — legislature.maine.gov
"""

from datetime import date
from typing import List, Dict


MAINE_LAWS: List[Dict] = [

    # ── Maine Constitution ────────────────────────────────────────────────────
    {
        "id": "ME_CONST_ART1_SEC5",
        "title": "Maine Constitution Art. I §5 — Unreasonable Searches",
        "category": "constitutional",
        "effective_date": "1820-03-15",
        "full_text": (
            "The people shall be secure in their persons, houses, papers and possessions "
            "from all unreasonable searches and seizures; and no warrant to search any "
            "place, or seize any person or thing, shall issue without a special designation "
            "of the place to be searched, and the person or thing to be seized, nor without "
            "probable cause — supported by oath or affirmation."
        ),
        "violations": ["warrantless_search", "illegal_seizure", "no_probable_cause"],
        "severity_base": 9,
        "notes": "Parallel to 4th Amendment but interpreted independently by Maine courts."
    },
    {
        "id": "ME_CONST_ART1_SEC6",
        "title": "Maine Constitution Art. I §6 — Rights of Accused",
        "category": "constitutional",
        "effective_date": "1820-03-15",
        "full_text": (
            "In all criminal prosecutions, the accused shall have the right to be heard "
            "by himself and his counsel, or either, at his election; to demand the nature "
            "and cause of the accusation, and to have a copy thereof; to meet the witnesses "
            "against him face to face; to have compulsory process for obtaining witnesses in "
            "his favor; to have a speedy, public and impartial trial, and, except in trials "
            "by the court, the accused shall not be compelled to give evidence against himself."
        ),
        "violations": ["right_to_counsel_denied", "self_incrimination_compelled", "speedy_trial_violation"],
        "severity_base": 9,
        "notes": "Broader right against self-incrimination than 5th Amendment in some cases."
    },

    # ── Maine Civil Rights Act ────────────────────────────────────────────────
    {
        "id": "ME_MCRA_4681",
        "title": "5 M.R.S.A. §4681 — Maine Civil Rights Act: Prohibition",
        "category": "civil_rights",
        "effective_date": "1993-10-01",
        "full_text": (
            "A person may not, whether or not acting under color of law, by physical force "
            "or violence or the threat of physical force or violence, intentionally interfere "
            "with, or attempt to intentionally interfere with, or intimidate or attempt to "
            "intimidate any other person in the exercise or enjoyment of that person's rights "
            "secured by the United States Constitution or the laws of the United States, or "
            "rights secured by the Constitution of Maine or laws of the State of Maine."
        ),
        "violations": ["civil_rights_violation", "intimidation", "interference_with_rights"],
        "severity_base": 8,
        "notes": (
            "Creates a private right of action; plaintiff does not need to prove race or "
            "class-based animus unlike federal §1985."
        ),
    },
    {
        "id": "ME_MCRA_4682",
        "title": "5 M.R.S.A. §4682 — Maine Civil Rights Act: Civil Action",
        "category": "civil_rights",
        "effective_date": "1993-10-01",
        "full_text": (
            "Any person who interferes or attempts to interfere by physical force or violence "
            "or by threat of physical force or violence with the exercise or enjoyment by any "
            "other person of rights secured by the United States Constitution or the laws of "
            "the United States or rights secured by the Maine Constitution or laws of the "
            "State, shall be liable in a civil action for damages and for injunctive and other "
            "equitable relief, including reasonable attorney's fees."
        ),
        "violations": ["civil_rights_violation"],
        "severity_base": 8,
        "notes": "Attorney's fees available — important for pro se litigants pursuing post-judgment counsel."
    },

    # ── Use of Force ──────────────────────────────────────────────────────────
    {
        "id": "ME_17A_107",
        "title": "17-A M.R.S.A. §107 — Use of Force in Law Enforcement",
        "category": "use_of_force",
        "effective_date": "1976-05-01",
        "amendments": [
            {"date": "2021-06-29", "summary": "LD 1884: Added duty to intervene; tightened deadly force standard."}
        ],
        "full_text": (
            "(1) A law enforcement officer is justified in using a degree of nondeadly force "
            "upon another person when and to the extent that the officer reasonably believes "
            "it necessary to: A. Effect an arrest or prevent the escape from custody of a "
            "person the officer reasonably believes has committed a crime, unless the officer "
            "knows that the arrest or custody is illegal; or B. Defend the officer or a 3rd "
            "person from what the officer reasonably believes to be the imminent use of "
            "unlawful nondeadly force. "
            "(2) The use of deadly force by a law enforcement officer is justified only when "
            "the officer reasonably believes that: A. The person to be arrested has committed "
            "or attempted to commit a crime involving the use of force or violence or is "
            "attempting to escape by the use of a deadly weapon; and B. The officer reasonably "
            "believes that the person poses a significant threat of death or serious bodily harm "
            "to the officer or others if apprehension is delayed. "
            "(3) [Added 2021] A law enforcement officer who witnesses another officer using "
            "excessive force has a duty to intervene to stop or prevent the use of excessive force."
        ),
        "violations": ["excessive_force", "unjustified_use_of_force", "deadly_force_unjustified", "failure_to_intervene"],
        "severity_base": 9,
        "notes": "2021 amendment added duty-to-intervene — check incident date to determine which version applies."
    },
    {
        "id": "ME_17A_108",
        "title": "17-A M.R.S.A. §108 — Use of Force: General Justification",
        "category": "use_of_force",
        "effective_date": "1976-05-01",
        "full_text": (
            "(1) A person is justified in using a degree of force upon another that the person "
            "reasonably believes to be necessary to defend the person or a 3rd person from what "
            "the person reasonably believes to be the imminent use of unlawful, nondeadly force. "
            "A person may not use deadly force in self-defense if the person can avoid it with "
            "complete safety by retreating."
        ),
        "violations": ["self_defense_interference"],
        "severity_base": 6,
        "notes": "Relevant when officer prevents lawful self-defense."
    },

    # ── Arrest Procedures ─────────────────────────────────────────────────────
    {
        "id": "ME_15_821",
        "title": "15 M.R.S.A. §821 — Arrest: Definition",
        "category": "arrest_procedure",
        "effective_date": "1965-01-01",
        "full_text": (
            "Arrest is the taking of a person into custody in order that the person may be "
            "forthcoming to answer for the commission of a crime."
        ),
        "violations": ["unlawful_arrest", "illegal_detention"],
        "severity_base": 7,
        "notes": "Basis for challenging whether an arrest was legal."
    },
    {
        "id": "ME_15_823",
        "title": "15 M.R.S.A. §823 — Arrest Without Warrant",
        "category": "arrest_procedure",
        "effective_date": "1965-01-01",
        "full_text": (
            "A law enforcement officer may arrest a person without a warrant if the officer "
            "has probable cause to believe that the person has committed or is committing: "
            "A. A crime; or B. A civil violation that is punishable by a fine of more than $500. "
            "An arrest without a warrant requires that the officer have probable cause — a "
            "reasonable belief based on articulable facts that the person committed the offense."
        ),
        "violations": ["arrest_without_probable_cause", "unlawful_arrest"],
        "severity_base": 8,
        "notes": "Key statute for challenging warrantless arrests."
    },
    {
        "id": "ME_15_1091",
        "title": "15 M.R.S.A. §1091 — Search Warrant Requirements",
        "category": "search_seizure",
        "effective_date": "1965-01-01",
        "full_text": (
            "A search warrant may be issued by a judge of any court of record authorizing "
            "the search of a designated place when the applicant demonstrates probable cause "
            "to believe that the property subject to seizure is located in the place designated. "
            "The warrant must specifically describe the place to be searched and the items "
            "to be seized. General warrants are prohibited."
        ),
        "violations": ["illegal_search", "warrantless_search", "general_warrant"],
        "severity_base": 9,
        "notes": "Fruit of the poisonous tree doctrine applies — suppression motion basis."
    },

    # ── Vehicle Stops ─────────────────────────────────────────────────────────
    {
        "id": "ME_29A_2104",
        "title": "29-A M.R.S.A. §2104 — Roadblock and Motor Vehicle Stop Standards",
        "category": "vehicle_stop",
        "effective_date": "1995-01-01",
        "full_text": (
            "A law enforcement officer may stop a motor vehicle only when the officer has "
            "an articulable suspicion that a violation of a traffic law has occurred, is "
            "occurring, or is about to occur. A stop based solely on a hunch, profile, or "
            "generalized suspicion of criminal activity is not lawful."
        ),
        "violations": ["unlawful_vehicle_stop", "pretextual_stop", "racial_profiling"],
        "severity_base": 7,
        "notes": "Must have reasonable articulable suspicion — mere hunch is insufficient."
    },

    # ── Recording Police ──────────────────────────────────────────────────────
    {
        "id": "ME_15_709",
        "title": "15 M.R.S.A. §709 — Interception of Oral/Electronic Communications",
        "category": "recording",
        "effective_date": "1977-01-01",
        "full_text": (
            "Maine is a one-party consent state for recordings of communications. A person "
            "may record a conversation to which they are a party without the consent of other "
            "parties. Recording by a bystander in a public space is protected under the First "
            "Amendment and courts have held that there is a First Amendment right to record "
            "police performing their duties in public."
        ),
        "violations": ["unlawful_seizure_of_recording", "interference_with_recording"],
        "severity_base": 6,
        "notes": "Citizen has a right to record police in public; seizing a recording device may be unconstitutional."
    },

    # ── Police Body Camera / Dashcam Requirements ─────────────────────────────
    {
        "id": "ME_25_2803B",
        "title": "25 M.R.S.A. §2803-B — Law Enforcement Policy Requirements",
        "category": "policy_procedure",
        "effective_date": "2001-09-29",
        "amendments": [
            {"date": "2021-06-29", "summary": "LD 1640: Added mandatory body-worn camera policies for agencies."}
        ],
        "full_text": (
            "Each law enforcement agency shall adopt written policies governing the conduct "
            "of its officers. Required policies include: use of force; high-speed pursuit; "
            "domestic violence response; civil rights; bias-free policing; body-worn cameras "
            "(if cameras are used); and electronic surveillance. "
            "Agencies that deploy body-worn cameras must have a written retention policy and "
            "must retain footage for at least 180 days (or longer if subject to a legal hold). "
            "Officers must activate cameras during: traffic stops; foot pursuits; arrests; "
            "any police-civilian encounter that escalates; serving search/arrest warrants. "
            "Failure to activate camera as required is a policy violation and may be an "
            "adverse inference in litigation."
        ),
        "violations": ["body_cam_not_activated", "body_cam_policy_violation", "footage_not_retained"],
        "severity_base": 7,
        "notes": (
            "Pre-2021 incidents: no mandatory body-cam law. Post-2021: failure to activate "
            "is a documented policy violation. Always check agency-specific policy."
        ),
    },

    # ── Maine Unlawful Detention ───────────────────────────────────────────────
    {
        "id": "ME_17A_351",
        "title": "17-A M.R.S.A. §351 — Criminal Restraint / Unlawful Detention",
        "category": "detention",
        "effective_date": "1976-05-01",
        "full_text": (
            "A person is guilty of criminal restraint if, knowing the restraint is unlawful "
            "and with the intent to prevent liberation, they restrain another person. "
            "Law enforcement officers acting within their lawful authority are excepted, but "
            "an officer acting without authority or probable cause may be liable."
        ),
        "violations": ["unlawful_detention", "false_imprisonment"],
        "severity_base": 7,
    },

    # ── Unlawful Discrimination ───────────────────────────────────────────────
    {
        "id": "ME_5_4551",
        "title": "5 M.R.S.A. §4551 — Maine Human Rights Act",
        "category": "discrimination",
        "effective_date": "1972-01-01",
        "full_text": (
            "It is unlawful to discriminate against any person because of race, color, sex, "
            "sexual orientation, physical or mental disability, religion, ancestry, or national "
            "origin in the provision of or access to public services, including law enforcement "
            "services. Discriminatory policing based on any protected characteristic violates "
            "this Act."
        ),
        "violations": ["racial_profiling", "discriminatory_policing", "discrimination"],
        "severity_base": 8,
    },

    # ── Evidence Tampering / Destruction ──────────────────────────────────────
    {
        "id": "ME_17A_453",
        "title": "17-A M.R.S.A. §453 — Tampering with Physical Evidence",
        "category": "evidence",
        "effective_date": "1976-05-01",
        "full_text": (
            "A person is guilty of tampering with physical evidence if, believing that an "
            "official proceeding is about to be instituted or is pending, the person: "
            "A. Destroys, mutilates, conceals, removes or alters physical evidence with "
            "intent to impair its authenticity or availability in the official proceeding; or "
            "B. Makes, presents or uses physical evidence with knowledge that it is false and "
            "with intent to mislead a public servant who is engaged in an official proceeding."
        ),
        "violations": ["evidence_tampering", "video_tampering", "destruction_of_evidence"],
        "severity_base": 10,
    },

    # ── Perjury / False Reports ───────────────────────────────────────────────
    {
        "id": "ME_17A_451",
        "title": "17-A M.R.S.A. §451 — Perjury",
        "category": "false_statements",
        "effective_date": "1976-05-01",
        "full_text": (
            "A person is guilty of perjury if, in any official proceeding, the person makes "
            "a false statement under oath or affirmation, or swears or affirms the truth of "
            "a false statement previously made, when the statement is material and the person "
            "does not believe it to be true."
        ),
        "violations": ["false_police_report", "false_affidavit", "perjury"],
        "severity_base": 9,
    },
    {
        "id": "ME_17A_452",
        "title": "17-A M.R.S.A. §452 — False Swearing / False Report",
        "category": "false_statements",
        "effective_date": "1976-05-01",
        "full_text": (
            "A person is guilty of false swearing if, in a governmental matter or official "
            "proceeding, the person intentionally makes a false statement under oath or "
            "affirmation which is material to the proceeding and which the person does not "
            "believe to be true. A law enforcement officer who files a false police report "
            "may be charged under this provision."
        ),
        "violations": ["false_police_report", "false_affidavit"],
        "severity_base": 9,
    },
]


def get_maine_laws_for_date(incident_date_str: str) -> List[Dict]:
    """
    Return Maine laws that were in effect on the date of the incident.
    Respects amendment dates to avoid citing a law not yet enacted.
    """
    try:
        incident_date = date.fromisoformat(incident_date_str)
    except (ValueError, TypeError):
        # If date unknown, return all laws (most recent version)
        return MAINE_LAWS

    applicable = []
    for law in MAINE_LAWS:
        try:
            eff = date.fromisoformat(law["effective_date"])
        except (ValueError, KeyError):
            eff = date(1820, 1, 1)  # Default to statehood

        if eff <= incident_date:
            law_copy = dict(law)
            # Strip amendments not yet in effect
            if "amendments" in law:
                applicable_amendments = [
                    a for a in law["amendments"]
                    if date.fromisoformat(a["date"]) <= incident_date
                ]
                law_copy["amendments"] = applicable_amendments
            applicable.append(law_copy)

    return applicable
