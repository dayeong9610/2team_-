import { Fragment, useEffect, useMemo, useState } from "react";

import DietPillPhoto from "./DietPillPhoto";
import DietReviewPhoto from "./DietReviewPhoto";

interface DialogueMessage {
  sender: string;
  text: string;
  image?: "product" | "review";
}

interface InstagramBubbleProps {
  messages: DialogueMessage[];
}

interface MessageGroup {
  sender: string;
  items: DialogueMessage[];
}

function groupMessages(messages: DialogueMessage[]): MessageGroup[] {
  const groups: MessageGroup[] = [];

  messages.forEach((message) => {
    const lastGroup = groups[groups.length - 1];

    if (lastGroup && lastGroup.sender === message.sender) {
      lastGroup.items.push(message);
    } else {
      groups.push({ sender: message.sender, items: [message] });
    }
  });

  return groups;
}

const TYPING_DELAY_MS = 700;

function InstagramMessageGroup({ group }: { group: MessageGroup }) {
  const [visibleCount, setVisibleCount] = useState(1);

  useEffect(() => {
    if (visibleCount >= group.items.length) {
      return;
    }

    const timer = setTimeout(() => {
      setVisibleCount((count) => count + 1);
    }, TYPING_DELAY_MS);

    return () => clearTimeout(timer);
  }, [visibleCount, group.items.length]);

  const isTyping = visibleCount < group.items.length;

  return (
    <div className="ig-message">
      {group.items.slice(0, visibleCount).map((item, itemIndex) => {
        if (item.image === "product" || item.image === "review") {
          const Photo =
            item.image === "product" ? DietPillPhoto : DietReviewPhoto;

          return (
            <Fragment key={itemIndex}>
              <div className="ig-bubble ig-bubble--image">
                <Photo />
              </div>
              <div className="ig-bubble">{item.text}</div>
            </Fragment>
          );
        }

        return (
          <div className="ig-bubble" key={itemIndex}>
            {item.text}
          </div>
        );
      })}

      {isTyping && (
        <div className="ig-bubble ig-bubble--typing">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      )}
    </div>
  );
}

// EP03 인스타그램 DM 연출용 - 상단에 상대 계정명이 이미 나오므로
// 말풍선마다 이름을 반복하지 않는, 실제 DM에 가까운 모양입니다.
export default function InstagramBubble({ messages }: InstagramBubbleProps) {
  const groups = useMemo(
    () => groupMessages(messages),
    [messages]
  );

  return (
    <>
      {groups.map((group, index) => (
        <InstagramMessageGroup group={group} key={index} />
      ))}
    </>
  );
}
