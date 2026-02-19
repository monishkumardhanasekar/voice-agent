# Human Evaluation Report (V1)
## Clinic bot evaluation — findings from human testing

**Scope:** Evaluation of the **clinic agent** (the AI that answers the clinic phone), not the patient/test caller.  
**Purpose:** Document human-observed issues, supported by transcripts and LLM evaluation reports where available.  
---

## 1. Stall response — rescheduling never completes

**Finding:** In one call, the clinic bot entered a stall loop: it repeatedly said it would check availability and “update you as soon as I have…” but never returned with any times or resolution.

**Scenario:** Rescheduling with a sudden day change mid-conversation (patient first asked for Monday, then switched to Friday).

**Evidence:**

- **Transcript:** [transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json)
- **Report:** [reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json)

**Transcript excerpts (clinic = bot under evaluation):**

- After patient says “Actually, Friday might be better. Can we do Friday instead?” the clinic says: *“Got it. I'll check Friday's opening and let you know what's avail It sounds”* (turn 22 — also truncated).
- Then many consecutive clinic turns with no new information, e.g.:
  - *“Thanks for your patience. I'll let you know as soon as I have the available times for Friday.”*
  - *“Understood. I'll update you as soon as I have the Friday appoint”* (truncated).
  - *“Got it. I'll look for morning openings on Friday and let you know as soon as I have 1.”*
  - Dozens of variants of *“I'll let you know as soon as I have the Friday morning availability”* / *“I'll update you as soon as I have the Friday morning option”* with no actual times ever offered.
- Later, garbled turn: *“Hi. I'm still check Got it.”* (turn 58).
- Call eventually ends with transfer to test line; no new appointment was confirmed or explicitly failed.

**Report support:** LLM-as-judge flags `stall_loop` (major), `awkward_phrasing` (major), `comprehension_failure` (major); task_resolution = 0/10, conversational_quality = 1/10.

**Why it matters:** The patient waits a long time with no outcome, no explanation, and no fallback (e.g. “we can’t find Friday slots, please call the front desk”). This undermines trust and leaves the original appointment status unclear.

---

## 2. Full address with ZIP code — bot cannot provide ZIP

**Finding:** When the caller explicitly asked for the **full address with the ZIP code**, the clinic bot said it could give the full address but **did not have the ZIP code** (or parking details).

**Scenario:** Office hours and location (caller requesting address and ZIP).

**Evidence:**

- **Transcript:** [transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json)

**Transcript excerpts:**

- **Caller (patient):** *“Can you give me the full address with the ZIP code? Also, is there parking on-site?”*
- **Clinic (bot):** *“I can give you the full address, but I don't have the ZIP code or parking details. Would you like me to send the address to your phone by text?”*

So despite offering “the full address,” the bot explicitly does not have the ZIP code. In the same call, the clinic also truncates when confirming hours: *“Yes. That's correct. We're open those hours at 2 2”* (cut off mid-sentence while saying “220”).

**Why it matters:** For navigation and forms, callers often need a complete address including ZIP. Saying “I can give you the full address” but then not having ZIP is inconsistent and unhelpful for a common office-info request.

---

## 3. Truncated or unclear speech — especially around numbers

**Finding:** In several calls, the clinic bot’s responses were **truncated or cut off mid-sentence**, often when giving times, dates, or numbers. This occurred even when the patient did not interrupt.

**Scenarios:** Multiple (scheduling, rescheduling, refill, office info).

**Evidence:**

**A. Scheduling — vague day reference**  
[transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json), [reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)

- Clinic: *“The next”* (turn 14).
- Clinic: *“the next”* (turn 16).
- Clinic: *“Yes. I'm here. The next available new patient consultation is Thursday, February 20 sixth. We have openings at 12 PM, 12 45 PM.”* (full sentence only after patient said “Hello? Are you still there?”)
- Clinic: *“Got it. To confirm you'd like to book a new patient”* (turn 26 — cut off).
- Clinic: *“Let me confirm booking you”* (turn 29 — cut off).

**B. Refill — dosage and dose**  
[transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json), [reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json)

- Clinic: *“What's the dosage, and how often do you”* (turn 10 — cut off).
- Clinic: *“can you tell me the dose”* (turn 13 — incomplete).

**C. Office hours confirmation**  
[transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json)

- Clinic: *“Yes. That's correct. We're open those hours at 2 2”* (cut off while stating “220”).

