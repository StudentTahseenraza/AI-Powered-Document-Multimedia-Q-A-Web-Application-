# backend/app/services/embeddings.py
import numpy as np
from typing import List
import logging
import hashlib

logger = logging.getLogger(__name__)

class SimpleEmbeddingService:
    """Simple embedding service without external APIs"""
    
    def __init__(self):
        self.use_local = True
        logger.info("Using local embedding service")
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to simple hash-based vector"""
        vector = np.zeros(384)
        words = text.split()[:100]
        
        for i, word in enumerate(words):
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = hash_val % 384
            vector[idx] += 1
        
        if np.linalg.norm(vector) > 0:
            vector = vector / np.linalg.norm(vector)
        
        return vector
    
    async def encode(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        vectors = [self._text_to_vector(text) for text in texts]
        return np.array(vectors)

embedding_service = SimpleEmbeddingService()