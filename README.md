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

---

## Scenarios

Scenarios define **what the patient (our bot) is trying to do** on each call. Each scenario has a **category** and a **variant** (prompt number). The runner uses these to build the system prompt and first message.

### Scenario categories

| Category       | Description |
|----------------|-------------|
| `scheduling`   | New appointment: knee pain, specialist routing, vague day references |
| `rescheduling` | Change or cancel existing appointment |
| `refill`       | Medication refill (routine, with dosage question, or needing doctor approval) |
| `office_info`  | Office hours, location, parking; insurance/billing; doctors and specialties |
| `edge_cases`   | Off-topic conversation; confusing requests; multiple appointments in one call |

Each category has **three variants** (0, 1, 2). For example, `scheduling` variant 0 is “Standard knee pain appointment”, variant 1 is “Force specialist routing”, variant 2 is “Vague day reference (‘this Thursday’ / ‘next Friday’)”.

### How scenarios are used

- **Category** = which prompt family (e.g. `office_info`).
- **Variant** = which prompt inside that family (0, 1, or 2).
- When you run the runner, it builds a list of **(category, variant)** pairs (and optionally repeats the same pair N times). Each pair becomes one outbound call with that scenario’s prompt.

---

## Phase 4 — Running scenarios sequentially

Phase 4 runs multiple scenario calls **one after another**: start call → wait for transcript (up to 16 minutes) → optional delay → next call. No overlapping calls.

**Before you run:** Start the webhook server (`python webhook_server.py`) and ngrok (`ngrok http 8765`), and set `WEBHOOK_BASE_URL` in `.env` to your ngrok URL. The runner uses the same webhook to receive transcripts.

### Three run modes

| Mode        | What it does | When to use |
|-------------|--------------|-------------|
| **all**     | Runs **every** (category, variant) once. 5 categories × 3 variants = **15 calls** in a fixed order. | Full test suite in one go. |
| **scenario**| Runs **all variants** of **one category** once. You choose the category (e.g. `office_info` → 3 calls). | Test one category only. |
| **task**    | Runs **one** (category, variant) **N times** (e.g. 2 runs). You choose category, variant, and `--runs N`. | Repeat the same prompt for consistency. |

### Command reference

**1. Run all tasks (15 calls: every category, every variant, once each)**

```bash
python main.py --mode all
```

No other args needed. Order: scheduling 0,1,2 → rescheduling 0,1,2 → refill 0,1,2 → office_info 0,1,2 → edge_cases 0,1,2.

**2. Run one scenario — all variants of a single category**

```bash
python main.py --mode scenario --scenario <CATEGORY>
```

- **Required:** `--scenario` = one of: `scheduling`, `rescheduling`, `refill`, `office_info`, `edge_cases`.
- **Effect:** 3 calls (variant 0, 1, 2 for that category).

Examples:

```bash
python main.py --mode scenario --scenario scheduling
python main.py --mode scenario --scenario office_info
python main.py --mode scenario --scenario edge_cases
```

**3. Run one task N times (same prompt, multiple calls)**

```bash
python main.py --mode task --scenario <CATEGORY> --variant <N> [--runs <N>]
```

- **Required:** `--scenario` (category), `--variant` (0, 1, or 2).
- **Optional:** `--runs` = how many times to run that (category, variant). Default: **2**.

Examples:

```bash
# Run office_info variant 0 twice (default --runs 2)
python main.py --mode task --scenario office_info --variant 0

# Run scheduling variant 1 three times
python main.py --mode task --scenario scheduling --variant 1 --runs 3

# Run refill variant 2 once
python main.py --mode task --scenario refill --variant 2 --runs 1
```

### All Phase 4 options

| Option | Default | Meaning |
|--------|---------|--------|
| `--mode` | `all` | `all` \| `scenario` \| `task` |
| `--scenario` | — | Category name (required for `scenario` and `task`) |
| `--variant` | — | Variant index 0, 1, or 2 (required for `task`) |
| `--runs` | `2` | Number of runs for `task` mode only |
| `--dry-run` | off | Print the run list and **do not place any calls** |
| `--delay` | `15` | Seconds to wait **between** calls (use `0` to disable) |
| `--max-wait` | `16` | Max minutes to wait for the transcript file **per call** (hard limit) |
| `--poll-interval` | `10` | Seconds between checks for the transcript file while waiting |

**Examples with options:**

```bash
# See what would run without making calls
python main.py --mode all --dry-run
python main.py --mode scenario --scenario office_info --dry-run
python main.py --mode task --scenario scheduling --variant 0 --runs 2 --dry-run

# Run all with 30 s between calls and 20 min max wait per transcript
python main.py --mode all --delay 30 --max-wait 20

# Run office_info scenario with no delay between the 3 calls
python main.py --mode scenario --scenario office_info --delay 0
```

**Help:**

```bash
python main.py --help
```

### What happens during a run

1. The runner builds the list of (scenario, run_index) from `--mode`, `--scenario`, `--variant`, and `--runs`.
2. For each run it: gets the scenario prompt → starts an outbound call via Vapi → waits for `transcripts/<call_id>.json` to appear (polling every `--poll-interval` seconds, up to `--max-wait` minutes).
3. When the file appears, it patches the transcript JSON with scenario metadata (category, id, name, run_index).
4. If the file does not appear before the timeout, that run is counted as failed/timeout and the runner continues to the next.
5. After each run (except the last), it waits `--delay` seconds before starting the next call.
6. At the end it prints a summary: started, succeeded, failed/timeout, and the path to `transcripts/`.

**Note:** Transcripts are only written when the webhook receives Vapi’s `end-of-call-report` (after the call ends). So the runner waits for that file; if the call or webhook is slow, it may take several minutes per run.

### Saved transcript format

Each transcript is saved as `transcripts/<call_id>.json` with:

- `call_id`, `ended_reason`, `started_at`, `ended_at`
- `scenario`: after the runner patches it: `id`, `category`, `name`, `run_index`
- `artifact.raw_transcript`: full text transcript; `artifact.recording_url`: **public recording URL when provided by Vapi**

**Recording URL:** We extract it from the webhook when present (`artifact.recording` as string or object, or `artifact.recordingUrl`). When you run the Phase 4 runner (`main.py`), if the saved transcript still has no recording URL, the runner fetches the call via the Vapi API (GET /call/{id}) and patches the transcript with `artifact.recording` from the response, so you get the public recording URL when Vapi has it available.

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
