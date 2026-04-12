"""
Configuration for Legal Video Analyzer
Reads from .env file or environment variables.

Supports two API providers:
  - Direct Anthropic (api.anthropic.com) — set ANTHROPIC_API_KEY
  - OpenRouter (openrouter.ai)           — set OPENROUTER_API_KEY
Auto-detects which key is present and configures the client accordingly.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")


class Config:
    # ── API keys ──────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str  = os.environ.get("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")

    # ── Auto-detect provider ──────────────────────────────────────────────────
    @property
    def active_api_key(self) -> str:
        """Return whichever key is configured (Anthropic takes priority)."""
        if self.ANTHROPIC_API_KEY and not self.ANTHROPIC_API_KEY.startswith("sk-ant-your"):
            return self.ANTHROPIC_API_KEY
        if self.OPENROUTER_API_KEY and not self.OPENROUTER_API_KEY.startswith("sk-or-your"):
            return self.OPENROUTER_API_KEY
        return ""

    @property
    def api_base_url(self) -> str:
        """Return the correct base URL for the active provider."""
        if self.OPENROUTER_API_KEY and not self.OPENROUTER_API_KEY.startswith("sk-or-your"):
            if not (self.ANTHROPIC_API_KEY and not self.ANTHROPIC_API_KEY.startswith("sk-ant-your")):
                return "https://openrouter.ai/api/v1"
        return ""  # Empty = use Anthropic default

    @property
    def api_provider(self) -> str:
        if self.ANTHROPIC_API_KEY and not self.ANTHROPIC_API_KEY.startswith("sk-ant-your"):
            return "anthropic"
        if self.OPENROUTER_API_KEY and not self.OPENROUTER_API_KEY.startswith("sk-or-your"):
            return "openrouter"
        return "none"

    @property
    def is_configured(self) -> bool:
        return bool(self.active_api_key)

    # ── Model name ────────────────────────────────────────────────────────────
    @property
    def active_model(self) -> str:
        base = os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")
        if self.api_provider == "openrouter":
            # OpenRouter requires provider prefix for some models
            if not base.startswith("anthropic/"):
                return f"anthropic/{base}"
        return base

    # ── Backwards-compat property ─────────────────────────────────────────────
    @property
    def CLAUDE_MODEL(self) -> str:
        return self.active_model

    # ── Flask ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "CHANGE-THIS-SECRET-KEY-IN-PROD")
    DEBUG: bool     = os.environ.get("DEBUG", "false").lower() == "true"
    HOST: str       = os.environ.get("HOST", "127.0.0.1")
    PORT: int       = int(os.environ.get("PORT", "5000"))

    # ── Storage paths ─────────────────────────────────────────────────────────
    DATABASE_PATH:    str = str(BASE_DIR / "data" / "cases.db")
    UPLOAD_FOLDER:    str = str(BASE_DIR / "data" / "uploads")
    CASES_FOLDER:     str = str(BASE_DIR / "data" / "cases")
    DOCUMENTS_FOLDER: str = str(BASE_DIR / "data" / "documents")
    EXPORTS_FOLDER:   str = str(BASE_DIR / "data" / "exports")

    # ── Video analysis ────────────────────────────────────────────────────────
    VIDEO_FRAME_INTERVAL: int = int(os.environ.get("VIDEO_FRAME_INTERVAL", "5"))
    FRAMES_PER_BATCH:     int = int(os.environ.get("FRAMES_PER_BATCH", "4"))
    MAX_FRAME_SIZE:       int = int(os.environ.get("MAX_FRAME_SIZE", "1024"))
    MAX_CONTENT_LENGTH:   int = 4 * 1024 * 1024 * 1024

    # ── Jurisdiction ──────────────────────────────────────────────────────────
    STATE:      str = os.environ.get("STATE", "Maine")
    STATE_CODE: str = "ME"


config = Config()
