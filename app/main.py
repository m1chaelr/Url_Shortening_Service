from fastapi import FastAPI, Depends, status, HTTPException
from app.database import create_db_tables, get_db
from app import crud, schemas
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
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

# Read original url for short_code
@app.get("/shorten/{short_code}", response_model=schemas.URLResponse)
def get_short_url(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)

    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return db_url

# Update the original url
@app.put("/shorten/{short_code}", response_model=schemas.URLResponse)
def update_short_url(url_data: schemas.URLUpdate, short_code: str, db: Session = Depends(get_db)):
    db_url = crud.update_short_url(db, short_code, url_data)

    if db_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    return db_url
    
