


from fastapi import FastAPI

from src.api.expiry_routes import router as expiry_router
from src.api.ocr_routes import router as ocr_router


app = FastAPI(
    title="StockWise AI API",
    description="Backend API for StockWise AI inventory intelligence system",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to StockWise AI API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "StockWise AI"
    }


# Register API routes
app.include_router(expiry_router)
app.include_router(ocr_router)
