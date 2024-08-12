from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router.auth_router import router as auth_router
from app.router.session_router import router as session_router
from app.router.chat_router import router as chat_router

import jwt

app = FastAPI()\

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "law-ai-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.middleware("http")
async def decode_access_token(request, call_next):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        request.state.jwt = None
        response = await call_next(request)
        return response

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.jwt = payload
    except (IndexError, jwt.PyJWTError):
        pass

    response = await call_next(request)
    return response


app.include_router(auth_router, prefix="/auth")
app.include_router(session_router, prefix="/sessions")
app.include_router(chat_router, prefix="/sessions/{session_id}/chats")
