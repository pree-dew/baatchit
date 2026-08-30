import anthropic

import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 512

REFLECT_TOOL = {
    "name": "save_notes",
    "description": "Record any durable, useful observations about this person from this session. Return an empty list if nothing new or noteworthy came up.",
    "input_schema": {
        "type": "object",
        "properties": {
            "notes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["intervention_preference", "feedback_interpretation"],
                        },
                        "note_text": {"type": "string"},
                    },
                    "required": ["category", "note_text"],
                },
            }
        },
        "required": ["notes"],
    },
}

REFLECT_PROMPT = """
You just finished a support conversation with someone. Review what happened
and decide if there's anything genuinely useful to remember about this
specific person for next time -- their preferences, what tends to help or
not help them, or how they tend to express feedback (e.g. downplaying
things). Only note things that are likely to hold true beyond this one
session. If nothing stands out, return an empty list -- don't invent notes
just to have something to say.
"""


def generate_notes(conversation_summary: str, outcome: str) -> list[dict]:
    message = f"{REFLECT_PROMPT}\n\nSession summary:\n{conversation_summary}\n\nOutcome: {outcome}"

    response = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=[REFLECT_TOOL],
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": message}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input["notes"]

    return []
