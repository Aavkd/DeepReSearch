from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import json
import httpx

from perplexity_core.contracts import SearchRequest, SearchResponse
from perplexity_core.pipeline.runner import Pipeline
from perplexity_core.config import settings

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


@app.get("/api/models")
async def get_models():
    """
    Get available models from all configured providers.
    """
    models = {
        "openrouter": {
            "configured": settings.OPENROUTER_MODEL if settings.OPENROUTER_API_KEY else None,
            "available": [],
            "error": None
        },
        "ollama": {
            "configured": settings.OLLAMA_MODEL,
            "available": [],
            "host": settings.OLLAMA_HOST,
            "error": None
        }
    }
    
    # Get Ollama models
    try:
        print(f"Attempting to connect to Ollama at: {settings.OLLAMA_HOST}")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=10.0)
            print(f"Ollama response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Ollama response data: {data}")
                models["ollama"]["available"] = [model["name"] for model in data.get("models", [])]
                if not models["ollama"]["available"]:
                    models["ollama"]["error"] = "No models installed. Run 'ollama pull <model_name>' to install models."
            else:
                models["ollama"]["error"] = f"Ollama API returned status {response.status_code}"
    except httpx.ConnectError as e:
        models["ollama"]["error"] = f"Connection failed to {settings.OLLAMA_HOST}: {str(e)}"
        print(f"Connection error to Ollama: {e}")
    except httpx.TimeoutException as e:
        models["ollama"]["error"] = f"Timeout connecting to {settings.OLLAMA_HOST}: {str(e)}"
        print(f"Timeout error to Ollama: {e}")
    except Exception as e:
        models["ollama"]["error"] = f"Failed to connect to Ollama: {str(e)}"
        print(f"Failed to fetch Ollama models: {e}")
    
    # For OpenRouter, validate the configuration
    if settings.OPENROUTER_API_KEY and settings.OPENROUTER_MODEL:
        models["openrouter"]["available"] = [settings.OPENROUTER_MODEL]
    elif not settings.OPENROUTER_API_KEY:
        models["openrouter"]["error"] = "OpenRouter API key not configured"
    
    return models


if __name__ == "__main__":
    import uvicorn
    from perplexity_core.config import settings
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )