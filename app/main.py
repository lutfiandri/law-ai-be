
from fastapi import FastAPI

from app.util.ai.rag_chain import load_rag_chain_model
from app.router.auth_router import router as auth_router
from app.router.session_router import router as session_router
from app.router.chat_router import router as chat_router

# load_rag_chain_model()

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(session_router, prefix="/sessions")
app.include_router(chat_router, prefix="/sessions/{session_id}/chats")
