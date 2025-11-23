"""FastAPI web service for Wikipedia Research Agent."""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional

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
        config = _config or Config()
        
        return HealthResponse(
            status="healthy",
            provider=config.llm_provider,
            model=config.llm_config.get("model", "unknown"),
            ready=agent.is_ready,
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
        agent = get_agent()
        
        # Override output format if specified in request
        if request.output_format:
            # Create a temporary agent with the requested format
            temp_config = Config()
            temp_config._config["agent"]["output_format"] = request.output_format
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
        config = _config or Config()
        return {
            "provider": config.llm_provider,
            "model": config.llm_config.get("model", "unknown"),
            "output_format": config.output_format,
            "max_articles": config.wikipedia_config.get("max_articles", 3),
            "language": config.wikipedia_config.get("language", "en"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")


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
