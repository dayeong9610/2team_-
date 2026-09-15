import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

export async function sendChat(
  data: ChatRequest
): Promise<ChatResponse> {

  const response = await fetch(
    "http://localhost:8000/api/chat",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    throw new Error(
      "채팅 응답을 불러오지 못했습니다."
    );
  }

  const result: ChatResponse =
    await response.json();

  return result;
}