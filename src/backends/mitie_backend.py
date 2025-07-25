from typing import List, Dict, Any
import logging
import os
from .base import NERBackend

logger = logging.getLogger(__name__)

class MitieNERBackend(NERBackend):
    """MITIE-based Named Entity Recognition backend"""
    
    def __init__(self, model_path: str = None, **kwargs):
        """
        Initialize the MITIE NER backend
        
        Args:
            model_path: Path to MITIE NER model file
            **kwargs: Additional parameters
        """
        # Default model path - can be overridden
        default_model = "MITIE-models/spanish/ner_model.dat"
        model_name = model_path or default_model
        
        super().__init__(model_name, **kwargs)
        self.model_path = model_name
        self.ner = None
        self.mitie = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load the MITIE NER model"""
        try:
            # Import MITIE - will raise ImportError if not installed
            import mitie
            self.mitie = mitie
            
            logger.info(f"Loading MITIE model: {self.model_path}")
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"MITIE model file not found: {self.model_path}\n"
                    f"Please download the Spanish model from:\n"
                    f"https://github.com/mit-nlp/MITIE/releases/download/v0.4/MITIE-models-v0.2-Spanish.zip\n"
                    f"And extract it to the project directory."
                )
            
            # Load the NER model
            self.ner = mitie.named_entity_extractor(self.model_path)
            self.is_loaded = True
            logger.info("MITIE model loaded successfully")
            
        except ImportError as e:
            raise ImportError(
                f"MITIE not installed. Install with:\n"
                f"pip install git+https://github.com/mit-nlp/MITIE.git\n"
                f"Original error: {e}"
            )
        except Exception as e:
            logger.error(f"Error loading MITIE model: {e}")
            raise RuntimeError(f"Could not load MITIE NER model: {e}")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text using MITIE
        
        Args:
            text: Text to analyze
            
        Returns:
            List of unique entities with format:
            [{"tag": str, "score": str, "label": str}]
        """
        if not self.is_loaded or not self.ner:
            raise RuntimeError("MITIE NER model is not loaded")
        
        if not text or not text.strip():
            return []
        
        try:
            # Tokenize text for MITIE
            tokens = self.mitie.tokenize(text)
            
            # Extract entities
            entities = []
            ner_results = self.ner.extract_entities(tokens)
            
            for entity in ner_results:
                # MITIE returns: (range, tag) or (range, tag, score)
                # Handle both cases
                if len(entity) == 2:
                    entity_range, tag = entity
                    score = 0.95  # Default score when not provided
                elif len(entity) == 3:
                    entity_range, tag, score = entity
                else:
                    logger.warning(f"Unexpected MITIE entity format: {entity}")
                    continue
                
                # Extract entity text from tokens - entity_range is a range object
                # Convert bytes to string if needed
                token_slice = tokens[entity_range.start:entity_range.stop]
                if token_slice and isinstance(token_slice[0], bytes):
                    entity_text = " ".join(token.decode('utf-8') for token in token_slice)
                else:
                    entity_text = " ".join(token_slice)
                
                # Normalize tag to our standard format
                normalized_tag = self._normalize_mitie_tag(tag)
                
                # Filter only required tags and minimum score
                if normalized_tag in self.get_supported_entities() and score >= 0.5:
                    entities.append({
                        "tag": normalized_tag,
                        "score": f"{score:.4f}",  # MITIE provides actual confidence scores
                        "label": entity_text
                    })
            
            # Ensure uniqueness
            return self._ensure_unique_entities(entities)
            
        except Exception as e:
            logger.error(f"Error processing text with MITIE: {e}")
            raise RuntimeError(f"Error in MITIE NER processing: {e}")
    
    def _normalize_mitie_tag(self, tag: str) -> str:
        """
        Normalize MITIE-specific tags to standard format
        
        Args:
            tag: Original MITIE tag
            
        Returns:
            Normalized tag
        """
        # MITIE typically uses: PERSON, LOCATION, ORGANIZATION
        # Map to our standard format
        mitie_mapping = {
            "PERSON": "PERSON",
            "LOCATION": "LOCATION",
            "ORGANIZATION": "ORGANIZATION",
            "ORG": "ORGANIZATION",
            "LOC": "LOCATION",
            "PER": "PERSON",
            # MITIE might have other tags, map them to MISC
        }
        
        normalized = mitie_mapping.get(tag.upper())
        if normalized:
            return normalized
        else:
            # Use base class normalization for unknown tags
            return self._normalize_tag(tag)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the MITIE backend
        
        Returns:
            Dictionary with backend information
        """
        return {
            "backend": "mitie",
            "model_path": self.model_path,
            "is_loaded": self.is_loaded,
            "version": "0.4+",  # MITIE version
            "description": "MITIE state-of-the-art NER using Structural Support Vector Machines",
            "performance": "High accuracy with distributional word embeddings",
            "model_size": "~451MB (Spanish model)",
            "technology": "Built on dlib, uses SVM and word embeddings"
        }
    
    def get_supported_entities(self) -> List[str]:
        """
        Get list of supported entity types for MITIE backend
        
        Returns:
            List of supported entity type strings
        """
        return ["PERSON", "LOCATION", "ORGANIZATION", "MISC", "PLACE"]