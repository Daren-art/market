from fastapi import FastAPI
from database.database import engine
from database.models import Base
from routers.auth import router as auth_router
from routers.products import router as products_router
from routers.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
from routers.cart import router as cart_router
from starlette.middleware.sessions import SessionMiddleware
from routers.admin_orders import router as admin_orders_router
from config import SECRET_KEY

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(admin_router)
app.include_router(cart_router)
app.include_router(admin_orders_router)
