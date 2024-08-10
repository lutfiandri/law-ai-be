from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import enum


class ChatAnswerLawResponse(BaseModel):
    jawaban: Optional[str] = None
    undang_undang: Optional[str] = None
    bab: Optional[str] = None
    pasal: Optional[str] = None
    ayat: Optional[str] = None


class ChatAnswerResponse(BaseModel):
    full_answer: str
    laws: List[ChatAnswerLawResponse]


# class ChatType(enum.StrEnum):
#     first = "first"
#     followup = "followup"


class ChatResponse(BaseModel):
    id: int
    session_id: int
    # type: ChatType
    type: str
    question: Optional[str] = None
    answer: Optional[ChatAnswerResponse] = None
    question_at: Optional[datetime] = None
    answer_at: Optional[datetime] = None


class CreateChatRequest(BaseModel):
    # type: ChatType
    type: str
    question: str
