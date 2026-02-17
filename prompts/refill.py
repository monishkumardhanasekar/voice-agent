"""
Medication refill scenarios: patient calls to refill a prescription.

3 variants testing different refill situations.
Prompt content will be written properly in the prompt-writing step.
"""

from scenario_manager import ScenarioConfig, register_scenarios

# ---------------------------------------------------------------------------
# Variant 0: Standard refill request
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient needs a routine medication refill for blood pressure meds.
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: Refill with dosage question
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient asks about dosage or side effects during refill request.
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Refill for a medication that may need doctor approval
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient requests refill that requires doctor sign-off.
""".strip()

# ---------------------------------------------------------------------------
# Register with scenario_manager
# ---------------------------------------------------------------------------
REFILL_SCENARIOS = [
    ScenarioConfig(
        id="refill_standard",
        category="refill",
        variant=0,
        name="Standard medication refill",
        goal="Successfully request a refill and get confirmation or clear next steps.",
        eval_hints=[
            "Did the agent collect medication name?",
            "Did the agent verify patient identity?",
            "Was a clear outcome provided (refill confirmed or next step)?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="refill_dosage_question",
        category="refill",
        variant=1,
        name="Refill with dosage question",
        goal="Get refill processed and dosage question answered or escalated properly.",
        eval_hints=[
            "Did the agent handle the medical question appropriately?",
            "Was the refill still processed?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="refill_needs_approval",
        category="refill",
        variant=2,
        name="Refill needing doctor approval",
        goal="Understand that approval is needed and get clear timeline or next steps.",
        eval_hints=[
            "Did the agent explain the approval process?",
            "Was a callback or timeline provided?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("refill", REFILL_SCENARIOS)
