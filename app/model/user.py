from sqlalchemy import Column, Integer, String

from app.dependency import engine
from app.model.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


Base.metadata.create_all(engine)
