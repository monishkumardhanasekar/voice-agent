"""
Edge-case scenarios: stress-test the agent with confusing, off-topic, or
adversarial inputs. Inspired by real bugs found during manual testing.

3 variants targeting specific weaknesses.
Prompt content will be written properly in the prompt-writing step.
"""

from scenario_manager import ScenarioConfig, register_scenarios

# ---------------------------------------------------------------------------
# Variant 0: Off-topic / unstructured conversation
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient goes off-topic, talks about unrelated things, tests
whether the agent can steer back or handle gracefully.
""".strip()

# ---------------------------------------------------------------------------
# Variant 1: Confusing / contradictory requests (repeated questions)
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient gives contradictory info, repeats questions, changes
their mind. Tests agent's ability to handle confusion without breaking.
""".strip()

# ---------------------------------------------------------------------------
# Variant 2: Multiple appointments in one call
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
TODO: Prompt will be written in the prompt-writing step.
Scenario: Patient tries to book multiple appointments in a single call.
Tests whether the agent handles this correctly or drops one.
""".strip()

# ---------------------------------------------------------------------------
# Register with scenario_manager
# ---------------------------------------------------------------------------
EDGE_CASE_SCENARIOS = [
    ScenarioConfig(
        id="edge_off_topic",
        category="edge_cases",
        variant=0,
        name="Off-topic unstructured conversation",
        goal="Agent handles off-topic input gracefully without breaking or hallucinating.",
        eval_hints=[
            "Did the agent stay professional?",
            "Did it redirect to the task or handle gracefully?",
            "Did it hallucinate information?",
        ],
        prompt_block=_VARIANT_0_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="edge_confusing_contradictory",
        category="edge_cases",
        variant=1,
        name="Confusing and contradictory requests",
        goal="Agent asks for clarification and doesn't blindly accept contradictions.",
        eval_hints=[
            "Did the agent notice contradictions?",
            "Did it ask clarifying questions?",
            "Did it loop or get stuck?",
        ],
        prompt_block=_VARIANT_1_PROMPT,
        first_message="Hello.",
    ),
    ScenarioConfig(
        id="edge_multiple_appointments",
        category="edge_cases",
        variant=2,
        name="Multiple appointments in one call",
        goal="Both appointments are booked correctly, or agent clearly explains limitations.",
        eval_hints=[
            "Were both appointments acknowledged?",
            "Were they booked at different times?",
            "Did the agent confirm both or explain why not?",
        ],
        prompt_block=_VARIANT_2_PROMPT,
        first_message="Hello.",
    ),
]

register_scenarios("edge_cases", EDGE_CASE_SCENARIOS)
