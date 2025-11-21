from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.core.config import settings
from app.core.metrics import setup_metrics
app = FastAPI(default_response_class=ORJSONResponse)

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}

@app.get("/")
async def root():
    return {"message": "Hello World"}

setup_metrics(app)
