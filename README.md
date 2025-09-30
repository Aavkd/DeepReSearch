# Local Perplexity-like RAG Search Engine

A production-ready implementation of a Perplexity-style search engine with a dual-runner architecture. The Python runner is now the primary implementation, with n8n available as an alternative workflow orchestrator.

## Features

- Real-time web answers with citations
- Fast, reliable, deterministic JSON outputs
- Dual-runner architecture (Python + n8n)
- Modular pipeline with replaceable search and scrape backends
- Built-in caching, retries, rate-limiting, and deduplication
- Safety measures and attribution

## Architecture Overview

```
[Client/UI/Webhook] → Python Runner or n8n
  ├─ Query Normalizer (LLM optional)
  ├─ Search API (Tavily/Brave/SearchAPI)
  ├─ URL Dedup + Ranking
  ├─ Content Fetch (Firecrawl / Article Extractor)
  ├─ Clean/Chunk/Trim → (optional) Cache/Vectorize
  ├─ Synthesis LLM (Ollama/OpenRouter) → JSON answer + citations
  ├─ Safety pass (LLM or rule set)
  ├─ Persist (DB/Sheet) + Cache
  └─ Respond (JSON)
```

## Prerequisites

- Docker and Docker Compose
- API keys for the services you want to use:
  - Search: Tavily, Brave, or SearchAPI
  - Content extraction: Firecrawl
  - LLMs: OpenRouter API key or Ollama setup

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd perplexity-engine
   ```

2. **Configure environment variables**
   Copy the `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your actual API keys:
   - Search provider keys (Tavily, Brave, or SearchAPI)
   - Firecrawl API key
   - OpenRouter API key (if using remote LLMs)
   - Configure Ollama settings if using local LLMs
   
   You can verify your environment variables are set correctly:
   ```bash
   python check_host_env.py
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Pull the Ollama model (if using local LLMs)**
   ```bash
   docker exec -it perplexity-engine-ollama-1 ollama pull qwen2.5:14b-instruct
   ```

5. **Access the reference UI**
   Open `ui/index.html` in a web browser or serve it with a web server.

## Usage

The Python runner is now the default and recommended approach. You can use either the API or CLI interfaces.

### API Endpoint

Send a POST request to the Python API endpoint:

```
POST http://localhost:8080/api/search
```

Example payload:
```json
{
  "query": "What happened with the latest Artemis mission?",
  "maxResults": 6,
  "locale": "en",
  "timeRange": "30d",
  "strict": true,
  "forceLocal": false,
  "includeDomains": ["nasa.gov", "esa.int"],
  "excludeDomains": ["reddit.com"],
  "ui": { "mode": "concise" }
}
```

### CLI Usage

```bash
# Install dependencies
pip install -e .

# Run a search
python -m apps.cli run "What is the latest in AI research?"

# Start the API server
python -m apps.cli serve
```

### Expected Response

```json
{
  "answer": "...short synthesis...",
  "bullets": ["…", "…"],
  "sources": [
    {
      "title": "...",
      "url": "https://...",
      "published": "2025-09-15",
      "snippet": "...",
      "relevance": 0.92
    }
  ],
  "diagnostics": {
    "searchProvider": "brave",
    "llm": "x-ai/grok-4-fast:free",
    "latencyMs": 2380,
    "cached": false,
    "tokens": null
  }
}
```

## Dual-Runner Architecture

This project implements a dual-runner architecture where you can choose between:

1. **Python Runner (Default)**: Code-based implementation with FastAPI and CLI interfaces
2. **n8n Runner**: Visual workflow-based implementation

Both runners share the same data contracts, caching, and persistence layers.

### Python Runner (Recommended)

#### Using Docker (Recommended)

```bash
# Start all services including the Python API
docker-compose up -d

# The Python API will be available at http://localhost:8080
```

#### Using CLI

```bash
# Install dependencies
pip install -e .

# Run a search
python -m apps.cli run "What is the latest in AI research?"

# Start the API server
python -m apps.cli serve
```

#### Using Direct API Calls

```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the latest in AI research?",
    "maxResults": 5,
    "locale": "en",
    "timeRange": "30d"
  }'
