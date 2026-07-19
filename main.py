from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from logging_config import logger

app = FastAPI()

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    try:
        logger.info("Root endpoint called")
        print(1/0)
        return {"message": "Hello"}
    except Exception as e:
        logger.error(f"Error found {e}")
        return JSONResponse("Error found", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)