**Report support:** Multiple reports flag `awkward_phrasing` (major) with descriptions such as “truncated,” “incomplete,” “cut off,” affecting conversational_quality and clarity when conveying numbers/dates.

**Why it matters:** Truncation during key information (times, dates, dosages, address numbers) forces the caller to guess, repeat the request, or lose confidence in the bot. It feels like the bot “stopped in between,” especially when telling numbers.

---

## 4. “This week” vs “next week” — wrong day interpretation

**Finding:** The clinic agent sometimes **misinterprets relative day references** such as “this Thursday” vs “next Thursday,” leading to the wrong calendar date being offered.

**Scenario:** Scheduling with vague day reference (“this Thursday” / “next Friday”).

**Evidence:**

- **Transcript:** [transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)
- **Report:** [reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)

**Transcript flow:**

- **Caller:** *“Can I come in this Thursday?”*
- **Clinic:** Checks and then says: *“The next available new patient consultation is Thursday, February 20 sixth.”* (February 26 is *next* Thursday, not *this* Thursday.)
- **Caller:** *“Wait. I was hoping for this Thursday. Is there anything on Thursday, nineteenth?”*
- **Clinic:** *“I checked, but the earliest Thursday available is February 20 sixth. There are no open slots this Thursday, February nineteenth.”*

So the bot initially offered February 26 when the patient asked for “this Thursday,” and only after correction did it align with “this Thursday” = February 19.

**Report support (eval_hints):**

- *“Did the agent correctly interpret 'this Thursday'?”* → **no** — *“The bot initially misunderstood 'this Thursday' as February 26th instead of February 19th (Turn 18-20).”*
- *“If the agent got the day wrong, did the patient catch it?”* → **yes** — patient corrected.

**Why it matters:** “This” vs “next” week is a common source of scheduling errors. Misinterpretation can book the wrong week and cause no-shows or confusion.

---

## 5. Refill — all questions asked, then “technical issue” and fallback without task completion

**Finding:** In a refill scenario requiring doctor approval, the clinic bot **asked every needed question** (medication, dosage, pharmacy, days left, etc.) but then reported a **technical issue** sending the refill request and **fell back to connecting the caller to support** without completing the task or explaining the approval process.

**Scenario:** Refill needing doctor approval (e.g. hydrocodone-acetaminophen).

**Evidence:**

- **Transcript:** [transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json)
- **Report:** [reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json)

**Transcript flow:**

- Bot collects: medication (hydrocodone acetaminophen 5-325), dosage (1 tablet every 6 hours), last refill (~3 weeks), pharmacy (Walgreens Hermitage TN), days left (couple of days).
- Clinic: *“There was a problem sending your refill request. Let me try again.”*
- Clinic: *“I'm having trouble processing your refill request due to a technical issue. I'll connect you to our clinic support team now. Please stay on the line. Connecting you to a representative.”*
- Call ends with test-line goodbye; no refill confirmation, no approval timeline, no clear next steps.

**Report support:** Task resolution 2/10; boundary_violation (no fallback/alternative when unable to process); eval_hints: “Did the agent explain the approval process?” → no, “Was a callback or timeline provided?” → no.

**Why it matters:** The bot correctly gathered all information and then failed without explaining what went wrong or what the caller should expect (e.g. “we’ll need doctor approval; you’ll get a callback within 24 hours”). So it’s falling back to transfer without completing the task or setting expectations — a fallback logic failure from the user’s perspective.

---

## 6. Cancel appointment — reason for cancellation asked inconsistently

**Finding:** When testing **cancel appointment** flows, the clinic agent **sometimes asks for a reason** for cancellation and **sometimes does not**. In particular, when the caller went **off topic** and then said they wanted to cancel, the bot **skipped asking for the reason**.

**Scenario:** Cancel appointment (rescheduling_cancel); tested with and without going off topic first.

**Evidence:** This is a **human-observed behavior** across multiple personal test calls. The exact call(s) where the reason was skipped (after going off topic) are not in the final submitted transcript set, but the pattern was consistent enough to note: cancellation reason is not reliably requested, and going off topic appears to affect whether the bot asks for the reason.

**Why it matters:** Inconsistent collection of cancellation reasons can affect clinic analytics, no-show follow-up, and policy compliance. Users may also be unsure what to expect from the bot.

---

## 7. Misgendering — “sir” for female-named caller (Sarah)

**Finding:** The clinic bot **repeatedly used “sir”** when addressing the caller even though the **name was Sarah** and the **voice was female**, indicating a failure to infer or use appropriate gender/honorific.

