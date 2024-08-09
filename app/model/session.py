from sqlalchemy import Column, Integer, String, ForeignKey

from app.dependency import engine
from app.model.base import Base


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


Base.metadata.create_all(engine)
