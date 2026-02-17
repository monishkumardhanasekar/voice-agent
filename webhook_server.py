"""
Minimal Flask server exposing the Vapi webhook endpoint.

Phase 3, step 3.1: just accept POSTs on /webhook/vapi and return 200.
In later steps we will call into webhook_handler and storage to parse and
persist transcripts.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from webhook_handler import extract_transcript_from_webhook
from storage import save_transcript

load_dotenv()

app = Flask(__name__)


@app.post("/webhook/vapi")
def vapi_webhook() -> tuple[dict, int]:
    """
    Receive Vapi server events.

    - Logs the event type.
    - When the event is an end-of-call report, normalizes the transcript and
      writes it to `transcripts/` using `storage.save_transcript`.
    - Always returns 200 quickly so we don't impact telephony timing.
    """
    try:
        payload = request.get_json(force=True, silent=False) or {}
    except Exception:
        # If payload is not JSON, still return 200 so we don't break calls,
        # but surface a minimal error in the body.
        print("[webhook] Received invalid JSON payload")
        return {"status": "error", "reason": "invalid_json"}, 200

    message = payload.get("message") or {}
    event_type = message.get("type", "unknown")

    # Lightweight log to stdout so you can see events arriving while testing.
    print(f"[webhook] Received event type={event_type}")

    # If this is an end-of-call report, normalize and save the transcript.
    try:
        transcript = extract_transcript_from_webhook(payload)
        if transcript is not None:
            path = save_transcript(transcript)
            print(f"[webhook] Saved transcript for call_id={transcript.get('call_id')} at {path}")
    except Exception as e:
        # Do not break the webhook response on errors; just log them.
        print(f"[webhook] Error while processing transcript: {e}")

    # Always respond 200 quickly; Vapi does not expect a complex response
    # for status / transcript / end-of-call-report events.
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

