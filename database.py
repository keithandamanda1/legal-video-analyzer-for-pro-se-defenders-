"""
Persistent SQLite database layer.
Memory NEVER resets automatically — only via explicit admin action.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import config


def get_db() -> sqlite3.Connection:
    """Return a thread-local database connection with row_factory set."""
    db_path = Path(config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    conn = get_db()
    try:
        conn.executescript("""
        -- ── Cases ────────────────────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS cases (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            case_number TEXT,
            defendant_name TEXT,
            incident_date  TEXT,
            arrest_date    TEXT,
            court          TEXT,
            county         TEXT,
            charge         TEXT,
            description    TEXT,
            status         TEXT DEFAULT 'active',
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ── Evidence files ────────────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS evidence (
            id            TEXT PRIMARY KEY,
            case_id       TEXT NOT NULL,
            file_path     TEXT NOT NULL,
            file_type     TEXT,
            original_name TEXT,
            file_size     INTEGER,
            duration      REAL,
            upload_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analyzed      INTEGER DEFAULT 0,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );

        -- ── Analysis runs ─────────────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS analyses (
            id              TEXT PRIMARY KEY,
            evidence_id     TEXT NOT NULL,
            case_id         TEXT NOT NULL,
            analysis_type   TEXT DEFAULT 'full',
            status          TEXT DEFAULT 'pending',
            progress        INTEGER DEFAULT 0,
            results_json    TEXT,
            win_probability REAL,
            error_message   TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at    TIMESTAMP,
            FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE,
            FOREIGN KEY (case_id)    REFERENCES cases(id)    ON DELETE CASCADE
        );

        -- ── Individual violation findings ─────────────────────────────────────
        CREATE TABLE IF NOT EXISTS violations (
            id               TEXT PRIMARY KEY,
            analysis_id      TEXT NOT NULL,
            case_id          TEXT NOT NULL,
            violation_type   TEXT,
            category         TEXT,
            severity         INTEGER,
            confidence       TEXT,
            description      TEXT,
            timestamp_secs   REAL,
            timestamp_label  TEXT,
            law_reference    TEXT,
            law_title        TEXT,
            law_text         TEXT,
            recommendation   TEXT,
            is_illegal       INTEGER DEFAULT 0,
            is_red_flag      INTEGER DEFAULT 0,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        );

        -- ── Metadata findings ─────────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS metadata_findings (
            id          TEXT PRIMARY KEY,
            evidence_id TEXT NOT NULL,
            case_id     TEXT NOT NULL,
            key         TEXT,
            value       TEXT,
            flag        TEXT,
            severity    INTEGER DEFAULT 0,
            note        TEXT,
            FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE
        );

        -- ── Generated documents ───────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS documents (
            id            TEXT PRIMARY KEY,
            case_id       TEXT NOT NULL,
            document_type TEXT,
            title         TEXT,
            file_path     TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );

        -- ── Case notes (never deleted unless user says so) ────────────────────
        CREATE TABLE IF NOT EXISTS case_notes (
            id         TEXT PRIMARY KEY,
            case_id    TEXT NOT NULL,
            note       TEXT NOT NULL,
            author     TEXT DEFAULT 'User',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );

        -- ══════════════════════════════════════════════════════════════════════
        -- HOUSING CASE DASHBOARD  (H25-0389 / H25-0395 — FHA federal track)
        -- ══════════════════════════════════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS housing_evidence (
            id            TEXT PRIMARY KEY,
            event_date    TEXT,
            category      TEXT,   -- 'fact','email','foaa','denial','document','testimony'
            title         TEXT NOT NULL,
            description   TEXT,
            source        TEXT,
            exhibit_label TEXT,
            verified      INTEGER DEFAULT 0,
            flagged       INTEGER DEFAULT 0,
            flag_reason   TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS housing_emails (
            id            TEXT PRIMARY KEY,
            sent_date     TEXT,
            sender        TEXT,
            recipient     TEXT,
            subject       TEXT NOT NULL,
            summary       TEXT,
            exhibit_label TEXT,
            produced      INTEGER DEFAULT 0,
            missing       INTEGER DEFAULT 0,
            notes         TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS housing_denial_changes (
            id              TEXT PRIMARY KEY,
            change_date     TEXT,
            reason_before   TEXT,
            reason_after    TEXT,
            source_document TEXT,
            significance    TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS housing_deadlines (
            id          TEXT PRIMARY KEY,
            deadline_date TEXT NOT NULL,
            label       TEXT NOT NULL,
            description TEXT,
            authority   TEXT,
            critical    INTEGER DEFAULT 0,
            met         INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ══════════════════════════════════════════════════════════════════════
        -- PCR PETITION ORGANIZER  (CR-2018-03023, 15 M.R.S. §§ 2121-2132)
        -- ══════════════════════════════════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS pcr_evidence (
            id            TEXT PRIMARY KEY,
            event_date    TEXT,
            category      TEXT,   -- 'stop','chain_of_custody','phone','plea','newly_discovered','brady'
            ground_number INTEGER,
            title         TEXT NOT NULL,
            description   TEXT,
            source        TEXT,
            exhibit_label TEXT,
            law_reference TEXT,
            status        TEXT DEFAULT 'documented',  -- 'documented','obtained','missing','needed'
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pcr_contradictions (
            id              TEXT PRIMARY KEY,
            contradiction_date TEXT,
            ground_number   INTEGER,
            item_a_label    TEXT,
            item_a_text     TEXT,
            item_b_label    TEXT,
            item_b_text     TEXT,
            significance    TEXT,
            law_reference   TEXT,
            resolution_needed TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pcr_exhibits (
            id            TEXT PRIMARY KEY,
            exhibit_label TEXT NOT NULL,
            title         TEXT NOT NULL,
            description   TEXT,
            source        TEXT,
            ground_numbers TEXT,
            obtained      INTEGER DEFAULT 0,
            filed         INTEGER DEFAULT 0,
            notes         TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pcr_notes (
            id         TEXT PRIMARY KEY,
            note       TEXT NOT NULL,
            ground_num INTEGER,
            author     TEXT DEFAULT 'User',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    finally:
        conn.close()


# ── Helper functions ──────────────────────────────────────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())


def now_str() -> str:
    return datetime.utcnow().isoformat()


# ── Case CRUD ─────────────────────────────────────────────────────────────────

def create_case(name: str, **kwargs) -> dict:
    cid = new_id()
    fields = {
        "id": cid, "name": name,
        "case_number": kwargs.get("case_number"),
        "defendant_name": kwargs.get("defendant_name"),
        "incident_date": kwargs.get("incident_date"),
        "arrest_date": kwargs.get("arrest_date"),
        "court": kwargs.get("court"),
        "county": kwargs.get("county"),
        "charge": kwargs.get("charge"),
        "description": kwargs.get("description"),
        "status": "active",
    }
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO cases (id,name,case_number,defendant_name,incident_date,
               arrest_date,court,county,charge,description,status)
               VALUES (:id,:name,:case_number,:defendant_name,:incident_date,
               :arrest_date,:court,:county,:charge,:description,:status)""",
            fields
        )
        conn.commit()
    finally:
        conn.close()
    return fields


def get_case(case_id: str) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_cases() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM cases ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_case(case_id: str, **kwargs) -> None:
    kwargs["updated_at"] = now_str()
    kwargs["id"] = case_id
    sets = ", ".join(f"{k}=:{k}" for k in kwargs if k != "id")
    conn = get_db()
    try:
        conn.execute(f"UPDATE cases SET {sets} WHERE id=:id", kwargs)
        conn.commit()
    finally:
        conn.close()


def delete_case(case_id: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM cases WHERE id=?", (case_id,))
        conn.commit()
    finally:
        conn.close()


# ── Evidence CRUD ─────────────────────────────────────────────────────────────

def add_evidence(case_id: str, file_path: str, **kwargs) -> dict:
    eid = new_id()
    fields = {
        "id": eid, "case_id": case_id, "file_path": file_path,
        "file_type": kwargs.get("file_type"),
        "original_name": kwargs.get("original_name"),
        "file_size": kwargs.get("file_size"),
        "duration": kwargs.get("duration"),
    }
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO evidence (id,case_id,file_path,file_type,original_name,file_size,duration)
               VALUES (:id,:case_id,:file_path,:file_type,:original_name,:file_size,:duration)""",
            fields
        )
        conn.commit()
    finally:
        conn.close()
    return fields


def get_evidence(evidence_id: str) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_evidence(case_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM evidence WHERE case_id=? ORDER BY upload_date", (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Analysis CRUD ─────────────────────────────────────────────────────────────

def create_analysis(case_id: str, evidence_id: str, analysis_type: str = "full") -> dict:
    aid = new_id()
    fields = {
        "id": aid, "case_id": case_id, "evidence_id": evidence_id,
        "analysis_type": analysis_type, "status": "pending", "progress": 0
    }
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO analyses (id,case_id,evidence_id,analysis_type,status,progress)
               VALUES (:id,:case_id,:evidence_id,:analysis_type,:status,:progress)""",
            fields
        )
        conn.commit()
    finally:
        conn.close()
    return fields


def update_analysis(analysis_id: str, **kwargs) -> None:
    if "results_json" in kwargs and not isinstance(kwargs["results_json"], str):
        kwargs["results_json"] = json.dumps(kwargs["results_json"])
    kwargs["id"] = analysis_id
    sets = ", ".join(f"{k}=:{k}" for k in kwargs if k != "id")
    conn = get_db()
    try:
        conn.execute(f"UPDATE analyses SET {sets} WHERE id=:id", kwargs)
        conn.commit()
    finally:
        conn.close()


def get_analysis(analysis_id: str) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("results_json"):
            try:
                d["results"] = json.loads(d["results_json"])
            except Exception:
                d["results"] = {}
        return d
    finally:
        conn.close()


def list_analyses(case_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM analyses WHERE case_id=? ORDER BY created_at DESC", (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Violations ────────────────────────────────────────────────────────────────

def save_violation(analysis_id: str, case_id: str, data: dict) -> str:
    vid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO violations
               (id,analysis_id,case_id,violation_type,category,severity,confidence,
                description,timestamp_secs,timestamp_label,law_reference,law_title,
                law_text,recommendation,is_illegal,is_red_flag)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                vid, analysis_id, case_id,
                data.get("violation_type"), data.get("category"),
                data.get("severity", 0), data.get("confidence", "low"),
                data.get("description"), data.get("timestamp_secs"),
                data.get("timestamp_label"), data.get("law_reference"),
                data.get("law_title"), data.get("law_text"),
                data.get("recommendation"),
                1 if data.get("is_illegal") else 0,
                1 if data.get("is_red_flag") else 0,
            )
        )
        conn.commit()
    finally:
        conn.close()
    return vid


def get_violations(analysis_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM violations WHERE analysis_id=? ORDER BY timestamp_secs",
            (analysis_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_case_violations(case_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM violations WHERE case_id=? ORDER BY severity DESC, timestamp_secs",
            (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Metadata findings ─────────────────────────────────────────────────────────

def save_metadata_finding(evidence_id: str, case_id: str, key: str,
                          value: str, flag: str = None, severity: int = 0, note: str = None):
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO metadata_findings (id,evidence_id,case_id,key,value,flag,severity,note)
               VALUES (?,?,?,?,?,?,?,?)""",
            (new_id(), evidence_id, case_id, key, value, flag, severity, note)
        )
        conn.commit()
    finally:
        conn.close()


def get_metadata_findings(evidence_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM metadata_findings WHERE evidence_id=? ORDER BY severity DESC",
            (evidence_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Documents ─────────────────────────────────────────────────────────────────

def save_document(case_id: str, doc_type: str, title: str, file_path: str) -> str:
    did = new_id()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO documents (id,case_id,document_type,title,file_path) VALUES (?,?,?,?,?)",
            (did, case_id, doc_type, title, file_path)
        )
        conn.commit()
    finally:
        conn.close()
    return did


def list_documents(case_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM documents WHERE case_id=? ORDER BY created_at DESC", (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_document(doc_id: str) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ── Case notes ────────────────────────────────────────────────────────────────

def add_note(case_id: str, note: str, author: str = "User") -> str:
    nid = new_id()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO case_notes (id,case_id,note,author) VALUES (?,?,?,?)",
            (nid, case_id, note, author)
        )
        conn.commit()
    finally:
        conn.close()
    return nid


def get_notes(case_id: str) -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM case_notes WHERE case_id=? ORDER BY created_at", (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# HOUSING DASHBOARD — H25-0389 / H25-0395
# ══════════════════════════════════════════════════════════════════════════════

def housing_add_evidence(event_date, category, title, description="", source="",
                         exhibit_label="", verified=0, flagged=0, flag_reason="") -> str:
    eid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO housing_evidence
               (id,event_date,category,title,description,source,exhibit_label,
                verified,flagged,flag_reason)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (eid, event_date, category, title, description, source,
             exhibit_label, verified, flagged, flag_reason)
        )
        conn.commit()
    finally:
        conn.close()
    return eid


def housing_list_evidence(category=None) -> list:
    conn = get_db()
    try:
        if category:
            rows = conn.execute(
                "SELECT * FROM housing_evidence WHERE category=? ORDER BY event_date, created_at",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM housing_evidence ORDER BY event_date, created_at"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def housing_delete_evidence(eid: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM housing_evidence WHERE id=?", (eid,))
        conn.commit()
    finally:
        conn.close()


def housing_add_email(sent_date, sender, recipient, subject, summary="",
                      exhibit_label="", produced=0, missing=0, notes="") -> str:
    eid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO housing_emails
               (id,sent_date,sender,recipient,subject,summary,exhibit_label,
                produced,missing,notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (eid, sent_date, sender, recipient, subject, summary,
             exhibit_label, produced, missing, notes)
        )
        conn.commit()
    finally:
        conn.close()
    return eid


def housing_list_emails() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM housing_emails ORDER BY sent_date, created_at"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def housing_delete_email(eid: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM housing_emails WHERE id=?", (eid,))
        conn.commit()
    finally:
        conn.close()


def housing_add_denial_change(change_date, reason_before, reason_after,
                               source_document="", significance="") -> str:
    did = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO housing_denial_changes
               (id,change_date,reason_before,reason_after,source_document,significance)
               VALUES (?,?,?,?,?,?)""",
            (did, change_date, reason_before, reason_after, source_document, significance)
        )
        conn.commit()
    finally:
        conn.close()
    return did


def housing_list_denial_changes() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM housing_denial_changes ORDER BY change_date"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def housing_add_deadline(deadline_date, label, description="",
                          authority="", critical=0, met=0) -> str:
    did = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO housing_deadlines
               (id,deadline_date,label,description,authority,critical,met)
               VALUES (?,?,?,?,?,?,?)""",
            (did, deadline_date, label, description, authority, critical, met)
        )
        conn.commit()
    finally:
        conn.close()
    return did


def housing_list_deadlines() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM housing_deadlines ORDER BY deadline_date"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def housing_seeded() -> bool:
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM housing_evidence").fetchone()[0]
        return count > 0
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# PCR ORGANIZER — CR-2018-03023
# ══════════════════════════════════════════════════════════════════════════════

def pcr_add_evidence(event_date, category, ground_number, title,
                     description="", source="", exhibit_label="",
                     law_reference="", status="documented") -> str:
    eid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO pcr_evidence
               (id,event_date,category,ground_number,title,description,
                source,exhibit_label,law_reference,status)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (eid, event_date, category, ground_number, title, description,
             source, exhibit_label, law_reference, status)
        )
        conn.commit()
    finally:
        conn.close()
    return eid


def pcr_list_evidence(ground_number=None) -> list:
    conn = get_db()
    try:
        if ground_number is not None:
            rows = conn.execute(
                "SELECT * FROM pcr_evidence WHERE ground_number=? ORDER BY event_date, created_at",
                (ground_number,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM pcr_evidence ORDER BY event_date, created_at"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def pcr_delete_evidence(eid: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM pcr_evidence WHERE id=?", (eid,))
        conn.commit()
    finally:
        conn.close()


def pcr_add_contradiction(contradiction_date, ground_number, item_a_label, item_a_text,
                           item_b_label, item_b_text, significance="",
                           law_reference="", resolution_needed="") -> str:
    cid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO pcr_contradictions
               (id,contradiction_date,ground_number,item_a_label,item_a_text,
                item_b_label,item_b_text,significance,law_reference,resolution_needed)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (cid, contradiction_date, ground_number, item_a_label, item_a_text,
             item_b_label, item_b_text, significance, law_reference, resolution_needed)
        )
        conn.commit()
    finally:
        conn.close()
    return cid


def pcr_list_contradictions(ground_number=None) -> list:
    conn = get_db()
    try:
        if ground_number is not None:
            rows = conn.execute(
                "SELECT * FROM pcr_contradictions WHERE ground_number=? ORDER BY contradiction_date",
                (ground_number,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM pcr_contradictions ORDER BY ground_number, contradiction_date"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def pcr_delete_contradiction(cid: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM pcr_contradictions WHERE id=?", (cid,))
        conn.commit()
    finally:
        conn.close()


def pcr_add_exhibit(exhibit_label, title, description="", source="",
                    ground_numbers="", obtained=0, filed=0, notes="") -> str:
    eid = new_id()
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO pcr_exhibits
               (id,exhibit_label,title,description,source,ground_numbers,obtained,filed,notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (eid, exhibit_label, title, description, source,
             ground_numbers, obtained, filed, notes)
        )
        conn.commit()
    finally:
        conn.close()
    return eid


def pcr_list_exhibits() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM pcr_exhibits ORDER BY exhibit_label"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def pcr_delete_exhibit(eid: str) -> None:
    conn = get_db()
    try:
        conn.execute("DELETE FROM pcr_exhibits WHERE id=?", (eid,))
        conn.commit()
    finally:
        conn.close()


def pcr_add_note(note: str, ground_num: int = None, author: str = "User") -> str:
    nid = new_id()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO pcr_notes (id,note,ground_num,author) VALUES (?,?,?,?)",
            (nid, note, ground_num, author)
        )
        conn.commit()
    finally:
        conn.close()
    return nid


def pcr_list_notes() -> list:
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM pcr_notes ORDER BY created_at"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def pcr_seeded() -> bool:
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM pcr_evidence").fetchone()[0]
        return count > 0
    finally:
        conn.close()
