from pydantic import BaseModel
from typing import Optional


class SessionResponse(BaseModel):
    id: int
    name: Optional[str] = None
    user_id: Optional[int] = None


class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None


class UpdateSessionRequest(BaseModel):
    name: Optional[str] = None
