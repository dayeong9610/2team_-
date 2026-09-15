export interface ChatRequest {
  session_id: string;
  episode_id: string;
  stage_id: string;
  message: string;
}

export interface Scores {
  risk_awareness: number;
  refusal: number;
  help_request: number;
}

export interface ChatResponse {
  npc_response: string;
  feedback: string;

  scores: Scores;

  next_stage: string | null;

  is_episode_complete: boolean;
}