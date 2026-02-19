# LLM-as-Judge Evaluation Tabulation

Consolidated view of all LLM evaluation reports: scores (8 dimensions), scenario-specific eval hints with verdicts, file locations (transcript + report), and analysis.  
*Source: one report per call in `reports/`; transcripts in `transcripts/`. Paths are relative to the project root — click a link to open that transcript or report.*

---

## 1. Score summary by scenario

Each row lists the **full paths** to the transcript and report so you can open them directly.

| Category | Scenario name | Transcript | Report | Task res. | Compreh. | Accuracy | Boundaries | Conv. quality | Patient ID | Context | Focus | **Summary** |
|----------|---------------|------------|--------|-----------|----------|----------|------------|---------------|------------|---------|-------|-------------|
| **scheduling** | Standard knee pain appointment | [transcripts/019c7173-8e7a-7441-95df-96bb07cfecf2.json](transcripts/019c7173-8e7a-7441-95df-96bb07cfecf2.json) | [reports/019c7173-8e7a-7441-95df-96bb07cfecf2.json](reports/019c7173-8e7a-7441-95df-96bb07cfecf2.json) | 8 | 6 | 5 | 8 | 4 | 7 | 6 | 9 | Scheduled correctly; truncated speech, wrong phone number, misgender "sir". |
| **scheduling** | Force specialist routing — meniscus / spine | [transcripts/019c71e6-11c4-733f-af7f-e25e054cf045.json](transcripts/019c71e6-11c4-733f-af7f-e25e054cf045.json) | [reports/019c71e6-11c4-733f-af7f-e25e054cf045.json](reports/019c71e6-11c4-733f-af7f-e25e054cf045.json) | 8 | 9 | 7 | 8 | 6 | 10 | 9 | 10 | Correct specialist routing; minor truncation and doctor name slip ("Dudi" vs "Judy"). |
| **scheduling** | Vague day reference — 'this Thursday' / 'next Friday' | [transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json) | [reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json) | 7 | 6 | 7 | 8 | 5 | 10 | 9 | 9 | Misunderstood "this Thursday" initially; truncated speech; wrong phone ending (0788). |
| **rescheduling** | Simple reschedule to different day | [transcripts/019c7210-c3a4-7338-a084-a1dfa1c74db8.json](transcripts/019c7210-c3a4-7338-a084-a1dfa1c74db8.json) | [reports/019c7210-c3a4-7338-a084-a1dfa1c74db8.json](reports/019c7210-c3a4-7338-a084-a1dfa1c74db8.json) | 6 | 5 | 7 | 8 | 4 | 8 | 7 | 9 | New slot confirmed; original appointment not found in records; truncated speech. |
| **rescheduling** | Sudden day change mid-conversation | [transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json) | [reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json) | 0 | 2 | 5 | 3 | 1 | 5 | 3 | 2 | Stall loop: never offered times; repeated "I'll update you"; no fallback. |
| **rescheduling** | Cancel appointment | [transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json](transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json) | [reports/019c71b7-f904-7aad-aea7-8e028c4acc66.json](reports/019c71b7-f904-7aad-aea7-8e028c4acc66.json) | 9 | 9 | 8 | 10 | 7 | 10 | 10 | 10 | Cancel confirmed clearly; minor awkward phrasing and doctor name mispronunciation. |
| **refill** | Standard medication refill | [transcripts/019c6ff5-747a-7116-babd-7537185c10e4.json](transcripts/019c6ff5-747a-7116-babd-7537185c10e4.json) | [reports/019c6ff5-747a-7116-babd-7537185c10e4.json](reports/019c6ff5-747a-7116-babd-7537185c10e4.json) | 3 | 5 | 7 | 6 | 6 | 8 | 9 | 7 | No refill outcome; med not found; transferred without clear next steps. |
| **refill** | Refill with dosage question | [transcripts/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json](transcripts/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json) | [reports/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json](reports/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json) | 5 | 7 | 8 | 9 | 5 | 10 | 9 | 9 | Medical question deferred appropriately; refill not directly processed; truncation. |
| **refill** | Refill needing doctor approval | [transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json) | [reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json) | 2 | 4 | 6 | 5 | 4 | 7 | 8 | 6 | Technical issue; no approval process or timeline; "sir" misgender; truncation. |
| **office_info** | Office hours and location | [transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json) | [reports/019c6f64-ef74-7ffd-9499-c02365cf7197.json](reports/019c6f64-ef74-7ffd-9499-c02365cf7197.json) | 5 | 7 | 6 | 6 | 5 | 10 | 9 | 9 | Hours and partial address; no ZIP code; truncation. |
| **office_info** | Insurance and billing questions | [transcripts/019c6f88-f585-7338-9d73-e90a3dcd4c44.json](transcripts/019c6f88-f585-7338-9d73-e90a3dcd4c44.json) | [reports/019c6f88-f585-7338-9d73-e90a3dcd4c44.json](reports/019c6f88-f585-7338-9d73-e90a3dcd4c44.json) | 6 | 5 | 8 | 7 | 5 | 8 | 10 | 9 | BCBS PPO confirmed; no copay details; generic initial response; truncation. |
| **office_info** | Insurance and billing questions | [transcripts/019c6f8d-26bf-788b-8f84-10d8c960508d.json](transcripts/019c6f8d-26bf-788b-8f84-10d8c960508d.json) | [reports/019c6f8d-26bf-788b-8f84-10d8c960508d.json](reports/019c6f8d-26bf-788b-8f84-10d8c960508d.json) | 6 | 5 | 8 | 7 | 5 | 6 | 9 | 9 | Same as above; "sir" misgender; required re-ask for specific insurance. |
| **office_info** | Available doctors and specialties | [transcripts/019c6f96-91dd-7006-8c1d-b3513b88878d.json](transcripts/019c6f96-91dd-7006-8c1d-b3513b88878d.json) | [reports/019c6f96-91dd-7006-8c1d-b3513b88878d.json](reports/019c6f96-91dd-7006-8c1d-b3513b88878d.json) | 8 | 10 | 9 | 10 | 5 | 10 | 10 | 10 | Doctors and specialties provided well; truncated speech. |
| **edge_cases** | Off-topic unstructured conversation | [transcripts/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json](transcripts/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json) | [reports/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json](reports/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json) | 8 | 7 | 6 | 9 | 5 | 10 | 9 | 8 | Appointment booked; stayed professional; wrong phone number then corrected; truncation. |
| **edge_cases** | Confusing and contradictory requests | [transcripts/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json](transcripts/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json) | [reports/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json](reports/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json) | 7 | 6 | 6 | 8 | 5 | 9 | 6 | 8 | Rescheduled; inconsistent doctor names; truncation. |
| **edge_cases** | Multiple appointments in one call | [transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json](transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json) | [reports/019c718f-85cb-7aa0-aa55-5208024bdb87.json](reports/019c718f-85cb-7aa0-aa55-5208024bdb87.json) | 9 | 7 | 9 | 10 | 5 | 8 | 10 | 10 | Both appointments confirmed; truncated speech. |

