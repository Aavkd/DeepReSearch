from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import json

from perplexity_core.contracts import SearchRequest, SearchResponse
from perplexity_core.pipeline.runner import Pipeline

app = FastAPI(
    title="Local Perplexity API",
    description="AI-powered search engine with citation capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = Pipeline()


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    """
    Perform a search and return a synthesized answer with citations.
    """
    try:
        response = await pipeline.run(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.post("/api/search-raw")
async def search_raw(req: SearchRequest):
    """
    Perform a search and return raw response (for debugging).
    """
    try:
        response = await pipeline.run(req)
        return json.loads(response.model_dump_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from perplexity_core.config import settings
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )