# Voice Patient Testing Bot

Automated patient voice bot that calls Pretty Good AI’s clinic test line, runs scenarios, records transcripts, and produces bug reports. Built with Vapi and Python.

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set all required environment variables (see below). **Do not commit `.env` or any secrets.**

### Required environment variables

| Variable | Description |
|----------|-------------|
| `VAPI_API_KEY` | API key from [Vapi Dashboard](https://dashboard.vapi.ai) |
| `VAPI_PHONE_NUMBER_ID` | ID of the Vapi number used to place outbound calls |
| `WEBHOOK_BASE_URL` | Public URL for webhooks (e.g. ngrok URL when testing locally) |
| `OPENAI_API_KEY` | OpenAI API key for the evaluation step |

## How to run

**Test one outbound call (Phase 1):**

```bash
python vapi_client.py
```

Requires `VAPI_API_KEY` and `VAPI_PHONE_NUMBER_ID` in `.env`. Dials the test line (805-439-8008) with a minimal patient assistant.

**Full run (after Phase 4):** Start the webhook server (and optionally ngrok), then run:

```bash
python main.py
```

## Project structure

| Path | Purpose |
|------|---------|
| `main.py` | Entrypoint; runs scenarios and coordinates calls + evaluation |
| `vapi_client.py` | Vapi API client; starts outbound calls |
| `webhook_handler.py` | Parses Vapi webhook payloads; extracts transcripts |
| `scenario_manager.py` | Loads scenarios; builds base + scenario prompt |
| `evaluator.py` | LLM-based evaluation; produces bug report JSON |
| `storage.py` | Saves transcripts and reports to local JSON |
| `prompts/` | Base system prompt for the patient agent |
| `scenarios/` | Scenario JSON files (goal, persona, constraints) |
| `transcripts/` | Saved call transcripts (JSON) |
| `reports/` | Evaluation / bug report JSON per call |

## Architecture

See `IMPLEMENTATION_PLAN.md` for the full implementation plan and design. A short architecture summary will be added here (or in `ARCHITECTURE.md`) before submission.
