import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

import type {
  SessionCreateResponse,
  SessionStateResponse,
  SessionResultResponse,
} from "../types/session";

import {
  applyRemoteChatResult,
  createFallbackChat,
  createFallbackSession,
  deleteFallbackSession,
  getFallbackSessionResult,
  getFallbackSessionState,
  isFallbackSession,
  mirrorRemoteSession,
  promoteSessionToFallback,
} from "./resilience";

/*
 * 개발 중에는 Vite가 /api 요청을 127.0.0.1:8000으로 프록시합니다.
 * Backend 또는 DB/AI 일부가 장애여도 학생 학습 흐름이 멈추지 않도록
 * 각 API 함수는 검수된 frontend fallback으로 자동 전환합니다.
 */
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "/api"
).replace(/\/$/, "");

async function apiFetch(
  path: string,
  init?: RequestInit,
  timeoutMs = 4000
): Promise<Response> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function sendChat(
  data: ChatRequest
): Promise<ChatResponse> {
  // 한 번 fallback으로 전환된 세션은 서버의 메모리 상태와 어긋나지 않도록
  // 해당 에피소드가 끝날 때까지 로컬 시나리오 흐름으로 계속 진행합니다.
  if (isFallbackSession(data.session_id)) {
    return createFallbackChat(data);
  }

  try {
    const response = await apiFetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }, 22000);

    if (!response.ok) {
      throw new Error("CHAT_API_UNAVAILABLE");
    }

    const result = (await response.json()) as ChatResponse;
    applyRemoteChatResult(data, result);
    return result;
  } catch {
    // Backend/AI/세션 장애 시 사용자 원문은 저장하지 않고 검수된 시나리오
    // 기반 반응·코칭으로 즉시 전환합니다.
    promoteSessionToFallback(data.session_id);
    return createFallbackChat(data);
  }
}

export async function createSession(
  episodeId: string
): Promise<SessionCreateResponse> {
  try {
    const response = await apiFetch("/sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        episode_id: episodeId,
      }),
    }, 3500);

    if (!response.ok) {
      throw new Error("SESSION_API_UNAVAILABLE");
    }

    const result = (await response.json()) as SessionCreateResponse;
    mirrorRemoteSession(result);
    return result;
  } catch {
    // FastAPI 자체가 내려가도 학생은 local session으로 에피소드를 시작합니다.
    return createFallbackSession(episodeId);
  }
}

export async function getSessionState(
  sessionId: string
): Promise<SessionStateResponse> {
  if (isFallbackSession(sessionId)) {
    const localState = getFallbackSessionState(sessionId);
    if (localState) return localState;
  }

  try {
    const response = await apiFetch(`/sessions/${sessionId}`, undefined, 3500);

    if (!response.ok) {
      throw new Error("SESSION_STATE_UNAVAILABLE");
    }

    return response.json();
  } catch {
    const fallback = promoteSessionToFallback(sessionId);
    const localState = fallback ? getFallbackSessionState(sessionId) : null;

    if (localState) {
      return localState;
    }

    throw new Error("진행 상태를 복구하지 못했습니다.");
  }
}

export async function getSessionResult(
  sessionId: string
): Promise<SessionResultResponse> {
  if (isFallbackSession(sessionId)) {
    const localResult = getFallbackSessionResult(sessionId);
    if (localResult) return localResult;
  }

  try {
    const response = await apiFetch(
      `/sessions/${sessionId}/result`,
      undefined,
      3500
    );

    if (!response.ok) {
      throw new Error("SESSION_RESULT_UNAVAILABLE");
    }

    return response.json();
  } catch {
    const localResult = getFallbackSessionResult(sessionId);

    if (localResult) {
      return localResult;
    }

    throw new Error("결과 정보를 불러오지 못했습니다.");
  }
}

export async function deleteSession(
  sessionId: string
): Promise<void> {
  // 로컬 복구 데이터는 먼저 지워 재도전이 항상 새 세션으로 시작되게 합니다.
  deleteFallbackSession(sessionId);

  if (sessionId.startsWith("local-")) {
    return;
  }

  try {
    await apiFetch(`/sessions/${sessionId}`, {
      method: "DELETE",
    }, 2500);
  } catch {
    // 종료된 학습 세션 삭제는 best-effort. 실패해도 재도전을 막지 않습니다.
  }
}
