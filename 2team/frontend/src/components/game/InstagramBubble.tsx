interface DialogueMessage {
  sender: string;
  text: string;
}

interface InstagramBubbleProps {
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

// EP03 인스타그램 DM 연출용 - 상단에 상대 계정명이 이미 나오므로
// 말풍선마다 이름을 반복하지 않는, 실제 DM에 가까운 모양입니다.
export default function InstagramBubble({ messages }: InstagramBubbleProps) {
  const groups = groupMessages(messages);

  return (
    <>
      {groups.map((group, index) => (
        <div className="ig-message" key={index}>
          {group.texts.map((text, textIndex) => (
            <div className="ig-bubble" key={textIndex}>
              {text}
            </div>
          ))}
        </div>
      ))}
    </>
  );
}
