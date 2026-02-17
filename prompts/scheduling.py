"""
Scheduling scenarios: patient calls to book a new appointment.

3 variants that test different aspects of the scheduling flow.
Prompt content will be written properly in the prompt-writing step;
these are structural placeholders with enough detail to run.
"""

from scenario_manager import ScenarioConfig, register_scenarios

# ---------------------------------------------------------------------------
# Variant 0: Standard knee pain appointment (the original Sarah scenario)
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
You're calling to schedule an orthopedic consultation for knee pain you've
been experiencing for the past 3 weeks.

**Your situation:**
- Right knee pain, worse when climbing stairs
- No recent injury, just gradual onset
- Haven't seen a doctor for this yet
- Want to get it checked out before it gets worse

**Your preferences:**
- Prefer appointments within the next 2 weeks
- Mornings work best (before noon)
- Flexible if those aren't available

**Your goal:**
Secure a confirmed appointment with date, time, and doctor name.

**Call flow:**
- Opening: "Hi, I'd like to schedule an appointment for knee pain."
- Middle: Answer questions about your pain, timing, insurance naturally.
- Closing: Confirm date, time, doctor. Ask "Do I need to bring anything?"
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: First-time patient, unsure what type of doctor to see
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: New patient, doesn't know if they need orthopedics or general.
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Urgent same-day appointment request
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient wants a same-day or next-day appointment, tests urgency handling.
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
        goal="Secure a confirmed appointment with date, time, and doctor name.",
        eval_hints=[
            "Did the agent collect patient name?",
            "Did the agent collect DOB or insurance?",
            "Did the agent confirm a specific date and time?",
            "Did the agent provide a doctor name?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="scheduling_new_patient_unsure",
        category="scheduling",
        variant=1,
        name="New patient unsure about doctor type",
        goal="Get guidance on which doctor to see and book an appointment.",
        eval_hints=[
            "Did the agent help clarify the right department?",
            "Did the agent still collect required info?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="scheduling_urgent_sameday",
        category="scheduling",
        variant=2,
        name="Urgent same-day appointment request",
        goal="Get a same-day or next-day appointment, or clear next steps if unavailable.",
        eval_hints=[
            "Did the agent handle urgency appropriately?",
            "Was an alternative offered if same-day not available?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("scheduling", SCHEDULING_SCENARIOS)

# Backward compat: used by vapi_client fallback
SCHEDULING_PROMPT = _VARIANT_0_PROMPT
