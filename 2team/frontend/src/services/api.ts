import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

import type {
  SessionCreateResponse,
  SessionStateResponse,
  SessionResultResponse,
} from "../types/session";

/*
 * 개발 중에는 Vite가 /api 요청을 localhost:8000으로 프록시합니다.
 * 배포 후 FastAPI가 frontend/dist를 같이 서비스할 때도 같은 /api 경로를
 * 그대로 사용할 수 있으므로 localhost 하드코딩보다 안전합니다.
 * 다른 API 주소가 필요하면 .env에 VITE_API_BASE_URL을 지정하세요.
 */
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "/api"
).replace(/\/$/, "");

async function apiFetch(
  path: string,
  init?: RequestInit
): Promise<Response> {
  try {
    return await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new Error(
      "백엔드 서버에 연결할 수 없습니다. 서버가 8000번 포트에서 실행 중인지 확인해주세요."
    );
  }
}

export async function sendChat(
  data: ChatRequest
): Promise<ChatResponse> {
  const response = await apiFetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail ?? "채팅 응답을 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function createSession(
  episodeId: string
): Promise<SessionCreateResponse> {
  const response = await apiFetch("/sessions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      episode_id: episodeId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? "세션을 시작하지 못했습니다."
    );
  }

  return response.json();
}

export async function getSessionState(
  sessionId: string
): Promise<SessionStateResponse> {
  const response = await apiFetch(`/sessions/${sessionId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? "진행 상태를 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function getSessionResult(
  sessionId: string
): Promise<SessionResultResponse> {
  const response = await apiFetch(`/sessions/${sessionId}/result`);

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? "결과를 불러오지 못했습니다."
    );
  }

  return response.json();
}

export async function deleteSession(
  sessionId: string
): Promise<void> {
  const response = await apiFetch(`/sessions/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? "세션을 삭제하지 못했습니다."
    );
  }
}
