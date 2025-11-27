"""FastAPI web service for Wikipedia Research Agent."""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..agent import WikipediaAgent
from ..config import Config


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    stream: bool = True
    output_format: Optional[str] = None  # "mla" or "json"
    # Optional provider override ("ollama" or "openrouter")
    provider: Optional[str] = None
    # Optional OpenRouter model override (only used when provider == \"openrouter\")
    model: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for non-streaming queries."""
    response: str
    output_format: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    provider: str
    model: str
    ready: bool
    default_ollama_model: Optional[str] = None
    default_openrouter_model: Optional[str] = None


class ModelInfo(BaseModel):
    """Model metadata exposed to the web UI."""
    id: str
    name: str
    provider: str
    prompt_price_per_million: float
    completion_price_per_million: float
    context_length: Optional[int] = None


class OllamaModelInfo(BaseModel):
    """Ollama model metadata exposed to the web UI."""
    name: str
    model: str


# Initialize FastAPI app
app = FastAPI(
    title="Wikipedia Research Agent",
    description="AI-powered Wikipedia research with citations",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
_agent: Optional[WikipediaAgent] = None
_config: Optional[Config] = None


def get_agent() -> WikipediaAgent:
    """Get or create the global agent instance."""
    global _agent, _config
    if _agent is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        _config = Config(config_path)
        _agent = WikipediaAgent(_config)
    return _agent


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    try:
        get_agent()
        print("✅ Wikipedia Agent initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize agent: {e}")


@app.get("/")
async def root():
    """Serve the main web UI."""
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Wikipedia Research Agent API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        agent = get_agent()
        config = _config or Config(os.getenv("CONFIG_PATH", "config.yaml"))
        
        # Get model name based on provider
        if config.llm_provider == "ollama":
            model = config.ollama_config.get("model", "unknown")
        elif config.llm_provider == "openrouter":
            model = config.openrouter_config.get("model", "unknown")
        else:
            model = "unknown"
        
        return HealthResponse(
            status="healthy",
            provider=config.llm_provider,
            model=model,
            ready=agent.is_ready,
            default_ollama_model=config.ollama_config.get("model"),
            default_openrouter_model=config.openrouter_config.get("model"),
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "provider": "unknown",
                "model": "unknown",
                "ready": False,
                "error": str(e),
            }
        )


@app.post("/api/query")
async def query_endpoint(request: QueryRequest):
    """
    Main query endpoint for Wikipedia research.
    
    Supports both streaming and non-streaming responses.
    """
    try:
        # Start from the base config used to create the global agent
        base_config_path = os.getenv("CONFIG_PATH", "config.yaml")
        config = _config or Config(base_config_path)
        agent = get_agent()

        # If the client requested a different output format, provider, and/or model,
        # create a temporary agent with an overridden config.
        if request.output_format or request.provider or request.model:
            temp_config = Config(base_config_path)

            # Ensure nested structures exist before mutation
            temp_config._config.setdefault("agent", {})
            temp_config._config.setdefault("llm", {})

            # Override provider if specified
            if request.provider:
                temp_config._config["llm"]["provider"] = request.provider

            # Override output format if specified
            if request.output_format:
                temp_config._config["agent"]["output_format"] = request.output_format

            # Override model for the effective provider if specified
            if request.model:
                effective_provider = request.provider or temp_config.llm_provider
                if effective_provider == "openrouter":
                    temp_config._config["llm"].setdefault("openrouter", {})
                    temp_config._config["llm"]["openrouter"]["model"] = request.model
                elif effective_provider == "ollama":
                    temp_config._config["llm"].setdefault("ollama", {})
                    temp_config._config["llm"]["ollama"]["model"] = request.model
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Model selection is not supported for provider '{effective_provider}'.",
                    )

            agent = WikipediaAgent(temp_config)
        
        if not agent.is_ready:
            raise HTTPException(
                status_code=503,
                detail="Agent is not ready. Please check your LLM configuration."
            )
        
        if request.stream:
            # Streaming response
            async def generate():
                """Generate streaming response."""
                try:
                    # Run the sync generator in thread pool
                    loop = asyncio.get_event_loop()
                    
                    def sync_query():
                        for chunk in agent.query(request.query, stream=True):
                            return chunk
                    
                    # Stream chunks
                    for chunk in agent.query(request.query, stream=True):
                        # Send as Server-Sent Events format
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    
                    # Send completion signal
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
                except Exception as e:
                    error_data = json.dumps({'error': str(e)})
                    yield f"data: {error_data}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # Non-streaming response
            response = agent.query(request.query, stream=False)
            return QueryResponse(
                response=response,
                output_format=agent.output_format,
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/api/config")
async def get_config():
    """Get current configuration (sanitized)."""
    try:
        config = _config or Config(os.getenv("CONFIG_PATH", "config.yaml"))
        
        # Get model name based on provider
        if config.llm_provider == "ollama":
            model = config.ollama_config.get("model", "unknown")
        elif config.llm_provider == "openrouter":
            model = config.openrouter_config.get("model", "unknown")
        else:
            model = "unknown"
        
        return {
            "provider": config.llm_provider,
            "model": model,
            "output_format": config.output_format,
            "max_articles": config.wikipedia_config.get("max_articles", 3),
            "language": config.wikipedia_config.get("language", "en"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")


def _fetch_openrouter_models(config: Config) -> List[ModelInfo]:
    """Fetch a curated list of OpenRouter models with current pricing."""
    openrouter_cfg = config.openrouter_config
    api_key = openrouter_cfg.get("api_key", os.getenv("OPENROUTER_API_KEY", ""))
    base_url = openrouter_cfg.get("base_url", "https://openrouter.ai/api/v1").rstrip("/")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API key is not configured. Set OPENROUTER_API_KEY or llm.openrouter.api_key.",
        )

    url = f"{base_url}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/wikipedia-agent",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch models from OpenRouter: {e}",
        )

    configured_allowed = config.openrouter_allowed_models
    if configured_allowed:
        allowed_ids = set(configured_allowed)
    else:
        allowed_ids = {
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3.5-haiku",
        }
    default_model_id = openrouter_cfg.get("model")
    if default_model_id:
        allowed_ids.add(default_model_id)

    models: List[ModelInfo] = []
    for item in data.get("data", []):
        model_id = item.get("id", "")
        if model_id not in allowed_ids:
            continue

        pricing = item.get("pricing", {}) or {}
        architecture = item.get("architecture", {}) or {}

        try:
            prompt_price = float(pricing.get("prompt", 0.0)) * 1_000_000
            completion_price = float(pricing.get("completion", 0.0)) * 1_000_000
        except (TypeError, ValueError):
            # Skip models with malformed pricing
            continue

        models.append(
            ModelInfo(
                id=model_id,
                name=item.get("name", model_id),
                provider=item.get("provider", ""),
                prompt_price_per_million=prompt_price,
                completion_price_per_million=completion_price,
                context_length=architecture.get("context_length"),
            )
        )

    return models


def _fetch_ollama_models(config: Config) -> List[OllamaModelInfo]:
    """Fetch available models from the configured Ollama server."""
    ollama_cfg = config.ollama_config
    base_url = ollama_cfg.get("base_url", "http://masterroshi:11434").rstrip("/")

    url = f"{base_url}/api/tags"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch models from Ollama at {base_url}: {e}",
        )

    configured_allowed = config.ollama_allowed_models
    has_allowlist = bool(configured_allowed)
    allowed_set = set(configured_allowed) if has_allowlist else set()
    default_model_id = ollama_cfg.get("model")
    if default_model_id:
        allowed_set.add(default_model_id)

    models: List[OllamaModelInfo] = []
    for item in (data.get("models") or []):
        name = item.get("name")
        model = item.get("model", name)
        if not name:
            continue
        if has_allowlist and model not in allowed_set and name not in allowed_set:
            continue
        models.append(OllamaModelInfo(name=name, model=model))

    return models


@app.get("/api/models", response_model=List[ModelInfo])
async def get_models():
    """
    Return a list of supported models with current OpenRouter pricing.

    Only returns models when the configured provider is OpenRouter; for other
    providers, an empty list is returned.
    """
    try:
        config = _config or Config(os.getenv("CONFIG_PATH", "config.yaml"))
        if config.llm_provider != "openrouter":
            # Model selection is only relevant for OpenRouter for now.
            return []

        return _fetch_openrouter_models(config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")


@app.get("/api/ollama/models", response_model=List[OllamaModelInfo])
async def get_ollama_models():
    """Return available models from the configured Ollama server."""
    try:
        config = _config or Config(os.getenv("CONFIG_PATH", "config.yaml"))
        if config.llm_provider != "ollama":
            return []
        return _fetch_ollama_models(config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Ollama models: {str(e)}")


# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def start_server():
    """Entry point for running the web server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wikipedia Research Agent Web Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Set config path environment variable
    os.environ["CONFIG_PATH"] = args.config
    
    print(f"🚀 Starting Wikipedia Research Agent Web Service")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"⚙️  Config: {args.config}")
    
    uvicorn.run(
        "src.web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    start_server()
