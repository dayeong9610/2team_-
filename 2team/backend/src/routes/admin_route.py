from pathlib import Path
import io
import json
import logging
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, StreamingResponse

from sqlmodel import select, func

from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate, optional_authenticate
from database.connection import get_session
from model.admin import Admin
from model.llm_role import LlmRole, WriteLlmRole
from model.chat_room import ChatRoom
from model.chatting import Chatting, ChatterEnum
from model.score import Score
from core.scenario_engine import list_episodes, load_episode

router = APIRouter(prefix="/admins", tags=["Admins"])

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
template = Jinja2Templates(directory=str(TEMPLATE_DIR))

password_encoder = HashPassword()

logger = logging.getLogger(__name__)

@router.get("/")
async def admin_index(
    request: Request,
    current_user: str | None = Depends(optional_authenticate),
    session=Depends(get_session),
):
    context = {
        "is_authenticated": current_user is not None,
        "current_user": current_user,
        "dashboard": None,
        "dashboard_error": None,
    }

    if current_user is not None:
        try:
            # llm_role이 Episode 저장소 역할을 합니다.
            episode_filter = LlmRole.episode_id.is_not(None)

            total_scenarios = session.exec(
                select(func.count(LlmRole.lr_num)).where(episode_filter)
            ).one() or 0

            my_scenarios = session.exec(
                select(func.count(LlmRole.lr_num)).where(
                    episode_filter,
                    LlmRole.admin_id == current_user,
                )
            ).one() or 0

            published_scenarios = session.exec(
                select(func.count(LlmRole.lr_num)).where(
                    episode_filter,
                    LlmRole.status == "published",
                )
            ).one() or 0

            total_admins = session.exec(
                select(func.count(Admin.admin_id))
            ).one() or 0

            active_admins = session.exec(
                select(func.count(Admin.admin_id)).where(
                    Admin.enabled == True  # noqa: E712
                )
            ).one() or 0

            category_rows = session.exec(
                select(
                    LlmRole.category,
                    func.count(LlmRole.lr_num),
                )
                .where(episode_filter)
                .group_by(LlmRole.category)
            ).all()

            category_map = {
                row[0]: int(row[1])
                for row in category_rows
                if row[0] is not None
            }

            categories = [
                {"key": "school", "label": "교내", "count": category_map.get("school", 0)},
                {"key": "trip", "label": "해외여행", "count": category_map.get("trip", 0)},
                {"key": "club", "label": "클럽마약", "count": category_map.get("club", 0)},
                {"key": "user_defined", "label": "사용자 정의", "count": category_map.get("user_defined", 0)},
            ]

            recent_scenarios = session.exec(
                select(LlmRole)
                .where(episode_filter)
                .order_by(LlmRole.created_at.desc())
                .limit(5)
            ).all()

            dashboard = {
                "total_scenarios": int(total_scenarios),
                "my_scenarios": int(my_scenarios),
                "total_admins": int(total_admins),
                "active_admins": int(active_admins),
                "published_scenarios": int(published_scenarios),
                "categories": categories,
                "recent_scenarios": recent_scenarios,
                "score_stats": {
                    "available": True,
                    "count": 0,
                    "avg_risk_awareness": 0.0,
                    "avg_refusal": 0.0,
                    "avg_help_request": 0.0,
                    "axis_counts": {},
                    "stage_stats": [],
                },
            }

            # 실제 GPT 평가 결과는 score -> chatting -> chat_room -> llm_role 관계로 집계합니다.
            try:
                rows = session.exec(
                    select(Score, Chatting, ChatRoom, LlmRole)
                    .join(Chatting, Score.chat_id == Chatting.chat_id)
                    .join(ChatRoom, Chatting.room_id == ChatRoom.room_id)
                    .join(LlmRole, ChatRoom.lr_num == LlmRole.lr_num)
                    .where(Chatting.chatter == ChatterEnum.USER)
                    .order_by(Chatting.created_at.desc())
                ).all()

                axis_values = {
                    "risk_awareness": [],
                    "refusal": [],
                    "help_request": [],
                }
                stage_buckets: dict[tuple[str, str], dict] = {}
                evaluated_chat_ids: set[int] = set()
                role_stage_cache: dict[tuple[int, str], dict] = {}

                for score_row, chat_row, room_row, role_row in rows:
                    if role_row.episode_id is None or chat_row.chat_id is None:
                        continue

                    cache_key = (int(role_row.lr_num), chat_row.stage_id)
                    stage = role_stage_cache.get(cache_key)
                    if stage is None:
                        stage = {}

                        # 1) DB llm_role.content에 실제 Episode JSON이 있으면 우선 사용합니다.
                        try:
                            payload = json.loads(role_row.content or "{}")
                            for candidate in payload.get("stages", []):
                                if candidate.get("stage_id") == chat_row.stage_id:
                                    stage = candidate
                                    break
                        except (TypeError, json.JSONDecodeError):
                            stage = {}

                        # 2) ai_evaluation -> 기존 테이블 마이그레이션 직후에는
                        #    llm_role가 stages=[]인 draft placeholder일 수 있습니다.
                        #    이 경우 기본 scenario JSON까지 fallback해서 평가축을 복구합니다.
                        if not stage and role_row.episode_id:
                            episode = load_episode(role_row.episode_id)
                            if episode is not None:
                                for candidate in episode.get("stages", []):
                                    if candidate.get("stage_id") == chat_row.stage_id:
                                        stage = candidate
                                        break

                        role_stage_cache[cache_key] = stage

                    axis = stage.get("evaluation_axis")
                    if axis not in axis_values or score_row.category != axis:
                        continue

                    value = int(score_row.score)
                    axis_values[axis].append(value)
                    evaluated_chat_ids.add(int(chat_row.chat_id))

                    key = (role_row.episode_id, chat_row.stage_id)
                    bucket = stage_buckets.setdefault(
                        key,
                        {
                            "episode_id": role_row.episode_id,
                            "stage_id": chat_row.stage_id,
                            "title": stage.get("title", chat_row.stage_id),
                            "axis": axis,
                            "values": [],
                        },
                    )
                    bucket["values"].append(value)

                stage_stats = []
                for bucket in stage_buckets.values():
                    values = bucket.pop("values")
                    bucket["count"] = len(values)
                    bucket["average"] = sum(values) / len(values) if values else 0.0
                    stage_stats.append(bucket)
                stage_stats.sort(key=lambda row: (row["episode_id"], row["stage_id"]))

                def axis_avg(key: str) -> float:
                    values = axis_values[key]
                    return sum(values) / len(values) if values else 0.0

                dashboard["score_stats"] = {
                    "available": True,
                    "count": len(evaluated_chat_ids),
                    "avg_risk_awareness": axis_avg("risk_awareness"),
                    "avg_refusal": axis_avg("refusal"),
                    "avg_help_request": axis_avg("help_request"),
                    "axis_counts": {key: len(values) for key, values in axis_values.items()},
                    "stage_stats": stage_stats,
                }
            except Exception as exc:
                session.rollback()
                dashboard["score_stats"]["available"] = False
                logger.warning(
                    "ADMIN DASHBOARD score statistics unavailable: %s",
                    type(exc).__name__,
                )

            context["dashboard"] = dashboard

        except Exception as exc:
            session.rollback()
            context["dashboard_error"] = (
                "DB 현황을 불러오지 못했습니다. DB 연결 상태를 확인해주세요."
            )
            logger.exception(
                "ADMIN DASHBOARD query failed: %s",
                type(exc).__name__,
            )

    return template.TemplateResponse(
        request,
        "admin/admin_index.html",
        context,
    )


