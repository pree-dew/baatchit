import { useState } from "react";

export default function TextInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-lg flex gap-2">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder="Type instead of speaking..."
        className="flex-1 bg-surface-container-high/60 border border-outline-variant/40 rounded-full px-5 py-3 text-body-md text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/40"
      />
      <button
        type="submit"
        disabled={disabled}
        className="bg-primary text-on-primary rounded-full px-5 py-3 text-label-md disabled:opacity-40"
      >
        Send
      </button>
    </form>
  );
}