```

### n8n Runner (Alternative)

If you prefer to use the n8n workflow:

1. **Import and configure the n8n workflow**
   - Open n8n at http://localhost:5678
   - If this is your first time, use the default credentials (admin/admin) to log in
   - Click on "Workflows" in the left sidebar
   - Click the "+" button to create a new workflow
   - Click on the workflow name at the top to rename it to "Local Perplexity RAG"
   - Click on the "Workflow" menu (three dots) and select "Import from File"
   - Select the file `n8n/workflows/local_perplexity_rag.json`
   - Follow our detailed [Step-by-Step Credentials Configuration Guide](CREDENTIALS_GUIDE.md) to properly configure all credentials
   - Click the "Activate" toggle to activate the workflow

2. **Use the n8n API endpoint**
   ```
   POST http://localhost:5678/webhook/api/search
   ```

### Project Structure

```
.
├── apps/
│   ├── api/           # FastAPI application
│   └── cli/           # Command-line interface
├── perplexity_core/   # Core pipeline components
│   ├── cache/         # Redis caching
│   ├── search/        # Search providers
│   ├── extract/       # Content extraction
│   ├── rank/          # Ranking and deduplication
│   ├── llm/           # LLM providers
│   ├── synth/         # Synthesis and prompts
│   ├── safety/        # Safety guard
│   ├── pipeline/      # Main orchestrator
│   ├── util/          # Utility functions
│   ├── store/         # Persistence
│   ├── config.py      # Configuration
│   ├── contracts.py   # Data contracts
│   └── hashing.py     # Cache key generation
├── n8n/               # n8n workflow
├── docker/            # Docker files
├── ui/                # Reference UI
├── .env.example       # Environment example
├── docker-compose.yml # Service orchestration
├── requirements.txt   # Python dependencies
└── pyproject.toml     # Package configuration
```

## Testing

We provide several test scripts to help you verify your setup:

1. **Environment Variables Test**:
   - `check_host_env.py` - Check if environment variables are accessible from the host
   - `test_env_vars.py` - Test if n8n can access environment variables
   - `test_env_vars.ps1` - PowerShell version of the same test

2. **Service Connectivity Test**:
   - `test_redis.py` - Test Redis connectivity
   - `test_redis.ps1` - PowerShell version of Redis test

3. **Workflow Test**:
   - `test_search.py` - Test the complete search workflow
   - `test_webhook.ps1` - PowerShell version of the search test
   - `test_n8n_webhook.py` - Direct test of n8n webhooks
   - `test_cache_fix.py` - Test the cache fix implementation
   - `test_cache_fix.ps1` - PowerShell version of cache fix test

4. **Test Workflows**:
   - `test_n8n_env.json` - Test environment variable access in n8n
   - `test_http_env.json` - Test HTTP Request node environment variable usage
   - `debug_env_vars.json` - Debug environment variable access issues
   - `test_http_env_vars.json` - Test HTTP environment variables
   - `comprehensive_env_test.json` - Comprehensive environment variable test
   - `test_cache_fix.json` - Test the cache fix implementation

## Customization

### Switching Between Search Providers

The workflow supports multiple search providers. Configure your preferred provider by setting the appropriate API key in the `.env` file.

### Using Local LLMs

To use Ollama for local inference:
1. Ensure Ollama is running (via Docker in this setup)
2. Pull your preferred model: `ollama pull qwen2.5:14b-instruct`
3. Set `OLLAMA_HOST` and `OLLAMA_MODEL` in `.env`

### Using Remote LLMs

To use OpenRouter for remote inference:
1. Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` in `.env`

## Extending the System

The modular architecture allows for easy extensions:

1. **Vector RAG**: Add vector storage (pgvector) for enhanced retrieval
2. **Multi-Agent Planning**: Add decision-making steps for complex queries
3. **Summarize-then-Read**: Implement hierarchical processing for long documents

## Troubleshooting

See our detailed [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common issues.

For environment variable specific issues, see our [Environment Variable Troubleshooting Guide](ENV_TROUBLESHOOTING.md).

Quick troubleshooting steps:
- Check that all environment variables are properly set
- For Ollama issues, ensure the model is pulled and the service is accessible
- For search API errors, verify your API keys and quota limits
- Check the service logs with: `docker-compose logs`

## License

This project is open-source and available under the MIT License.