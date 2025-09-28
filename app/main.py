"""FastAPI application setup and main router."""

from fastapi import FastAPI
from app.routes import recommend

app = FastAPI(title="Lumia Financial API", version="1.0.0")

# Include routers
app.include_router(recommend.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Lumia Financial API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)