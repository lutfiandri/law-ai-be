from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime
import json
import copy

from app.dependency import SQLSession
from app.model.session import Session
from app.model.chat import Chat
from app.rest.chat_rest import *
from app.util.ai.rag_chain import create_retriever_and_chain, create_rag_chain, post_process_answer

router = APIRouter()

retriever, chain = create_retriever_and_chain()


@router.post("/")
async def create_chat(r: Request, req: CreateChatRequest, session_id: int) -> ChatResponse:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    # check session exists
    session = sql_session.query(Session).where(
        Session.id == session_id, Session.user_id == user_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # answer
    rag_chain = create_rag_chain(retriever, chain)

    # load history
    chat_history = []
    if req.type == "followup":
        chats = sql_session.query(Chat).where(
            Chat.session_id == session_id).all()
        for chat in chats:
            single_chat_history = [chat.question, chat.answer]
            chat_history.extend(single_chat_history)

    print("chat_history")
    print(chat_history)
    print()

    qa = rag_chain.invoke(
        {"input": req.question, "chat_history": chat_history})

    chat = Chat(
        session_id=session_id,
        type=req.type,
        question=req.question,
        question_at=datetime.now(),
    )

    sql_session.add(chat)

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


@router.get("/")
async def get_chats(r: Request, session_id: int) -> List[ChatResponse]:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    # check session exists
    session = sql_session.query(Session).filter(
        Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    chats = sql_session.query(Chat).where(
        Chat.session_id == session_id, Session.user_id == user_id).all()

    sql_session.commit()

    responses = []
    for chat in chats:
        response = ChatResponse(
            id=chat.id,
            session_id=chat.session_id,
            type=chat.type,
            question=chat.question,
            answer=json.loads(chat.answer) if chat.answer else None,
            question_at=chat.question_at,
            answer_at=chat.answer_at,
        )
        responses.append(response)

    return responses
