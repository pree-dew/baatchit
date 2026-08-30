"""Entry point. At this stage: confirms config loads correctly.

Later stages will wire in db.init_db(), audio capture, and the session
state machine here.
"""

import config


def main():
    print("baatchit -- stage 1 scaffold check")
    print(f"  DB path:       {config.DB_PATH}")
    print(f"  Recordings:    {config.RECORDINGS_DIR}")
    print(f"  Sample rate:   {config.SAMPLE_RATE}")
    print(f"  Anthropic key: {'set' if config.ANTHROPIC_API_KEY else 'NOT set'}")
    print(f"  OpenAI key:    {'set' if config.OPENAI_API_KEY else 'NOT set'}")


if __name__ == "__main__":
    main()
