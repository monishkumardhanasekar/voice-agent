"""
Scenario manager: loads scenarios, composes prompts, and provides metadata.

Each scenario is a Python module in prompts/ that exports a list of
ScenarioConfig dicts. The manager combines the stable base persona with
a scenario-specific prompt block to produce the final system prompt.

Usage:
    from scenario_manager import get_scenario, list_scenarios, build_prompt

    scenario = get_scenario("scheduling", variant=0)
    full_prompt = build_prompt(scenario)
"""

from dataclasses import dataclass, field
from typing import Optional

from prompts.base_prompt import BASE_PROMPT


@dataclass(frozen=True)
class ScenarioConfig:
    """Immutable description of a single test scenario (one call)."""

    # Identity
    id: str                         # e.g. "scheduling_knee_pain"
    category: str                   # e.g. "scheduling", "rescheduling", "refill"
    variant: int                    # index within category (0, 1, 2)
    name: str                       # human-readable label

    # What the evaluator needs
    goal: str                       # success criteria for this call
    eval_hints: list[str] = field(default_factory=list)  # things to check

    # Prompt
    prompt_block: str = ""          # scenario-specific text injected after base
    first_message: str = "Hello."   # what the patient says first


# ---------------------------------------------------------------------------
# Registry: maps category -> list of ScenarioConfig
# Populated by register_scenarios() calls from each prompt module.
# ---------------------------------------------------------------------------
_REGISTRY: dict[str, list[ScenarioConfig]] = {}


def register_scenarios(category: str, scenarios: list[ScenarioConfig]) -> None:
    """Register a list of scenarios under a category (called by prompt modules)."""
    _REGISTRY[category] = scenarios


def _ensure_loaded() -> None:
    """Import all prompt modules so they register their scenarios."""
    if _REGISTRY:
        return
    # Each module's top-level code calls register_scenarios()
    import prompts.scheduling  # noqa: F401
    import prompts.rescheduling  # noqa: F401
    import prompts.refill  # noqa: F401
    import prompts.office_info  # noqa: F401
    import prompts.edge_cases  # noqa: F401


def list_categories() -> list[str]:
    """Return all registered scenario category names."""
    _ensure_loaded()
    return list(_REGISTRY.keys())


def list_scenarios(category: Optional[str] = None) -> list[ScenarioConfig]:
    """Return scenarios, optionally filtered by category."""
    _ensure_loaded()
    if category:
        return _REGISTRY.get(category, [])
    return [s for group in _REGISTRY.values() for s in group]


def get_scenario(category: str, variant: int = 0) -> ScenarioConfig:
    """
    Get a specific scenario by category and variant index.

    Raises KeyError if category not found, IndexError if variant out of range.
    """
    _ensure_loaded()
    if category not in _REGISTRY:
        raise KeyError(
            f"Unknown scenario category '{category}'. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    variants = _REGISTRY[category]
    if variant < 0 or variant >= len(variants):
        raise IndexError(
            f"Variant {variant} out of range for '{category}' "
            f"(has {len(variants)} variants: 0-{len(variants)-1})"
        )
    return variants[variant]


def build_prompt(scenario: ScenarioConfig) -> str:
    """
    Compose the full system prompt: base persona + scenario block.

    The base prompt ends with "# SCENARIO INSTRUCTIONS" header.
    The scenario's prompt_block is appended after it.
    """
    return f"{BASE_PROMPT}\n\n{scenario.prompt_block}"
