"""
Rescheduling scenarios: patient calls to change or cancel an existing appointment.

3 variants covering different rescheduling/cancellation behaviors.
Prompt content will be written properly in the prompt-writing step.
"""

from scenario_manager import ScenarioConfig, register_scenarios

# ---------------------------------------------------------------------------
# Variant 0: Simple reschedule to a different day
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient has an existing appointment and wants to move it to a different day.
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: Reschedule with a sudden day change mid-conversation
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient picks a day then suddenly changes to another day before
confirming. Tests whether agent asks reason and handles the switch properly.
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Cancel appointment (tests different cancellation paths)
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient wants to cancel. Tests whether cancellation works consistently.
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
