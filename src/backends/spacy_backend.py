import spacy
from typing import List, Dict, Any
import logging
from .base import NERBackend

logger = logging.getLogger(__name__)

class SpacyNERBackend(NERBackend):
    """spaCy-based Named Entity Recognition backend"""
    
    def __init__(self, model_name: str = "es_core_news_md", **kwargs):
        """
        Initialize the spaCy NER backend
        
        Args:
            model_name: Name of the spaCy model to use
            **kwargs: Additional parameters (unused for spaCy)
        """
        super().__init__(model_name, **kwargs)
        self.nlp = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load the spaCy NER model"""
        try:
            logger.info(f"Loading spaCy model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
            self.is_loaded = True
            logger.info("spaCy model loaded successfully")
        except OSError as e:
            logger.error(f"Error loading spaCy model {self.model_name}: {e}")
            logger.info("Model not found. Please install it with: python -m spacy download es_core_news_md")
            
            # Try fallback to small model  
            try:
                logger.info("Trying fallback model es_core_news_sm...")
                self.model_name = "es_core_news_sm"
                self.nlp = spacy.load(self.model_name)
                self.is_loaded = True
                logger.info("Fallback spaCy model loaded successfully")
            except OSError as e2:
                logger.error(f"Error loading fallback model: {e2}")
                raise RuntimeError(
                    f"Could not load any Spanish spaCy NER model. Please install with:\n"
                    f"python -m spacy download es_core_news_md\n" 
                    f"or: python -m spacy download es_core_news_sm"
                )
        except Exception as e:
            logger.error(f"Unexpected error loading spaCy model: {e}")
            raise RuntimeError(f"Could not load spaCy NER model: {e}")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text using spaCy
        
        Args:
            text: Text to analyze
            
        Returns:
            List of unique entities with format:
            [{"tag": str, "score": str, "label": str}]
        """
        if not self.is_loaded or not self.nlp:
            raise RuntimeError("spaCy NER model is not loaded")
        
        if not text or not text.strip():
            return []
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = []            
            for ent in doc.ents:
                normalized_tag = self._normalize_tag(ent.label_)
                
                # Filter only required tags
                if normalized_tag in self.get_supported_entities():
                    entities.append({
                        "tag": normalized_tag,
                        "score": "0.95",  # High confidence for spaCy's rule-based NER
                        "label": ent.text
                    })
            
            # Ensure uniqueness
            return self._ensure_unique_entities(entities)
            
        except Exception as e:
            logger.error(f"Error processing text with spaCy: {e}")
            raise RuntimeError(f"Error in spaCy NER processing: {e}")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the spaCy backend
        
        Returns:
            Dictionary with backend information
        """
        return {
            "backend": "spacy",
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "version": spacy.__version__ if spacy else "unknown",
            "description": "spaCy CNN-based NER with Spanish language support",
            "performance": "89.01% F-score for Spanish NER",
            "model_size": "93MB (es_core_news_md) or 12MB (es_core_news_sm)"
        }
    
    def get_supported_entities(self) -> List[str]:
        """
        Get list of supported entity types for spaCy backend
        
        Returns:
            List of supported entity type strings
        """
        return ["PERSON", "LOCATION", "ORGANIZATION", "MISC", "PLACE"]