export interface Stage {
  stageId: string;
  title: string;
  npcMessages: string[];
  question: string;
  nextStage: string | null;
}

export interface Episode {
  episodeId: string;
  title: string;
  stages: Stage[];
}