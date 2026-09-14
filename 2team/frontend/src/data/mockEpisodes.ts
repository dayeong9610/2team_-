export const mockEpisode = {
  episodeId: "EP01",
  title: "시험기간 스터디 그룹",

  stages: [
    {
      stageId: "EP01_STAGE01",

      title: "위험 인지",

      npcMessages: [
        "나 요즘 이거 먹고 공부하는데 잠이 하나도 안 온다.",
        "집중도 엄청 잘 됨.",
        "나도 써봄.",
        "효과 좋음."
      ],

      question:
        "이 상황에서 어떤 점이 가장 신경 쓰이나요?",

      nextStage: "EP01_STAGE02"
    }
  ]
};