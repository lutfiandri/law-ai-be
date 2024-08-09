from app.router.auth_router import router as auth_router

from fastapi import FastAPI

from app.util.ai.rag_chain import load_rag_chain_model

load_rag_chain_model()

# app = FastAPI()

# app.include_router(auth_router, prefix="/auth")
