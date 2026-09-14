from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from database.connection import conn
from routes.admin_route import router, template


@asynccontextmanager
async def lifespan(_: FastAPI):
    conn()
    yield

app = FastAPI(title="2Team API", lifespan=lifespan)
app.include_router(router)

templates = Jinja2Templates("templates/")

@app.get("/")
async def health_check(request : Request) -> dict[str, str]:
    return templates.TemplateResponse(request, "index.html")


if __name__ == "__main__":
    uvicorn.run(
            "app:app",
                host="127.0.0.1",
                port=8000,
                reload=True
                )
