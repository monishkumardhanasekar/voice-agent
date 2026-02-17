"""
Save structured transcripts and evaluation reports to local JSON files.

Phase 3.3: implement helpers to write normalized transcript dicts into the
`transcripts/` directory with a clear naming convention.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"


def _ensure_transcripts_dir() -> None:
    """Make sure the transcripts directory exists."""
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def _default_filename_for_transcript(transcript: Dict[str, Any]) -> str:
    """
    Derive a filename for a transcript.

    Prefer call_id when available; otherwise fall back to a timestamp-based
    name to avoid collisions.
    """
    call_id = (transcript or {}).get("call_id")
    if call_id:
        safe_id = str(call_id).replace("/", "_")
        return f"{safe_id}.json"

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    return f"call_{ts}.json"


def save_transcript(transcript: Dict[str, Any]) -> Path:
    """
    Save a normalized transcript dict to `transcripts/` as JSON.

    Returns the full Path to the written file.
    """
    _ensure_transcripts_dir()
    filename = _default_filename_for_transcript(transcript)
    path = TRANSCRIPTS_DIR / filename

    # Write JSON with UTF-8 and pretty-print for easier manual inspection.
    with path.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    print(f"[storage] Saved transcript to {path}")
    return path


def load_transcript(path: os.PathLike[str] | str) -> Dict[str, Any]:
    """
    Convenience helper to load a transcript JSON back into a dict.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

