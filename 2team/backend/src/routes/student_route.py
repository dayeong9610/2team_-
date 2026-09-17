from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.templating import  Jinja2Templates
from fastapi.routing import RedirectResponse, Request
from sqlalchemy import select

from database.connection import get_session
from model.chat_room import ChatRoom
from model.chatting import Chatting
from model.score import Score
from model.llm_role import LlmRole

# 여기부터는 학생들이 이용할 서비스 라우터입니다.
# /students 부터 시작
student_router = APIRouter(prefix = "/students",tags = ["Students"])

template = Jinja2Templates("templates/")

# 초기화면
@student_router.get("/")
async def student(request : Request):
    return template.TemplateResponse(request, "/student/student.html")

# 에피소드 선택 화면을 띄워주는 경로
@student_router.get("/episode")
async def episodes(request : Request):


    return template.TemplateResponse(request, "/student/episode_select.html")

@student_router.post("/episode/{category}")
async def select_episode(
        request : Request,
        category : str,
        session = Depends(get_session)
):
    if category == "EP01":
        category = "club"
    elif category == "EP02":
        category = "school"
    elif category == "EP03":
        category = "trip"

    statement = select(LlmRole).where(
        LlmRole.category == category
    )
    llm_role = session.scalars(statement = statement).one_or_none()
    if llm_role:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = ""
        )

    return template.TemplateResponse(request, "path" )

