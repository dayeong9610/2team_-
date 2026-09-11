interface NPCBubbleProps {
  name?: string;
  message: string;
}

export default function NPCBubble({
  name = "친구",
  message
}: NPCBubbleProps) {
  return (
    <div className="npc-bubble">
      <strong>{name}</strong>
      <p>{message}</p>
    </div>
  );
}