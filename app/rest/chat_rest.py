from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AnswerLawResponse(BaseModel):
    jawaban: Optional[str] = None
    undang_undang: Optional[str] = None
    bab: Optional[str] = None
    pasal: Optional[str] = None
    ayat: Optional[str] = None


class AnswerResponse(BaseModel):
    full_answer: str
    laws: List[AnswerLawResponse]


class ChatResponse(BaseModel):
    id: int
    session_id: int
    type: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[AnswerResponse] = None
    question_at: Optional[datetime] = None
    answer_at: Optional[datetime] = None


class CreateChatRequest(BaseModel):
    type: str
    question: str
