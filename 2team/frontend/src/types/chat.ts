export interface ChatRequest {
  sessionId: string;
  episodeId: string;
  stageId: string;
  message: string;
}

export interface Scores {
  riskAwareness: number;
  refusal: number;
  helpRequest: number;
}

export interface ChatResponse {
  npcResponse: string;
  feedback: string;
  scores: Scores;
  nextStage: string | null;
}