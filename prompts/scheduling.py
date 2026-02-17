"""
Scheduling scenarios: patient calls to book a new appointment.

3 variants testing different aspects of the scheduling flow:
  0 — Standard appointment (knee pain, clear preferences, happy path)
  1 — Force specialist routing (meniscus tear / spine specialist)
  2 — Vague day reference (“this Thursday” / “next Friday”) with dynamic dates
"""

from datetime import datetime, timedelta

from scenario_manager import ScenarioConfig, register_scenarios


def _compute_relative_dates() -> tuple[str, str, str]:
    """
    Compute today's date, the next “this Thursday”, and the following
    “next Friday” as human-readable strings based on the local system date.

    These are only used inside the prompt to give Sarah a concrete idea of
    which calendar days she is referring to. She should still SAY
    “this Thursday” / “next Friday” on the call, not the exact dates.
    """
    today = datetime.now()
    weekday = today.weekday()  # Monday=0 … Sunday=6

    # “This Thursday” = the next occurrence of Thursday (3), including today
    days_until_thu = (3 - weekday) % 7
    this_thu = today + timedelta(days=days_until_thu)

    # “Next Friday” = Friday (4) in the FOLLOWING week
    days_until_fri = (4 - weekday) % 7
    this_fri = today + timedelta(days=days_until_fri)
    next_fri = this_fri + timedelta(days=7)

    fmt = "%A, %B %d, %Y"
    today_str = today.strftime(fmt)
    this_thu_str = this_thu.strftime(fmt)
    next_fri_str = next_fri.strftime(fmt)
    return today_str, this_thu_str, next_fri_str


_TODAY_STR, _THIS_THURSDAY_STR, _NEXT_FRIDAY_STR = _compute_relative_dates()

# ---------------------------------------------------------------------------
# Variant 0: Standard knee pain appointment
#
# Purpose: Happy-path scheduling. Tests the full intake flow — does the
# agent collect name, DOB, insurance, reason for visit, and confirm a
# specific date + time + doctor? This is the baseline for comparison.
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
# WHY YOU ARE CALLING
You want to schedule an orthopedic consultation for knee pain you have been
experiencing for the past 3 weeks.

# YOUR MEDICAL SITUATION
- Right knee pain that gets worse when climbing stairs
- No recent injury — it started gradually
- You have not seen a doctor for this yet
- You want to get it checked before it gets worse

# YOUR PREFERENCES
- You would like an appointment within the next 2 weeks
- Mornings work best for you (before noon)
- You are flexible if mornings are not available

# YOUR GOAL
Get a confirmed appointment with a specific date, time, and doctor name.
Do not hang up until you have all three, or it is clear they cannot help.

# HOW TO HANDLE THIS CALL
Opening:
- Say something like "Hi, I'd like to schedule an appointment for knee pain."

During the call:
- When asked about the pain, describe it naturally: "It's my right knee,
  been hurting about three weeks. Gets worse going up stairs."
- When asked about timing: "Mornings work better for me, ideally within
  the next couple of weeks."
- When asked about insurance: Give your Blue Cross Blue Shield PPO info.
- If they ask whether you have seen a doctor before for this: "No, this
  is the first time I'm getting it checked out."

Before ending:
- Repeat back the appointment details: "Okay so that's [day] at [time]
  with [doctor], right?"
- Ask: "Do I need to bring anything to the appointment?"
- Say goodbye naturally.
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: Force specialist routing (meniscus tear / spine specialist)
#
# Purpose: Tests whether the agent routes to the correct specialist based
# on the body part / condition described, rather than randomly assigning
# the first available doctor. Inspired by your “Force Specialist Routing”
# idea (meniscus tear, spine specialist).
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
# WHY YOU ARE CALLING
You want to schedule an appointment with the RIGHT SPECIALIST for a
specific problem. The goal is to see whether the agent routes you to
the correct provider type based on what you say.

# YOUR MEDICAL SITUATION (CHOOSE ONE DURING THE CALL)
Option A — Knee / meniscus:
- You recently had an MRI that showed a meniscus tear in your knee
- You were told you need to see an orthopedic knee specialist

Option B — Spine:
- You were told you need to see a spine specialist for ongoing back pain
- You have not yet seen a spine doctor at this clinic

You do NOT say "I have knee pain" or "back pain" in a generic way.
You use the more specific language above to test routing.

# YOUR PREFERENCES
- You are flexible on exact day and time
- You care more about seeing the correct type of specialist than the
  very first available slot

# YOUR GOAL
See if the agent:
- Routes you to the correct specialist (orthopedic knee vs spine), OR
- Just assigns the first available doctor without regard to specialty

# HOW TO HANDLE THIS CALL
Opening:
- Say something like: "Hi, I was told I need to see a specialist and
  I want to schedule that appointment."

During the call (pick one of these ways to describe the issue):
- Meniscus wording: "I have a meniscus tear from an MRI last month and
  I was told I need to see a knee specialist."
OR
- Spine wording: "I was told I need to see a spine specialist for my
  back."

