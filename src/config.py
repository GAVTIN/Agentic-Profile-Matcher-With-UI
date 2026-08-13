"""
Central configuration for the Resume Matching Agent.

Everything that varies between environments (API keys, model names, data
paths, screening thresholds) lives here so the rest of the codebase never
reads os.environ directly.

MODE controls the agent's brain:
  - "live": uses Groq (LLM) + local HuggingFace sentence-transformers
    (embeddings) - real semantic search, real LLM reasoning. Requires
    GROQ_API_KEY.
  - "mock": zero external calls. TF-IDF keyword search + rule-based
    scoring/report generation. Lets anyone clone the repo and run the full
    pipeline in seconds with no API key and no model download. This is not
    a stub - it's a genuinely useful offline mode, and every test scenario
    in tests/test_scenarios.md was captured running in this mode.

MODE is decided once, at startup, by matching_agent.py / app_streamlit.py
based on a --mode flag (default "auto": live if GROQ_API_KEY is set, else
mock with a warning).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RESUME_DIR = DATA_DIR / "resumes"
RESUME_METADATA_PATH = RESUME_DIR / "_metadata.json"
JD_DIR = DATA_DIR / "job_descriptions"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Model / provider settings
# --------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# Groq deprecated llama-3.1-8b-instant / llama-3.3-70b-versatile in mid-2026.
# These are their official replacements (see console.groq.com/docs/deprecations).
GROQ_MODEL_SMART = os.getenv("GROQ_MODEL_SMART", "openai/gpt-oss-120b")
GROQ_MODEL_FAST = os.getenv("GROQ_MODEL_FAST", "openai/gpt-oss-20b")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --------------------------------------------------------------------------
# Screening thresholds (Part C: multi-round screening)
# --------------------------------------------------------------------------
INITIAL_POOL_SIZE = int(os.getenv("INITIAL_POOL_SIZE", "100"))       # resumes considered in round 1
ROUND1_SHORTLIST_SIZE = int(os.getenv("ROUND1_SHORTLIST_SIZE", "10"))  # survivors of round 1
BORDERLINE_SCORE_BAND = (55, 74)   # inclusive score range treated as "borderline" for improvement tips
STRONG_MATCH_THRESHOLD = 75
HIRE_SCORE_THRESHOLD = 80
HIRE_WITH_RESERVATIONS_THRESHOLD = 60

# --------------------------------------------------------------------------
# Mode (set once at process startup by the entry point)
# --------------------------------------------------------------------------
MODE = "mock"  # "live" or "mock" - overwritten by set_mode()


def set_mode(mode: str) -> str:
    """Resolve and set the global MODE. 'auto' picks live iff a Groq key is present."""
    global MODE
    if mode == "auto":
        mode = "live" if has_groq_key() else "mock"
    if mode not in ("live", "mock"):
        raise ValueError(f"Unknown mode: {mode!r}")
    MODE = mode
    return MODE


def has_groq_key() -> bool:
    return bool(GROQ_API_KEY)