**Evidence:**

**A. Cancel appointment call**  
[transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json](transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json)

- End of call, clinic: *“Got it. Have a good day, **sir**.”*  
- Caller had identified as Sarah and used female voice throughout.

**B. Refill needing approval**  
[transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json), [reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json)

- After caller says “Yes. This is Sarah Martinez,” clinic: *“Got it, **sir**. You please tell me your date of birth to verify your identity?”*  
- Report flags incorrect_response (major): *“The bot incorrectly referred to the patient as 'sir' despite the patient identifying as Sarah Martinez.”*

**C. Scheduling — vague day reference**  
[transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)

- End of call, clinic: *“Got it. Have a great day, **sir**.”*  
- Caller was Sarah throughout.

**Report support:** Multiple LLM reports flag misgendering / “sir” as detail_inaccuracy or incorrect_response (major) and note impact on patient_identification or accuracy_and_consistency.

**Why it matters:** Misgendering is disrespectful and can make callers, especially transgender or non-binary patients, feel unwelcome. The bot has the name “Sarah” and voice signal but still defaults to “sir,” so this is a fixable logic or prompt issue.

---

## 8. Multiple appointments — first confirmation missing one booking; second message without appointment details

**Finding:** During **direct human testing** of the **multiple-appointments** scenario (booking two slots in one call), the following bug was observed: sometimes the bot **sent only the first appointment’s details** in the first confirmation; when the caller said they had received only one detail, the bot sent **another message that did not include the missing appointment information**. This occurred in **2 out of 4** test iterations, so the behavior is inconsistent.

**Scenario:** Multiple appointments in one call (e.g. knee + shoulder, two separate bookings).

**Evidence:**

- **Human testing:** Caller (evaluator) called the clinic bot directly and booked two appointments. In 2/4 runs:
  - First confirmation contained only one appointment.
  - After saying “I received only one detail,” the follow-up message did not contain the second appointment’s details (e.g. date, time, provider).
- **Supporting transcript (successful case):** [transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json](transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json) shows a call where both appointments were confirmed in voice and the bot correctly summarized: *“You have 2 appointments scheduled. First, with doctor Judy Hauser, on Thursday, February 20 sixth at 12 45 PM, for your knee. Second, with doctor Adam Bricker on Monday, March second at 10 30 AM for your shoulder.”* So the bot *can* handle multiple appointments correctly, but the failure mode (incomplete first confirmation + uninformative second message) was observed in other runs.
- **Image (failing run):** Screenshot from one of the failing runs — first confirmation with only one appointment and/or follow-up message without appointment details.

<p align="center">
  <img src="static/IMG_6708.jpg" width="350" alt="Multiple appointments bug — incomplete confirmation example"/>
</p>
<p align="center"><em>Failing run example: first confirmation missing second appointment; follow-up message lacked appointment details.</em></p>


**Why it matters:** When the bot sends only one appointment or a follow-up with no details, the patient may miss the second appointment or be unsure it was ever booked. This is a context/state and messaging bug in the multiple-booking flow.

---

## Summary table (Human evaluation V1)

| # | Finding | Scenario / context | Severity (human) | Evidence |
|---|--------|--------------------|------------------|----------|
| 1 | Stall response; no resolution | Rescheduling (sudden day change) | Critical | [Transcript](transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json) + [Report](reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json) |
| 2 | Full address offered but no ZIP code | Office hours & location | Major | [Transcript](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json) |
| 3 | Truncated/unclear speech (e.g. numbers) | Multiple | Major | [019c6fdb](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json), [019c6ffb](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json), [019c6f64](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json) + reports |
| 4 | “This Thursday” vs “next” wrong; date/day mismatch (e.g. “Thursday, Feb 19” when Feb 19 is Wednesday) | Scheduling / rescheduling | Major | [Transcript](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json) + [Report](reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json); report v1/019c7118 |
| 5 | Refill: technical issue → fallback, task not completed | Refill needs approval | Major | [Transcript](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json) + [Report](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json) |
| 6 | Cancel reason asked inconsistently | Cancel appointment | Medium | Human observation |
| 7 | Misgendering (“sir” for Sarah) | Multiple | Major | [019c71b7](transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json), [019c6ffb](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json), [019c6fdb](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json) + reports |
| 8 | Multiple appointments: incomplete first confirmation; second message without details | Multiple appointments | Major | Human testing 2/4 runs + [transcript 019c718f](transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json) (success case) |

---
