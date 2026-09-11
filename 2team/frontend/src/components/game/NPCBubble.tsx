interface NPCBubbleProps {
  message: string;
  name?: string;
}

export default function NPCBubble({
  message,
  name = "스터디 친구",
}: NPCBubbleProps) {
  return (
    <div className="npc-message">
      <div className="npc-avatar">
        👤
      </div>

      <div>
        <strong>{name}</strong>

        <div className="npc-bubble">
          {message}
        </div>
      </div>
    </div>
  );
}