from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Order, OrderItem, Product, User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/orders", response_class=HTMLResponse)
def admin_orders(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/", status_code=303)
    orders = db.query(Order).order_by(Order.id.desc()).all()
    orders_data = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        user = db.query(User).filter(User.id == order.user_id).first()
        products = []
        order_total = 0
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                products.append({
                    "name": product.name,
                    "price": product.price,
                    "quantity": item.quantity,
                    "subtotal": product.price * item.quantity
                })
                order_total += product.price * item.quantity
        orders_data.append({
            "id": order.id,
            "user_id": order.user_id,
            "username": user.username if user else f"Пользователь #{order.user_id}",
            "status": order.status,
            "products": products,
            "total": order_total
        })
    return templates.TemplateResponse(
        request=request,
        name="admin_orders.html",
        context={"request": request, "orders": orders_data}
    )

@router.post("/admin/orders/{order_id}/confirm")
def confirm_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/", status_code=303)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "подтверждён"
        db.commit()
    return RedirectResponse(url="/admin/orders", status_code=303)

@router.post("/admin/orders/{order_id}/cancel")
def cancel_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/", status_code=303)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "отменён"
        db.commit()
    return RedirectResponse(url="/admin/orders", status_code=303)
