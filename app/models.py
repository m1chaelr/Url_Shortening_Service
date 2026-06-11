from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ShortenedURL(Base):
    '''Add a ShortenedURL table model. Extending the declarative_base adds this model to the metadata registry.'''
    __tablename__ = "shortened_urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)