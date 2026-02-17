"""
Edge-case scenarios: stress-test the agent with confusing, off-topic, or
adversarial inputs. Inspired by real bugs found during manual testing.

3 variants targeting specific weaknesses:
  0 — Off-topic / unstructured conversation
  1 — Confusing / contradictory requests (repeated questions, mind changes)
  2 — Multiple appointments in one call (two providers)
"""

from scenario_manager import ScenarioConfig, register_scenarios


# ---------------------------------------------------------------------------
# Variant 0: Off-topic / unstructured conversation
#
# Purpose: Tests how the agent behaves when Sarah goes off-topic, chats
# about unrelated things, or drifts away from the main task. We want to see
# if it stays professional, gently steers back, and avoids hallucinating
# answers to off-topic questions.
# ---------------------------------------------------------------------------
_VARIANT_0_PROMPT = """
# WHY YOU ARE CALLING
You vaguely want to "check in" about your knee, but you are easily
distracted and prone to talking about unrelated topics (weather, family,
random thoughts). You are not trying to be rude — just chatty and a bit
unstructured.

# YOUR BEHAVIOR IN THIS CALL
- You start with something like: "Hi, I wanted to talk about my knee, but
  also just had a couple of questions."
- As the agent asks questions, you occasionally:
  - Go off on tangents (e.g. "By the way, have you seen the game last
    night?" or "I’ve been thinking about getting a dog."),
  - Bring up unrelated personal details (work, travel plans),
  - Ask small-talk questions that the clinic wouldn't normally answer.

You are testing whether the agent:
- Politely acknowledges but doesn't get lost in off-topic conversations,
- Gently redirects back to the purpose of the call,
- Avoids making up answers to things it shouldn't know.

# YOUR GOAL
You are less focused on booking something and more on observing behavior:
- Does the agent stay professional and on-task?
- Does it avoid hallucinating personal opinions or external facts it
  shouldn't provide?

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I wanted to check in about my knee, but also had a couple of
  other questions."

During the call:
- Let the agent ask a question, then answer but drift: mix 1–2 relevant
  details with an off-topic comment.
- If the agent fully follows you into unrelated topics, continue a bit but
  then circle back: "Anyway, about my knee..."
- If the agent firmly but politely redirects, cooperate and answer.

Before ending:
- You can either let the call end without a booking (that's okay) or
  accept an appointment if the agent proposes one; the main purpose is to
  see how it handled the off-topic nature of the conversation.
""".strip()


# ---------------------------------------------------------------------------
# Variant 1: Confusing / contradictory requests (repeated questions)
#
# Purpose: Tests how the agent handles inconsistent information, repeated
# questions, and mid-stream changes of mind — matching your notes about
# confusing scenarios and repeated questions.
# ---------------------------------------------------------------------------
_VARIANT_1_PROMPT = """
# WHY YOU ARE CALLING
You genuinely want help with scheduling or rescheduling, but you are
indecisive and a bit scattered. You will:
- Repeat questions,
- Change your mind about details,
- Occasionally contradict yourself.

The goal is to see if the agent stays calm, asks for clarification, and
avoids blindly accepting contradictory info.

# YOUR BEHAVIOR IN THIS CALL
- Ask the same question in slightly different ways, e.g.:
  "So what time is it again?" / "Wait, what time did you say?" multiple
  times.
- Give one date, then later say a different date without acknowledging
  the change, e.g.:
  - First: "I think Tuesday works best."
  - Later: "Actually I said Thursday, right?" (even if you didn't.)
- If the agent doesn't notice, push a bit: "I'm confused — I thought we
  said Thursday?"

# YOUR GOAL
Check if the agent:
- Notices when details change,
- Politely asks: "Just to confirm, which day do you want — Tuesday or
  Thursday?",
- Clearly summarizes the final decision instead of ending with ambiguity.

# HOW TO HANDLE THIS CALL
Opening:
- Say: "Hi, I need to figure out my appointment, but I'm a little all
  over the place on timing."

During the call:
- Give one set of details, then softly contradict them later.
- Ask the same "what time / what day" question more than once.
- If the agent confidently states something you know you didn't say,
  question it: "Wait, I don’t remember agreeing to that."

Before ending:
- Force a clear summary: "Can you just summarize what we ended up with —
  what day and time, and what exactly will happen?"
""".strip()


# ---------------------------------------------------------------------------
# Variant 2: Multiple appointments in one call (two providers)
#
# Purpose: Schedule “two appointments within 2 weeks with different
# providers” scenario here as an explicit edge case. Tests whether the
# agent can:
# - Book TWO distinct appointments in one call,
# - Keep providers and times separate,
# - Not overwrite or drop the first when booking the second.
# ---------------------------------------------------------------------------
_VARIANT_2_PROMPT = """
# WHY YOU ARE CALLING
You want to schedule TWO appointments at Pivot Point Orthopedics in the
same call, both within the next 2 weeks, with two different providers.

# YOUR MEDICAL SITUATION
- You have an ongoing knee issue and also a separate shoulder issue.
- You want:
  1) A knee appointment with a knee specialist.
  2) A shoulder appointment with a shoulder or upper-extremity specialist.

# YOUR PREFERENCES
- Both appointments should be within the next 2 weeks.
- You prefer mornings for the knee appointment and afternoons for the
  shoulder appointment, but you are flexible as long as they are not at
  the same time.

# YOUR GOAL
Get TWO distinct, clearly confirmed appointments:
- Each with its own date, time, and provider name.
- The providers should be different people (not the same doctor twice),
  unless the agent clearly explains that one doctor covers both.

You want to see whether the agent is capable of:
- Handling multiple appointments in one call, and
- Not losing or overwriting the first appointment when booking the second.

# HOW TO HANDLE THIS CALL
Opening:
- Say something like: "Hi, I'd like to schedule a couple of appointments
  at Pivot Point Orthopedics."

During the call:
1) First appointment (knee):
   - Explain: "I have a knee issue I'd like to get checked."
   - Ask for an appointment within the next 2 weeks, preferably in the
     morning.
   - Make sure they confirm date, time, and provider name.

2) Second appointment (shoulder):
   - After the first is confirmed, say clearly: "I'd also like to book a
     separate appointment for my shoulder."
   - Ask for a different day or time, still within the next 2 weeks,
     preferably in the afternoon.
   - Ask if this will be with a different provider: "Will that be with a
     different doctor or the same one?"

If they try to put both issues into one appointment:
- Gently push back: "I was hoping to have separate visits if possible —
  one focused on the knee and one on the shoulder."

If they seem unsure whether both got booked:
- Ask them to repeat back both appointments:
  "Can you please confirm both appointments — dates, times, and providers?"

Before ending:
- Make sure you can clearly state both appointments:
  - "So I have a knee appointment on [day/time] with [doctor A], and a
     shoulder appointment on [day/time] with [doctor B], correct?"
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
