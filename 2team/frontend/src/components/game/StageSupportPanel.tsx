import { useState } from "react";

import unknownDrinkScene from "../../assets/scenes/unknown-free-drink.svg";
import type {
  StageSupportPanel as StageSupportPanelType,
  VisualCueMessage,
} from "../../data/episode01stages";

interface StageSupportPanelProps {
  panel: StageSupportPanelType;
  compact?: boolean;
  onConfirm?: () => void;
  onReopen?: () => void;
}

function messageToneClass(message: VisualCueMessage) {
  if (message.tone === "warning") {
    return "stage-support-panel__message stage-support-panel__message--warning";
  }
  if (message.tone === "pressure") {
    return "stage-support-panel__message stage-support-panel__message--pressure";
  }
  return "stage-support-panel__message";
}

function getSceneSummary(panel: StageSupportPanelType) {
  switch (panel.variant) {
    case "feed":
      return { icon: "📱", title: "SNS 게시물", detail: "출처 불명 계정의 게시물" };
    case "dm":
      return { icon: "💬", title: "익명 DM", detail: "프로필 없는 계정의 개인 메시지" };
    case "drink":
      return { icon: "🥤", title: "무료 음료 장면", detail: "라벨·성분·제공자 정보가 불명확함" };
    case "pressure":
      return { icon: "👥", title: "주변 압박 장면", detail: "또래의 반복 권유와 분위기 압박" };
    default:
      return { icon: "🖼️", title: "상황 장면", detail: "앞서 확인한 장면" };
  }
}

function renderPreview(panel: StageSupportPanelType) {
  switch (panel.variant) {
    case "feed":
      return (
        <div className="stage-support-panel__preview stage-support-panel__preview--feed">
          <div className="stage-support-panel__social-head">
            <div className="stage-support-panel__avatar stage-support-panel__avatar--ghost">?</div>
            <div>
              <strong>출처 불명 계정</strong>
              <p>광고 · 신뢰 정보 없음</p>
            </div>
          </div>
          <div className="stage-support-panel__message-list">
            {panel.messages?.map((message, index) => (
              <div className={messageToneClass(message)} key={index}>
                <span className="stage-support-panel__sender">{message.sender}</span>
                <p>{message.text}</p>
              </div>
            ))}
          </div>
        </div>
      );
    case "dm":
      return (
        <div className="stage-support-panel__preview stage-support-panel__preview--dm">
          <div className="stage-support-panel__social-head">
            <div className="stage-support-panel__avatar stage-support-panel__avatar--warning">!</div>
            <div>
              <strong>익명 DM</strong>
              <p>프로필 없음 · 개인 메시지</p>
            </div>
          </div>
          <div className="stage-support-panel__message-list">
            {panel.messages?.map((message, index) => (
              <div className={messageToneClass(message)} key={index}>
                <span className="stage-support-panel__sender">{message.sender}</span>
                <p>{message.text}</p>
              </div>
            ))}
          </div>
        </div>
      );
    case "drink":
      return (
        <div className="stage-support-panel__preview stage-support-panel__preview--drink">
          <div className="stage-support-panel__drink-card">
            <img
              className="stage-support-panel__scene-image"
              src={unknownDrinkScene}
              alt="학원가 앞에서 출처와 성분이 불분명한 무료 음료를 학생에게 건네는 상황"
            />
            <div className="stage-support-panel__drink-copy">
              <strong>정체 불분명한 무료 음료 배포 상황</strong>
              <p>그림을 먼저 보고, 어떤 점이 이상한지 스스로 생각해보세요.</p>
            </div>
          </div>
        </div>
      );
    case "pressure":
      return (
        <div className="stage-support-panel__preview stage-support-panel__preview--pressure">
          <div className="stage-support-panel__message-list">
            {panel.messages?.map((message, index) => (
              <div className={messageToneClass(message)} key={index}>
                <span className="stage-support-panel__sender">{message.sender}</span>
                <p>{message.text}</p>
              </div>
            ))}
          </div>
        </div>
      );
    default:
      return null;
  }
}

export default function StageSupportPanel({
  panel,
  compact = false,
  onConfirm,
  onReopen,
}: StageSupportPanelProps) {
  const [hintOpen, setHintOpen] = useState(false);
  const summary = getSceneSummary(panel);

  if (compact) {
    return (
      <section className="stage-support-panel stage-support-panel--compact" aria-label="확인한 상황 장면">
        <div className="stage-support-panel__compact-main">
          <span className="stage-support-panel__compact-icon" aria-hidden="true">{summary.icon}</span>
          <div className="stage-support-panel__compact-copy">
            <span>장면 확인 완료</span>
            <strong>{summary.title}</strong>
            <p>{summary.detail}</p>
          </div>
        </div>
        <button type="button" className="stage-support-panel__reopen" onClick={onReopen}>
          다시 보기
        </button>
      </section>
    );
  }

  return (
    <section
      className={`stage-support-panel stage-support-panel--decision-first${
        hintOpen ? " stage-support-panel--hint-open" : ""
      }`}
      aria-label="상황 시각 자료"
    >
      <div className="stage-support-panel__decision-head">
        <div>
          <span className="stage-support-panel__scene-label">장면 먼저 보기</span>
          <strong>먼저 보고 스스로 판단해보세요.</strong>
          <p>장면을 확인한 뒤 실제 대화로 넘어갑니다.</p>
        </div>
        <button
          type="button"
          className="stage-support-panel__hint-toggle"
          onClick={() => setHintOpen((open) => !open)}
          aria-expanded={hintOpen}
        >
          {hintOpen ? "힌트 접기" : "막막하면 힌트 보기"}
          <span aria-hidden="true">{hintOpen ? "▲" : "▼"}</span>
        </button>
      </div>

      <div className="stage-support-panel__visual-first">{renderPreview(panel)}</div>

      {hintOpen && (
        <div className="stage-support-panel__hint-content">
          <div className="stage-support-panel__copy">
            {panel.kicker && (
              <span className="stage-support-panel__kicker">{panel.kicker}</span>
            )}
            <strong className="stage-support-panel__title">{panel.title}</strong>
            {panel.subtitle && (
              <p className="stage-support-panel__subtitle">{panel.subtitle}</p>
            )}

            {panel.badges && panel.badges.length > 0 && (
              <div className="stage-support-panel__badges">
                {panel.badges.map((badge) => (
                  <span className="stage-support-panel__badge" key={badge}>
                    {badge}
                  </span>
                ))}
              </div>
            )}

            {panel.hintItems && panel.hintItems.length > 0 && (
              <div className="stage-support-panel__hint-box">
                <span className="stage-support-panel__hint-title">
                  {panel.hintTitle ?? "먼저 확인할 점"}
                </span>
                <ul className="stage-support-panel__hint-list">
                  {panel.hintItems.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {panel.note && <p className="stage-support-panel__note">{panel.note}</p>}
        </div>
      )}

      <button type="button" className="stage-support-panel__confirm" onClick={onConfirm}>
        <span>상황 확인했어요</span>
        <span aria-hidden="true">→</span>
      </button>
    </section>
  );
}
