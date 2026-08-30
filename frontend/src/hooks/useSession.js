import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8765/ws/session";
export const HTTP_BASE = WS_URL.replace(/^ws/, "http").replace(/\/ws\/session$/, "");

export function useSession() {
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("idle");
  const [messages, setMessages] = useState([]);
  const [intervention, setIntervention] = useState(null);
  const [sessionOutcome, setSessionOutcome] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    const playAudioAndAck = (url) => {
      const audio = new Audio(`${HTTP_BASE}${url}`);
      audio.style.display = "none";
      document.body.appendChild(audio);
      const ack = () => {
        ws.send(JSON.stringify({ type: "audio_finished" }));
        audio.remove();
      };
      audio.onended = ack;
      audio.onerror = ack;
      audio.play().catch((err) => {
        console.error("Audio playback failed:", err);
        ack();
      });
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "status":
          setStatus(data.value);
          break;
        case "transcript":
          setMessages((prev) => [...prev, { role: data.role, text: data.text }]);
          break;
        case "intervention_started":
          setIntervention({ action: data.action, args: data.args, tickState: null });
          break;
        case "intervention_tick":
          setIntervention((prev) => (prev ? { ...prev, tickState: data.state } : prev));
          break;
        case "intervention_media":
          setIntervention((prev) =>
            prev ? { ...prev, media: { type: data.media_type, url: data.url, data: data.data } } : prev
          );
          break;
        case "intervention_ended":
          setIntervention(null);
          break;
        case "session_closed":
          setSessionOutcome(data.outcome);
          break;
        case "audio":
          playAudioAndAck(data.url);
          break;
        default:
          break;
      }
    };

    return () => ws.close();
  }, []);

  const send = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const sendTextTurn = useCallback(
    (text) => {
      setMessages((prev) => [...prev, { role: "user", text }]);
      send({ type: "text_turn", text });
    },
    [send]
  );

  const sendAudioTurn = useCallback(
    (base64Audio) => {
      send({ type: "audio_turn", data: base64Audio });
    },
    [send]
  );

  return {
    connected,
    status,
    messages,
    intervention,
    sessionOutcome,
    send,
    sendTextTurn,
    sendAudioTurn,
  };
}
