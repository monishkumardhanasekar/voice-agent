"""
Vapi API client: create assistant config and start outbound calls.

Uses the official Vapi server SDK (vapi_server_sdk 1.9.0). Assistant config
uses only API-valid properties. Prompt is provided by scenario_manager
(base persona + scenario block). Falls back to scheduling variant 0 if
no scenario is specified.
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Default destination: Pretty Good AI test line
DEFAULT_DESTINATION_NUMBER = "+18054398008"


def _get_config() -> tuple[str, str]:
    """Read required env vars. Raises ValueError if missing."""
    api_key = os.getenv("VAPI_API_KEY")
    phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
    if not api_key:
        raise ValueError("VAPI_API_KEY is not set. Add it to .env")
    if not phone_number_id:
        raise ValueError("VAPI_PHONE_NUMBER_ID is not set. Add it to .env")
    return api_key, phone_number_id


def _build_assistant(
    system_prompt: str,
    first_message: str = "Hello.",
    first_message_mode: str = "assistant-speaks-first",
    webhook_url: Optional[str] = None,
) -> dict:
    """
    Build a transient assistant payload matching VAPI UI custom properties.

    Includes: model (OpenAI gpt-4o), voice (11labs Sarah), transcriber (Deepgram),
    startSpeakingPlan, stopSpeakingPlan, timeouts, voicemailDetection, privacy.
    """
    # API expects model.messages (system message); firstMessage/firstMessageMode are top-level on assistant
    model = {
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": system_prompt}],
    }

    # 11labs: API expects voiceId (use your 11labs voice ID or name if supported by dashboard)
    voice = {
        "provider": "11labs",
        "voiceId": "EXAVITQu4vr4xnSDxMaL",
        "model": "eleven_turbo_v2_5",
        "inputMinCharacters": 30,
        "stability": 0.7,
        "similarityBoost": 0.75,
        "speed": 0.9,
        "style": 0,
        "useSpeakerBoost": False,
        "autoMode": False,
    }

    # Deepgram: only API-valid keys (no backgroundDenoising). Use "numerals" not "useNumerals".
    transcriber = {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en",
        "confidenceThreshold": 0.5,
        "numerals": False,
    }

    # StartSpeakingPlan: only waitSeconds (API rejects onPunctuationSeconds, smartEndpointing, etc.)
    start_speaking_plan = {"waitSeconds": 3}

    # StopSpeakingPlan: API expects numWords (not numberOfWords)
    stop_speaking_plan = {
        "numWords": 3,
        "voiceSeconds": 0.4,
        "backoffSeconds": 3,
    }

    # VoicemailDetection: only provider and backoffPlan (no initialDelaySeconds)
    voicemail_detection = {
        "provider": "vapi",
        "backoffPlan": {
            "frequencySeconds": 5.0,
            "maxRetries": 6,
        },
    }

    # ArtifactPlan: recordingFormat must be "wav;l16" or "mp3" per API
    artifact_plan = {
        "recordingEnabled": True,
        "loggingEnabled": True,
        "transcriptPlan": {"enabled": True},
        "recordingFormat": "wav;l16",
        "videoRecordingEnabled": False,
    }

    # No "timeouts" object; API uses top-level maxDurationSeconds only
    assistant: dict = {
        "name": "Sarah Martinez Test Caller",
        "firstMessage": first_message,
        "firstMessageMode": first_message_mode,
        "model": model,
        "voice": voice,
        "transcriber": transcriber,
        "startSpeakingPlan": start_speaking_plan,
        "stopSpeakingPlan": stop_speaking_plan,
        "maxDurationSeconds": 1500,
        "voicemailDetection": voicemail_detection,
        "artifactPlan": artifact_plan,
    }

    if webhook_url:
        base = webhook_url.rstrip("/")
        assistant["server"] = {"url": f"{base}/webhook/vapi"}

    return assistant


def start_call(
    destination_number: Optional[str] = None,
    system_prompt: Optional[str] = None,
    first_message: Optional[str] = None,
    first_message_mode: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> dict:
    """
    Start an outbound phone call from our patient assistant to the given number.

    Args:
        destination_number: E.164 number to call (default: 805-439-8008).
        system_prompt: Full system prompt. If None, uses scenario_manager
                       to build the default (scheduling variant 0).
        first_message: First utterance (default: from scenario or "Hello.").
        first_message_mode: e.g. "assistant-speaks-first" (default).
        webhook_url: Optional webhook base URL for transcript events.

    Returns:
        Call object from Vapi (includes id, status, etc.).

    Raises:
        ValueError: If VAPI_API_KEY or VAPI_PHONE_NUMBER_ID is missing.
    """
    from vapi import Vapi

    api_key, phone_number_id = _get_config()
    dest = destination_number or DEFAULT_DESTINATION_NUMBER

    # Build prompt from scenario_manager if not explicitly provided
    if system_prompt is not None:
        prompt = system_prompt
        first = first_message or "Hello."
    else:
        from scenario_manager import get_scenario, build_prompt
        scenario = get_scenario("scheduling", variant=0)
        prompt = build_prompt(scenario)
        first = first_message or scenario.first_message

    mode = first_message_mode or "assistant-speaks-first"
    webhook = webhook_url or os.getenv("WEBHOOK_BASE_URL")

    assistant = _build_assistant(prompt, first, mode, webhook)
    customer = {"number": dest}

    client = Vapi(token=api_key)
    call = client.calls.create(
        phone_number_id=phone_number_id,
        customer=customer,
        assistant=assistant,
    )
    return call


def _serialize_call(call) -> dict:
    """Convert SDK call response to a JSON-serializable dict."""
    if hasattr(call, "model_dump"):
        return call.model_dump()
    if hasattr(call, "dict"):
        return call.dict()
    return dict(call) if not isinstance(call, dict) else call


def get_call(call_id: str) -> Optional[dict]:
    """
    Fetch a call by ID from the Vapi API (GET /call/{id}).
    Returns the call object as a dict, or None on error.
    Per docs: artifact.recording is the recording URL when available.
    """
    from vapi import Vapi

    try:
        api_key, _ = _get_config()
    except ValueError:
        return None
    client = Vapi(token=api_key)
    try:
        call = client.calls.get(call_id)
        return _serialize_call(call)
    except Exception:
        return None


def get_recording_url(call_id: str) -> Optional[str]:
    """
    Get the public recording URL for a call from the Vapi API (GET /call/{id}).
    In SDK 1.9.x the URL is often at call.recordingUrl, not inside artifact.
    """
    call = get_call(call_id)
    if not call:
        return None
    artifact = call.get("artifact") or {}
    # Same order as webhook: call first, then artifact, then artifact.recording.url
    recording_url = (
        call.get("recordingUrl")
        or call.get("recording_url")
        or artifact.get("recordingUrl")
        or artifact.get("recording_url")
        or (artifact.get("recording") or {}).get("url")
    )
    if not recording_url and isinstance(artifact.get("recording"), str):
        recording_url = artifact.get("recording")
    return recording_url or None


if __name__ == "__main__":
    import json

    try:
        result = start_call()
        print("Call created successfully.")
        print(json.dumps(_serialize_call(result), indent=2, default=str))
    except ValueError as e:
        print("Configuration error:", e)
    except Exception as e:
        print("Error starting call:", e)
        raise