@router.get("/class-qr")
async def class_qr_page(
    request: Request,
    current_user: str = Depends(authenticate),
):
    """DB 저장 없이 Episode 접속용 수업코드/QR을 생성하는 화면입니다."""
    episodes = []
    for episode in list_episodes():
        episode_id = str(episode.get("episode_id") or "").strip().upper()
        if not episode_id:
            continue
        episodes.append({
            "episode_id": episode_id,
            "title": str(episode.get("title") or episode_id),
        })

    return template.TemplateResponse(
        request,
        "admin/class_qr.html",
        {
            "current_user": current_user,
            "episodes": episodes,
        },
    )


@router.get("/class-qr/image")
async def class_qr_image(
    episode_id: str,
    base_url: str,
    current_user: str = Depends(authenticate),
):
    """현재 브라우저 주소 + Episode ID를 QR PNG로 즉석 생성합니다. DB 저장 없음."""
    normalized = episode_id.strip().upper()
    episode = load_episode(normalized)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid base URL")

    try:
        import qrcode
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail='QR 패키지가 없습니다. python -m pip install "qrcode[pil]" 실행 후 재시작해주세요.',
        ) from exc

    join_url = f"{base_url.rstrip('/')}/class/{normalized}"
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(join_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )

@router.get("/signup")
async def admin_join_form(request : Request):
    return template.TemplateResponse(request, "admin/admin_joinform.html")

