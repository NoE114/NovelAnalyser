"""
Pathway REST Service
Blezecon's responsibility (OPTIONAL)

Exposes Pathway app as HTTP REST API for real-time queries.
This allows external systems to query your pipeline.
"""
import pathway as pw
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

from .app import NovelAnalyzerApp
from .schema import ReasoningResultSchema


# ============= REQUEST/RESPONSE MODELS =============

class QueryRequest(BaseModel):
    """Request model for consistency check"""
    story_id: str
    backstory: str
    top_k: Optional[int] = 15


class QueryResponse(BaseModel):
    """Response model for consistency check"""
    story_id: str
    decision: int  # 0 or 1
    reasoning: str
    confidence: float
    evidence_used: List[Dict]
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    pathway_version: str
    models_loaded: bool


# ============= FASTAPI APP =============

# Initialize FastAPI
api = FastAPI(
    title="Novel Analyzer API",
    description="Pathway-based consistency checking service",
    version="1.0.0"
)

# Global app instance (initialized on startup)
pathway_app: Optional[NovelAnalyzerApp] = None


# ============= ENDPOINTS =============

@api.on_event("startup")
async def startup_event():
    """Initialize Pathway app on service startup"""
    global pathway_app
    
    print("🚀 Starting Pathway service...")
    
    # Initialize your Pathway app
    pathway_app = NovelAnalyzerApp(config_path="configs/pathway.yaml")
    
    # Build the pipeline
    pathway_app.build_pipeline()
    
    print("✅ Pathway service ready!")


@api.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Service health status
    """
    return HealthResponse(
        status="healthy" if pathway_app is not None else "initializing",
        pathway_version=pw.__version__,
        models_loaded=pathway_app is not None
    )


@api.post("/query", response_model=QueryResponse)
async def query_consistency(request: QueryRequest):
    """
    Check backstory consistency
    
    Args:
        request: Query request with story_id and backstory
        
    Returns:
        Consistency check result
        
    Example:
        POST /query
        {
            "story_id": "1",
            "backstory": "Character grew up in Chicago...",
            "top_k": 15
        }
    """
    if pathway_app is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Please wait for initialization."
        )
    
    try:
        import time
        start_time = time.time()
        
        # Call your Pathway app
        result = pathway_app.query(
            story_id=request.story_id,
            backstory=request.backstory
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return QueryResponse(
            story_id=request.story_id,
            decision=result['decision'],
            reasoning=result['reasoning'],
            confidence=result.get('confidence', 0.0),
            evidence_used=result.get('evidence_used', []),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@api.get("/stories")
async def list_stories():
    """
    List all available stories
    
    Returns:
        List of story IDs
    """
    if pathway_app is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # TODO: Implement story listing
    return {"stories": ["1", "2", "3"]}  # Placeholder


@api.get("/story/{story_id}/metadata")
async def get_story_metadata(story_id: str):
    """
    Get metadata for a specific story
    
    Args:
        story_id: Story identifier
        
    Returns:
        Story metadata
    """
    if pathway_app is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # TODO: Load metadata from data/metadata/
    import json
    
    try:
        metadata_path = f"data/metadata/novel_{story_id}_metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Story {story_id} not found"
        )


# ============= PATHWAY INTEGRATION =============

def create_pathway_service(
    host: str = "0.0.0.0",
    port: int = 8080,
    config_path: str = "configs/pathway.yaml"
):
    """
    Create and run Pathway service
    
    This uses Pathway's native REST connector for streaming data.
    For batch processing, we use FastAPI above.
    
    Args:
        host: Service host
        port: Service port
        config_path: Path to Pathway config
    """
    print(f"🌐 Starting Pathway REST service on {host}:{port}...")
    
    # Initialize app
    global pathway_app
    pathway_app = NovelAnalyzerApp(config_path)
    pathway_app.build_pipeline()
    
    # Run FastAPI server
    uvicorn.run(api, host=host, port=port)


# ============= MAIN =============

if __name__ == "__main__":
    # Run service
    create_pathway_service(
        host="0.0.0.0",
        port=8080
    )