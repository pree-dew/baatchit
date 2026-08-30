import re

CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bkilling myself\b",
    r"\bwant to die\b",
    r"\bwanna die\b",
    r"\bsuicid\w*\b",
    r"\bend my life\b",
    r"\b(not|don'?t|dont)\s+want(ing)?\s+to\s+be\s+alive\b",
    r"\bharm(ing)? myself\b",
    r"\bhurt(ing)? myself\b",
    r"\bself[\s-]harm\w*\b",
    r"\bno reason to live\b",
    r"\bbetter off dead\b",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CRISIS_PATTERNS]

CRISIS_RESPONSE_TEXT = (
    "It sounds like you're going through something really heavy right now, "
    "and I want to take that seriously. I'm not able to give you the kind of "
    "support that's needed here, but please reach out to someone who can -- "
    "a crisis line, a therapist, or someone you trust, right now if you can. "
    "You can call KIRAN, India's free 24/7 mental health helpline, at "
    "1800-599-0019, anytime, in multiple languages. You don't have to go "
    "through this alone."
)


def check_for_crisis(transcript: str) -> bool:
    return any(pattern.search(transcript) for pattern in _COMPILED_PATTERNS)
