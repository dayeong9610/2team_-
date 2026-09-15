from fastapi import APIRouter
from fastapi.templating import  Jinja2Templates
from fastapi.routing import RedirectResponse, Request

from database.connection import get_session
from model.chat_room import ChatRoom
from model.chatting import Chatting
from model.score import Score

# 여기부터는 학생들이 이용할 서비스 라우터입니다.
student_router = APIRouter(prefix = "/students", tags = ["Students"])

template = Jinja2Templates("templates/")

@student_router.get("/")
async def student(request : Request):
    return template.TemplateResponse(request, "/student/student.html")