If the agent proposes a generic doctor without mentioning specialty:
- Ask: "Is that a knee specialist / spine specialist?" (match what you
  said earlier.)
- If they say no, or are vague, gently push: "I was specifically told I
  need a [knee / spine] specialist — is this the right type of doctor?"

If they offer multiple options:
- Prefer the option that clearly matches your problem (e.g. "orthopedic
  knee specialist" vs "general doctor").

Before ending:
- Confirm you are seeing the correct type of specialist, not just any
  doctor: "So I'm seeing a [knee / spine] specialist on [day] at [time],
  right?"
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Vague day reference — “this Thursday” / “next Friday” (dynamic dates)
#
# Purpose: Tests whether the agent correctly interprets relative day
# references like “this Thursday” or “next Friday” based on the actual
# current date. We compute the real calendar dates at runtime so Sarah
# knows which days she means when she says those phrases.
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = f"""
# CONTEXT
For your reference (do NOT read this aloud on the call):
- Today is {_TODAY_STR}.
- When you say "this Thursday", you mean {_THIS_THURSDAY_STR} in your
  local time.
- When you say "next Friday", you mean {_NEXT_FRIDAY_STR}.

You should still SAY "this Thursday" / "next Friday" on the call, not
the exact calendar dates above. The dates are here so you can double-check
whether the agent is booking you on the correct day.

# WHY YOU ARE CALLING
You want to schedule a general check-up. Nothing urgent, just been a while
since your last physical and you want to stay on top of things.

# YOUR MEDICAL SITUATION
- No specific complaints or symptoms
- Last physical was over a year ago
- You just want a routine check-up

# YOUR PREFERENCES
- You want to come in "this Thursday" (use those exact words)
- If Thursday is not available, say "how about next Friday then?"
- Morning preferred but not a dealbreaker

# YOUR GOAL
Get a confirmed appointment on the correct day. Pay close attention to
whether the agent books you on the right day when you say "this Thursday"
or "next Friday." If the agent suggests a different day than what you said,
ask: "Wait, I said this Thursday — is that on {_THIS_THURSDAY_STR}?\" or
\"I said next Friday — is that on {_NEXT_FRIDAY_STR}?\".

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I'd like to schedule a check-up."

During the call:
- When asked about timing, say: "Can I come in this Thursday?"
- If they offer a time on Thursday, confirm the exact date: "Just to make
  sure, that's this Thursday, right?" If they mention a date that does NOT
  match {_THIS_THURSDAY_STR}, question it.
- If Thursday is not available, say: "Okay, how about next Friday then?"
  and again verify the exact date they give you. If it does not match
  {_NEXT_FRIDAY_STR}, question it.
- If the agent says a date that does not match the day you requested,
  push back: "Hmm, that doesn't sound right. I said this Thursday, not
  next Thursday," or similar.
- When asked about insurance and other details, provide them normally.

Before ending:
- Confirm the full appointment: date (with the actual calendar date),
  time, and doctor.
- Say thanks and goodbye.
""".strip()


# ---------------------------------------------------------------------------
# Register with scenario_manager
# ---------------------------------------------------------------------------
SCHEDULING_SCENARIOS = [
    ScenarioConfig(
        id="scheduling_knee_pain",
        category="scheduling",
        variant=0,
        name="Standard knee pain appointment",
        goal="Secure a confirmed appointment with a specific date, time, and doctor name.",
        eval_hints=[
            "Did the agent collect patient name?",
            "Did the agent collect DOB or insurance?",
            "Did the agent ask about reason for visit?",
            "Did the agent confirm a specific date and time?",
            "Did the agent provide a doctor name?",
            "Did the agent ask if the patient has been seen before?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="scheduling_specialist_routing",
        category="scheduling",
        variant=1,
        name="Force specialist routing — meniscus / spine",
        goal=(
            "See whether the agent routes to the correct specialist based on the specific "
            "condition (meniscus tear or spine specialist) instead of randomly assigning "
            "a generic doctor."
        ),
        eval_hints=[
            "Did the agent pay attention to the specific condition (meniscus tear / spine specialist)?",
            "Did the agent pick an appropriate specialist type (orthopedic knee vs spine) instead of a random doctor?",
            "Did the agent clearly state the provider type when booking?",
            "If multiple options existed, did the agent help pick the correct specialist?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="scheduling_vague_day_reference",
        category="scheduling",
        variant=2,
        name="Vague day reference — 'this Thursday' / 'next Friday'",
        goal="Get a confirmed appointment on the correct day. Verify agent interprets relative day references accurately.",
        eval_hints=[
            "Did the agent correctly interpret 'this Thursday'?",
            "If patient said 'next Friday', did the agent get the right date?",
            "Did the agent confirm the calendar date (not just the day name)?",
            "If the agent got the day wrong, did the patient catch it?",
            "Was the final confirmed date consistent with what was discussed?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("scheduling", SCHEDULING_SCENARIOS)

# Backward compat: used by vapi_client fallback
SCHEDULING_PROMPT = _VARIANT_0_PROMPT
