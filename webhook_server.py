"""
Minimal Flask server exposing the Vapi webhook endpoint.

Phase 3, step 3.1: just accept POSTs on /webhook/vapi and return 200.
In later steps we will call into webhook_handler and storage to parse and
persist transcripts.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from webhook_handler import extract_transcript_from_webhook
from storage import save_transcript

load_dotenv()

app = Flask(__name__)


def _log_webhook_event(event_type: str, call_id: Optional[str], extra: str = "") -> None:
    """Log every webhook with server time so we can see order and when events arrive."""
    now = datetime.now(timezone.utc).isoformat()
    call_part = f" call_id={call_id}" if call_id else ""
    msg = f"[webhook] {now} type={event_type}{call_part}"
    if extra:
        msg += f" {extra}"
    print(msg)


@app.post("/webhook/vapi")
def vapi_webhook() -> tuple[dict, int]:
    """
    Receive Vapi server events.

    - Logs every event with UTC timestamp and event type (and call_id when present).
    - When the event is an end-of-call report, normalizes the transcript and
      writes it to `transcripts/` using `storage.save_transcript`, and adds
      webhook_received_at (server time) to the saved JSON.
    - Always returns 200 quickly so we don't impact telephony timing.
    """
    try:
        payload = request.get_json(force=True, silent=False) or {}
    except Exception:
        print("[webhook] Received invalid JSON payload")
        return {"status": "error", "reason": "invalid_json"}, 200

    message = payload.get("message") or {}
    event_type = message.get("type", "unknown")
    call = message.get("call") or {}
    call_id = call.get("id")

    _log_webhook_event(event_type, call_id)

    # Only save transcript for end-of-call-report (sent by Vapi after call ends).
    try:
        transcript = extract_transcript_from_webhook(payload)
        if transcript is not None:
            # Record when we received this webhook (server time) for debugging timing.
            transcript["webhook_received_at"] = datetime.now(timezone.utc).isoformat()
            path = save_transcript(transcript)
            _log_webhook_event(
                event_type,
                transcript.get("call_id"),
                extra=f"SAVED -> {path}",
            )
    except Exception as e:
        print(f"[webhook] Error while processing transcript: {e}")

    return {"status": "ok"}, 200


def run() -> None:
    """Run the Flask app on a configurable host/port."""
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port_str = os.getenv("WEBHOOK_PORT", "8765")
    try:
        port = int(port_str)
    except ValueError:
        port = 8765

    app.run(host=host, port=port)


if __name__ == "__main__":
    run()

