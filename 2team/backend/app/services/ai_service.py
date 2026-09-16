import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ai.evaluator import AIResponse
from app.ai.safety import check_user_message

load_dotenv()

# gpt용 코드
# llm = ChatOpenAI(
#     model=os.environ["LLM_MODEL"],
#     temperature=0.4
# )

# LangChain google용 코드
llm = ChatGoogleGenerativeAI(
    model=os.environ["LLM_MODEL"],
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.4,
)
# LangChain 제공 구조화 메서드
structured_llm = llm.with_structured_output(AIResponse)

async def evaluate_response(
    episode_id: str,
    stage_id: str,
    user_message: str,
    stage_data: dict
) -> dict:

    # 1. Safety 검사
    safety_result = check_user_message(user_message)

    if safety_result.blocked:
        return {
            "npc_response": (
                "그 내용보다는 지금 상황에서 "
                "어떻게 안전하게 행동할지 생각해보자."
            ),

            "feedback": safety_result.feedback,

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            }
        }

    try:

        user_prompt = build_user_prompt(
            episode_id=episode_id,
            stage_id=stage_id,
            user_message=user_message,
            stage_data=stage_data
        )

        result = await structured_llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
        )

        return result.model_dump()

    except Exception as e:

        print(f"AI ERROR: {e}")

        return {
            "npc_response":
                "잠시 문제가 생겼어. 다시 한 번 말해줄래?",

            "feedback":
                "답변을 처리하는 중 문제가 발생했습니다.",

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            }
        }