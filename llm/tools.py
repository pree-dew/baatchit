_SPOKEN_TEXT_PROPERTY = {
    "spoken_text": {
        "type": "string",
        "description": "What to say out loud right now, in your own natural words.",
    }
}

_EMOTION_PROPERTY = {
    "emotion": {
        "type": "string",
        "enum": ["anxiety", "anger", "sadness", "stress", "exhaustion", "irritation"],
        "description": "The primary emotion this action is addressing right now.",
    }
}

TOOLS = [
    {
        "name": "breathing",
        "description": "Guide the person through a paced breathing exercise. Use when slowing down their physical state would help.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "pace": {
                    "type": "string",
                    "enum": ["4-7-8", "box", "simple_slow"],
                    "description": "The breathing pattern to guide them through.",
                },
            },
            "required": ["spoken_text", "emotion", "pace"],
        },
    },
    {
        "name": "music",
        "description": "Suggest music matched to what would help their mood right now.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "mood": {
                    "type": "string",
                    "enum": ["calming", "upbeat", "instrumental"],
                    "description": "The mood of music to suggest.",
                },
            },
            "required": ["spoken_text", "emotion", "mood"],
        },
    },
    {
        "name": "walk_timer",
        "description": "Suggest a short walk or physical break, with a timer.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "duration_minutes": {
                    "type": "integer",
                    "description": "How long the walk/break should be, in minutes.",
                },
            },
            "required": ["spoken_text", "emotion", "duration_minutes"],
        },
    },
    {
        "name": "distraction",
        "description": "Offer a light distraction to shift focus away from the stressor briefly. spoken_text must contain the actual trivia question, word game prompt, or conversation starter itself, in full -- not just an announcement that a game is coming.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "style": {
                    "type": "string",
                    "enum": ["trivia", "word_game", "light_conversation"],
                    "description": "The kind of distraction to offer.",
                },
            },
            "required": ["spoken_text", "emotion", "style"],
        },
    },
    {
        "name": "journal",
        "description": "Offer a journaling prompt for reflection, when writing might help more than talking. spoken_text must contain the actual journaling prompt itself, in full -- not just an announcement that a prompt is coming.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "prompt_theme": {
                    "type": "string",
                    "enum": ["gratitude", "venting", "reframing"],
                    "description": "The theme of the journaling prompt.",
                },
            },
            "required": ["spoken_text", "emotion", "prompt_theme"],
        },
    },
    {
        "name": "soothing_images",
        "description": "Show calming imagery, for a lower-intensity option than an active exercise.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                **_EMOTION_PROPERTY,
                "theme": {
                    "type": "string",
                    "enum": ["nature", "ocean", "soft_abstract"],
                    "description": "The theme of imagery to show.",
                },
            },
            "required": ["spoken_text", "emotion", "theme"],
        },
    },
    {
        "name": "just_listen",
        "description": "Hold space without taking action yet -- either acknowledge warmly, or ask at most one gentle follow-up question if more understanding is genuinely needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                "mode": {
                    "type": "string",
                    "enum": ["acknowledge", "ask_question"],
                    "description": "Whether spoken_text is a pure acknowledgment or contains one gentle question.",
                },
            },
            "required": ["spoken_text", "mode"],
        },
    },
    {
        "name": "check_in",
        "description": "Ask naturally whether the last thing you did together helped. Only available once enough time/signal has passed since an intervention.",
        "input_schema": {
            "type": "object",
            "properties": _SPOKEN_TEXT_PROPERTY,
            "required": ["spoken_text"],
        },
    },
    {
        "name": "close_session",
        "description": "End the session with a warm goodbye, once feedback on the last intervention has been resolved.",
        "input_schema": {
            "type": "object",
            "properties": {
                **_SPOKEN_TEXT_PROPERTY,
                "outcome": {
                    "type": "string",
                    "enum": ["helped", "not_helped"],
                    "description": "Whether the last intervention helped, based on what the person said.",
                },
            },
            "required": ["spoken_text", "outcome"],
        },
    },
]

TOOLS_BY_STAGE = {
    "venting": ["just_listen", "breathing", "music", "walk_timer", "distraction", "journal", "soothing_images"],
    "intervening": ["breathing", "music", "walk_timer", "distraction", "journal", "soothing_images"],
    "monitoring": ["just_listen", "breathing", "music", "walk_timer", "distraction", "journal", "soothing_images"],
    "checking_in": ["check_in"],
    "closing": ["close_session", "just_listen"],
}


def get_tools_for_stage(stage: str) -> list[dict]:
    allowed_names = TOOLS_BY_STAGE[stage]
    return [tool for tool in TOOLS if tool["name"] in allowed_names]


def get_tool_by_name(name: str) -> dict:
    return next(tool for tool in TOOLS if tool["name"] == name)
