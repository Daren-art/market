from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Product, CartItem, Order, OrderItem
from csrf import get_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    user_id = request.session.get("user_id")
    cart_count = 0
    if user_id:
        cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
        cart_count = sum(item.quantity for item in cart_items)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "products": products,
            "cart_count": cart_count,
            "csrf_token": get_csrf_token(request)
        }
    )


@router.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).all()
    orders_data = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        products_list = []
        order_total = 0
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                subtotal = product.price * item.quantity
                products_list.append({
                    "name": product.name,
                    "price": product.price,
                    "quantity": item.quantity,
                    "subtotal": subtotal
                })
                order_total += subtotal
        orders_data.append({
            "id": order.id,
            "status": order.status,
            "products": products_list,
            "total": order_total
        })
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={"request": request, "orders": orders_data}
    )
