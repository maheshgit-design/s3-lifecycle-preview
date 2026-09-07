"""Offline S3 lifecycle eligibility simulation. No AWS client or network calls."""
from .engine import PreviewError, simulate

__all__ = ["PreviewError", "simulate"]
__version__ = "0.1.0"
