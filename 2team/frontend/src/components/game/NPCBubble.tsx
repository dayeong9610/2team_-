import { useEffect, useMemo, useState } from "react";

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

const TYPING_DELAY_MS = 700;

function NPCMessageGroup({ group }: { group: MessageGroup }) {
  const [visibleCount, setVisibleCount] = useState(1);

  useEffect(() => {
    if (visibleCount >= group.texts.length) {
      return;
    }

    const timer = setTimeout(() => {
      setVisibleCount((count) => count + 1);
    }, TYPING_DELAY_MS);

    return () => clearTimeout(timer);
  }, [visibleCount, group.texts.length]);

  const isTyping = visibleCount < group.texts.length;

  return (
    <div className="npc-message">
      <div className="npc-avatar">{group.sender.charAt(0)}</div>

      <div className="npc-message-content">
        <span className="npc-name">{group.sender}</span>

        <div className="npc-bubble-group">
          {group.texts.slice(0, visibleCount).map((text, textIndex) => (
            <div className="npc-bubble" key={textIndex}>
              {text}
            </div>
          ))}

          {isTyping && (
            <div className="npc-bubble npc-bubble--typing">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function NPCBubble({ messages }: NPCBubbleProps) {
  const groups = useMemo(
    () => groupMessages(messages),
    [messages]
  );

  return (
    <>
      {groups.map((group, index) => (
        <NPCMessageGroup group={group} key={index} />
      ))}
    </>
  );
}
