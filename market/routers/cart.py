from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import CartItem, Product, Order, OrderItem

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/cart/add/{product_id}")
def add_to_cart(product_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    existing = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.product_id == product_id).first()
    if existing:
        existing.quantity += 1
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
        db.add(item)
    db.commit()
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/cart/remove/{product_id}")
def remove_from_cart(product_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.product_id == product_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/cart", status_code=303)

@router.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    products = []
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            subtotal = product.price * item.quantity
            products.append({"id": product.id, "name": product.name, "price": product.price, "image": product.image, "quantity": item.quantity, "subtotal": subtotal})
            total += subtotal
    return templates.TemplateResponse(request=request, name="cart.html", context={"request": request, "products": products, "total": total})

@router.post("/checkout")
def checkout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        return RedirectResponse(url="/cart", status_code=303)
    order = Order(user_id=user_id, status="ожидает")
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(order_item)
    db.commit()
    for item in cart_items:
        db.delete(item)
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)
