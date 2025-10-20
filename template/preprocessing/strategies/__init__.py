"""
Estrategias de chunking - __init__
"""
from .simple_chunker import SimpleChunker
from .legal_chunker import LegalChunker
from .semantic_chunker import SemanticChunker

__all__ = [
    'SimpleChunker',
    'LegalChunker',
    'SemanticChunker'
]
