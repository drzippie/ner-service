from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging
from .ner_core import extract_entities, get_backend_info, get_supported_backends

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Spanish NER API",
    description="API for Named Entity Recognition in Spanish",
    version="1.0.0"
)

class NERRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for entity extraction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Juan lives in Madrid and works at Google Spain."
            }
        }

class EntityResponse(BaseModel):
    tag: str = Field(..., description="Entity type (PERSON, LOCATION, ORGANIZATION, MISC, PLACE)")
    score: str = Field(..., description="Model confidence score")
    label: str = Field(..., description="Name of the found entity")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Spanish NER API",
        "version": "1.0.0",
        "description": "API for Named Entity Recognition in Spanish",
        "endpoints": {
            "ner": "/ner - POST - Named entity analysis (returns array directly)",
            "health": "/health - GET - API status with backend info",
            "backends": "/backends - GET - Available backends info",
            "docs": "/docs - Interactive documentation"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Endpoint to check API status"""
    try:
        # Get backend information
        backend_info = get_backend_info()
        
        return {
            "status": "healthy",
            "backend": backend_info,
            "supported_backends": get_supported_backends(),
            "message": "API working correctly"
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "message": "Error with NER backend",
                "supported_backends": get_supported_backends()
            }
        )

@app.post("/ner", response_model=List[EntityResponse], tags=["NER"])
async def analyze_text(request: NERRequest):
    """
    Analyze text and extract named entities
    
    - **text**: Spanish text to analyze
    
    Returns an array of unique entities with:
    - **tag**: Entity type (PERSON, LOCATION, ORGANIZATION, MISC, PLACE)
    - **score**: Model confidence score (real scores for MITIE, 0.95 for spaCy)
    - **label**: Name of the found entity
    
    Note: Duplicate entities with the same label and tag are automatically filtered out.
    Only entities with score >= 0.5 are returned when using MITIE backend.
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="The 'text' field cannot be empty"
            )
        
        # Limit text length to avoid memory issues
        if len(request.text) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Text is too long. Maximum 10,000 characters."
            )
        
        logger.info(f"Processing text of {len(request.text)} characters")
        
        # Extract entities
        entities = extract_entities(request.text)
        
        # Convert to response format
        entity_responses = [
            EntityResponse(
                tag=entity["tag"],
                score=entity["score"], 
                label=entity["label"]
            )
            for entity in entities
        ]
        
        logger.info(f"Found {len(entity_responses)} entities")
        
        return entity_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing NER request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/backends", tags=["General"])
async def get_backends():
    """
    Get information about all available NER backends
    
    Returns detailed information about each available backend including
    their status, performance characteristics, and configuration.
    """
    try:
        backends_info = {}
        supported = get_supported_backends()
        
        for backend_name in supported:
            try:
                backend_info = get_backend_info(backend=backend_name)
                backends_info[backend_name] = backend_info
            except Exception as e:
                backends_info[backend_name] = {
                    "backend": backend_name,
                    "is_loaded": False,
                    "error": str(e),
                    "status": "unavailable"
                }
        
        return {
            "supported_backends": supported,
            "backends": backends_info,
            "default_backend": get_backend_info()["backend"]
        }
        
    except Exception as e:
        logger.error(f"Error getting backends info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving backends information: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)