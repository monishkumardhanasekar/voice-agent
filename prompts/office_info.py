"""
Office information scenarios: patient asks about hours, location, insurance, etc.

3 variants testing general information handling.
Prompt content will be written properly in the prompt-writing step.
"""

from scenario_manager import ScenarioConfig, register_scenarios

# ---------------------------------------------------------------------------
# Variant 0: Ask about office hours and location
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient asks about office hours, directions, parking.
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: Insurance and billing questions
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient asks whether their insurance is accepted, copay info.
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Ask about available doctors / specialties
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient asks about which doctors are available and their specialties.
""".strip()

# ---------------------------------------------------------------------------
# Register with scenario_manager
# ---------------------------------------------------------------------------
OFFICE_INFO_SCENARIOS = [
    ScenarioConfig(
        id="office_info_hours_location",
        category="office_info",
        variant=0,
        name="Office hours and location",
        goal="Get accurate office hours, address, and directions.",
        eval_hints=[
            "Were office hours provided?",
            "Was address or directions given?",
            "Was information consistent and not hallucinated?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="office_info_insurance",
        category="office_info",
        variant=1,
        name="Insurance and billing questions",
        goal="Get clear answer about insurance acceptance and any cost info.",
        eval_hints=[
            "Did the agent confirm insurance acceptance?",
            "Was copay or billing info addressed?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="office_info_doctors",
        category="office_info",
        variant=2,
        name="Available doctors and specialties",
        goal="Get names and specialties of available doctors.",
        eval_hints=[
            "Were specific doctor names provided?",
            "Were specialties mentioned?",
            "Was the info consistent (not hallucinated)?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("office_info", OFFICE_INFO_SCENARIOS)
