import { useState } from "react";
import ModeSelect from "./screens/ModeSelect.jsx";
import VoiceSession from "./screens/VoiceSession.jsx";
import Welcome from "./screens/Welcome.jsx";

const SCREENS = {
  WELCOME: "welcome",
  MODE_SELECT: "mode_select",
  SESSION: "session",
};

export default function App() {
  const [screen, setScreen] = useState(SCREENS.WELCOME);
  const [mode, setMode] = useState("voice");

  if (screen === SCREENS.WELCOME) {
    return <Welcome onBegin={() => setScreen(SCREENS.MODE_SELECT)} />;
  }

  if (screen === SCREENS.MODE_SELECT) {
    return (
      <ModeSelect
        onContinue={(selectedMode) => {
          setMode(selectedMode);
          setScreen(SCREENS.SESSION);
        }}
      />
    );
  }

  return (
    <VoiceSession
      key={mode}
      mode={mode}
      onBack={() => setScreen(SCREENS.MODE_SELECT)}
    />
  );
}
