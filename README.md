# baatchit

A voice-based personal companion agent for in-the-moment emotional support. You talk,
it reads how you're actually feeling (words + voice prosody — pitch, energy, jitter,
shimmer, speaking rate), suggests or runs a short intervention (breathing exercise,
calming music, a walk prompt, distraction, journaling, soothing images), and learns
over time which interventions actually help *you*.

Not a replacement for real relationships or professional help — it's the first response
in the moment, when you're keyed up and don't have anyone to call.

## Why this exists

Most "wellness" apps ask you to open an app, pick a category, and read a static
exercise — friction that's hard to push through when you're actually anxious or upset.
baatchit removes that: you just start talking, the way you would to a person.

**Example — late-night spiral before a deadline**
It's 1am, you're re-reading the same paragraph of a report due in the morning and your
chest is tight. You open baatchit and say what's actually happening: *"I can't focus, I
keep rereading the same line and I'm panicking about tomorrow."* baatchit hears the
words and also picks up the tension in your voice — fast speech, raised pitch. Instead
of a generic "have you tried breathing exercises?", it walks you through a 4-7-8
breathing pace live, ticking the timer with you, then checks in afterward: are you
calmer, or still keyed up? If breathing didn't help last time, it won't lead with that
next time — it tries music or a short walk prompt instead, because it remembers what
actually worked for you.

**Example — venting after a hard conversation**
You just got off a call that went badly and you need to get it out of your system
before you can think straight. You talk it through out loud. baatchit mostly just
listens and reflects back — it recognizes from your prosody that you're venting, not
asking for a fix, and doesn't jump straight to an intervention. Only once your voice
settles does it offer something concrete, like a short journaling prompt to close the
loop on what you're feeling.

**Example — can't stay in your body, need a distraction**
You're anxious in a way that breathing doesn't touch — you need to *not* be in your
head for a few minutes. You say so, and it switches to a quick distraction exercise or
puts on soothing imagery instead of another exercise, because it's tracked that
distraction has worked better for you than breathing does when you're in this specific
state.

Over repeated sessions it builds a personality profile (via short reflective notes
after each conversation) and an outcome score per intervention type, so the same
message next month gets a response shaped by what's actually worked for you, not a
one-size-fits-all script.

## Project structure

- `web/` — FastAPI backend: WebSocket session endpoint (`/ws/session`), audio streaming
  endpoints, and intervention rendering for the browser client.
- `frontend/` — React + Vite + Tailwind UI: push-to-talk recording, live status, and
  intervention panels (breathing pace, walk timer, music player, soothing images).
- `state_machine/` — Conversation stage tracking (venting → intervention → monitoring →
  checking in → closing) and the improvement detector that decides when to check in.
- `llm/` — Talks to the LLM (tool-calling agent) for turn responses, and generates
  reflective personality notes after each session.
- `interventions/` — Implementations of breathing, walk timer, music, distraction,
  journal, and soothing-image interventions.
- `prosody/` — Extracts voice features (pitch, energy, jitter, shimmer, speaking rate,
  pause ratio) from recorded audio.
- `stt/` / `tts/` — Speech-to-text transcription and text-to-speech synthesis.
- `scoring/` — Exponential-moving-average scores per intervention type/emotion, used to
  bias which intervention gets suggested next.
- `db/` — SQLite persistence (sessions, utterances, interventions, feedback,
  personality notes).
- `baseline/` — Prosody-to-language description helpers (e.g. "fast and tense" vs.
  "steady").

## Setup

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in ANTHROPIC_API_KEY / OPENAI_API_KEY
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env   # optional -- only needed if tunneling the backend separately
```

## Run locally

Start the backend (FastAPI + WebSocket server) from the project root:

```bash
source .venv/bin/activate
uvicorn web.app:app --reload --port 8765
```

In a separate terminal, start the frontend dev server:

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`), allow microphone access,
and hold the push-to-talk button to start a conversation.
