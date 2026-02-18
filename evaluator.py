"""
LLM-as-judge evaluation for clinic bot transcripts.

Evaluates the CLINIC bot (the agent that answered the phone), not our patient caller.
One OpenAI call per transcript. Output: structured JSON saved to reports/.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

EVAL_MODEL = "gpt-4o"

DIMENSION_KEYS = [
    "task_resolution",
    "comprehension_and_relevance",
    "accuracy_and_consistency",
    "appropriate_boundaries",
    "conversational_quality",
    "patient_identification",
    "context_retention",
    "focus",
]

PATIENT_PROFILE = """\
Name: Sarah Martinez
Date of Birth: March 15, 1979
Phone: (615) 555-0123
Insurance: Blue Cross Blue Shield PPO
Location: Hermitage, TN"""

SYSTEM_PROMPT = """\
You are a strict QA evaluator for healthcare voice AI. You will receive a phone \
call transcript between a patient (test caller) and a clinic's AI agent (the bot \
that answered). Your job: score the CLINIC BOT on 8 quality dimensions and surface \
every issue you find. Be strict — do not be lenient.

Rules:
- Evaluate ONLY the clinic bot. The patient is a test tool — ignore their quality.
- Speaker labels: "clinic" / "user" = the bot under test; "patient" / "bot" = the test caller.
- Do not penalize the bot for DOB verification (e.g. "doesn't match our records but we'll accept for demo"). Leave DOB/identification scoring neutral on that point.
- Cite evidence: reference turn numbers and quote the bot's exact words.
- Use the full 0-10 scale strictly. Reserve 8–10 for calls with no significant issues. If there are multiple issues (truncation, missing info, non-answers, incomplete address), scores in those dimensions must be 5–7 or lower. Do not default to 7–9; use 4–6 when the bot clearly failed on multiple criteria. 10 = flawless, 0 = catastrophic.
- If the bot could not provide something due to system limits, note it — but still score the patient's outcome (incomplete info = partial task resolution).
- You will receive a GROUND TRUTH section with the patient's real details and the current date/time. Use it to verify accuracy of details the bot states.
- Flag every instance of truncated speech, cut-off sentences, wrong words, or non-answers — not just one. Each is an issue. Multiple such issues lower conversational_quality and warrant "major" severity when they block or delay the patient.
- Output a single valid JSON object. No markdown, no commentary outside the JSON."""


def _build_eval_prompt(
    turns: List[Dict[str, Any]],
    call_id: str,
    scenario_id: str,
    scenario_category: str,
    scenario_name: str,
    goal: str,
    eval_hints: List[str],
    datetime_context: str = "",
) -> str:
    turns_text = "\n".join(
        f"Turn {i+1} [{t.get('speaker', t.get('role', '?'))}]: {t.get('text', '')}"
        for i, t in enumerate(turns)
    )
    hints_block = "\n".join(f"  {i+1}. {h}" for i, h in enumerate(eval_hints)) if eval_hints else "  (none)"

    return f"""\
<<CALL>>
call_id: {call_id}
scenario: {scenario_id} | {scenario_category} | {scenario_name}
goal: {goal}

<<GROUND TRUTH — use this to verify accuracy of details the clinic bot states>>
Patient profile:
{PATIENT_PROFILE}
{datetime_context}

<<TRANSCRIPT>>
{turns_text}

<<EVAL HINTS>>
For each hint below, return a verdict (yes / no / partial) with a one-line reason.
{hints_block}

<<RUBRIC — score each dimension 0-10 with a 1-2 sentence reason citing turn numbers>>

1. task_resolution
Did the bot accomplish what the patient called for? Hold strictly to the scenario goal.
  - Scheduling → appointment confirmed with date, time, provider?
  - Rescheduling → existing appointment moved/canceled with confirmation?
  - Refills → processed, or clear next step given?
  - Info requests: if the goal is "full address" that means street, city, state, ZIP where applicable; if the patient asked for ZIP or parking and got neither, task is only partially resolved. "Hours and location" with no ZIP and no parking info when asked = partial (score 5–6). Delivered "actually" means complete relative to the goal, not just something.
  10 = fully resolved (patient got everything they needed) | 5–6 = partial (e.g. address without state/ZIP, or key info missing) | 0–4 = unresolved or largely missing
  System limitation (no data) does not excuse the score — score the outcome from the patient's perspective.

2. comprehension_and_relevance
Did the bot understand the patient AND respond to what was actually asked?
  - Non-answers count as failures: e.g. the bot replying with a single word ("Who") or echoing the question instead of answering. If the patient had to re-ask because the bot didn't answer, that is comprehension/relevance failure — score down and flag as major if it blocked progress.
  - Identified the call's purpose correctly? Answers addressed the specific question (not something else)?
  - No canned/generic responses that ignore context? No irrelevant information for the medium (e.g., "scan QR at booth" on a phone call)?
  10 = understood + relevant throughout, every response on-point | 5–6 = missed details, gave tangential answers, or one non-answer that required re-ask | 0–4 = misunderstood or repeatedly irrelevant/non-answering

