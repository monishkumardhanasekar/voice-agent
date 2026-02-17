"""
Parse Vapi webhook payloads and extract transcript / end-of-call data.

Phase 3.2 focuses ONLY on taking the raw JSON payload from Vapi and
normalizing it into a clean transcript object in Python. Writing the
transcript to disk and wiring it into the Flask route are handled in later
steps.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _map_role_to_speaker(role: str) -> str:
    """
    Map Vapi role to our speaker label.
    
    - "assistant" or "bot" -> "patient" (our Sarah Martinez agent)
    - "user" -> "clinic" (Pivot Point Orthopedics agent)
    - "system" -> None (filtered out, not included in turns)
    """
    role_lower = (role or "").lower()
    if role_lower in ("assistant", "bot"):
        return "patient"   # this is Sara
    if role_lower == "user":
        return "clinic"    # this is Pivot Point
    return role_lower or "unknown"



def extract_transcript_from_webhook(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Given a raw webhook payload from Vapi, return a normalized transcript
    dict if this is an end-of-call event, otherwise return None.

    Normalized transcript structure (subject to small evolution as we
    integrate evaluator and storage):

    {
      "call_id": str,
      "ended_reason": str | None,
      "started_at": str | None,   # ISO8601 if available
      "ended_at": str | None,     # ISO8601 if available
      "scenario": {
          "id": str | None,
          "category": str | None,
          "name": str | None,
      },
      "artifact": {
          "raw_transcript": str | None,
          "recording_url": str | None,
      },
      "turns": [
          {
              "speaker": "patient" | "clinic" | "unknown",
              "role": "user" | "assistant" | str,
              "text": str,
          },
          ...
      ],
    }
    """
    message = (payload or {}).get("message") or {}
    event_type = message.get("type")
    if event_type != "end-of-call-report":
        return None

    call = message.get("call") or {}
    artifact = message.get("artifact") or {}

    call_id = call.get("id")
    ended_reason = message.get("endedReason") or call.get("endedReason")

    # Timestamps: try multiple paths in the payload
    # Vapi may put them in call, message, or top-level
    started_at = (
        call.get("startedAt") 
        or message.get("startedAt") 
        or payload.get("startedAt")
    )
    ended_at = (
        call.get("endedAt") 
        or message.get("endedAt") 
        or payload.get("endedAt")
    )

    # Scenario metadata: we may attach this later via assistant/call metadata.
    # For now, we keep placeholders so evaluator/storage can rely on structure.
    scenario_meta = {
        "id": None,
        "category": None,
        "name": None,
    }

    # Raw transcript: Vapi may send string ("AI: ... User: ...") or array of {role, message, time}
    _raw = artifact.get("transcript")
    if isinstance(_raw, list):
        lines = []
        for item in _raw:
            if isinstance(item, dict):
                role = (item.get("role") or "unknown").capitalize()
                msg = item.get("message") or item.get("content") or ""
                lines.append(f"{role}: {msg}")
            else:
                lines.append(str(item))
        raw_transcript = "\n".join(lines) if lines else None
    else:
        raw_transcript = _raw if isinstance(_raw, str) else None

    # Recording URL: in SDK 1.9.x it most often appears at message.call.recordingUrl, NOT in artifact
    rec = artifact.get("recording")
    recording_url = (
        call.get("recordingUrl")
        or artifact.get("recordingUrl")
        or (rec.get("url") if isinstance(rec, dict) else None)
    )
    if not recording_url and isinstance(rec, str):
        recording_url = rec

    # Structured turns from artifact.messages (if present)
    # Filter out system prompts - they shouldn't appear in conversation turns
    turns: List[Dict[str, Any]] = []
    for msg in artifact.get("messages") or []:
        role = msg.get("role") or ""
        
        # Skip system role messages - these are prompts, not conversation turns
        if role.lower() == "system":
            continue
        
        text = msg.get("message") or msg.get("content") or ""
        if not text:
            continue

        speaker = _map_role_to_speaker(role)
        turns.append(
            {
                "speaker": speaker,
                "role": role,
                "text": text,
            }
        )

    normalized: Dict[str, Any] = {
        "call_id": call_id,
        "ended_reason": ended_reason,
        "started_at": started_at,
        "ended_at": ended_at,
        "scenario": scenario_meta,
        "artifact": {
            "raw_transcript": raw_transcript,
            "recording_url": recording_url,
        },
        "turns": turns,
    }

    return normalized

