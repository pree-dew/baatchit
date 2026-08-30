import { useEffect, useRef, useState } from "react";

import { HTTP_BASE } from "../hooks/useSession.js";

const PHASE_SCALE = {
  "Breathe in": "scale-125",
  Hold: "scale-125",
  "Breathe out": "scale-75",
};

function BreathingCircle({ tickState }) {
  const scale = tickState ? PHASE_SCALE[tickState.phase] || "scale-100" : "scale-100";
  return (
    <div className="flex flex-col items-center gap-6">
      <div
        className={`w-40 h-40 rounded-full bg-primary/30 border-2 border-primary flex items-center justify-center transition-transform duration-[1000ms] ease-in-out ${scale}`}
      >
        <span className="text-headline-md text-primary font-semibold">
          {tickState ? tickState.seconds_remaining : ""}
        </span>
      </div>
      <p className="text-body-lg text-on-surface">{tickState ? tickState.phase : "Starting..."}</p>
      {tickState && (
        <p className="text-label-sm text-on-surface-variant uppercase tracking-wide">
          Cycle {tickState.cycle} of {tickState.total_cycles}
        </p>
      )}
    </div>
  );
}

function WalkTimer({ tickState }) {
  if (!tickState) return <p className="text-body-lg text-on-surface">Starting your walk timer...</p>;
  const minutes = Math.floor(tickState.remaining_seconds / 60);
  const seconds = tickState.remaining_seconds % 60;
  return (
    <div className="flex flex-col items-center gap-4">
      <span className="text-display-lg text-primary font-bold">
        {minutes}:{String(seconds).padStart(2, "0")}
      </span>
      <p className="text-body-md text-on-surface-variant">Take your time -- there's no rush.</p>
    </div>
  );
}

function MusicPlayer({ media }) {
  const audioRef = useRef(null);

  useEffect(() => {
    if (media && audioRef.current) {
      audioRef.current.play().catch((err) => console.error("Music playback failed:", err));
    }
  }, [media]);

  if (!media) {
    return <p className="text-body-lg text-on-surface">Getting a track ready for you...</p>;
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-sm">
      <span className="material-symbols-outlined text-5xl text-primary">music_note</span>
      <p className="text-body-md text-on-surface-variant">Playing something for you</p>
      <audio ref={audioRef} controls className="w-full" src={`${HTTP_BASE}${media.url}`} />
    </div>
  );
}

function SoothingImage({ media }) {
  const [loaded, setLoaded] = useState(false);

  if (!media) {
    return (
      <div className="flex flex-col items-center gap-4">
        <span className="material-symbols-outlined text-5xl text-primary animate-ambient-pulse">
          image
        </span>
        <p className="text-body-lg text-on-surface">Finding something calming for you...</p>
      </div>
    );
  }

  return (
    <div className="relative w-full max-w-2xl">
      <div
        className="absolute -inset-6 rounded-[2rem] bg-gradient-to-br from-primary-container/30 to-secondary-container/30 blur-2xl animate-ambient-pulse"
        aria-hidden="true"
      />
      <div className="relative rounded-[1.75rem] p-1.5 bg-gradient-to-br from-primary/40 via-surface-variant/40 to-secondary/40 shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
        <img
          src={`data:image/png;base64,${media.data}`}
          alt="A calming scene"
          onLoad={() => setLoaded(true)}
          className={`rounded-[1.4rem] w-full max-h-[65vh] object-cover transition-all duration-700 ease-out ${
            loaded ? "opacity-100 scale-100" : "opacity-0 scale-[0.98]"
          }`}
        />
      </div>
      <p className="text-label-sm text-on-surface-variant text-center mt-4 tracking-wide uppercase opacity-70">
        Take a slow breath and let your eyes rest here
      </p>
    </div>
  );
}

const ACTION_LABELS = {
  distraction: "Here's a little distraction",
  journal: "A prompt to reflect on",
};

function GenericIntervention({ action }) {
  return (
    <div className="flex flex-col items-center gap-4">
      <span className="material-symbols-outlined text-5xl text-primary">spa</span>
      <p className="text-body-lg text-on-surface">{ACTION_LABELS[action] || "In progress..."}</p>
    </div>
  );
}

export default function InterventionPanel({ intervention, onStop }) {
  const { action, tickState, media } = intervention;

  const imageAlreadyShown = action === "soothing_images" && !!media;

  return (
    <div className="w-full flex flex-col items-center gap-8 mb-8">
      {action === "breathing" && <BreathingCircle tickState={tickState} />}
      {action === "walk_timer" && <WalkTimer tickState={tickState} />}
      {action === "music" && <MusicPlayer media={media} />}
      {action === "soothing_images" && <SoothingImage media={media} />}
      {action !== "breathing" &&
        action !== "walk_timer" &&
        action !== "music" &&
        action !== "soothing_images" && <GenericIntervention action={action} />}

      {!imageAlreadyShown && (
        <button
          onClick={onStop}
          className="text-label-md text-on-surface-variant hover:text-error border border-outline-variant/50 hover:border-error/50 rounded-full px-6 py-2 transition-colors"
        >
          Stop
        </button>
      )}
    </div>
  );
}
