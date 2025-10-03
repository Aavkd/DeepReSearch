import time
import json
from typing import List, Dict, Any, Optional
from ..contracts import SearchRequest, SearchResponse, SearchResult, Diagnostics
from ..config import settings
from ..hashing import query_key
from ..cache.redis_cache import Cache
from ..search.tavily import TavilySearchProvider
from ..search.brave import BraveSearchProvider
from ..search.searchapi import SearchApiProvider
from ..extract.firecrawl import FirecrawlExtractor
from ..extract.readability import ReadabilityExtractor
from ..rank.ranker import rank
from ..llm.openrouter import OpenRouterProvider
from ..llm.ollama import OllamaProvider
from ..synth.prompts import QUERY_NORMALIZER_SYSTEM, QUERY_NORMALIZER_USER, SYNTHESIS_SYSTEM
from ..synth.prompts import SYNTHESIS_USER, SAFETY_GUARD_SYSTEM
from ..synth.composer import compose_synthesis_prompt, compose_query_normalization_prompt
from ..synth.repair import ensure_json
from ..synth.structured_prompt import compose_structured_prompt, get_structured_prompts
from ..safety.guard import apply_safety_guard
from ..util.text import clean_text, clean_query_response


class Pipeline:
    """
    Main pipeline orchestrator that mirrors the n8n workflow.
    """
    
    def __init__(self):
        self.cache = Cache()
        self.firecrawl = FirecrawlExtractor()
        self.readability = ReadabilityExtractor()
        print("Pipeline initialized with Firecrawl and Readability extractors")
    
    def _get_llm_provider(self, req: SearchRequest):
        """
        Get the appropriate LLM provider based on the request settings.
        """
        # Check if a specific model and provider are selected
        if req.selectedModel and req.selectedProvider:
            if req.selectedProvider == "ollama":
                return OllamaProvider(model=req.selectedModel)
            elif req.selectedProvider == "openrouter":
                return OpenRouterProvider(model=req.selectedModel)
        
        # Fall back to forceLocal logic
        if req.forceLocal:
            selected_model = req.selectedModel if req.selectedProvider == "ollama" else None
            return OllamaProvider(model=selected_model)
        else:
            selected_model = req.selectedModel if req.selectedProvider == "openrouter" else None
            return OpenRouterProvider(model=selected_model)
    
    async def run(self, req: SearchRequest) -> SearchResponse:
        """
        Run the complete search pipeline.
        """
        print(f"Starting pipeline for query: {req.query}")
        start_time = time.time()
        
        # 1. Cache lookup
        print("Step 1: Checking cache...")
        cache_key = query_key(req)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            try:
                print("Cache hit! Returning cached result...")
                cached_data = json.loads(cached_result)
                response = SearchResponse(**cached_data)
                response.diagnostics.latencyMs = int((time.time() - start_time) * 1000)
                response.diagnostics.cached = True
                return response
            except Exception as e:
                print(f"Cache corrupted, continuing with normal processing: {e}")
                # If cache is corrupted, continue with normal processing
                pass
        else:
            print("Cache miss, proceeding with search...")
        
        # 2. Query normalization (optional)
        print("Step 2: Normalizing query...")
        normalized_query = await self._maybe_normalize(req)
        query_to_use = normalized_query or req.query
        print(f"Using query: {query_to_use}")
        
        # 3. Search
        print("Step 3: Performing search...")
        search_results = await self._search(query_to_use, req)
        print(f"Found {len(search_results)} search results")
        
        # 4. Rank and deduplicate
        print("Step 4: Ranking and deduplicating results...")
        ranked_results = rank(
            search_results, 
            req.includeDomains, 
            req.excludeDomains, 
            req.maxResults
        )
        print(f"Ranked down to {len(ranked_results)} results")
        
        # 5. Extract content
        print("Step 5: Extracting content from URLs...")
        urls = [result.url for result in ranked_results]
        print(f"Extracting from {len(urls)} URLs: {urls}")
        extracted_docs = await self._fetch_extract(urls)
        print(f"Successfully extracted content from {len(extracted_docs)} URLs")
        
        # 6. Synthesize answer
        print("Step 6: Synthesizing answer...")
        if req.output_type and settings.STRUCTURED_ENABLED:
            # Structured content generation
            structured_payload = compose_structured_prompt(req.output_type, req.query, extracted_docs)
            raw_response = await self._synthesize_structured(structured_payload, req)
            print("Structured synthesis completed, repairing JSON...")
            repaired_response = await ensure_json(raw_response)
            print("JSON repair completed")
            
            # Apply safety guard to structured content
            safe_response = apply_safety_guard(repaired_response)
            print("Safety guard applied")
            
            # Create diagnostics
            diagnostics = Diagnostics(
                searchProvider="brave",  # Default to brave since it's configured
                llm=settings.OPENROUTER_MODEL if not req.forceLocal else settings.OLLAMA_MODEL,
                latencyMs=int((time.time() - start_time) * 1000),
                cached=False
            )
            
            # Create final response with structured content
            response = SearchResponse(
                answer=safe_response.get("answer", ""),
                bullets=safe_response.get("bullets", []),
                sources=safe_response.get("sources", []),
                diagnostics=diagnostics,
                structured=safe_response  # The entire safe_response is the structured content
            )
        else:
            # Default answer mode
            synthesis_payload = compose_synthesis_prompt(req, extracted_docs)
            raw_response = await self._synthesize(synthesis_payload, req)
            print("Synthesis completed, repairing JSON...")
            repaired_response = await ensure_json(raw_response)
            print("JSON repair completed")
            
            # Apply safety guard
            safe_response = apply_safety_guard(repaired_response)
            print("Safety guard applied")
            
            # Create diagnostics
            diagnostics = Diagnostics(
                searchProvider="brave",  # Default to brave since it's configured
                llm=settings.OPENROUTER_MODEL if not req.forceLocal else settings.OLLAMA_MODEL,
                latencyMs=int((time.time() - start_time) * 1000),
                cached=False
            )
            
            # Create final response
            response = SearchResponse(
                answer=safe_response.get("answer", ""),
                bullets=safe_response.get("bullets", []),
                sources=safe_response.get("sources", []),
                diagnostics=diagnostics
            )
        
        # 7. Cache result
        print("Step 7: Caching result...")
        try:
            await self.cache.set(
                cache_key, 
                response.model_dump_json(), 
                ttl=settings.CACHE_TTL_S
            )
            print("Result cached successfully")
        except Exception as e:
            print(f"Failed to cache result: {e}")
            # Cache failure shouldn't break the pipeline
        
        print("Pipeline completed successfully")
        return response
    
    async def _maybe_normalize(self, req: SearchRequest) -> Optional[str]:
        """
        Optionally normalize the query using an LLM.
        """
        print("Normalizing query...")
        try:
            # Use selected provider/model or fall back to forceLocal logic
            provider = self._get_llm_provider(req)
            provider_name = "Ollama" if isinstance(provider, OllamaProvider) else "OpenRouter"
            print(f"Using {provider_name} ({provider.model}) for query normalization")
            
            prompt_data = compose_query_normalization_prompt(req)
            user_prompt = QUERY_NORMALIZER_USER.format(**prompt_data)
            
            normalized = await provider.chat(
                QUERY_NORMALIZER_SYSTEM,
                user_prompt,
                temperature=0.2
            )
            
            # Use specialized cleaning for query responses
            cleaned = clean_query_response(normalized)
            
            # Validate the cleaned result
            if not cleaned or len(cleaned.strip()) < 3:
                print(f"Normalization produced invalid result: '{cleaned}', using original query")
                return None
            
            # Don't use normalization if it's identical to original (likely failed)
            if cleaned.lower().strip() == req.query.lower().strip():
                print("Normalization returned identical query, skipping")
                return None
                
            print(f"Query normalized to: {cleaned}")
            return cleaned
        except json.JSONDecodeError as e:
            print(f"Query normalization failed due to JSON parsing error: {e}")
            print("This might be due to the model returning structured data instead of plain text")
            return None
        except Exception as e:
            print(f"Query normalization failed: {e}")
            # If normalization fails, return None to use original query
            return None
    
    async def _search(self, query: str, req: SearchRequest) -> List[SearchResult]:
        """
        Perform search using the appropriate provider.
        """
        print(f"Searching for: {query}")
        # Try Brave first since it's configured in the .env file
        try:
            print("Trying Brave Search...")
            provider = BraveSearchProvider()
            results = await provider.search(
                query, 
                req.maxResults, 
                req.includeDomains, 
                req.excludeDomains
            )
            print(f"Brave Search returned {len(results)} results")
            return results
        except Exception as e:
            print(f"Brave search failed: {e}")
        
        # Fallback to Tavily
        try:
            print("Trying Tavily Search...")
            provider = TavilySearchProvider()
            results = await provider.search(
                query, 
                req.maxResults, 
                req.includeDomains, 
                req.excludeDomains
            )
            print(f"Tavily Search returned {len(results)} results")
            return results
        except Exception as e:
            print(f"Tavily search failed: {e}")
        
        # Fallback to SearchAPI
        try:
            print("Trying SearchAPI...")
            provider = SearchApiProvider()
            results = await provider.search(
                query, 
                req.maxResults, 
                req.includeDomains, 
                req.excludeDomains
            )
            print(f"SearchAPI returned {len(results)} results")
            return results
        except Exception as e:
            print(f"SearchAPI search failed: {e}")
        
        # If all providers fail, return empty list
        print("All search providers failed, returning empty results")
        return []
    
    async def _fetch_extract(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch and extract content from URLs.
        """
        print(f"Fetching and extracting from {len(urls)} URLs")
        # Try to get from cache first
        docs = []
        uncached_urls = []
        
        for url in urls:
            url_cache_key = query_key(SearchRequest(query=url))  # Reuse query_key for URL hashing
            cached_content = await self.cache.get_url_content(url_cache_key)
            if cached_content:
                print(f"Cache hit for URL: {url}")
                docs.append(cached_content)
            else:
                print(f"Cache miss for URL: {url}")
                uncached_urls.append(url)
        
        # Extract content for uncached URLs
        if uncached_urls:
            print(f"Extracting content from {len(uncached_urls)} uncached URLs")
            # Try Firecrawl first
            try:
                print("Using Firecrawl extractor...")
                extracted = await self.firecrawl.extract_many(uncached_urls)
                docs.extend(extracted)
                print(f"Firecrawl extracted {len(extracted)} documents")
                
                # Cache the results
                for doc in extracted:
                    url_cache_key = query_key(SearchRequest(query=doc["url"]))
                    await self.cache.set_url_content(url_cache_key, doc)
                    print(f"Cached content for URL: {doc['url']}")
            except Exception as e:
                print(f"Firecrawl extraction failed: {e}")
                
                # Fallback to readability
                try:
                    print("Using Readability fallback extractor...")
                    extracted = await self.readability.extract_many(uncached_urls)
                    docs.extend(extracted)
                    print(f"Readability extracted {len(extracted)} documents")
                except Exception as e:
                    print(f"Readability extraction failed: {e}")
        else:
            print("All URLs were cached, no extraction needed")
        
        print(f"Total documents extracted: {len(docs)}")
        return docs
    
    async def _synthesize(self, payload: Dict[str, str], req: SearchRequest) -> str:
        """
        Synthesize the final answer using an LLM.
        """
        print("Synthesizing final answer...")
        user_prompt = SYNTHESIS_USER.format(
            query=payload["query"],
            docs_json=payload["docs_json"]
        )
        
        # Use selected provider/model or fall back to forceLocal logic  
        provider = self._get_llm_provider(req)
        provider_name = "Ollama" if isinstance(provider, OllamaProvider) else "OpenRouter"
        print(f"Using {provider_name} ({provider.model}) for synthesis")
        
        response = await provider.chat(
            SYNTHESIS_SYSTEM,
            user_prompt,
            temperature=0.2,
            top_p=0.9
        )
        
        print("Synthesis completed successfully")
        return response
    
    async def _synthesize_structured(self, payload: Dict[str, str], req: SearchRequest) -> str:
        """
        Synthesize structured content using an LLM.
        """
        print(f"Synthesizing structured content of type: {req.output_type}")
        
        # Use selected provider/model or fall back to forceLocal logic  
        provider = self._get_llm_provider(req)
        provider_name = "Ollama" if isinstance(provider, OllamaProvider) else "OpenRouter"
        print(f"Using {provider_name} ({provider.model}) for structured synthesis")
        
        # Add JSON response format for providers that support it
        kwargs = {
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": settings.STRUCTURED_MAX_TOKENS
        }
        
        # Try to use JSON mode if the provider supports it
        if isinstance(provider, OpenRouterProvider):
            kwargs["response_format"] = {"type": "json_object"}
        elif isinstance(provider, OllamaProvider):
            # Ollama doesn't have a specific JSON mode, but we can request it
            pass
        
        response = await provider.chat(
            payload["system_prompt"],
            payload["user_prompt"],
            **kwargs
        )
        
        print("Structured synthesis completed successfully")
        return response