from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from typing import Union

from app.router.auth import router as auth_router

from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
