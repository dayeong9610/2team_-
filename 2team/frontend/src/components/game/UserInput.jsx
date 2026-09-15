import { useState } from "react";

export default function UserInput({ onSubmit, onChange, disabled = false }) {
  const [message, setMessage] = useState("");

  const handleChange = (value) => {
    setMessage(value);
    onChange?.(value);
  };

  const handleSubmit = () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || disabled) {
      return;
    }

    onSubmit(trimmedMessage);

    setMessage("");
    onChange?.("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="dm-composer">
      <textarea
        className="dm-composer-input"
        value={message}
        disabled={disabled}
        placeholder="메시지 보내기..."
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
      />

      <button
        type="button"
        className="dm-composer-send"
        onClick={handleSubmit}
        disabled={!message.trim() || disabled}
        aria-label="전송"
      >
        ➤
      </button>
    </div>
  );
}
