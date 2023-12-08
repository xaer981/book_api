import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    'DB_URL',
    'postgresql://postgres:postgres@book_api-db/book_api'
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Connects to DB. Closes connection in final.

    Yields: db.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
