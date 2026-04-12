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
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
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
