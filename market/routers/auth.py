from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from csrf import get_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html",
        context={"error": None, "csrf_token": get_csrf_token(request)}
    )


@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),          # поле есть в форме, middleware уже проверил
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "Email уже используется", "csrf_token": get_csrf_token(request)}
        )
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "Имя пользователя занято", "csrf_token": get_csrf_token(request)}
        )
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html",
        context={"error": None, "csrf_token": get_csrf_token(request)}
    )


@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Неверный email или пароль", "csrf_token": get_csrf_token(request)}
        )
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
