const mockFeedback = {
    1: "좋아! 출처를 알 수 없는 물건은 먼저 안전성을 의심해보는 것이 중요해.",
    2: "좋아! 친구의 제안이라도 자신의 의사를 분명하게 표현하는 연습이 중요해.",
    3: "주변 친구들의 반응보다 자신의 판단을 유지하는 것도 중요한 대응이야.",
    4: "누군가 몸에 이상을 보인다면 혼자 해결하려 하기보다 믿을 수 있는 어른에게 도움을 요청하는 것이 중요해.",
    5: "좋아! 위험한 상황을 숨기기보다 적절한 도움을 요청하는 판단이 중요해.",
};
export default function ManyangCoach({ stage, }) {
    return (<div className="manyang-coach">
      <div className="manyang-character">
        😺
      </div>

      <div>
        <strong>마냥이</strong>

        <p>{mockFeedback[stage]}</p>
      </div>
    </div>);
}
