"""
Configuration for Legal Video Analyzer
Reads from .env file or environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")


class Config:
    # ── Anthropic / Claude ────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
    # Use the most capable model for legal video analysis
    CLAUDE_MODEL: str = os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")

    # ── Flask ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "CHANGE-THIS-SECRET-KEY-IN-PROD")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    HOST: str = os.environ.get("HOST", "127.0.0.1")
    PORT: int = int(os.environ.get("PORT", "5000"))

    # ── Storage paths ─────────────────────────────────────────────────────────
    DATABASE_PATH: str = str(BASE_DIR / "data" / "cases.db")
    UPLOAD_FOLDER: str = str(BASE_DIR / "data" / "uploads")
    CASES_FOLDER: str = str(BASE_DIR / "data" / "cases")
    DOCUMENTS_FOLDER: str = str(BASE_DIR / "data" / "documents")
    EXPORTS_FOLDER: str = str(BASE_DIR / "data" / "exports")

    # ── Video analysis ────────────────────────────────────────────────────────
    # Seconds between frame extractions (lower = more thorough, higher API cost)
    VIDEO_FRAME_INTERVAL: int = int(os.environ.get("VIDEO_FRAME_INTERVAL", "5"))
    # Max frames to send per Claude API call
    FRAMES_PER_BATCH: int = int(os.environ.get("FRAMES_PER_BATCH", "4"))
    # Max image dimension for frames sent to API (keeps cost manageable)
    MAX_FRAME_SIZE: int = int(os.environ.get("MAX_FRAME_SIZE", "1024"))
    # Max upload size: 4 GB
    MAX_CONTENT_LENGTH: int = 4 * 1024 * 1024 * 1024

    # ── Jurisdiction ──────────────────────────────────────────────────────────
    STATE: str = os.environ.get("STATE", "Maine")
    STATE_CODE: str = "ME"


config = Config()
