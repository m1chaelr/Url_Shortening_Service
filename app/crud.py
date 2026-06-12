import secrets
import string
from sqlalchemy.orm import Session
from app import models, schemas
import logging

logger = logging.getLogger(__name__)
CHARACTERS = string.ascii_letters + string.digits

def generate_short_code(length: int = 6) -> str:
    return "".join(secrets.choice(CHARACTERS) for _ in range(length))

def get_url_by_short_code(db: Session, short_code: str):
    return db.query(models.ShortenedURL).filter(models.ShortenedURL.short_code == short_code).first()

def create_short_url(db: Session, url_data: schemas.URLCreate):
    short_code = generate_short_code()

    # Collision handling
    while get_url_by_short_code(db, short_code) is not None:
        logger.warning(f"Collision for short_code = {short_code}, generating new short_code.")
        short_code = generate_short_code()
    
    # Create a row within the ShortenedUrl table
    db_url = models.ShortenedURL(
        original_url=str(url_data.original_url),
        short_code=short_code
    )

    logger.info(f"Creating new record for short_code = {short_code}")
    # Save the row
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url

def update_short_url(db: Session, short_code: str, url_data: schemas.URLUpdate):
    db_url = get_url_by_short_code(db, short_code)

    if db_url is None:
        return None
    
    db_url.original_url = str(url_data.original_url)

    logger.info(f"Updating record for short_code = {short_code}:")
    # Mutated records are marked as 'dirty' and resultant .commit() performs an UPDATE, not an INSERT
    db.commit()
    db.refresh(db_url)

    return db_url

def delete_short_url(db: Session, short_code: str):
    db_url = get_url_by_short_code(db, short_code)

    if db_url is None:
        return False
    
    logger.info(f"Deleting record for short_code = {short_code}.")
    db.delete(db_url)
    db.commit()
    
    return True

def increment_access_count(db: Session, db_url: models.ShortenedURL):

    if db_url is None:
        return None
    
    db_url.access_count += 1
    # TODO: access-count increments are note concurrency-hardened, if 2 users GET a url at the same time, we may only increment by 1, not 2.
    # in future development, use atomic database update

    db.commit()
    db.refresh(db_url)

    return db_url
