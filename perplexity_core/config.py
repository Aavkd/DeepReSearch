from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # n8n settings
    N8N_HOST: str = "localhost"
    N8N_PORT: int = 5678
    N8N_ENCRYPTION_KEY: str = "replace_me"
    
    # Search providers
    TAVILY_API_KEY: Optional[str] = None
    BRAVE_API_KEY: Optional[str] = None
    SEARCHAPI_IO_KEY: Optional[str] = None
    
    # Extraction
    FIRECRAWL_API_KEY: Optional[str] = None
    
    # LLMs
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "x-ai/grok-4-fast:free"
    OLLAMA_HOST: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    
    # Storage/Caching
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    POSTGRES_HOST: str = "localhost"
    POSTGRES_DB: str = "perplex"
    POSTGRES_USER: str = "perplex"
    POSTGRES_PASSWORD: str = "perplex"
    
    # Python runner settings
    RUNNER: str = "python"  # or "n8n"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENCY: int = 6
    REQUEST_TIMEOUT_S: int = 20
    CACHE_TTL_S: int = 3600  # 1 hour default
    
    # Structured content generation and discover sources
    STRUCTURED_ENABLED: bool = True
    DISCOVER_ENABLED: bool = True
    STRUCTURED_MAX_TOKENS: int = 2000
    DISCOVER_MAX_SOURCES: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()