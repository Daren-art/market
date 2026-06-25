import secrets
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

CSRF_TOKEN_KEY = "csrftoken"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

EXEMPT_PATHS = set()

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.cookies.get(CSRF_TOKEN_KEY)
        if not token:
            token = secrets.token_hex(32)

        if request.method not in SAFE_METHODS and request.url.path not in EXEMPT_PATHS:
            submitted: Optional[str] = None
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form = await request.form()
                submitted = form.get("csrf_token")
            else:
                submitted = request.headers.get("X-CSRFToken")
            if not submitted or not secrets.compare_digest(submitted, token):
                raise HTTPException(status_code=403, detail="CSRF token missing or invalid")

        response = await call_next(request)
        response.set_cookie(
            key=CSRF_TOKEN_KEY,
            value=token,
            httponly=False,   
            samesite="lax",
            secure=False,    
        )
        return response

def get_csrf_token(request: Request) -> str:
    token = request.cookies.get(CSRF_TOKEN_KEY)
    if not token:
        token = secrets.token_hex(32)
    return token
