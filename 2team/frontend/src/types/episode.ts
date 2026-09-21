export interface Stage {
  stageId: string;
  title: string;
  npcMessages: string[];
  question: string;
  nextStage: string | null;
}

export interface Episode {
  id: string;
  title: string;
  description: string;

  totalStages: number;
  estimatedTime: string;

  status: "available" | "locked" | "completed";

  episodeId?: string;
  stages?: Stage[];
}

// FastAPI GET /api/episodes 응답 계약
export interface EpisodeSummaryResponse {
  episode_id: string;
  title: string;
  description: string;
  total_stages: number;
}

export interface EpisodeStageMessageResponse {
  speaker: string;
  text: string;
}

export interface EpisodeStageResponse {
  stage_id: string;
  stage_number: number;
  title: string;
  type: string;
  location: string;
  description: string;
  messages: EpisodeStageMessageResponse[];
  question: string;
  evaluation_axis: "risk_awareness" | "refusal" | "help_request";
  evaluation_criteria: string[];
  next_stage: string | null;
  npc_speaker?: string;
  npc_identity?: string;
  npc_stance?: string;
  npc_boundaries?: string;
}

export interface EpisodeDetailResponse extends EpisodeSummaryResponse {
  stages: EpisodeStageResponse[];
}
