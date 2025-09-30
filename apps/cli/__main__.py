import asyncio
import json
import sys
from typing import Optional

import typer
from perplexity_core.contracts import SearchRequest, UIOptions
from perplexity_core.pipeline.runner import Pipeline

app = typer.Typer(
    name="perplexity",
    help="Local Perplexity CLI - AI-powered search engine"
)


@app.command()
def run(
    query: str,
    max_results: int = typer.Option(6, "--max-results", "-m", help="Maximum number of results"),
    concise: bool = typer.Option(True, "--concise/--detailed", help="Concise or detailed output"),
    force_local: bool = typer.Option(False, "--local", "-l", help="Force using local LLM (Ollama)"),
    include_domains: Optional[str] = typer.Option(None, "--include", "-i", help="Comma-separated domains to include"),
    exclude_domains: Optional[str] = typer.Option(None, "--exclude", "-e", help="Comma-separated domains to exclude")
):
    """
    Run a search query and print the results.
    """
    # Parse domain lists
    include_list = None
    exclude_list = None
    
    if include_domains:
        include_list = [d.strip() for d in include_domains.split(",")]
    
    if exclude_domains:
        exclude_list = [d.strip() for d in exclude_domains.split(",")]
    
    # Create search request
    req = SearchRequest(
        query=query,
        maxResults=max_results,
        forceLocal=force_local,
        includeDomains=include_list,
        excludeDomains=exclude_list,
        ui=UIOptions(mode="concise" if concise else "detailed")
    )
    
    # Run the pipeline
    async def _run():
        pipeline = Pipeline()
        response = await pipeline.run(req)
        return response
    
    try:
        response = asyncio.run(_run())
        print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to")
):
    """
    Start the API server.
    """
    import uvicorn
    from apps.api.main import app as api_app
    
    uvicorn.run(api_app, host=host, port=port)


if __name__ == "__main__":
    app()