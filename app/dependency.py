import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_URI = os.getenv("DB_URI")

# engine = create_engine('sqlite:///data/law-ai.db', echo=True)
engine = create_engine(DB_URI, echo=True)
SQLSession = sessionmaker(bind=engine)
