interface DialogueMessage {
  sender: string;
  text: string;
}

interface NPCBubbleProps {
  messages: DialogueMessage[];
}

interface MessageGroup {
  sender: string;
  texts: string[];
}

function groupMessages(messages: DialogueMessage[]): MessageGroup[] {
  const groups: MessageGroup[] = [];

  messages.forEach(({ sender, text }) => {
    const lastGroup = groups[groups.length - 1];

    if (lastGroup && lastGroup.sender === sender) {
      lastGroup.texts.push(text);
    } else {
      groups.push({ sender, texts: [text] });
    }
  });

  return groups;
}

export default function NPCBubble({ messages }: NPCBubbleProps) {
  const groups = groupMessages(messages);

  return (
    <>
      {groups.map((group, index) => (
        <div className="npc-message" key={index}>
          <div className="npc-avatar">{group.sender.charAt(0)}</div>

          <div className="npc-message-content">
            <span className="npc-name">{group.sender}</span>

            <div className="npc-bubble-group">
              {group.texts.map((text, textIndex) => (
                <div className="npc-bubble" key={textIndex}>
                  {text}
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </>
  );
}
