from typing import List
from fastapi import APIRouter, HTTPException, status

from app.dependency import SQLSession
from app.model.session import Session
from app.rest.session_rest import *

router = APIRouter()


@router.post("/")
async def create_session(req: CreateSessionRequest) -> SessionResponse:
    sql_session = SQLSession()

    new_session = Session(
        name=req.name,
        user_id=req.user_id
    )

    sql_session.add(new_session)

    sql_session.commit()

    response = SessionResponse(
        id=new_session.id,
        name=new_session.name,
        user_id=new_session.user_id
    )

    return response


@router.get("/")
async def get_sessions() -> List[SessionResponse]:
    sql_session = SQLSession()

    sessions = sql_session.query(Session).all()

    sql_session.commit()

    responses = []
    for session in sessions:
        responses.append(SessionResponse(
            id=session.id,
            name=session.name,
            user_id=session.user_id,
        ))
    return responses


@router.get("/{id}")
async def get_session(id: int) -> SessionResponse:
    sql_session = SQLSession()

    session = sql_session.query(Session).where(Session.id == id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    sql_session.commit()

    response = SessionResponse(
        id=session.id,
        name=session.name,
        user_id=session.user_id
    )

    return response


@router.put("/{id}")
async def update_session(id: int, req: UpdateSessionRequest) -> SessionResponse:
    sql_session = SQLSession()

    session = sql_session.query(Session).filter(Session.id == id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if req.name is not None:
        session.name = req.name

    sql_session.commit()
    sql_session.refresh(session)

    response = SessionResponse(
        id=session.id,
        name=session.name,
        user_id=session.user_id
    )

    return response


@router.delete("/{id}")
async def delete_session(id: int) -> None:
    sql_session = SQLSession()

    session = sql_session.query(Session).filter(Session.id == id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    sql_session.delete(session)
    sql_session.commit()

    return
