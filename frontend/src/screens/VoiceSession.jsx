import { useState } from "react";
import InterventionPanel from "../components/InterventionPanel.jsx";
import TextInput from "../components/TextInput.jsx";
import { useSession } from "../hooks/useSession.js";
import { usePushToTalk } from "../hooks/usePushToTalk.js";

const SPEAKING_STATUSES = ["thinking", "synthesizing_speech"];
const BLOCKING_ACTIONS = new Set(["breathing", "walk_timer"]);

export default function VoiceSession({ mode, onBack }) {
  const { connected, status, intervention, send, sendTextTurn, sendAudioTurn } = useSession();
  const [showTextInput, setShowTextInput] = useState(mode === "text");
  const { recording, startRecording, stopRecording } = usePushToTalk(sendAudioTurn);

  const inputDisabled =
    status === "thinking" ||
    status === "synthesizing_speech" ||
    (!!intervention && BLOCKING_ACTIONS.has(intervention.action));
  const isSpeaking = SPEAKING_STATUSES.includes(status);
  const isIdle = !connected;

  const statusText = isIdle
    ? "Connecting..."
    : recording
    ? "Listening -- release to send"
    : isSpeaking
    ? "baatचीत is speaking..."
    : status === "transcribing"
    ? "Understanding what you said..."
    : "Hold the mic to talk";

  const waveColorClass = isIdle
    ? "bg-outline"
    : recording
    ? "bg-primary"
    : isSpeaking
    ? "bg-secondary"
    : "bg-outline";

  const waveActive = recording || isSpeaking;

  return (
    <div className="bg-background text-on-background h-full min-h-screen flex flex-col antialiased relative">
      <header className="fixed top-0 w-full z-40 flex justify-between items-center px-gutter max-w-screen-xl mx-auto h-16 shadow-sm opacity-80 bg-surface/60 backdrop-blur-xl">
        <button
          onClick={onBack}
          className="text-on-surface-variant hover:opacity-70 transition-opacity p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 className="text-headline-md font-bold tracking-tight text-primary">baatचीत</h1>
        <button
          onClick={() => setShowTextInput((v) => !v)}
          className="text-on-surface-variant hover:opacity-70 transition-opacity p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <span className="material-symbols-outlined">keyboard</span>
        </button>
      </header>

      <main className="flex-1 flex flex-col items-center relative w-full pt-24 pb-6 px-margin-mobile md:px-margin-desktop">
        <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-0">
          <div className="w-[300px] h-[300px] md:w-[500px] md:h-[500px] rounded-full bg-primary-container/10 blur-[60px] md:blur-[100px] animate-ambient-pulse" />
          <div
            className="absolute w-[200px] h-[200px] md:w-[400px] md:h-[400px] rounded-full bg-secondary-container/10 blur-[50px] md:blur-[80px] animate-ambient-pulse"
            style={{ animationDelay: "-2s" }}
          />
        </div>

        <div className="relative z-10 flex flex-col items-center w-full max-w-2xl mx-auto">
          <p className="text-body-md text-primary mb-8 text-center opacity-80 transition-opacity duration-500">
            {statusText}
          </p>

          <div className="flex items-center justify-center gap-2 h-24 w-full max-w-[240px] mb-8">
            {[8, 16, 24, 12, 6].map((height, i) => (
              <div
                key={i}
                className={`wave-bar w-3 rounded-full transition-colors duration-300 ${waveColorClass}`}
                style={{
                  height: `${height * 4}px`,
                  opacity: waveActive ? 0.6 + i * 0.05 : 0.3,
                  animationPlayState: waveActive ? "running" : "paused",
                }}
              />
            ))}
          </div>

          {intervention && (
            <InterventionPanel intervention={intervention} onStop={() => send({ type: "stop_intervention" })} />
          )}
        </div>
      </main>

      <div className="sticky bottom-0 z-20 flex flex-col items-center w-full px-gutter pb-8 pt-4 bg-gradient-to-t from-background via-background/95 to-transparent">
        {showTextInput ? (
          <TextInput onSend={sendTextTurn} disabled={inputDisabled} />
        ) : (
          <>
            <button
              disabled={inputDisabled}
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={() => recording && stopRecording()}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              title="Hold to talk, release to send"
              className={
                "w-16 h-16 rounded-full text-on-primary shadow-[0_10px_30px_rgba(190,216,193,0.2)] flex items-center justify-center transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-primary/30 " +
                (recording
                  ? "bg-secondary scale-110"
                  : inputDisabled
                  ? "bg-primary/40 cursor-not-allowed"
                  : "bg-primary hover:scale-105 active:scale-95")
              }
            >
              <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                mic
              </span>
            </button>
            <button
              onClick={() => setShowTextInput(true)}
              className="mt-4 text-label-md text-on-surface-variant hover:text-primary flex items-center gap-2 transition-colors focus:outline-none py-2 px-4 rounded-full hover:bg-surface-variant/50"
            >
              <span className="material-symbols-outlined text-sm">keyboard</span>
              Switch to Text
            </button>
          </>
        )}
      </div>
    </div>
  );
}
