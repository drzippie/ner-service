from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging
from .ner_core import extract_entities

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

class NERResponse(BaseModel):
    entities: List[EntityResponse] = Field(..., description="List of found entities")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entities": [
                    {
                        "tag": "PERSON",
                        "score": "0.9998",
                        "label": "Juan"
                    },
                    {
                        "tag": "LOCATION", 
                        "score": "0.9995",
                        "label": "Madrid"
                    },
                    {
                        "tag": "ORGANIZATION",
                        "score": "0.9987", 
                        "label": "Google Spain"
                    }
                ]
            }
        }

@app.get("/", tags=["General"])
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Spanish NER API",
        "version": "1.0.0",
        "description": "API for Named Entity Recognition in Spanish",
        "endpoints": {
            "ner": "/ner - POST - Named entity analysis",
            "health": "/health - GET - API status",
            "docs": "/docs - Interactive documentation"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Endpoint to check API status"""
    try:
        # Verify that the model is loaded
        from .ner_core import get_ner_instance
        ner = get_ner_instance()
        
        return {
            "status": "healthy",
            "model": ner.model_name,
            "message": "API working correctly"
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "message": "Error loading NER model"
            }
        )

@app.post("/ner", response_model=NERResponse, tags=["NER"])
async def analyze_text(request: NERRequest):
    """
    Analyze text and extract named entities
    
    - **text**: Spanish text to analyze
    
    Returns a list of entities with:
    - **tag**: Entity type (PERSON, LOCATION, ORGANIZATION, MISC, PLACE)
    - **score**: Model confidence score
    - **label**: Name of the found entity
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
        
        return NERResponse(entities=entity_responses)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing NER request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)