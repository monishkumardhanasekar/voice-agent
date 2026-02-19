# Architecture

This document explains how the voice patient testing bot works and why the main design choices were made.

---

## How the system works

The system is an automated **patient** voice bot. It does not implement the clinic agent; it acts as the **caller** that dials Pretty Good AI's clinic test line. Our bot (e.g. "Sarah Martinez") is the patient; their system is the agent that answers the phone.

### Placing calls

We place outbound calls through the Vapi API. For each call we build a **transient assistant**: we send a full assistant configuration in the create-call request (model, voice, transcriber, system prompt) instead of referring to a saved assistant by ID. That configuration includes the **system prompt** that drives the patient's behavior. We get that prompt from the **scenario manager**: it combines a **base prompt** (patient identity, profile, communication style, turn-taking rules) with a **scenario block** (why they're calling, what to ask for, constraints) and the **current date and time** in the patient's timezone. So every call can use a different scenario (scheduling, refill, cancel, office info, edge cases) without changing code or dashboard.

### Running scenarios

The entrypoint is `main.py`. It can run all scenarios once, all variants of one category, or one specific (category, variant) multiple times. For each run it:

1. Gets the scenario from the scenario manager and builds the prompt.
2. Starts one outbound call via the Vapi client (with the webhook base URL set so Vapi can send us events).
3. Waits for the call's transcript file to appear on disk.
4. Patches that transcript with scenario metadata and optionally fetches the recording URL from the Vapi API if the webhook didn't include it.
5. Runs the evaluator on the transcript.
6. Saves the evaluation report.

Calls are run **one after another**; we do not start the next call until the current one's transcript has been saved.

### Getting the transcript

We do not poll the Vapi API for the transcript. When a call ends, Vapi **sends** an HTTP POST to our webhook URL (the "Server URL" we set on the assistant). That request is an **end-of-call report**: it contains the full conversation (e.g. `artifact.messages` with role and text). Our Flask server receives the POST, parses the payload, and hands it to the webhook handler.

The handler normalizes it into a single structure: call id, timestamps, and a list of **turns** with speaker labels. We map Vapi's "assistant" to **patient** (our bot) and "user" to **clinic** (their agent). That normalized object is saved as a JSON file under `transcripts/<call_id>.json`.

The runner, which is waiting for that file, then continues: it patches the transcript with scenario metadata, runs the evaluator, and saves the report to `reports/<call_id>.json`.

### Evaluation

The evaluator does not call Vapi. It reads the transcript JSON (turns, scenario goal, eval hints) and calls an LLM (e.g. OpenAI) once with a fixed rubric. The rubric asks for scores on several dimensions (task resolution, comprehension, accuracy, boundaries, conversational quality, etc.) and for structured issues (type, severity, evidence). The evaluator parses the LLM response into JSON and the runner writes it to `reports/<call_id>.json`. Those reports are used to produce the human-readable bug report and evaluation summaries.

---

## Key design choices

### Webhooks for transcript capture

Vapi is designed to push events to a URL you configure. We use that: when a call ends, Vapi POSTs the end-of-call report to our server. We chose this over **polling** the Vapi API (e.g. repeatedly calling GET /call/{id} until the transcript is ready) because:

- We get the transcript as soon as Vapi has it, without guessing poll interval or timeout.
- We make fewer API calls.
- The runner can synchronize by simply waiting for the transcript file to appear, which the webhook writes.

So the "fetch" of the transcript is Vapi pushing it to us, not us pulling it from them.

### Base prompt plus scenario injection

The base prompt defines **who** the patient is (name, DOB, phone, style, turn-taking). The scenario block defines **why** they're calling and **what** they want.

We keep these separate so the persona stays consistent across all tests and we can add or change scenarios by editing only the scenario block. The same scenario supplies the **goal** and **eval hints** for the evaluator, so the LLM judges the clinic bot against the intended test.

### Transient assistant per call

We don't create one "Sarah Martinez" assistant in the Vapi dashboard and reuse it. We build the assistant inline for each create-call request. That way we can pass a **different system prompt every time** (different scenario) without creating or updating saved assistants. One code path handles all scenarios.

### Local JSON for transcripts and reports

We store transcripts and evaluation reports as JSON files in `transcripts/` and `reports/`, not in a database.

We chose this to keep the project **self-contained and portable**: no DB setup, no migrations, and easy to open any transcript or report by call id. It fits the scope of the challenge and makes it straightforward to re-run the evaluator on existing transcripts.

### Sequential calls

We never start a new call until the previous one has finished and its transcript has been saved. That avoids overlapping conversations, mixed webhook payloads, and keeps a clear one-to-one link between call id, transcript file, and report file.

### Date/time injection

The patient bot often needs to reason about "this Thursday" or "next week." We inject the **current date and time** (in the patient's timezone, from env) into the system prompt so the bot doesn't guess; it knows "today" and "now" and can answer scheduling questions correctly.

### Why Vapi

Vapi handles the full voice pipeline — STT, LLM, and TTS — in one platform. We don't have to stitch together separate speech-to-text, language model, and text-to-speech services ourselves. We just configure the assistant (model, voice, transcriber) and Vapi runs the entire conversation in the cloud, which let us focus on scenarios, evaluation, and bug-finding instead of telephony plumbing.

### Decoupled evaluator

The evaluator only reads our normalized transcript and scenario metadata and calls the LLM. It does not depend on Vapi. That keeps evaluation logic independent of how we captured the conversation and allows re-running evaluation on old transcripts when we tune the rubric or prompt.
