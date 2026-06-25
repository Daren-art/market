from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Product, CartItem, OrderItem
from csrf import get_csrf_token
import shutil
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

from config import ADMIN_PASSWORD


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin_login.html",
        context={"error": None, "csrf_token": get_csrf_token(request)}
    )


@router.post("/admin/login")
def admin_login(request: Request, password: str = Form(...), csrf_token: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request, name="admin_login.html",
        context={"error": "Неверный пароль", "csrf_token": get_csrf_token(request)}
    )


@router.get("/admin/logout")
def admin_logout(request: Request):
    request.session.pop("is_admin", None)
    return RedirectResponse(url="/", status_code=303)


@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/admin/login", status_code=303)
    products = db.query(Product).all()
    return templates.TemplateResponse(
        request=request, name="admin.html",
        context={"products": products, "csrf_token": get_csrf_token(request)}
    )


@router.post("/admin/product")
def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/admin/login", status_code=303)
    os.makedirs("static/uploads", exist_ok=True)
    file_path = f"static/uploads/{image.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    product = Product(
        name=name,
        description=description,
        price=price,
        image=f"/static/uploads/{image.filename}"
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/product/{product_id}/delete")
def delete_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/admin/login", status_code=303)
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        # ИСПРАВЛЕНИЕ 4: удаляем связанные CartItem
        db.query(CartItem).filter(CartItem.product_id == product_id).delete()

        # ИСПРАВЛЕНИЕ 4: удаляем связанные OrderItem
        db.query(OrderItem).filter(OrderItem.product_id == product_id).delete()

        # ИСПРАВЛЕНИЕ 4: удаляем файл изображения с диска
        if product.image:
            # image хранится как "/static/uploads/filename.jpg"
            file_path = product.image.lstrip("/")
            if os.path.isfile(file_path):
                os.remove(file_path)

        db.delete(product)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)
