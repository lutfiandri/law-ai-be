from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router.auth_router import router as auth_router
from app.router.session_router import router as session_router
from app.router.chat_router import router as chat_router


app = FastAPI()\

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(session_router, prefix="/sessions")
app.include_router(chat_router, prefix="/sessions/{session_id}/chats")
