import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ai.evaluator import AIResponse

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

    # AI에게 전달할 사용자 프롬프트 생성
    user_prompt = build_user_prompt(
        episode_id=episode_id,
        stage_id=stage_id,
        user_message=user_message,
        stage_data=stage_data
    )

    # 이후 여기에서 실제 LLM API 호출

    result = await structured_llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
    )

    return result.model_dump()