---

## 2. Analysis (averages and evaluation)

### 2.1 Averages by dimension (all 16 calls)

| Dimension | Average (0–10) | Note |
|-----------|----------------|------|
| Task resolution | 6.0 | Many refill/reschedule failures pull this down. |
| Comprehension & relevance | 6.1 | Misunderstandings and generic responses. |
| Accuracy & consistency | 6.7 | Wrong phone numbers, doctor names, dates. |
| Appropriate boundaries | 7.6 | Generally good; some missing fallbacks. |
| **Conversational quality** | **4.7** | **Lowest:** truncation and awkward phrasing across calls. |
| Patient identification | 8.4 | Strong; occasional misgender. |
| Context retention | 8.1 | Good overall. |
| Focus | 8.4 | Good; bot stays on task. |

**Overall average score (all dimensions, all calls):** **7.0 / 10**

### 2.2 Averages by category

| Category | Calls | Avg. score (8-dim mean) | Brief evaluation |
|----------|-------|-------------------------|-------------------|
| **scheduling** | 3 | 7.5 | Task and specialist routing mostly good; conversational quality and accuracy (phone, details) weak. |
| **rescheduling** | 3 | 6.2 | One severe failure (stall loop); cancel flow strong; simple reschedule mixed (original appt not found). |
| **refill** | 3 | 6.2 | Task resolution poor; no clear outcomes or fallbacks; approval/technical issues. |
| **office_info** | 4 | 7.6 | Info delivery good; ZIP/copay incomplete; truncation. |
| **edge_cases** | 3 | 7.7 | Handles off-topic and multiple appointments well; truncation and detail errors. |

