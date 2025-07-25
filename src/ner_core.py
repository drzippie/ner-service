from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpanishNER:
    def __init__(self, model_name: str = "PlanTL-GOB-ES/roberta-base-bne-capitel-ner"):
        """
        Initialize the NER model for Spanish
        
        Args:
            model_name: Name of the HuggingFace model to use
        """
        self.model_name = model_name
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the NER model"""
        try:
            logger.info(f"Loading NER model: {self.model_name}")
            self.pipeline = pipeline(
                "ner",
                model=self.model_name,
                tokenizer=self.model_name,
                aggregation_strategy="simple"
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Using alternative BETO model...")
            try:
                self.model_name = "mrm8488/bert-spanish-cased-finetuned-ner"
                self.pipeline = pipeline(
                    "ner",
                    model=self.model_name,
                    tokenizer=self.model_name,
                    aggregation_strategy="simple"
                )
                logger.info("Alternative model loaded successfully")
            except Exception as e2:
                logger.error(f"Error loading alternative model: {e2}")
                raise RuntimeError(f"Could not load any NER model: {e2}")
    
    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize model tags to required tags
        
        Args:
            tag: Original model tag
            
        Returns:
            Normalized tag
        """
        tag_mapping = {
            "PER": "PERSON",
            "PERSON": "PERSON",
            "LOC": "LOCATION", 
            "LOCATION": "LOCATION",
            "ORG": "ORGANIZATION",
            "ORGANIZATION": "ORGANIZATION",
            "MISC": "MISC",
            "GPE": "PLACE",
            "PLACE": "PLACE"
        }
        
        # Remove B- and I- prefixes if they exist
        clean_tag = tag.replace("B-", "").replace("I-", "")
        
        return tag_mapping.get(clean_tag.upper(), "MISC")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of found entities with format:
            [{"tag": str, "score": str, "label": str}]
        """
        if not self.pipeline:
            raise RuntimeError("NER model is not loaded")
        
        if not text or not text.strip():
            return []
        
        try:
            # Run NER
            results = self.pipeline(text)
            
            # Format results
            entities = []
            for entity in results:
                normalized_tag = self._normalize_tag(entity['entity_group'])
                
                # Filter only required tags
                if normalized_tag in ["LOCATION", "MISC", "ORGANIZATION", "PERSON", "PLACE"]:
                    entities.append({
                        "tag": normalized_tag,
                        "score": f"{entity['score']:.4f}",
                        "label": entity['word']
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise RuntimeError(f"Error in NER processing: {e}")

# Global model instance
_ner_instance = None

def get_ner_instance() -> SpanishNER:
    """
    Get the singleton instance of the NER model
    
    Returns:
        SpanishNER instance
    """
    global _ner_instance
    if _ner_instance is None:
        _ner_instance = SpanishNER()
    return _ner_instance

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Convenience function to extract entities
    
    Args:
        text: Text to analyze
        
    Returns:
        List of found entities
    """
    ner = get_ner_instance()
    return ner.extract_entities(text)