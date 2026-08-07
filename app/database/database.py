from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Neon suspends an idle compute and drops its connections, so check a pooled
# connection is still alive before handing it out and retire it well before then.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base that every ORM model inherits from.
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
