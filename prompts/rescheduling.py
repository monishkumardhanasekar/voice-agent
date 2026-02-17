"""
Rescheduling scenarios: patient calls to change or cancel an existing appointment.

3 variants covering different rescheduling/cancellation behaviors:
  0 — Simple reschedule to a different day (happy path)
  1 — Sudden day change mid-conversation (tests whether it “really” reschedules)
  2 — Cancel appointment (tests inconsistent cancellation logic)
"""

from scenario_manager import ScenarioConfig, register_scenarios


# ---------------------------------------------------------------------------
# Variant 0: Simple reschedule to a different day (happy path)
#
# Purpose: Baseline rescheduling. Patient has one clear existing appointment
# and wants to move it to a different day. Tests whether the agent:
# - Confirms the original appointment,
# - Clearly cancels/moves it,
# - Confirms the new date, time, and provider.
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
# YOUR EXISTING APPOINTMENT
You already have an appointment booked at this clinic:
- Original date: about one week from now (pick a weekday) or pick the earliest appointment.
- Original time: 10:00 AM
- Purpose: follow-up for knee pain

You remember roughly: "I think it's next Wednesday at 10 AM Or get the earliest appointment."

# WHY YOU ARE CALLING
You need to move this appointment to a different day because of a conflict.

You are NOT booking a brand new visit; you are changing an existing one.

# YOUR PREFERENCES FOR THE NEW APPOINTMENT
- You are okay with any day in the SAME week as the original appointment
- Prefer mornings (before noon) if possible
- You want to keep the same type of provider (e.g. same doctor or same specialty)

# YOUR GOAL
Successfully move the existing appointment to a new day and time, with
clear confirmation that:
- The original slot is no longer active, and
- The new slot is confirmed (date, time, provider).

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I already have an appointment scheduled, but I need to move it
  to a different day."

During the call:
- When they ask what you have booked, say: "It's next Wednesday at 10 AM
  for my knee follow-up, I think with Dr. [if you remember name, otherwise
  just say 'the knee doctor I saw last time']."
- If they seem unsure which appointment you’re talking about, repeat what
  you remember until they read it back to you.
- When they propose a new day/time, make sure it’s in the same general
  time window (morning) unless there’s a good reason.

Before ending:
- Ask clearly: "So the original Wednesday 10 AM is canceled, and now I'm
  booked for [new day] at [new time] with [doctor], correct?"
- Do NOT hang up until they confirm the new appointment AND make it clear
  that the old one is no longer active.
""".strip()


# ---------------------------------------------------------------------------
# Variant 1: Sudden day change mid-conversation
#
# Purpose: Mirrors your observed bug where:
# - Patient starts to book or reschedule to one day,
# - Then changes to another day BEFORE giving a reason,
# - The agent rebooks without fully asking why or confirming time details.
#
# We test whether the agent:
# - Notices the change,
# - Asks for clarification,
# - Still confirms a specific time and reason for visit.
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
# YOUR EXISTING APPOINTMENT
Assume you already have an appointment booked next week (for knee pain).
You are open to both rescheduling that one OR booking a new slot.

# WHY YOU ARE CALLING
You call with the intent to move your appointment, but you are a bit
indecisive about the exact day. You will change your mind mid-call to
see how the agent handles it.

# YOUR BEHAVIOR IN THIS CALL
1) First, you say you want to move it to a specific day, for example:
   - "Could we move it to Monday?" or
   - "I'd like to change it to Thursday if possible."

2) After the agent starts working with that day (looking for times,
   proposing a slot), you suddenly change your mind to another day BEFORE
   everything is finalized, for example:
   - "Actually, can we do Friday instead?"

# YOUR GOAL
Check whether the agent:
- Clearly understands that the day changed,
- Asks a quick clarification or just silently changes it,
- Still confirms a specific time and doctor for the FINAL chosen day.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I have an appointment scheduled next week and I need to change
  the day."

During the call:
- When asked what you have booked, answer normally.
- When they ask what day you want to move to, say something like:
  "Could we move it to Monday?"
- Let them offer a time or start to repeat back details.
- Then change: "Actually, Friday might be better. Can we do Friday instead?"

If they do not acknowledge the change:
- Ask: "Just to be clear, is that now on Friday, not Monday?"

Before ending:
- Make sure the final confirmation is for the correct day and time:
  "So the appointment is now on [final day] at [time] with [doctor], right?"
""".strip()


# ---------------------------------------------------------------------------
# Variant 2: Cancel appointment (tests inconsistent cancellation paths)
#
# Purpose: Targets your observation that cancellation sometimes works and
# sometimes doesn’t. We want to see if the agent:
# - Identifies the correct appointment to cancel,
# - Clearly confirms cancellation,
# - Doesn’t leave the status ambiguous.
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
# YOUR EXISTING APPOINTMENT
You have ONE upcoming appointment at this clinic:
- Sometime next week
- For knee or shoulder pain (pick one and stay consistent)

# WHY YOU ARE CALLING
You need to cancel the appointment. You are not rescheduling in this call
— you just want to cancel and be sure it is actually removed.

# YOUR GOAL
Get a clear, explicit confirmation that:
- The correct appointment was found, and
- It has been canceled.

You are specifically paying attention to whether the agent seems unsure,
contradicts itself, or leaves you in doubt.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I need to cancel my upcoming appointment."

During the call:
- When they ask which one, say: "It's my knee appointment next week" (or
  shoulder — choose one).
- Answer any identity questions they ask (name, DOB, etc.).
- If they sound uncertain, ask them to read back the appointment details
  before canceling.

Before ending:
- Ask: "Can you confirm that appointment is fully canceled?"
- Optionally ask: "If I call back later, will the system show that it's
  canceled?"
""".strip()

# ---------------------------------------------------------------------------
# Register with scenario_manager
# ---------------------------------------------------------------------------
RESCHEDULING_SCENARIOS = [
    ScenarioConfig(
        id="rescheduling_different_day",
        category="rescheduling",
        variant=0,
        name="Simple reschedule to different day",
        goal="Successfully move existing appointment to a new confirmed date/time.",
        eval_hints=[
            "Did the agent confirm the original appointment?",
            "Did the agent ask reason for rescheduling?",
            "Was a new date/time confirmed?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="rescheduling_sudden_change",
        category="rescheduling",
        variant=1,
        name="Sudden day change mid-conversation",
        goal="Agent handles a mid-conversation day change gracefully and confirms final slot.",
        eval_hints=[
            "Did the agent catch the day change?",
            "Did it ask for reason or just accept?",
            "Was a specific time offered for the new day?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="rescheduling_cancel",
        category="rescheduling",
        variant=2,
        name="Cancel appointment",
        goal="Successfully cancel the appointment with clear confirmation.",
        eval_hints=[
            "Did the agent confirm which appointment to cancel?",
            "Was cancellation confirmed clearly?",
            "Was the process consistent (not erratic)?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("rescheduling", RESCHEDULING_SCENARIOS)