@router.post("/signup")
async def signup(
    admin_id: str = Form(...),
    admin_pw: str = Form(...),
    teacher_num: int = Form(...),
    admin_name : str = Form(...),
    contact: str = Form(...),
    session = Depends(get_session)
):
    admin_exist = session.get(Admin, admin_id)
    if admin_exist:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail = "User with supplied username exists."
        )
    admin = Admin(
        admin_id=admin_id,
        teacher_num=teacher_num,
        admin_name=admin_name,
        contact=contact,
        admin_pw=password_encoder.create_hash(admin_pw),
    )

    session.add(admin)
    session.commit()
    session.refresh(admin)

    return RedirectResponse("/admins/", status_code = 303)

@router.get("/signin")
async def user_signin(request : Request):
    return template.TemplateResponse(request, "admin/login_form.html")

@router.post("/signin")
async def sign_user_in(
                       user: OAuth2PasswordRequestForm = Depends(),
                       session =  Depends(get_session)
                       ) -> dict:
    admin_exist = session.get(Admin, user.username)
    if not admin_exist:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Invalid username or password"
        )

    if not password_encoder.verify_hash(user.password, admin_exist.admin_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid details passed",
        )

    if admin_exist.enabled == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )

    access_token = create_access_token(admin_exist.admin_id)
    response = RedirectResponse("/admins/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )
    return response
    
@router.get("/signout")
async def signout():
    response = RedirectResponse("/admins/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/update")
async def update_admin(
    request: Request,
    current_user: str = Depends(authenticate),
    session = Depends(get_session),
):
    admin_exist = session.get(Admin, current_user)
    if not admin_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )
    return template.TemplateResponse(request, "admin/update_form.html", {"admin" : admin_exist})

@router.post("/update")
async def update_admin(
        admin_pw: str | None = Form(None),
        contact: str | None = Form(None),
        current_user: str = Depends(authenticate),
        session = Depends(get_session)
):
    admin = session.get(Admin, current_user)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )

    updated_fields: list[str] = []

    if admin_pw is not None and admin_pw.strip():
        admin.admin_pw = password_encoder.create_hash(admin_pw.strip())
        updated_fields.append("admin_pw")

    if contact is not None and contact.strip():
        admin.contact = contact.strip()
        updated_fields.append("contact")

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    admin.enabled = 1
    session.add(admin)
    session.commit()
    logger.info("ADMIN UPDATE SUCCESS admin_id=%s fields=%s", admin.admin_id, updated_fields)

    return RedirectResponse("/admins/", status_code=303)

@router.post("/resign")
async def resign(
    current_user: str = Depends(authenticate),
    session = Depends(get_session),
):
    admin = session.get(Admin, current_user)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )

    admin.enabled = 0
    session.add(admin)
    session.commit()
    logger.info("ADMIN RESIGN SUCCESS admin_id=%s enabled=0", admin.admin_id)

    response = RedirectResponse("/admins/", status_code=303)
    response.delete_cookie("access_token")
    return response

def _validate_episode_payload(payload: dict) -> list[str]:
    errors: list[str] = []
    episode_id = str(payload.get("episode_id", "")).strip().upper()
    stages = payload.get("stages")

    if not episode_id.startswith("EP") or len(episode_id) < 4:
        errors.append("episode_id는 EP01 같은 형식이어야 합니다.")
    if not payload.get("title"):
        errors.append("title이 필요합니다.")
    if not isinstance(payload.get("background"), dict):
        errors.append("background 객체가 필요합니다.")
    if not isinstance(stages, list) or not stages:
        errors.append("stages 배열이 최소 1개 필요합니다.")
        return errors

    stage_ids = {str(stage.get("stage_id", "")) for stage in stages}
    required = {"stage_id", "stage_number", "title", "type", "location", "description", "messages", "question", "evaluation_axis", "evaluation_criteria", "next_stage"}
    for index, stage in enumerate(stages, start=1):
        missing = [key for key in required if key not in stage]
        if missing:
            errors.append(f"Stage {index}: 누락 필드 {', '.join(missing)}")
        if stage.get("evaluation_axis") not in {"risk_awareness", "refusal", "help_request"}:
            errors.append(f"Stage {index}: evaluation_axis 값이 올바르지 않습니다.")
        next_stage = stage.get("next_stage")
        if next_stage is not None and next_stage not in stage_ids:
            errors.append(f"Stage {index}: next_stage '{next_stage}'를 stages에서 찾을 수 없습니다.")

    if payload.get("total_stages") != len(stages):
        errors.append("total_stages와 실제 stages 개수가 다릅니다.")
    return errors