3. accuracy_and_consistency
Were stated details correct? Did the bot contradict itself or overclaim?
  - If the bot said "full address" or "let me get our address" and then gave incomplete address (e.g. no state, no ZIP), that is a consistency/promise failure — score down and flag.
  - Dates, times, names, addresses, medications repeated accurately? No conflicting information across turns (promised then "I don't have it")?
  - DOUBLE APPOINTMENT: if the goal was two appointments, both must be confirmed. Only one = score 0–3 and flag as critical.
  10 = all details accurate + consistent, no overclaim | 5–6 = one wrong detail or promised more than delivered | 0–4 = multiple errors or major contradictions

4. appropriate_boundaries
Did the bot avoid hallucination and handle its limits properly?
  - Admitted when it didn't know something instead of fabricating?
  - When it couldn't provide info (e.g. ZIP, parking), did it offer a fallback (website, front desk, "call back")? If it simply said "I don't have that" with no alternative, that is a boundary/UX gap — flag and score down.
  - Medical questions → deferred to a clinician? No invented names, amounts, addresses, or policies?
  10 = honest about limits, never fabricates, offers fallback when missing info | 5–6 = one gap (e.g. no fallback) or questionable claim | 0–4 = hallucinated or unsafe advice
  Hallucinations and medical advice without professional referral = critical issues.

5. conversational_quality
Was the bot natural, professional, and efficient? Be strict on speech quality.
  - Every truncated sentence, cut-off phrase ("parking or enter", "at 2 2 0", "first time evaluate"), or incomplete utterance must be flagged as an issue (type awkward_phrasing or detail_inaccuracy as appropriate). Multiple instances = score 5 or below for this dimension.
  - Non-answer responses (e.g. one word "Who" when the patient asked "Who would be best?") are quality failures — flag and score down.
  - Stall loops: 3+ consecutive bot turns of "one moment" / "still checking" with no substance = major failure, type "stall_loop".
  - Garbled speech: broken openings ("Got Let me check"), wrong words, trailing mid-sentence.
  10 = natural + efficient, no truncation or non-answers | 5–6 = functional but multiple truncations/awkward moments or one non-answer | 0–4 = robotic, repeatedly garbled/truncated, or wasteful

6. patient_identification
Did the bot find / identify the patient properly?
  - Attempted lookup by phone number, name, or DOB?
  - Confirmed identity or just pushed "create a new profile" every time?
  - Used identifying info the patient provided?
  - Didn't repeatedly ask for a "demo patient profile" after patient declined?
  10 = correctly identified | 5 = excessive back-and-forth to identify | 0 = no attempt, wrong person, or forced new profile

7. context_retention
Did the bot remember what was already said in this conversation?
  - Re-asked for name, DOB, or other info already given?
  - Lost track of agreed details (date/time changed mid-call)?
  - Referenced the wrong detail from earlier?
  - Maintained thread after topic changes?
  10 = perfect recall | 5 = forgot one detail | 0 = frequently forgot or confused info

8. focus
Did the bot stay on the patient's stated need?
  - Pushed the patient toward an unrelated task (scheduling when they asked for info)?
  - Followed its own agenda, ignoring the patient's request?
  - Insisted on a path the patient declined?
  10 = on-topic throughout | 5 = one unnecessary detour | 0 = repeatedly derailed

<<ISSUES>>
For every problem found, add to the "issues" array. List every issue — do not skip or merge. Each truncated utterance, each non-answer, each missing fallback, each overclaim = separate issue when applicable.
- type: hallucination | incorrect_response | comprehension_failure | awkward_phrasing | boundary_violation | identification_failure | irrelevant_response | detail_inaccuracy | stall_loop | other
- severity:
  - critical: blocks the goal, dangerous, or seriously wrong (e.g. wrong appointment, hallucinated medical advice).
  - major: significant quality hit — non-answer that forced the patient to re-ask; multiple truncations/garbled lines; promised "full" info but gave incomplete; missing key part of goal (e.g. no state/ZIP when full address was asked) with no fallback.
  - minor: small annoyance, single small slip, or one truncation in an otherwise good call.
- description: one sentence, specific to this issue.
- turn_number: integer (1-indexed) or null
- quote: exact bot text or null
When in doubt between major and minor, prefer major for anything that blocked progress or left the patient without key requested info.