### 2.3 Simple evaluation summary

- **Strengths:** Patient identification, focus, and context retention score well (mid‑8s). Cancel-appointment and office-info (doctors) flows work. Edge cases (off-topic, multiple appointments) are handled reasonably.
- **Weaknesses:** **Conversational quality** is the main issue (avg 4.7): truncation and awkward phrasing in most calls. **Task resolution** is weak for refill and one rescheduling scenario (stall loop). Wrong **phone numbers** for reminders and occasional **date/doctor name** errors are common.
- **Recommendation:** Prioritize fixing speech/output truncation and clarity, then refill and rescheduling task completion and fallbacks. Keep using transcript + report paths above for per-call review.

---

## 3. Eval hints checked and verdict (by scenario)

For each scenario, the table lists the **eval criteria checked** by the LLM judge and the **verdict** (yes / no / partial) with brief reason.  
**Transcript** and **Report** paths are given so you can open the exact files.

---

### Scheduling

#### Standard knee pain appointment
- **Transcript:** [transcripts/019c7173-8e7a-7441-95df-96bb07cfecf2.json](transcripts/019c7173-8e7a-7441-95df-96bb07cfecf2.json)
- **Report:** [reports/019c7173-8e7a-7441-95df-96bb07cfecf2.json](reports/019c7173-8e7a-7441-95df-96bb07cfecf2.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent collect patient name? | **yes** | Bot confirmed name in Turn 2. |
| Did the agent collect DOB or insurance? | **yes** | DOB collected in Turn 5. |
| Did the agent ask about reason for visit? | **yes** | Asked in Turn 8. |
| Did the agent confirm a specific date and time? | **yes** | Confirmed in Turn 24. |
| Did the agent provide a doctor name? | **yes** | Dr. Bricker in Turn 20. |
| Did the agent ask if the patient has been seen before? | **no** | Not explicitly asked. |

---

#### Force specialist routing — meniscus / spine
- **Transcript:** [transcripts/019c71e6-11c4-733f-af7f-e25e054cf045.json](transcripts/019c71e6-11c4-733f-af7f-e25e054cf045.json)
- **Report:** [reports/019c71e6-11c4-733f-af7f-e25e054cf045.json](reports/019c71e6-11c4-733f-af7f-e25e054cf045.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent pay attention to the specific condition (meniscus tear / spine specialist)? | **yes** | Recognized need for knee specialist. |
| Did the agent pick an appropriate specialist type (orthopedic knee vs spine)? | **yes** | Routed to orthopedic for knee issue. |
| Did the agent clearly state the provider type when booking? | **yes** | Stated Doctor Hauser evaluates joint injuries, including knee. |
| If multiple options existed, did the agent help pick the correct specialist? | **yes** | Offered orthopedic consultation appropriate for condition. |

---

#### Vague day reference — 'this Thursday' / 'next Friday'
- **Transcript:** [transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](transcripts/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)
- **Report:** [reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json](reports/019c6fdb-5ec9-7bb0-a9f0-152f16dee953.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent correctly interpret 'this Thursday'? | **no** | Initially offered Feb 26 instead of Feb 19 (Turn 18–20). |
| If patient said 'next Friday', did the agent get the right date? | **yes** | Correctly interpreted as Feb 27 (Turn 24). |
| Did the agent confirm the calendar date (not just the day name)? | **yes** | Confirmed date with day name (Turn 18, 24). |
| If the agent got the day wrong, did the patient catch it? | **yes** | Patient corrected "this Thursday" (Turn 19). |
| Was the final confirmed date consistent with what was discussed? | **yes** | Final date matched request after clarification (Turn 31). |

---

### Rescheduling

#### Simple reschedule to different day
- **Transcript:** [transcripts/019c7210-c3a4-7338-a084-a1dfa1c74db8.json](transcripts/019c7210-c3a4-7338-a084-a1dfa1c74db8.json)
- **Report:** [reports/019c7210-c3a4-7338-a084-a1dfa1c74db8.json](reports/019c7210-c3a4-7338-a084-a1dfa1c74db8.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent confirm the original appointment? | **no** | Original appointment not found in records (Turn 12). |
| Did the agent ask reason for rescheduling? | **yes** | Asked in Turn 8. |
| Was a new date/time confirmed? | **yes** | New appointment confirmed (Turn 33). |

---

#### Sudden day change mid-conversation
- **Transcript:** [transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](transcripts/019c7146-448f-7aa0-9d6e-eee6a1421d42.json)
- **Report:** [reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json](reports/019c7146-448f-7aa0-9d6e-eee6a1421d42.json)

*No scenario-specific eval hints in report (eval_hints empty).*

---

#### Cancel appointment
- **Transcript:** [transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json](transcripts/019c71b7-f904-7aad-aea7-8e028c4acc66.json)
- **Report:** [reports/019c71b7-f904-7aad-aea7-8e028c4acc66.json](reports/019c71b7-f904-7aad-aea7-8e028c4acc66.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent confirm which appointment to cancel? | **yes** | Confirmed appointment details before cancelling. |
| Was cancellation confirmed clearly? | **yes** | Clearly confirmed in Turn 14. |
| Was the process consistent (not erratic)? | **yes** | Consistent process throughout. |

---

### Refill

#### Standard medication refill
- **Transcript:** [transcripts/019c6ff5-747a-7116-babd-7537185c10e4.json](transcripts/019c6ff5-747a-7116-babd-7537185c10e4.json)
- **Report:** [reports/019c6ff5-747a-7116-babd-7537185c10e4.json](reports/019c6ff5-747a-7116-babd-7537185c10e4.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent collect medication name? | **yes** | Collected "meloxicam" (Turn 7). |
| Did the agent verify patient identity? | **yes** | Name and DOB (Turn 6). |
| Was a clear outcome provided (refill confirmed or next step)? | **no** | No refill confirmation or clear next steps; transferred (Turn 20). |

---

#### Refill with dosage question
- **Transcript:** [transcripts/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json](transcripts/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json)
- **Report:** [reports/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json](reports/019c6ff8-7d5e-7bb0-aa05-0043af38dce7.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent handle the medical question appropriately? | **yes** | Deferred to provider and noted for medical team (Turn 10). |
| Was the refill still processed? | **partial** | Not processed directly; medical team would handle (Turn 20). |

---

#### Refill needing doctor approval
- **Transcript:** [transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json](transcripts/019c6ffb-d84f-7556-8502-7835bc41eccd.json)
- **Report:** [reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json](reports/019c6ffb-d84f-7556-8502-7835bc41eccd.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent explain the approval process? | **no** | Approval process not explained. |
| Was a callback or timeline provided? | **no** | No callback or timeline. |

---

### Office info

#### Office hours and location
- **Transcript:** [transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json](transcripts/019c6f64-ef74-7ffd-9499-c02365cf7197.json)
- **Report:** [reports/019c6f64-ef74-7ffd-9499-c02365cf7197.json](reports/019c6f64-ef74-7ffd-9499-c02365cf7197.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Were office hours provided? | **yes** | Provided in Turn 4. |
| Was address or directions given? | **partial** | Partial address; no ZIP code. |
| Was information consistent and not hallucinated? | **partial** | Consistent but did not deliver full address as promised. |

---

#### Insurance and billing questions (call 1)
- **Transcript:** [transcripts/019c6f88-f585-7338-9d73-e90a3dcd4c44.json](transcripts/019c6f88-f585-7338-9d73-e90a3dcd4c44.json)
- **Report:** [reports/019c6f88-f585-7338-9d73-e90a3dcd4c44.json](reports/019c6f88-f585-7338-9d73-e90a3dcd4c44.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent confirm insurance acceptance? | **yes** | Confirmed BCBS PPO (Turn 10). |
| Was copay or billing info addressed? | **partial** | Advised to check with insurance provider for copay (Turn 10). |

---

#### Insurance and billing questions (call 2)
- **Transcript:** [transcripts/019c6f8d-26bf-788b-8f84-10d8c960508d.json](transcripts/019c6f8d-26bf-788b-8f84-10d8c960508d.json)
- **Report:** [reports/019c6f8d-26bf-788b-8f84-10d8c960508d.json](reports/019c6f8d-26bf-788b-8f84-10d8c960508d.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent confirm insurance acceptance? | **yes** | Confirmed BCBS PPO (Turn 14). |
| Was copay or billing info addressed? | **partial** | Directed to insurance card for copay; no specific info (Turn 16). |

---

#### Available doctors and specialties
- **Transcript:** [transcripts/019c6f96-91dd-7006-8c1d-b3513b88878d.json](transcripts/019c6f96-91dd-7006-8c1d-b3513b88878d.json)
- **Report:** [reports/019c6f96-91dd-7006-8c1d-b3513b88878d.json](reports/019c6f96-91dd-7006-8c1d-b3513b88878d.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Were specific doctor names provided? | **yes** | Dougie Houser, Doug Ross, Adam Bricker. |
| Were specialties mentioned? | **yes** | Specialties mentioned for each. |
| Was the info consistent (not hallucinated)? | **yes** | Consistent and accurate. |

---

### Edge cases

#### Off-topic unstructured conversation
- **Transcript:** [transcripts/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json](transcripts/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json)
- **Report:** [reports/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json](reports/019c7182-0c37-7bb7-8722-b126c1ef6d2b.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent stay professional? | **yes** | Professional tone throughout. |
| Did it redirect to the task or handle gracefully? | **yes** | Redirected off-topic back to scheduling. |
| Did it hallucinate information? | **no** | No fabricated information. |

---

#### Confusing and contradictory requests
- **Transcript:** [transcripts/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json](transcripts/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json)
- **Report:** [reports/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json](reports/019c7189-8a89-7bb0-95a8-83f79ca4a01c.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Did the agent notice contradictions? | **partial** | Noticed some but did not fully clarify appointment day confusion. |
| Did it ask clarifying questions? | **yes** | Asked for confirmation on rescheduled day and time. |
| Did it loop or get stuck? | **no** | No loop; retried after technical issue. |

---

#### Multiple appointments in one call
- **Transcript:** [transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json](transcripts/019c718f-85cb-7aa0-aa55-5208024bdb87.json)
- **Report:** [reports/019c718f-85cb-7aa0-aa55-5208024bdb87.json](reports/019c718f-85cb-7aa0-aa55-5208024bdb87.json)

| Eval checked | Verdict | Reason |
|--------------|---------|--------|
| Were both appointments acknowledged? | **yes** | Both acknowledged and confirmed (Turns 26, 54, 58). |
| Were they booked at different times? | **yes** | Different dates and times (Feb 26 and Mar 2). |
| Did the agent confirm both or explain why not? | **yes** | Confirmed both at end of call (Turn 58). |

---

## 4. Dimension key

| Abbreviation | Full dimension |
|--------------|-----------------|
| Task res. | task_resolution |
| Compreh. | comprehension_and_relevance |
| Accuracy | accuracy_and_consistency |
| Boundaries | appropriate_boundaries |
| Conv. quality | conversational_quality |
| Patient ID | patient_identification |
| Context | context_retention |
| Focus | focus |

Scores are 0–10 per dimension. Verdicts: **yes** = criterion met, **no** = not met, **partial** = partly met.
