from pydantic import BaseModel


class RegisterRequest(BaseModel):
    password: str
    name: str
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