# 여기부터 LLM_ROLE에 추가를 하는 로직임
# 사실상 게시판에 글을 올리는 로직과도 같음
# LLM_ROLE은 ADMIN_TABLE을 참조


@router.get("/episodes")
async def admin_episode_list(
    request: Request,
    mine: int = 0,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    """관리자용 Episode 목록 화면. /api/episodes와 역할을 분리합니다."""
    db_rows = session.exec(
        select(LlmRole).where(LlmRole.episode_id.is_not(None)).order_by(LlmRole.episode_id)
    ).all()
    db_by_id = {row.episode_id.upper(): row for row in db_rows}

    items: list[dict] = []
    seen: set[str] = set()

    # 게임 엔진이 실제로 읽을 수 있는 공개 Episode를 먼저 보여줍니다.
    for episode in list_episodes():
        episode_id = str(episode.get("episode_id") or "").upper()
        if not episode_id:
            continue
        row = db_by_id.get(episode_id)
        if mine and (row is None or row.admin_id != current_user):
            continue
        stages = episode.get("stages") if isinstance(episode.get("stages"), list) else []
        items.append({
            "episode_id": episode_id,
            "title": str(episode.get("title") or episode_id),
            "stage_count": len(stages),
            "status": row.status if row is not None else "static",
            "source": "DB" if row is not None else "기본 JSON",
            "admin_id": row.admin_id if row is not None else "시스템",
            "updated_at": row.updated_at if row is not None else None,
            "is_db": row is not None,
            "is_owner": row is not None and row.admin_id == current_user,
        })
        seen.add(episode_id)

    # draft는 게임 API에는 안 보이므로 관리자 목록에 별도로 추가합니다.
    for row in db_rows:
        episode_id = row.episode_id.upper()
        if episode_id in seen:
            continue
        if mine and row.admin_id != current_user:
            continue
        try:
            payload = json.loads(row.content)
        except (TypeError, json.JSONDecodeError):
            payload = {}
        stages = payload.get("stages") if isinstance(payload.get("stages"), list) else []
        items.append({
            "episode_id": episode_id,
            "title": row.title or episode_id,
            "stage_count": len(stages),
            "status": row.status,
            "source": "DB",
            "admin_id": row.admin_id or "-",
            "updated_at": row.updated_at,
            "is_db": True,
            "is_owner": row.admin_id == current_user,
        })

    items.sort(key=lambda item: item["episode_id"])
    return template.TemplateResponse(
        request,
        "admin/episode_list.html",
        {
            "episodes": items,
            "current_user": current_user,
            "mine_only": bool(mine),
        },
    )


@router.get("/episodes/{episode_id}")
async def admin_episode_detail(
    request: Request,
    episode_id: str,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    """관리자가 저장된 Episode JSON을 읽기 전용으로 확인합니다."""
    normalized = episode_id.strip().upper()
    row = session.exec(
        select(LlmRole).where(LlmRole.episode_id == normalized)
    ).first()

    if row is not None:
        raw_json = row.content
        status_value = row.status
        source = "DB"
        owner = row.admin_id or "-"
    else:
        episode = next(
            (item for item in list_episodes() if str(item.get("episode_id") or "").upper() == normalized),
            None,
        )
        if episode is None:
            raise HTTPException(status_code=404, detail="Episode not found")
        raw_json = json.dumps(episode, ensure_ascii=False, indent=2)
        status_value = "static"
        source = "기본 JSON"
        owner = "시스템"

    try:
        pretty_json = json.dumps(json.loads(raw_json), ensure_ascii=False, indent=2)
    except (TypeError, json.JSONDecodeError):
        pretty_json = str(raw_json)

    return template.TemplateResponse(
        request,
        "admin/episode_detail.html",
        {
            "episode_id": normalized,
            "scenario_json": pretty_json,
            "status": status_value,
            "source": source,
            "owner": owner,
            "current_user": current_user,
            "is_db": row is not None,
            "is_owner": row is not None and row.admin_id == current_user,
        },
    )



def _owned_episode_or_404(session, episode_id: str, current_user: str) -> LlmRole:
    normalized = episode_id.strip().upper()
    row = session.exec(
        select(LlmRole).where(LlmRole.episode_id == normalized)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="DB Episode not found")
    if row.admin_id != current_user:
        raise HTTPException(status_code=403, detail="다른 관리자가 작성한 Episode입니다.")
    return row


@router.post("/episodes/{episode_id}/publish")
async def publish_episode(
    episode_id: str,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    """초안 Episode를 학생용 게임 목록/API에 공개합니다."""
    row = _owned_episode_or_404(session, episode_id, current_user)
    try:
        payload = json.loads(row.content)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="저장된 Episode JSON이 손상되었습니다.") from exc
    errors = _validate_episode_payload(payload)
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Episode JSON 검증 실패", "errors": errors})
    row.status = "published"
    session.add(row)
    session.commit()
    logger.info("EPISODE PUBLISHED episode_id=%s admin_id=%s", row.episode_id, current_user)
    return RedirectResponse(f"/admins/episodes/{row.episode_id}", status_code=303)


@router.post("/episodes/{episode_id}/unpublish")
async def unpublish_episode(
    episode_id: str,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    """공개 Episode를 다시 초안으로 돌려 학생용 목록에서 숨깁니다."""
    row = _owned_episode_or_404(session, episode_id, current_user)
    row.status = "draft"
    session.add(row)
    session.commit()
    logger.info("EPISODE UNPUBLISHED episode_id=%s admin_id=%s", row.episode_id, current_user)
    return RedirectResponse(f"/admins/episodes/{row.episode_id}", status_code=303)


@router.post("/episodes/{episode_id}/delete")
async def delete_episode(
    episode_id: str,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    """관리자가 직접 작성한 DB Episode를 삭제합니다. 기본 JSON Episode는 삭제하지 않습니다."""
    row = _owned_episode_or_404(session, episode_id, current_user)
    normalized = row.episode_id
    session.delete(row)
    session.commit()
    logger.info("EPISODE DELETED episode_id=%s admin_id=%s", normalized, current_user)
    return RedirectResponse("/admins/episodes?mine=1", status_code=303)


@router.get("/episodes/{episode_id}/edit")
async def edit_episode_form(
    request: Request,
    episode_id: str,
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    row = _owned_episode_or_404(session, episode_id, current_user)
    try:
        pretty_json = json.dumps(json.loads(row.content), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        pretty_json = row.content
    return template.TemplateResponse(
        request,
        "/llm_role/write_form.html",
        {
            "sample_json": pretty_json,
            "selected_category": row.category,
            "editing_episode_id": row.episode_id,
            "editing_status": row.status,
        },
    )


@router.get("/writeform")
async def write_form(
        request : Request,
        current_user: str = Depends(authenticate),
        session = Depends(get_session),
):
    if not session.get(Admin, current_user).enabled:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )
    sample_path = Path(__file__).resolve().parents[3] / "scenario" / "episodes" / "episode01.json"
    sample_json = sample_path.read_text(encoding="utf-8") if sample_path.exists() else "{}"
    return template.TemplateResponse(
        request,
        "/llm_role/write_form.html",
        {
            "sample_json": sample_json,
            "selected_category": "school",
            "editing_episode_id": None,
            "editing_status": None,
        },
    )

@router.post("/write")
async def write(
    category: str = Form(...),
    scenario_json: str = Form(...),
    publish: str | None = Form(None),
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    try:
        payload = json.loads(scenario_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"JSON 형식 오류: {exc.msg}") from exc

    errors = _validate_episode_payload(payload)
    if errors:
        raise HTTPException(status_code=400, detail={"message": "Episode JSON 검증 실패", "errors": errors})

    episode_id = payload["episode_id"].strip().upper()
    payload["episode_id"] = episode_id
    status_value = "published" if publish == "published" else "draft"

    existing = session.exec(
        select(LlmRole).where(LlmRole.episode_id == episode_id)
    ).first()

    if existing is None:
        row = LlmRole(
            episode_id=episode_id,
            title=str(payload["title"]).strip(),
            category=category.strip(),
            content=json.dumps(payload, ensure_ascii=False, indent=2),
            status=status_value,
            admin_id=current_user,
        )
        session.add(row)
    else:
        if existing.admin_id != current_user:
            raise HTTPException(status_code=403, detail="다른 관리자가 작성한 Episode입니다.")
        existing.title = str(payload["title"]).strip()
        existing.category = category.strip()
        existing.content = json.dumps(payload, ensure_ascii=False, indent=2)
        existing.status = status_value
        session.add(existing)

    session.commit()
    logger.info("EPISODE SCENARIO SAVED episode_id=%s status=%s", episode_id, status_value)
    return RedirectResponse(f"/admins/episodes/{episode_id}", status_code=303)


@router.get("/llmRoleList")
async def llm_role_list(
        request : Request,
        session = Depends(get_session),
        current_user: str = Depends(authenticate)
):
    if not session.get(Admin, current_user).enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )

    # 전체보기는 select
    statement = select(LlmRole)
    llm_roles = session.exec(statement).all()

    return template.TemplateResponse(request, "/llm_role/llm_roles.html", {"llm_roles" : llm_roles})

@router.get("/llmRole/{lr_num}")
async def select_one_llm_role(
        request: Request,
        lr_num : int,
        current_user: str | None = Depends(optional_authenticate),
        session = Depends(get_session),
):
    llm_role = session.get(LlmRole, lr_num)
    if not llm_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM role not found",
        )

    return template.TemplateResponse(
        request,
        "llm_role/selectOneLlmRole.html",
        {
                "is_owner": current_user is not None and current_user == llm_role.admin_id,
                "llm_role": llm_role,
        } )
@router.get("/updateLlmRole/{lr_num}")
async def update_llm_role(
        request : Request,
        lr_num : int,
        session = Depends(get_session),
):
    llm_role = session.get(LlmRole, lr_num)

    return template.TemplateResponse(
        request,
        "/llm_role/updateLRForm.html",
        {"llm_role" : llm_role}
    )

@router.post("/updateLlmRole/{lr_num}")
async def update_llm_role(
    lr_num: int,
    category: str = Form(...),
    content: str = Form(...),
    title: str = Form(...),
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    # 한 번 조회한 객체
    llm_role = session.get(LlmRole, lr_num)

    if not llm_role:
        raise HTTPException(
            status_code=404,
            detail="LLM role not found",
        )

    if llm_role.admin_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="Only the author can update this role",
        )

    llm_role.category = category.strip()
    llm_role.title = title.strip()
    llm_role.content = content.strip()

    # update
    session.add(llm_role)
    session.commit()
    session.refresh(llm_role)

    return RedirectResponse(
        f"/admins/llmRole/{lr_num}",
        status_code=303,
    )

# 삭제 로직
@router.get("/deleteLlmRole/{lr_num}")
async def my_llm_roles(
    lr_num : int,
    current_user: str = Depends(authenticate),
    session = Depends(get_session)
):
    llm_role = session.get(LlmRole, lr_num)

    if not llm_role:
        raise HTTPException(
            status_code=404,
            detail="LLM role not found",
        )

    if llm_role.admin_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="Only the author can update this role",
        )

    session.delete(llm_role)
    session.commit()

    return RedirectResponse(
        "/admins/llmRoleList",
        status_code=303,
    )

# 자기가 작성한 것만 조회 -> 마이페이지 격인 곳
@router.get("/myRoles")
async def myRoles(
    request : Request,
    session = Depends(get_session),
    current_user = Depends(authenticate)
):

    total_count = session.exec(
        select(func.count(LlmRole.admin_id)).where(LlmRole.admin_id == current_user)
    ).one()

    statement = (
        select(LlmRole.lr_num, LlmRole.title, LlmRole.created_at)
        .join(Admin, Admin.admin_id == LlmRole.admin_id)
        .where(Admin.admin_id == current_user)
    )
    llm_roles = session.exec(statement).all()

    response = template.TemplateResponse(
        request,
        "/admin/myRoles.html",
        {"llm_roles" : llm_roles , "total_count" : total_count, "admin_id" : current_user}
    )
    return response
