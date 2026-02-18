"""
Office information scenarios: patient asks about hours, location, insurance, etc.

3 variants testing general information handling:
  0 — Office hours, address, and parking (basic info)
  1 — Insurance acceptance and billing questions
  2 — Available doctors and specialties
"""

from scenario_manager import ScenarioConfig, register_scenarios


# ---------------------------------------------------------------------------
# Variant 0: Office hours, address, and parking
#
# Purpose: Simple information request. Tests whether the agent can provide
# accurate, non-hallucinated info about when and where to come, and how to
# get there (including parking / building details).
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
# WHY YOU ARE CALLING
You want basic information about the clinic so you know when they are open
and how to get there. You are not trying to schedule in this call, only to
understand logistics.

# WHAT YOU WANT TO KNOW
- Office hours (weekday schedule, weekend/holiday if relevant)
- Full address (street, city, state, ZIP)
- Any key details about:
  - Parking (lot vs street, paid vs free)
  - Building entrance (which floor, suite number, landmarks)

# YOUR GOAL
End the call with:
- Clear office hours you can repeat back,
- A usable address you could plug into your maps app,
- Any important parking/entry instructions.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "I was just calling to get your office hours and where exactly
  you're located."

During the call:
- If they only give partial info (e.g. just a street name), ask for the
  full address including city and ZIP.
- Ask a natural follow-up: "Is there parking on-site?" or "Is there a
  parking garage or street parking nearby?"
- If they mention multiple locations, ask which one they recommend for
  your orthopedic visit.

Before ending:
- Repeat back what you heard: "So you're open from [hours] at [address],
  and parking is [description], right?"
""".strip()


# ---------------------------------------------------------------------------
# Variant 1: Insurance and billing questions
#
# Purpose: Tests whether the agent can handle common insurance questions
# without hallucinating specifics. It should:
# - Confirm whether your plan is generally accepted (or not),
# - Explain any need to verify details (e.g. plan ID, copay),
# - Avoid making up exact prices when it shouldn't.
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
# YOUR INSURANCE
You have Blue Cross Blue Shield PPO, as described in the base persona.

# WHY YOU ARE CALLING
You want to know:
- Whether Pivot Point Orthopedics accepts your insurance, and
- Roughly what to expect for copay or out-of-pocket costs for a visit.

# YOUR GOAL
Get:
- A clear "yes" or "no" on whether your insurance is accepted, OR a clear
  explanation if they need more information to be sure.
- Any high-level info they are allowed to give about copays or billing,
  OR a clear handoff to billing staff/website if they cannot quote it.

You are specifically watching for:
- Confident but wrong statements ("Yes we definitely cover everything"),
- Hallucinated dollar amounts pulled out of nowhere.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "I just wanted to check if you take Blue Cross Blue Shield PPO,
  and what I might expect for a copay."

During the call:
- If they just say "we take most insurances," ask directly:
  "Do you specifically take Blue Cross Blue Shield PPO?"
- If they cannot give exact numbers, that is okay — ask what they CAN say:
  "Is there a typical copay range, or should I call the number on my card?"
- If they give very specific dollar amounts confidently, accept the answer
  but mentally flag it — we will later judge whether that seems realistic.

Before ending:
- Restate the plan:
  "So you do take Blue Cross Blue Shield PPO, and for exact copay info I
   should [check my card / your billing department / your portal], right?"
""".strip()


# ---------------------------------------------------------------------------
# Variant 2: Available doctors and specialties
#
# Purpose: Tests whether the agent can talk concretely about the types of
# doctors at Pivot Point Orthopedics (knee, spine, shoulder, etc.) without
# inventing fake specialties. Also checks if it can name actual providers
# and match them to body areas.
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
# WHY YOU ARE CALLING
You are trying to figure out which doctor you should see at Pivot Point
Orthopedics. You want to understand:
- What kinds of specialists they have (knee, hip, spine, shoulder, hand),
- Which doctors focus on which areas.

You are not booking yet (unless they insist). You mainly want good
information to choose the right provider later.

# YOUR GOAL
End the call with:
- At least one or two specific doctor names and what they specialize in,
- A clear sense of whether they have a doctor suitable for YOUR issue
  (e.g. knee pain, meniscus tear, shoulder pain, spine issues).

You are watching out for:
- Vague answers ("all our doctors see everything"),
- Inconsistent or obviously made-up specialties.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "I was wondering which doctors you have there and what they
  specialize in. I'm trying to figure out who I should see."

During the call:
- Describe your issue briefly: "I've been having knee pain and was told I
  might need an orthopedic specialist."
- Ask directly: "Do you have someone who focuses on knees? What’s their
  name?" and similar for other body parts if relevant.
- If they say "any of our doctors can see you," ask:
  "Is there anyone who especially focuses on knees / shoulders / spine?"

Before ending:
- Summarize: "So for my knee I could see Dr. [Name], who focuses on [area],
  and for spine there is Dr. [Name], right?"
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
