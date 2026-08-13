"""
Milestone 1: File system tools.

Reimplemented here (self-contained submission - no prior milestone code was
supplied) as thin, well-typed wrappers around data/resumes/ and
data/job_descriptions/. These are what the RAG index (Milestone 2) reads
from, and what the agent uses directly for things like "read John's full
resume" or "save this report to disk".

All five are LangChain @tool functions, so they can be called directly
(`read_resume.invoke({"candidate_id": "CAND-001"})`) or bound to an LLM for
tool-calling in the human-feedback loop.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from langchain_core.tools import tool

from .. import config


@tool
def list_resumes() -> list[str]:
    """List the candidate IDs of every resume available to search over."""
    return sorted(p.stem for p in config.RESUME_DIR.glob("CAND-*.txt"))


@tool
def read_resume(candidate_id: str) -> str:
    """Read the full raw resume text for one candidate by their candidate_id (e.g. 'CAND-001')."""
    path = config.RESUME_DIR / f"{candidate_id}.txt"
    if not path.exists():
        return f"ERROR: no resume found for candidate_id={candidate_id!r}"
    return path.read_text(encoding="utf-8")


@tool
def list_job_descriptions() -> list[str]:
    """List the filenames of sample job descriptions bundled with the demo."""
    return sorted(p.name for p in config.JD_DIR.glob("*.txt"))


@tool
def read_job_description(filename: str) -> str:
    """Read a job description file by name (see list_job_descriptions for valid names)."""
    path = config.JD_DIR / filename
    if not path.exists():
        return f"ERROR: no job description found named {filename!r}"
    return path.read_text(encoding="utf-8")


@tool
def save_report(filename: str, content: str) -> str:
    """Save markdown report content to data/reports/<filename>.md and return the saved path."""
    safe_name = "".join(c for c in filename if c.isalnum() or c in ("-", "_")) or "report"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = config.REPORTS_DIR / f"{safe_name}-{ts}.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


def load_candidate_metadata() -> dict:
    """Not an LLM tool - internal helper used by mock-mode scoring and the
    data generator. Loads the structured ground-truth sidecar file.
    LIVE mode never calls this; it only ever reads resumes via read_resume()
    and extracts facts itself, same as a real deployment would."""
    if not config.RESUME_METADATA_PATH.exists():
        return {}
    return json.loads(config.RESUME_METADATA_PATH.read_text(encoding="utf-8"))


FILESYSTEM_TOOLS = [list_resumes, read_resume, list_job_descriptions, read_job_description, save_report]
