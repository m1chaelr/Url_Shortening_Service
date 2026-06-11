from fastapi import FastAPI, Depends, status
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
