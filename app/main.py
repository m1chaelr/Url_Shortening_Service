from fastapi import FastAPI
app = FastAPI()

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
