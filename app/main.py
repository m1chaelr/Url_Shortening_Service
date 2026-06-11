from fastapi import FastAPI
from app.database import create_db_tables
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
