from typing import List, Dict, Any, Optional
import logging
from .backends.base import NERBackend
from .backends.spacy_backend import SpacyNERBackend
from .backends import get_mitie_backend
from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NERBackendFactory:
    """Factory for creating NER backends"""
    
    @staticmethod
    def create_backend(backend_name: Optional[str] = None, **kwargs) -> NERBackend:
        """
        Create a NER backend instance
        
        Args:
            backend_name: Name of the backend ("spacy" or "mitie"). If None, uses config default.
            **kwargs: Additional backend-specific arguments
            
        Returns:
            NERBackend instance
            
        Raises:
            ValueError: If backend_name is not supported
            ImportError: If required backend dependencies are not installed
        """
        backend_name = backend_name or config.ner_backend
        backend_name = backend_name.lower()
        
        if backend_name == "spacy":
            backend_config = config.get_backend_config("spacy")
            backend_config.update(kwargs)  # Allow override
            return SpacyNERBackend(**backend_config)
        
        elif backend_name == "mitie":
            # Lazy import MITIE to avoid import errors
            try:
                MitieNERBackend = get_mitie_backend()
                backend_config = config.get_backend_config("mitie")
                backend_config.update(kwargs)  # Allow override
                return MitieNERBackend(**backend_config)
            except ImportError as e:
                logger.error(f"MITIE backend not available: {e}")
                raise
        
        else:
            supported = config.get_supported_backends()
            raise ValueError(
                f"Unsupported backend: {backend_name}. "
                f"Supported backends: {', '.join(supported)}"
            )

class SpanishNER:
    """
    Main Spanish NER class with configurable backends
    
    This class provides a unified interface for Spanish Named Entity Recognition
    using different backends (spaCy, MITIE, etc.)
    """
    
    def __init__(self, backend: Optional[str] = None, **kwargs):
        """
        Initialize the Spanish NER with configurable backend
        
        Args:
            backend: Backend to use ("spacy" or "mitie"). If None, uses config default.
            **kwargs: Backend-specific arguments
        """
        self.backend_name = backend or config.ner_backend
        self.backend = NERBackendFactory.create_backend(self.backend_name, **kwargs)
        logger.info(f"Initialized Spanish NER with {self.backend_name} backend")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of found entities with format:
            [{"tag": str, "score": str, "label": str}]
        """
        return self.backend.extract_entities(text)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the current backend
        
        Returns:
            Dictionary with backend information
        """
        return self.backend.get_backend_info()
    
    def get_supported_entities(self) -> List[str]:
        """
        Get list of supported entity types
        
        Returns:
            List of supported entity type strings
        """
        return self.backend.get_supported_entities()
    
    @property
    def is_loaded(self) -> bool:
        """Check if the backend is loaded and ready"""
        return self.backend.is_loaded

# Global model instance
_ner_instance = None
_current_backend = None

def get_ner_instance(backend: Optional[str] = None, force_reload: bool = False) -> SpanishNER:
    """
    Get the singleton instance of the NER model
    
    Args:
        backend: Backend to use. If None, uses config default.
        force_reload: Force recreation of the instance even if it exists
        
    Returns:
        SpanishNER instance
    """
    global _ner_instance, _current_backend
    
    requested_backend = backend or config.ner_backend
    
    # Create new instance if:
    # 1. No instance exists
    # 2. Backend has changed
    # 3. Force reload requested
    if (_ner_instance is None or 
        _current_backend != requested_backend or 
        force_reload):
        
        logger.info(f"Creating new NER instance with {requested_backend} backend")
        _ner_instance = SpanishNER(backend=requested_backend)
        _current_backend = requested_backend
    
    return _ner_instance

def extract_entities(text: str, backend: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to extract entities
    
    Args:
        text: Text to analyze
        backend: Backend to use. If None, uses current instance or config default.
        
    Returns:
        List of found entities
    """
    ner = get_ner_instance(backend=backend)
    return ner.extract_entities(text)

def get_backend_info(backend: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about the current or specified backend
    
    Args:
        backend: Backend to get info for. If None, uses current instance.
        
    Returns:
        Dictionary with backend information
    """
    ner = get_ner_instance(backend=backend)
    return ner.get_backend_info()

def get_supported_backends() -> List[str]:
    """
    Get list of all supported backends
    
    Returns:
        List of supported backend names
    """
    return config.get_supported_backends()

def set_backend(backend: str) -> None:
    """
    Set the default backend for future operations
    
    Args:
        backend: Backend name to set as default
    """
    if not config.is_valid_backend(backend):
        supported = get_supported_backends()
        raise ValueError(f"Invalid backend: {backend}. Supported: {', '.join(supported)}")
    
    config.set_backend(backend)
    # Force reload of global instance with new backend
    get_ner_instance(backend=backend, force_reload=True)