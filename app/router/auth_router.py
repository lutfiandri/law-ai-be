from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import bcrypt
import jwt
import datetime

from app.dependency import SQLSession
from app.model.user import User
from app.rest.auth_rest import *

router = APIRouter()

# Secret key to encode and decode the JWT tokens
SECRET_KEY = "law-ai-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register")
async def register(req: RegisterRequest) -> None:
    session = SQLSession()

    user = session.query(User).filter_by(username=req.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(req.password.encode('utf-8'), salt)

    new_user = User(
        name=req.name,
        username=req.username,
        password=password_hash
    )

    session.add(new_user)

    session.commit()
    return


@router.post("/login")
async def login(req: LoginRequest) -> LoginResponse:
    session = SQLSession()

    user = session.query(User).filter_by(username=req.username).first()
    if user is None or not bcrypt.checkpw(req.password.encode('utf-8'), user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user.username})

    session.commit()

    response = LoginResponse(
        access_token=access_token,
        token_type="Bearer"
    )
    return response


# helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.datetime.now(datetime.UTC) +
                     datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
