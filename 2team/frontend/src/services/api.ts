import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

import type {
  SessionCreateResponse,
  SessionStateResponse,
  SessionResultResponse,
} from "../types/session";

const API_BASE_URL =
  "http://localhost:8000/api";

export async function sendChat(
  data: ChatRequest
): Promise<ChatResponse> {

  const response = await fetch(
    `${API_BASE_URL}/chat`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(
      () => null
    );

    throw new Error(
      error?.detail ??
      "채팅 응답을 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function createSession(
  episodeId: string
): Promise<SessionCreateResponse> {

  const response = await fetch(
    `${API_BASE_URL}/sessions`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        episode_id: episodeId,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "세션을 시작하지 못했습니다."
    );
  }

  return response.json();
}

export async function getSessionState(
  sessionId: string
): Promise<SessionStateResponse> {

  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}`
  );

  if (!response.ok) {
    throw new Error(
      "진행 상태를 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function getSessionResult(
  sessionId: string
): Promise<SessionResultResponse> {

  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}/result`
  );

  if (!response.ok) {
    throw new Error(
      "결과를 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function deleteSession(
  sessionId: string
): Promise<void> {

  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error(
      "세션을 삭제하지 못했습니다."
    );
  }
}