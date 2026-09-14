interface NPCBubbleProps {
  messages: string[];
  name?: string;
}

export default function NPCBubble({
  messages,
  name = "스터디 친구",
}: NPCBubbleProps) {
  return (
    <div className="npc-message">
      <div className="npc-avatar">{name.charAt(0)}</div>

      <div className="npc-message-content">
        <span className="npc-name">{name}</span>

        <div className="npc-bubble-group">
          {messages.map((message, index) => (
            <div className="npc-bubble" key={index}>
              {message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
