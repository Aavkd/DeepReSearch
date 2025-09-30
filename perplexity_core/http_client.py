import httpx
import asyncio
from contextlib import asynccontextmanager
from .config import settings


@asynccontextmanager
async def get_client():
    """
    Create an async HTTP client with appropriate settings.
    """
    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10
    )
    
    timeout = httpx.Timeout(
        timeout=settings.REQUEST_TIMEOUT_S
    )
    
    headers = {
        "User-Agent": "Perplexity-Python-Runner/1.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    async with httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        headers=headers
    ) as client:
        yield client