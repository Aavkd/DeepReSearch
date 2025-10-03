# Local Perplexity-like RAG Search Engine

A production-ready implementation of a Perplexity-style search engine with a dual-runner architecture. The Python runner is now the primary implementation, with n8n available as an alternative workflow orchestrator.

## Features

- Real-time web answers with citations
- Fast, reliable, deterministic JSON outputs
- Dual-runner architecture (Python + n8n)
- Modular pipeline with replaceable search and scrape backends
- Built-in caching, retries, rate-limiting, and deduplication
- Safety measures and attribution
- **Structured Content Generation** (NotebookLM-style Studio Panel)
- **Discover Sources** feature for research planning

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
   - Set `STRUCTURED_ENABLED=true` and `DISCOVER_ENABLED=true` to enable new features
   
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

### Structured Content Generation

The search endpoint now supports structured content generation with the `output_type` parameter:

```json
{
  "query": "Quantum sensing advances since 2023",
  "maxResults": 6,
  "timeRange": "365d",
  "output_type": "briefing_doc",
  "strict": true,
  "forceLocal": false
}
```

Supported output types:
- `answer` (default)
- `faq`
- `study_guide`
- `briefing_doc`
- `timeline`
- `mind_map`

When `output_type` is specified, the response includes a `structured` field with the generated content:

```json
{
  "answer": "One-paragraph overview.",
  "bullets": ["…", "…"],
  "sources": [{ "title": "...", "url": "...", "published": "2025-09-15", "snippet": "...", "relevance": 0.92 }],
  "structured": {
    "type": "briefing_doc",
    "version": "1.0",
    "sections": [
      {"heading": "Executive Summary", "content_md": "…"},
      {"heading": "Key Developments", "items": ["…", "…"]},
      {"heading": "Risks & Open Questions", "items": ["…"]}
    ]
  },
  "diagnostics": { "searchProvider": "brave", "llm": "…", "latencyMs": 0, "cached": false }
}
```

### Discover Sources Endpoint

A new endpoint helps discover and curate authoritative sources for research topics:

```
POST http://localhost:8080/api/discover
```

Example payload:
```json
{
  "topic": "Impacts of CRISPR in agriculture",
  "maxSources": 10,
  "timeRange": "365d",
  "locale": "en"
}
```

Response:
```json
{
  "recommendations": [
    {
      "title": "...",
      "url": "...",
      "why_md": "Why this matters",
      "summary_md": "2–4 sentence annotated summary",
      "published": "2025-07-01",
      "score": 0.0
    }
  ],
  "queries_planned": ["...", "..."],
  "diagnostics": { "searchProvider": "tavily", "llm": "…", "latencyMs": 0 }
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
# Standard search
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the latest in AI research?",
    "maxResults": 5,
    "locale": "en",
    "timeRange": "30d"
  }'

# Structured content generation
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Status of Artemis II crewed mission delays and risks",
    "timeRange": "365d",
    "maxResults": 6,
    "output_type": "briefing_doc"
  }' | jq .

# Discover sources
curl -X POST http://localhost:8080/api/discover \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in healthcare diagnostics post-2023",
    "maxSources": 10,
    "timeRange": "730d"
  }' | jq .
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