from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data/law-ai.db', echo=True)
SQLSession = sessionmaker(bind=engine)
