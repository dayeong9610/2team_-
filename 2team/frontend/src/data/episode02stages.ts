import type { GameStage } from "./episode01stages";

// EP02 "SNS에서 시작된 유혹"
// Backend scenario/episodes/episode02.json과 대사/질문/평가기준을 맞춰 유지합니다.
// sceneType은 프론트 장면 표현용이며, feed / dm / dialog로 UI를 구분합니다.
export const episode02Stages: GameStage[] = [
  {
    id: 1,
    stageid: "EP02_STAGE01",
    title: "SNS 속 유혹 인지",
    location: "SNS 피드",
    sceneType: "feed",
    sceneTitle: "SNS 홍보 게시물",
    sceneSubtitle: "출처와 성분 정보가 불분명한 다이어트 홍보 콘텐츠",
    description:
      "SNS를 보던 중 먹으면 살이 빠지고 기분이 좋아진다는 출처 불명의 약물을 소개하는 홍보 게시물을 발견합니다.",
    messages: [
      { sender: "홍보 게시물", text: "식욕 억제, 체지방 관리, 에너지 업에 도움 된다는 후기가 올라오고 있다." },
      { sender: "댓글 후기", text: "저는 먹고 나서 야식 생각이 줄었어요." },
      { sender: "댓글 후기", text: "운동 힘든 날에도 이걸로 관리한다는 사람 많더라고요." },
      { sender: "댓글 후기", text: "다이어트 중인데 기분도 한결 편해졌다는 반응도 보인다." },
    ],
    question: "이 게시물에서 어떤 점이 가장 신경 쓰이나요?",
    evaluation: [
      "약물의 출처와 성분이 불분명하다는 점을 인식하는가?",
      "SNS의 홍보 내용만으로 약물의 안전성을 판단하지 않는가?",
      "다이어트나 기분 개선을 이유로 약물을 사용하는 것의 위험성을 인식하는가?",
    ],
    scoreType: "위험 인지",
    supportPanel: {
      variant: "feed",
      kicker: "위험 신호 보기",
      title: "효과와 후기만으로 안전성을 판단할 수 있을까?",
      subtitle: "제품 사진과 후기형 게시물을 먼저 보고 이상한 점을 찾아보세요.",
      badges: ["홍보성 계정", "성분 정보 부족", "체중 감량 강조", "후기 중심"],
      hintTitle: "이 상황에서 먼저 확인할 점",
      hintItems: [
        "판매자와 제품 출처가 확인되는지 보기",
        "성분과 안전성 정보가 구체적으로 공개되어 있는지 확인하기",
        "후기나 비포·애프터 사진만으로 효과를 믿게 만드는지 살피기",
      ],
      messages: [
        { sender: "홍보 게시물", text: "식욕 억제 · 체지방 관리 · 에너지 UP", tone: "warning" },
        { sender: "댓글 후기", text: "2주 만에 빠졌어요", tone: "pressure" },
      ],
      note: "좋아 보이는 후기보다 출처·성분·안전성 정보가 있는지 먼저 확인하는 장면입니다.",
    },
  },

  {
    id: 2,
    stageid: "EP02_STAGE02",
    title: "개인 메시지 유혹",
    location: "SNS 개인 메시지",
    sceneType: "dm",
    sceneTitle: "홍보 계정 DM",
    sceneSubtitle: "게시물 이후 도착한 개인 메시지",
    description:
      "SNS를 이용하던 중 홍보성 계정에서 개인 메시지가 도착합니다. 상대방은 체중 감량이나 기분 개선에 도움이 된다는 약물을 보내주겠다고 제안합니다.",
    messages: [
      { sender: "홍보 계정", text: "게시물 보시고 관심 있으신 분들께 따로 안내드리고 있어요." },
      { sender: "홍보 계정", text: "체중 관리나 기분 전환에 도움 됐다는 반응이 많아서요." },
      { sender: "홍보 계정", text: "이 제품이에요.", image: "product" },
      { sender: "홍보 계정", text: "원하시면 처음엔 소량으로 보내드릴 수도 있어요." },
    ],
    question: "이 메시지를 받은 당신은 어떻게 답하겠습니까?",
    evaluation: [
      "약물을 받거나 사용하지 않겠다는 의사를 명확하게 표현하는가?",
      "출처가 불분명한 홍보 계정이 권하는 약물을 쉽게 받지 않으려 하는가?",
      "다이어트나 기분 개선을 이유로 약물을 사용하지 않으려 하는가?",
    ],
    scoreType: "거절 대응",
    supportPanel: {
      variant: "dm",
      kicker: "개인 메시지 확인",
      title: "홍보 계정이 먼저 DM을 보내왔어요.",
      subtitle: "친절한 말투여도 출처가 불분명한 약물 제안이라는 점은 달라지지 않아요.",
      badges: ["홍보 계정", "개인 DM", "제품 사진", "약물 제안"],
      hintTitle: "이 상황의 핵심 포인트",
      hintItems: [
        "홍보 계정이 먼저 접근했다는 점 보기",
        "제품 사진이 있어도 안전성이 확인된 것은 아님을 기억하기",
        "받지 않겠다는 의사를 분명히 표현하기",
      ],
      messages: [
        { sender: "홍보 계정", text: "관심 있으시면 따로 안내드릴게요" },
        { sender: "홍보 계정", text: "처음엔 소량으로 보내드릴 수도 있어요", tone: "warning" },
      ],
      note: "낯선 홍보 계정이 개인 메시지로 제품을 보내주겠다고 하는 상황입니다.",
    },
  },

  {
    id: 3,
    stageid: "EP02_STAGE03",
    title: "반복되는 권유와 압박",
    location: "SNS 개인 메시지",
    sceneType: "dm",
    sceneTitle: "계속되는 홍보 DM",
    sceneSubtitle: "후기와 다수 사용을 내세운 반복 권유",
    description:
      "홍보 계정에서 다시 메시지가 옵니다. 상대방은 약물을 사용하는 사람이 많다는 말과 외모 및 스트레스에 대한 이야기를 이용해 약물 사용을 권유합니다.",
    messages: [
      { sender: "홍보 계정", text: "생각보다 문의하시는 분들이 많아요." },
      { sender: "홍보 계정", text: "후기 보시면 반응 괜찮은 편이에요.", image: "review" },
      { sender: "홍보 계정", text: "주변에서도 부담 없이 시작해봤다는 반응이 많더라고요." },
      { sender: "홍보 계정", text: "요즘 체중이나 기분 때문에 스트레스가 있다면 한 번 고려해보셔도 돼요." },
    ],
    question: "상대방이 계속 약물을 권유한다면 어떻게 행동하겠습니까?",
    evaluation: [
      "반복적인 권유와 감정적 설득에도 약물을 사용하지 않겠다는 입장을 유지하는가?",
      "외모나 감정적인 고민을 이유로 약물을 사용하지 않는가?",
      "추가적인 권유를 거절하거나 대화를 중단하는 등 접촉을 줄이려 하는가?",
    ],
    scoreType: "거절 대응 심화",
    supportPanel: {
      variant: "pressure",
      kicker: "반복 권유 장면",
      title: "후기와 '많이 쓴다'는 말로 다시 설득하고 있어요.",
      subtitle: "후기 숫자나 친절한 말투가 안전성을 증명하지는 않습니다.",
      badges: ["후기 제시", "반복 권유", "외모 고민 자극", "접촉 지속"],
      hintTitle: "이럴 때 기억할 점",
      hintItems: [
        "후기나 좋아요 수를 안전성 근거로 받아들이지 않기",
        "외모와 스트레스를 이용한 설득인지 살피기",
        "반복되면 대화를 중단하고 차단·신고를 고려하기",
      ],
      messages: [
        { sender: "홍보 계정", text: "후기 보시면 반응 괜찮아요", tone: "pressure" },
        { sender: "홍보 계정", text: "많이들 문의하세요", tone: "pressure" },
      ],
      note: "반복 설득과 후기 제시는 사용자의 경계심을 낮추려는 압박이 될 수 있습니다.",
    },
  },

  {
    id: 4,
    stageid: "EP02_STAGE04",
    title: "친구의 호기심",
    location: "학교 복도",
    sceneType: "dialog",
    sceneTitle: "친구와의 대화",
    sceneSubtitle: "SNS에서 본 약물에 관심을 보이는 친구",
    description:
      "다음 날 학교에서 친구와 이야기를 나누던 중 친구가 SNS에서 본 약물에 관심을 보입니다. 친구는 체중과 스트레스에 대한 고민을 이야기하며 약물을 사용해보고 싶다고 말합니다.",
    messages: [
      { sender: "친구", text: "나도 요즘 살 때문에 스트레스인데." },
      { sender: "친구", text: "진짜 효과 있으면 한번 해보고 싶다." },
      { sender: "친구", text: "SNS에서 봤는데 그렇게 위험한 건 아닌 것 같던데?" },
    ],
    question: "친구가 그 약물을 사용해보고 싶다고 한다면 당신은 어떻게 행동하겠습니까?",
    evaluation: [
      "친구가 출처 불명의 약물을 사용하는 것이 위험할 수 있음을 알리는가?",
      "친구에게 약물을 사용하지 말라고 이야기하는가?",
      "보호자나 교사 등 신뢰할 수 있는 어른에게 도움을 요청하도록 권하는가?",
    ],
    scoreType: "도움 요청",
  },

  {
    id: 5,
    stageid: "EP02_STAGE05",
    title: "비밀 요구와 최종 판단",
    location: "그날 밤 SNS 개인 메시지",
    sceneType: "dm",
    sceneTitle: "비밀 요구 DM",
    sceneSubtitle: "비밀 유지와 접촉 지속을 요구하는 홍보 계정",
    description:
      "그날 밤 홍보 계정에서 다시 메시지가 옵니다. 상대방은 약물을 보내주는 대신 다른 사람에게 알리지 말고 비밀로 해달라고 요구합니다.",
    messages: [
      { sender: "홍보 계정", text: "이건 공개적으로 안내하는 건 아니라 조용히 진행하셔야 해요." },
      { sender: "홍보 계정", text: "다른 분들께는 말하지 말고 필요하시면 따로 보내드릴게요." },
      { sender: "홍보 계정", text: "부모님이나 선생님께 굳이 말씀드릴 필요는 없어요." },
    ],
    question: "이 상황에서 당신은 어떻게 대응하겠습니까?",
    evaluation: [
      "상대방의 비밀 유지 요구를 따르지 않는가?",
      "약물을 받거나 사용하지 않는 선택을 하는가?",
      "SNS 계정을 차단하거나 신고하는 등 위험한 접촉을 중단하려 하는가?",
      "보호자나 교사 등 신뢰할 수 있는 어른에게 상황을 알리려 하는가?",
    ],
    scoreType: "도움 요청 심화",
  },
];
