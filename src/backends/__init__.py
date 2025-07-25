from .base import NERBackend
from .spacy_backend import SpacyNERBackend

__all__ = ['NERBackend', 'SpacyNERBackend']

# Lazy import MITIE to avoid import errors if not installed
def get_mitie_backend():
    """Lazy import MITIE backend to avoid import errors if not installed"""
    try:
        from .mitie_backend import MitieNERBackend
        return MitieNERBackend
    except ImportError as e:
        raise ImportError(
            "MITIE backend not available. Install with:\n"
            "pip install git+https://github.com/mit-nlp/MITIE.git\n"
            f"Original error: {e}"
        )