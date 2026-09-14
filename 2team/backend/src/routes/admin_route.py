from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate, optional_authenticate
from database.connection import get_session
from model.admin import Admin, TokenResponse

router = APIRouter(prefix="/admins", tags=["Admins"])

template = Jinja2Templates("templates/")

password_encoder = HashPassword()

@router.get("/")
async def admin_index(
    request: Request,
    current_user: str | None = Depends(optional_authenticate),
):
    return template.TemplateResponse(
        request,
        "admin/admin_index.html",
        {"is_authenticated": current_user is not None},
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
    print(f"[ADMIN UPDATE SUCCESS] admin_id={admin.admin_id}, fields={updated_fields}")

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
    print(f"[ADMIN RESIGN SUCCESS] admin_id={admin.admin_id}, enabled=0")

    response = RedirectResponse("/admins/", status_code=303)
    response.delete_cookie("access_token")
    return response
