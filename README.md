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
| `WEBHOOK_BASE_URL` | Public URL for webhooks (e.g. ngrok URL when testing locally); this is what you set as the Vapi Server URL, e.g. `https://<ngrok-subdomain>.ngrok.io/webhook/vapi` |
| `OPENAI_API_KEY` | OpenAI API key for the evaluation step |
| `WEBHOOK_HOST` (optional) | Host for local webhook server (default `0.0.0.0`) |
| `WEBHOOK_PORT` (optional) | Port for local webhook server (default `8765`) |

## How to run

**Test one outbound call (Phase 1):**

```bash
python vapi_client.py
```

Requires `VAPI_API_KEY` and `VAPI_PHONE_NUMBER_ID` in `.env`. Dials the test line (805-439-8008) with a minimal patient assistant.

**Webhook server (Phase 3):**

1. Start the local webhook server:
   ```bash
   python webhook_server.py
   ```
2. In a separate terminal, start ngrok (or similar) to expose the port.

### Ngrok setup (for webhooks)

These steps assume macOS; adjust if you use a different OS.

1. **Install ngrok** (one-time):
   - Using Homebrew:
     ```bash
     brew install ngrok/ngrok/ngrok
     ```
   - Or download from `https://ngrok.com/download` and follow their instructions.

2. **Connect your ngrok account** (one-time):
   - Create a free account at `https://ngrok.com/`.
   - From the ngrok dashboard, copy your **authtoken**.
   - Run:
     ```bash
     ngrok config add-authtoken <YOUR_AUTHTOKEN>
     ```

3. **Expose the webhook server:**
   - With `webhook_server.py` running locally on port `8765`, run:
     ```bash
     ngrok http 8765
     ```
   - Ngrok will print an HTTPS URL like:
     ```text
     https://abcd1234.ngrok.io
     ```

4. **Configure Vapi Server URL:**
   - In the Vapi dashboard, set the **Server URL** (or equivalent setting) to:
     ```text
     https://abcd1234.ngrok.io/webhook/vapi
     ```
   - Optionally, also set `WEBHOOK_BASE_URL` in your `.env` to the same value:
     ```env
     WEBHOOK_BASE_URL=https://abcd1234.ngrok.io
     ```

5. **Test the webhook:**
   - Make a test call (e.g. using `vapi_client.py` with any scenario).
   - In the terminal where `webhook_server.py` is running, you should see lines like:
     ```text
     [webhook] Received event type=end-of-call-report
     ```

**Full run (after Phase 4):** Once the webhook server is running and configured, you will be able to run:

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
| `prompts/` | Base persona + scenario prompt definitions (Python) |
| `webhook_server.py` | Minimal Flask server exposing the `/webhook/vapi` endpoint |
| `transcripts/` | Saved call transcripts (JSON) |
| `reports/` | Evaluation / bug report JSON per call |

## Architecture

See `IMPLEMENTATION_PLAN.md` for the full implementation plan and design. A short architecture summary will be added here (or in `ARCHITECTURE.md`) before submission.
