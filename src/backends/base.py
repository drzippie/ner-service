from abc import ABC, abstractmethod
from typing import List, Dict, Any

class NERBackend(ABC):
    """Abstract base class for Named Entity Recognition backends"""
    
    def __init__(self, model_name: str = None, **kwargs):
        """
        Initialize the NER backend
        
        Args:
            model_name: Name of the model to use (backend-specific)
            **kwargs: Additional backend-specific parameters
        """
        self.model_name = model_name
        self.is_loaded = False
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the NER model"""
        pass
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of found entities with format:
            [{"tag": str, "score": str, "label": str}]
        """
        pass
    
    @abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the backend
        
        Returns:
            Dictionary with backend information
        """
        pass
    
    @abstractmethod
    def get_supported_entities(self) -> List[str]:
        """
        Get list of supported entity types
        
        Returns:
            List of supported entity type strings
        """
        pass
    
    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize backend-specific tags to standard format
        
        Args:
            tag: Original backend tag
            
        Returns:
            Normalized tag from: PERSON, LOCATION, ORGANIZATION, MISC, PLACE
        """
        # Standard mapping - can be overridden by backends
        tag_mapping = {
            "PER": "PERSON",
            "PERSON": "PERSON",
            "LOC": "LOCATION",
            "LOCATION": "LOCATION", 
            "GPE": "LOCATION",
            "ORG": "ORGANIZATION",
            "ORGANIZATION": "ORGANIZATION",
            "MISC": "MISC",
            "NORP": "MISC",
            "FACILITY": "PLACE",
            "FAC": "PLACE",
            "PLACE": "PLACE",
            "EVENT": "MISC",
            "WORK_OF_ART": "MISC",
            "LAW": "MISC",
            "LANGUAGE": "MISC",
            "DATE": "MISC",
            "TIME": "MISC",
            "PERCENT": "MISC",
            "MONEY": "MISC",
            "QUANTITY": "MISC",
            "ORDINAL": "MISC",
            "CARDINAL": "MISC"
        }
        
        return tag_mapping.get(tag.upper(), "MISC")
    
    def _ensure_unique_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure entity uniqueness across the results
        
        Args:
            entities: List of entities to deduplicate
            
        Returns:
            List of unique entities
        """
        seen_entities = set()
        unique_entities = []
        
        for entity in entities:
            # Clean the entity text
            clean_label = entity["label"].strip()
            
            # Create unique identifier (case-insensitive label + tag)
            entity_key = (clean_label.lower(), entity["tag"])
            
            # Only add if we haven't seen this exact entity before
            if entity_key not in seen_entities:
                seen_entities.add(entity_key)
                # Update the entity with clean label
                entity["label"] = clean_label
                unique_entities.append(entity)
        
        return unique_entities