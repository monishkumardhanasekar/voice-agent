# Voice Patient Testing Bot

An automated **patient** voice bot that calls Pretty Good AI's clinic test line, runs different scenarios (scheduling, refills, cancellations, office info), records conversations, and produces transcripts and evaluation reports. Built with **Vapi** (voice/telephony) and **Python**.

---

## Prerequisites

- **Python 3.10+**
- **Vapi account** — [dashboard.vapi.ai](https://dashboard.vapi.ai) (API key + a phone number to call *from*)
- **OpenAI API key** — for the evaluation step (LLM-as-judge)
- **ngrok** (or similar) — for local development, so Vapi can send webhooks to your machine

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd voice-agent
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`. **Do not commit `.env` or any secrets.**

| Variable | Required | Description |
|--------|----------|-------------|
| `VAPI_API_KEY` | Yes | API key from [Vapi Dashboard](https://dashboard.vapi.ai) |
| `VAPI_PHONE_NUMBER_ID` | Yes | ID of the Vapi phone number you use to place outbound calls (Dashboard → Phone Numbers) |
| `VAPI_DESTINATION_NUMBER` | Yes | E.164 number to call (the clinic test line, e.g. `+18054398008`) |
| `WEBHOOK_BASE_URL` | Yes for transcripts | Base URL of your webhook server. For local dev with ngrok: `https://YOUR-NGROK-SUBDOMAIN.ngrok.io` — **do not** add `/webhook/vapi`; the code adds it. |
| `OPENAI_API_KEY` | Yes for evaluation | OpenAI API key (evaluation step scores each call) |
| `WEBHOOK_HOST` | No | Host for webhook server (default `0.0.0.0`) |
| `WEBHOOK_PORT` | No | Port for webhook server (default `8765`) |

---

## Quick test: one call (no transcript) 
Note: This will run only the VAPI not the entire wokflow - use it for testing VAPI in local

To verify that Vapi and your keys work, place a single outbound call. No webhook or ngrok needed.

```bash
python vapi_client.py
```

This dials `VAPI_DESTINATION_NUMBER` with a minimal patient assistant. You should see a call object printed and the call connect. Transcripts are **not** saved unless the webhook is running (see below).

---

## Full workflow: transcripts and evaluation

To run scenarios and get **transcripts** and **evaluation reports**, Vapi must be able to send events to your machine. Use a webhook server and ngrok.

### Step 1: Start the webhook server

In a terminal (leave it running):

```bash
python webhook_server.py
```

Server runs on `http://0.0.0.0:8765` by default. When a call ends, Vapi will POST the transcript here.

### Step 2: Expose the server with ngrok

In a **second** terminal:

```bash
ngrok http 8765
```

ngrok will print an HTTPS URL, e.g. `https://abc123.ngrok.io`.

**One-time ngrok setup** (if you haven’t already): install ngrok, create an account at [ngrok.com](https://ngrok.com), then run `ngrok config add-authtoken <YOUR_TOKEN>`.

### Step 3: Update `.env` with your ngrok URL

Copy the HTTPS URL ngrok printed (e.g. `https://abc123.ngrok.io`) into your `.env`:

```env
WEBHOOK_BASE_URL=https://YOUR-NGROK-SUBDOMAIN.ngrok.io
```

Use only the base URL — **do not** add `/webhook/vapi`; the code adds it.  
If your Vapi account uses a Server URL for webhooks, set it once in the Vapi dashboard to `https://YOUR-NGROK-SUBDOMAIN.ngrok.io/webhook/vapi` so call events are sent to this server.

### Step 4: Run scenarios

In a **third** terminal (with the same venv and `.env`):

```bash
# Run one quick test call (office_info, one run)
python main.py --mode task --scenario office_info --variant 0 --runs 1
```

When the call ends, Vapi sends the transcript to the webhook → the server writes `transcripts/<call_id>.json` → the runner runs the evaluator and writes `reports/<call_id>.json`.

**Check:** In the webhook server terminal you should see something like `[webhook] ... type=end-of-call-report ... SAVED -> transcripts/...`.

---

## Running scenarios (main commands)

The entrypoint is `main.py`. It runs calls **one after another**: start call → wait for transcript (up to 16 minutes) → save transcript → run evaluation → optional delay → next call.

**Tip:** Use `--dry-run` to see which scenarios will run without placing any calls: `python main.py --mode all --dry-run`

### Modes

| Mode | Command | What it does |
|------|---------|--------------|
| **all** | `python main.py --mode all` | Runs every (category, variant) once → **15 calls** in sequence. **Warning:** typically **30+ minutes** total — see below. |
| **scenario** | `python main.py --mode scenario --scenario <CATEGORY>` | Runs all 3 variants of one category (3 calls). |
| **task** | `python main.py --mode task --scenario <CATEGORY> --variant <0\|1\|2>` | Runs one (category, variant) one or more times. Default 2 runs; use `--runs 1` for a single call. |

### What each command does (and warnings)

- **`python main.py --mode all`** — Runs all 15 scenarios back-to-back. **Warning:** Each call can take several minutes (call duration + up to 16 min wait for transcript + 15 s delay). **Total runtime is typically 30+ minutes.** Keep the webhook server and ngrok running for the whole period.
- **`python main.py --mode scenario --scenario <CATEGORY>`** — Runs the 3 variants of one category (3 calls). Use this to test one area without running the full suite.
- **`python main.py --mode task --scenario <CATEGORY> --variant <0|1|2>`** — Runs a single scenario type once or more. Use `--runs 1` for one call. Best for a quick test.

### Examples

```bash
# Full suite — 15 calls, 30+ minutes (see warning above)
python main.py --mode all

# One category only (3 calls)
python main.py --mode scenario --scenario office_info

# Single call — good first test of the full workflow
python main.py --mode task --scenario office_info --variant 0 --runs 1

# One scenario, three runs
python main.py --mode task --scenario refill --variant 2 --runs 3

# See what would run, no calls placed
python main.py --mode all --dry-run
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `all` | `all` \| `scenario` \| `task` |
| `--scenario` | — | Category (required for `scenario` and `task`): `scheduling`, `rescheduling`, `refill`, `office_info`, `edge_cases` |
| `--variant` | — | Variant 0, 1, or 2 (required for `task`) |
| `--runs` | `2` | Number of runs in `task` mode |
| `--dry-run` | off | Print run list and do not place calls |
| `--delay` | `15` | Seconds between calls (use `0` to disable) |
| `--max-wait` | `16` | Max minutes to wait for transcript file per call |
| `--poll-interval` | `10` | Seconds between checks for transcript file |

```bash
python main.py --help
```

---

## Scenario categories

Scenarios define **what the patient (our bot) is trying to do** on each call. Each category has **3 variants** (0, 1, 2).

| Category | Description |
|----------|-------------|
| `scheduling` | New appointment: knee pain, specialist routing, vague day (“this Thursday”) |
| `rescheduling` | Change or cancel existing appointment |
| `refill` | Medication refill (routine, dosage question, or needing doctor approval) |
| `office_info` | Hours, location, parking; insurance; doctors and specialties |
| `edge_cases` | Off-topic, confusing requests, multiple appointments in one call |

---

## Evaluation

After each transcript is saved, the runner automatically runs the **evaluator**: it sends the transcript and scenario (goal, hints) to an LLM (OpenAI GPT-4o) and saves a structured report to `reports/<call_id>.json` (scores, issues, verdicts).

- **Requires:** `OPENAI_API_KEY` in `.env`. If unset, evaluation is skipped with a warning.
- **Using the reports:** The JSON in `reports/` is used for LLM evaluation tabulation and human evaluation; see **Documentation** below.

---

## Output: transcripts and reports

- **Transcripts:** `transcripts/<call_id>.json` — call id, timestamps, scenario (after runner patch), turns (patient vs clinic), raw transcript, recording URL (when available).
- **Reports:** `reports/<call_id>.json` — evaluation output: dimension scores, issues, eval-hint verdicts.

Transcripts are written when the webhook receives Vapi’s `end-of-call-report`. If the webhook didn’t include a recording URL, the runner fetches it from the Vapi API and patches the transcript.

---

## Project structure

| Path | Purpose |
|------|---------|
| `main.py` | Entrypoint; runs scenarios, waits for transcripts, runs evaluator |
| `vapi_client.py` | Vapi API client; starts outbound calls with transient assistant |
| `webhook_server.py` | Flask server; receives Vapi webhooks, saves transcripts |
| `webhook_handler.py` | Parses webhook payloads; normalizes to transcript structure |
| `scenario_manager.py` | Loads scenarios; builds base prompt + scenario block + date/time |
| `evaluator.py` | LLM-based evaluation; produces report JSON |
| `storage.py` | Saves transcripts and reports to local JSON |
| `prompts/` | Base persona and scenario definitions (Python) |
| `transcripts/` | Saved call transcripts (JSON) |
| `reports/` | Evaluation report JSON per call |

---

## Iteration and tuning

This wasn't a one-shot build. The bot, prompts, and evaluation were shaped through multiple rounds of testing.

**Manual exploration first.** Before writing any code, I made multiple manual calls to the clinic bot to understand how it works — its flow, what it asks for, how it handles edge cases. I deliberately tried to confuse it, asked unexpected questions, and pushed it to find its limits. That hands-on understanding made it much easier to write targeted scenario prompts that test specific behaviors rather than guessing.

**Prompt iteration.** Every scenario prompt went through multiple iterations based on observed behavior. For example, early versions of the scheduling prompt didn't handle "this Thursday" vs "next Thursday" well, so I refined the prompt and added date/time injection. Turn-taking rules were added to the base prompt after observing the patient bot interrupting the clinic agent in early calls.

**Turn-taking parameter tuning.** The Vapi assistant's `stopSpeakingPlan` was tuned over several test calls. `numWords` started at 7 (too high — the bot waited too long to detect interruptions), `voiceSeconds` at 0.5 (too conservative), and `backoffSeconds` at 2.5 (too long a pause after being interrupted). These were adjusted to 2, 0.4, and 1.0 respectively until conversations flowed naturally.

**First message mode.** Started with `assistant-speaks-first` but switched to `assistant-waits-for-user` because the clinic agent expects to greet the caller first — our bot speaking first caused awkward overlaps.

**Evaluator rubric refinement.** Initial LLM evaluations were too lenient — scores clustered at 7–9 even for calls with clear issues. The rubric was tightened with explicit instructions to use the full 0–10 scale and stricter per-dimension criteria (e.g. "do not default to 7–9; use 4–6 when the bot clearly failed on multiple criteria").

**Repeated scenario runs.** Scenarios were run multiple times to distinguish consistent bugs from one-offs. For example, the multiple-appointments scenario was tested 4 times — the incomplete confirmation bug appeared in 2 out of 4 runs, confirming it as a real intermittent issue rather than a fluke.

---

## Documentation

| Document | Purpose |
|----------|---------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | How the system works and why the main design choices were made. |
| **LLM evaluation** | `LLM_EVALUATION_TABULATION.md` — LLM-as-judge scores and analysis by scenario. |
| **Human evaluation** | `HUMAN_EVALUATION_V1.md` — Human findings, evidence from transcripts/reports, and bug report summary. |

Transcripts live in `transcripts/`; evaluation report JSON per call in `reports/`.
