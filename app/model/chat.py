from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from app.dependency import engine
from app.model.base import Base


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    type = Column(String(32), nullable=True)  # first | followup
    question = Column(String(255), nullable=True)
    answer = Column(String(255), nullable=True)
    question_at = Column(DateTime, nullable=True)
    answer_at = Column(DateTime, nullable=True)


Base.metadata.create_all(engine)
