"""
Embedding utilities for semantic similarity search using sentence-transformers.
Handles encoding text to embeddings and normalizing vectors for FAISS.
"""

import numpy as np
import logging
from typing import Union, List
import hashlib

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Wrapper for sentence-transformers model with lazy loading and caching.
    Generates embeddings and normalizes vectors for FAISS.
    Loads model only when first needed to optimize memory usage.
    """
    
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):
        """
        Initialize embedding model (lazy loading).
        
        Args:
            model_name (str): HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.embedding_cache = {}
        self.embedding_dim = None
        self._model_loaded = False
    
    def _get_model(self):
        """
        Lazily load the SentenceTransformer model on first use.
        Imports are done here to defer memory allocation until needed.
        """
        if self._model_loaded:
            return self.model
        
        try:
            from sentence_transformers import SentenceTransformer
            
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self._model_loaded = True
            logger.info(f"✓ Loaded embedding model: {self.model_name} (dim: {self.embedding_dim})")
            return self.model
        except ImportError:
            logger.error("✗ sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise RuntimeError("sentence-transformers is required but not installed")
        except Exception as e:
            logger.error(f"✗ Error loading embedding model: {str(e)}")
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")
    
    def encode(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Encode text to embedding vector(s).
        
        Args:
            text: Single text string or list of strings
            normalize: Whether to normalize vectors to unit length (for IP distance)
            
        Returns:
            np.ndarray: Embedding vector(s) of shape (dim,) or (n, dim)
        """
        model = self._get_model()
        
        # Handle single string input
        if isinstance(text, str):
            text = [text]
            squeeze = True
        else:
            squeeze = False
        
        # Check cache for individual embeddings
        embeddings = []
        texts_to_encode = []
        indices_to_encode = []
        
        for i, t in enumerate(text):
            text_hash = hashlib.md5(t.encode()).hexdigest()
            if text_hash in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_hash])
            else:
                texts_to_encode.append(t)
                indices_to_encode.append(i)
                embeddings.append(None)
        
        # Encode uncached texts
        if texts_to_encode:
            new_embeddings = model.encode(texts_to_encode, convert_to_numpy=True)
            if new_embeddings.ndim == 1:  # Single embedding
                new_embeddings = new_embeddings.reshape(1, -1)
            
            for idx, embedding in zip(indices_to_encode, new_embeddings):
                text_hash = hashlib.md5(text[idx].encode()).hexdigest()
                self.embedding_cache[text_hash] = embedding
                embeddings[idx] = embedding
        
        # Stack embeddings
        embeddings = np.array(embeddings)
        
        # Normalize if requested (for inner product distance)
        if normalize:
            embeddings = self.normalize_vectors(embeddings)
        
        # Squeeze if single input
        if squeeze and len(embeddings) == 1:
            embeddings = embeddings[0]
        
        return embeddings
    
    @staticmethod
    def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
        """
        Normalize vectors to unit length (L2 normalization).
        Used for inner product (IP) distance in FAISS.
        
        Args:
            vectors: Array of shape (n, dim) or (dim,)
            
        Returns:
            np.ndarray: Normalized vectors
        """
        if vectors.ndim == 1:
            # Single vector
            norm = np.linalg.norm(vectors)
            return vectors / (norm + 1e-10)
        else:
            # Multiple vectors
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            return vectors / (norms + 1e-10)
    
    def clear_cache(self):
        """Clear embedding cache to free memory."""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")


def encode_text_batch(texts: List[str], embedding_model: EmbeddingModel) -> np.ndarray:
    """
    Encode multiple texts to embeddings.
    
    Args:
        texts: List of text strings
        embedding_model: EmbeddingModel instance
        
    Returns:
        np.ndarray: Array of shape (n, embedding_dim)
    """
    return embedding_model.encode(texts, normalize=True)


def encode_single_text(text: str, embedding_model: EmbeddingModel) -> np.ndarray:
    """
    Encode single text to embedding.
    
    Args:
        text: Text string
        embedding_model: EmbeddingModel instance
        
    Returns:
        np.ndarray: Embedding vector of shape (embedding_dim,)
    """
    return embedding_model.encode(text, normalize=True)


def cosine_similarity(embeddings_a: np.ndarray, embeddings_b: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity between embeddings (for reference).
    Note: FAISS uses distance metrics, not similarity directly.
    
    Args:
        embeddings_a: Array of shape (n, dim)
        embeddings_b: Array of shape (m, dim)
        
    Returns:
        np.ndarray: Similarity matrix of shape (n, m)
    """
    # Normalize vectors
    a_norm = embeddings_a / (np.linalg.norm(embeddings_a, axis=1, keepdims=True) + 1e-10)
    b_norm = embeddings_b / (np.linalg.norm(embeddings_b, axis=1, keepdims=True) + 1e-10)
    
    # Cosine similarity is just dot product of normalized vectors
    return np.dot(a_norm, b_norm.T)
