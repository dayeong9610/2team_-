import { useState } from "react";

interface UserInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
}

export default function UserInput({
  onSubmit,
  disabled = false,
}: UserInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || disabled) {
      return;
    }

    onSubmit(trimmedMessage);

    setMessage("");
  };

  return (
    <div className="user-input-area">
      <textarea
        value={message}
        disabled={disabled}
        placeholder="이 상황에서 어떻게 말하거나 행동할지 직접 입력해보세요."
        onChange={(e) => setMessage(e.target.value)}
        rows={4}
      />

      <button
        onClick={handleSubmit}
        disabled={!message.trim() || disabled}
      >
        답변하기
      </button>
    </div>
  );
}