import { useEffect } from "react";

import DietPillPhoto from "./DietPillPhoto";
import DietReviewPhoto from "./DietReviewPhoto";
import type { DialogueMessage } from "../../data/episode01stages";

interface SNSFeedViewProps {
  messages: DialogueMessage[];
  onRevealComplete?: () => void;
}

export default function SNSFeedView({
  messages,
  onRevealComplete,
}: SNSFeedViewProps) {
  useEffect(() => {
    onRevealComplete?.();
  }, [onRevealComplete]);

  const [caption, ...comments] = messages;

  return (
    <article className="sns-feed-card" aria-label="SNS 홍보 게시물">
      <header className="sns-feed-card__header">
        <div className="sns-feed-card__avatar" aria-hidden="true">S</div>
        <div>
          <strong>slimfit_daily</strong>
          <span>홍보성 계정 · 출처 정보 없음</span>
        </div>
        <span className="sns-feed-card__more" aria-hidden="true">•••</span>
      </header>

      <div className="sns-feed-card__media">
        <DietPillPhoto />
      </div>

      <div className="sns-feed-card__body">
        {caption && (
          <p className="sns-feed-card__caption">
            <strong>{caption.sender}</strong> {caption.text}
          </p>
        )}

        <div className="sns-feed-card__review-preview">
          <DietReviewPhoto />
          <span>후기·비포애프터 게시물 모음</span>
        </div>

        <div className="sns-feed-card__comments">
          {comments.map((message, index) => (
            <p key={`${message.sender}-${index}`}>
              <strong>{message.sender}</strong> {message.text}
            </p>
          ))}
        </div>
      </div>
    </article>
  );
}
