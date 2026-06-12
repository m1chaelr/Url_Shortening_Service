from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import logging
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./url_shortener.db")
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_tables():
    '''Create all the table models within the declarative_base metadata registry.'''
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)