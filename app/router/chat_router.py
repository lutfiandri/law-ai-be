from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import json
import copy

from app.dependency import SQLSession
from app.model.session import Session
from app.model.chat import Chat
from app.rest.chat_rest import *
from app.util.ai.rag_chain import load_rag_chain_model, post_process_answer

router = APIRouter()

rag_chain = load_rag_chain_model()


@router.post("/")
async def create_session(req: CreateChatRequest, session_id: int) -> ChatResponse:
    sql_session = SQLSession()

    # check session exists
    session = sql_session.query(Session).filter(
        Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    chat = Chat(
        session_id=session_id,
        type=req.type,
        question=req.question,
        question_at=datetime.now(),
    )

    sql_session.add(chat)

    # answer
    qa = rag_chain.invoke({"input": req.question, "chat_history": []})

    chat.answer = post_process_answer(qa["answer"])
    chat.answer_at = datetime.now()

    sql_session.commit()
    sql_session.refresh(chat)

    response = ChatResponse(
        id=chat.id,
        session_id=chat.session_id,
        type=chat.type,
        question=chat.question,
        answer=json.loads(chat.answer) if chat.answer else None,
        question_at=chat.question_at,
        answer_at=chat.answer_at,
    )

    return response
