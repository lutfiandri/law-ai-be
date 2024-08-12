from typing import List
from fastapi import APIRouter, HTTPException, status, Request

from app.dependency import SQLSession
from app.model.session import Session
from app.rest.session_rest import *

router = APIRouter()


@router.post("/")
async def create_session(r: Request, req: CreateSessionRequest) -> SessionResponse:
    print(r.state.jwt)

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        pass

    sql_session = SQLSession()

    new_session = Session(
        name=req.name,
        user_id=user_id
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
async def get_sessions(r: Request) -> List[SessionResponse]:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    query = sql_session.query(Session).where(Session.user_id == user_id)
    sessions = query.all()

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
async def get_session(r: Request, id: int) -> SessionResponse:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    session = sql_session.query(Session).where(
        Session.id == id, Session.user_id == user_id).first()
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
async def update_session(r: Request, id: int, req: UpdateSessionRequest) -> SessionResponse:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    session = sql_session.query(Session).filter(
        Session.id == id, Session.user_id == user_id).first()
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
async def delete_session(r: Request, id: int) -> None:
    sql_session = SQLSession()

    user_id = None
    try:
        user_id = r.state.jwt['user']['id']
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    session = sql_session.query(Session).filter(
        Session.id == id, Session.user_id == user_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    sql_session.delete(session)
    sql_session.commit()

    return
