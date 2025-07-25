import os
from typing import Optional, Dict, Any, List

class Config:
    """Configuration management for the NER service"""
    
    # Default values
    DEFAULT_BACKEND = "mitie"
    DEFAULT_SPACY_MODEL = "es_core_news_md"
    DEFAULT_MITIE_MODEL = "MITIE-models/spanish/ner_model.dat"
    
    def __init__(self):
        """Initialize configuration from environment variables and defaults"""
        self._config = {
            # Backend selection
            "ner_backend": os.getenv("NER_BACKEND", self.DEFAULT_BACKEND).lower(),
            
            # spaCy configuration
            "spacy_model": os.getenv("SPACY_MODEL", self.DEFAULT_SPACY_MODEL),
            
            # MITIE configuration
            "mitie_model_path": os.getenv("MITIE_MODEL_PATH", self.DEFAULT_MITIE_MODEL),
            
            # API configuration
            "api_host": os.getenv("API_HOST", "0.0.0.0"),
            "api_port": int(os.getenv("API_PORT", "8000")),
            
            # Logging
            "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
        }
    
    @property
    def ner_backend(self) -> str:
        """Get the selected NER backend"""
        return self._config["ner_backend"]
    
    @property
    def spacy_model(self) -> str:
        """Get the spaCy model name"""
        return self._config["spacy_model"]
    
    @property
    def mitie_model_path(self) -> str:
        """Get the MITIE model path"""
        return self._config["mitie_model_path"]
    
    @property
    def api_host(self) -> str:
        """Get the API host"""
        return self._config["api_host"]
    
    @property
    def api_port(self) -> int:
        """Get the API port"""
        return self._config["api_port"]
    
    @property
    def log_level(self) -> str:
        """Get the log level"""
        return self._config["log_level"]
    
    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific backend
        
        Args:
            backend: Backend name ("spacy" or "mitie"). If None, uses current backend.
            
        Returns:
            Dictionary with backend-specific configuration
        """
        backend = backend or self.ner_backend
        
        if backend == "spacy":
            return {
                "model_name": self.spacy_model
            }
        elif backend == "mitie":
            return {
                "model_path": self.mitie_model_path
            }
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def set_backend(self, backend: str) -> None:
        """
        Set the NER backend
        
        Args:
            backend: Backend name ("spacy" or "mitie")
        """
        if backend.lower() not in ["spacy", "mitie"]:
            raise ValueError(f"Invalid backend: {backend}. Must be 'spacy' or 'mitie'")
        
        self._config["ner_backend"] = backend.lower()
    
    def is_valid_backend(self, backend: str) -> bool:
        """
        Check if a backend name is valid
        
        Args:
            backend: Backend name to validate
            
        Returns:
            True if valid, False otherwise
        """
        return backend.lower() in ["spacy", "mitie"]
    
    def get_supported_backends(self) -> List[str]:
        """
        Get list of supported backends
        
        Returns:
            List of supported backend names
        """
        return ["spacy", "mitie"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary
        
        Returns:
            Dictionary with all configuration values
        """
        return self._config.copy()

# Global configuration instance
config = Config()