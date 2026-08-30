import anthropic

import config
from llm import safety
from llm.prompts import build_system_prompt
from llm.tools import get_tool_by_name, get_tools_for_stage

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1024


def get_response(
    transcript: str,
    conversation_history: list[dict],
    stage: str,
    personality_notes: list[str],
    prosody_context: str,
    intervention_scores: list[dict],
    forced_tool: str | None = None,
) -> dict:
    if safety.check_for_crisis(transcript):
        return {
            "action": "crisis_response",
            "spoken_text": safety.CRISIS_RESPONSE_TEXT,
        }

    system_prompt = build_system_prompt(stage, personality_notes, prosody_context, intervention_scores)
    tools = [get_tool_by_name(forced_tool)] if forced_tool else get_tools_for_stage(stage)

    messages = conversation_history + [{"role": "user", "content": transcript}]

    response = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        tools=tools,
        tool_choice={"type": "any"},
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use":
            return {
                "action": block.name,
                **block.input,
            }

    raise RuntimeError("Model did not call a tool despite tool_choice=any")