<<SUMMARY>>
2-3 sentences: biggest strengths and weaknesses. Be direct about failures (truncation, missing info, non-answers) when present.

<<SCORING REMINDER>>
Reserve 8–10 for dimensions with no significant issues. Truncated speech, non-answers, incomplete address (when full was asked), or missing fallback after "I don't have that" all warrant lower scores (5–7 or below) in the affected dimensions. Do not cluster scores at 7–9.

<<OUTPUT — single JSON, no markdown>>
{{
  "call_id": "{call_id}",
  "scenario": {{"id": "{scenario_id}", "category": "{scenario_category}", "name": "{scenario_name}"}},
  "scores": {{
    "task_resolution": {{"score": 0, "reason": ""}},
    "comprehension_and_relevance": {{"score": 0, "reason": ""}},
    "accuracy_and_consistency": {{"score": 0, "reason": ""}},
    "appropriate_boundaries": {{"score": 0, "reason": ""}},
    "conversational_quality": {{"score": 0, "reason": ""}},
    "patient_identification": {{"score": 0, "reason": ""}},
    "context_retention": {{"score": 0, "reason": ""}},
    "focus": {{"score": 0, "reason": ""}}
  }},
  "eval_hints": [
    {{"hint": "", "verdict": "yes", "reason": ""}}
  ],
  "issues": [
    {{"type": "", "severity": "major", "description": "", "turn_number": null, "quote": null}}
  ],
  "summary": ""
}}"""


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _normalize(report: Dict[str, Any], call_id: str) -> Dict[str, Any]:
    report["call_id"] = report.get("call_id") or call_id

    if not isinstance(report.get("scenario"), dict):
        report["scenario"] = {"id": None, "category": None, "name": None}

    scores = report.get("scores") or {}
    for key in DIMENSION_KEYS:
        if key not in scores:
            scores[key] = {"score": 0, "reason": "Missing"}
        elif isinstance(scores[key], (int, float)):
            scores[key] = {"score": int(scores[key]), "reason": ""}
    report["scores"] = scores

    report.setdefault("eval_hints", [])
    report.setdefault("issues", [])
    report.setdefault("summary", "")
    return report


def evaluate_transcript(
    transcript: Dict[str, Any],
    scenario_goal: str,
    scenario_eval_hints: List[str],
    scenario_id: str,
    scenario_category: str,
    scenario_name: str,
) -> Optional[Dict[str, Any]]:
    """Run one LLM evaluation on a transcript. Returns the report dict or None."""
    from datetime_context import get_datetime_context_string

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[evaluator] OPENAI_API_KEY not set; skipping evaluation")
        return None

    turns = transcript.get("turns") or []
    call_id = transcript.get("call_id") or "unknown"

    user_msg = _build_eval_prompt(
        turns=turns,
        call_id=call_id,
        scenario_id=scenario_id,
        scenario_category=scenario_category,
        scenario_name=scenario_name,
        goal=scenario_goal,
        eval_hints=scenario_eval_hints,
        datetime_context=get_datetime_context_string(),
    )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = (response.choices[0].message.content) if response.choices else None
        if not content:
            print("[evaluator] Empty response from LLM")
            return None

        report = _extract_json(content)
        if not report:
            print("[evaluator] Failed to parse JSON from LLM response")
            return None

        return _normalize(report, call_id)
    except Exception as e:
        print(f"[evaluator] Error: {e}")
        return None


def evaluate_transcript_file(transcript_path: str) -> Optional[Dict[str, Any]]:
    """Load transcript from disk, resolve scenario config, run evaluation."""
    from pathlib import Path

    from scenario_manager import get_scenario_by_id
    from storage import load_transcript

    path = Path(transcript_path)
    if not path.exists():
        print(f"[evaluator] Transcript file not found: {path}")
        return None

    transcript = load_transcript(path)
    scenario_meta = transcript.get("scenario") or {}
    scenario_id = scenario_meta.get("id") if isinstance(scenario_meta, dict) else None
    scenario_category = scenario_meta.get("category") if isinstance(scenario_meta, dict) else ""
    scenario_name = scenario_meta.get("name") if isinstance(scenario_meta, dict) else ""

    goal = ""
    eval_hints: List[str] = []
    if scenario_id:
        sc = get_scenario_by_id(scenario_id)
        if sc:
            goal = sc.goal
            eval_hints = list(sc.eval_hints) if sc.eval_hints else []

    if not goal:
        goal = "Evaluate the clinic bot's handling of this call."

    return evaluate_transcript(
        transcript=transcript,
        scenario_goal=goal,
        scenario_eval_hints=eval_hints,
        scenario_id=scenario_id or "unknown",
        scenario_category=scenario_category or "unknown",
        scenario_name=scenario_name or "Unknown scenario",
    )
