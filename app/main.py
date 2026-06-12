from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import get_db
from app.logging_config import setup_logging
from app import crud, schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(lifespan=lifespan)

# Root response
@app.get("/")
def root_response():
    return {
        "status" : "ok",
        "message" : "This is the root endpoint of the server",
    }

# Health Check
@app.get("/health")
def health_check():
    # Perform check to the server state
    return {"status": "ok"}

# Create short url
@app.post("/shorten", response_model=schemas.URLResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(url_data: schemas.URLCreate, db: Session = Depends(get_db)):
    return crud.create_short_url(db, url_data)

# Read-only stats for a shortened URL
@app.get("/shorten/{short_code}/stats", response_model=schemas.URLStats)
def get_short_url_stats(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)

    if db_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    return db_url

# Read original url for short_code
@app.get("/shorten/{short_code}", response_model=schemas.URLResponse)
def get_short_url(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)

    if db_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    return crud.increment_access_count(db, db_url)

# Update the original url
@app.put("/shorten/{short_code}", response_model=schemas.URLResponse)
def update_short_url(url_data: schemas.URLUpdate, short_code: str, db: Session = Depends(get_db)):
    db_url = crud.update_short_url(db, short_code, url_data)

    if db_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    return db_url

# Delete shortened url
@app.delete("/shorten/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_url(short_code: str, db: Session = Depends(get_db)):
    
    if not crud.delete_short_url(db, short_code):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    return

# Redirect to Original url
@app.get("/{short_code}") # Could also use 307 (temporary) or 301 (permanent)
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)

    if db_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    db_url = crud.increment_access_count(db, db_url)

    return RedirectResponse(db_url.original_url, status_code=status.HTTP_302_FOUND)
