"""Legal knowledge base package."""
from .maine_laws import MAINE_LAWS, get_maine_laws_for_date
from .federal_laws import FEDERAL_LAWS
from .violation_patterns import VIOLATION_PATTERNS, MISCONDUCT_PATTERNS

__all__ = [
    "MAINE_LAWS",
    "FEDERAL_LAWS",
    "VIOLATION_PATTERNS",
    "MISCONDUCT_PATTERNS",
    "get_maine_laws_for_date",
]
