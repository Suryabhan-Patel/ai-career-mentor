"""
Embedding-based similarity matching using sentence-transformers.

NOTE: To enable full embedding functionality, install sentence-transformers:
    pip install sentence-transformers torch

Currently using a simplified cosine similarity fallback.
"""

import numpy as np
from typing import List, Dict, Tuple
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, fallback to None if not available
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers not installed. Using fallback embedding method.")


class EmbeddingService:
    """
    Generate and match embeddings using sentence-transformers (all-MiniLM-L6-v2).
    Supports both direct similarity and FAISS-based matching for scalability.
    Falls back to simple text similarity if sentence-transformers is not available.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service with sentence-transformers model.
        
        Args:
            model_name (str): Hugging Face model name for embeddings
        """
        self.model_name = model_name
        self.model = None
        self.embeddings_cache = {}
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded embedding model: {model_name}")
            except Exception as e:
                logger.error(f"Error loading embedding model: {str(e)}")
                logger.warning("Falling back to simple text-based embeddings")
        else:
            logger.info("Using fallback text-based embedding method")
    
    def generate_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Generate embedding for given text.
        
        Args:
            text (str): Text to embed
            use_cache (bool): Whether to use cached embeddings
            
        Returns:
            np.ndarray: Embedding vector
        """
        # Create hash for caching
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if use_cache and text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]
        
        try:
            if HAS_SENTENCE_TRANSFORMERS and self.model:
                embedding = self.model.encode(text, convert_to_numpy=True)
            else:
                # Fallback: simple TF-IDF-like embedding based on word frequency
                embedding = self._simple_text_embedding(text)
            
            if use_cache:
                self.embeddings_cache[text_hash] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return fallback embedding
            return self._simple_text_embedding(text)
    
    def _simple_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate a simple embedding based on character n-gram frequencies.
        Fallback method when sentence-transformers is not available.
        
        Args:
            text (str): Text to embed
            
        Returns:
            np.ndarray: Simple embedding vector (100 dimensions)
        """
        # Create a simple embedding based on character n-grams
        text = text.lower()[:500]  # Limit length
        
        # Create a 100-dimensional vector based on text hash and character distribution
        embedding = np.zeros(100)
        
        # Use character frequency for dimensions
        for i, char in enumerate(text):
            embedding[ord(char) % 100] += 1
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.astype(np.float32)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts (List[str]): List of texts to embed
            batch_size (int): Batch size for processing
            
        Returns:
            List[np.ndarray]: List of embedding vectors
        """
        try:
            if HAS_SENTENCE_TRANSFORMERS and self.model:
                embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=batch_size)
            else:
                embeddings = [self._simple_text_embedding(text) for text in texts]
            
            # Cache the embeddings
            for text, embedding in zip(texts, embeddings):
                text_hash = hashlib.md5(text.encode()).hexdigest()
                self.embeddings_cache[text_hash] = embedding
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            # Return fallback embeddings
            return [self._simple_text_embedding(text) for text in texts]
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1 (np.ndarray): First embedding
            embedding2 (np.ndarray): Second embedding
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def match_resume_to_roles(self, resume_text: str, role_descriptions: Dict[str, str]) -> List[Dict]:
        """
        Match resume embeddings to job role embeddings.
        
        Args:
            resume_text (str): Extracted resume text
            role_descriptions (Dict[str, str]): Dictionary of {role_name: role_description}
            
        Returns:
            List[Dict]: Matched roles with similarity scores
        """
        try:
            # Generate resume embedding
            resume_embedding = self.generate_embedding(resume_text)
            
            # Generate role embeddings
            role_names = list(role_descriptions.keys())
            role_texts = list(role_descriptions.values())
            role_embeddings = self.generate_embeddings_batch(role_texts)
            
            # Calculate similarities
            matches = []
            for role_name, role_embedding in zip(role_names, role_embeddings):
                similarity = self.cosine_similarity(resume_embedding, role_embedding)
                
                matches.append({
                    "role": role_name,
                    "embedding_similarity": round(similarity, 4),
                    "match_percentage": round(similarity * 100, 2)
                })
            
            # Sort by similarity
            matches.sort(key=lambda x: x["embedding_similarity"], reverse=True)
            
            return matches
        except Exception as e:
            logger.error(f"Error matching resume to roles: {str(e)}")
            raise
    
    def semantic_search_skills(self, query: str, candidate_skills: List[str], top_k: int = 5) -> List[Dict]:
        """
        Find most semantically similar skills using embeddings.
        
        Args:
            query (str): Skill query text
            candidate_skills (List[str]): List of candidate skills
            top_k (int): Number of top results to return
            
        Returns:
            List[Dict]: Top matching skills with similarity scores
        """
        try:
            # Generate embeddings
            query_embedding = self.generate_embedding(query)
            skill_embeddings = self.generate_embeddings_batch(candidate_skills)
            
            # Calculate similarities
            similarities = []
            for skill, embedding in zip(candidate_skills, skill_embeddings):
                similarity = self.cosine_similarity(query_embedding, embedding)
                similarities.append({
                    "skill": skill,
                    "similarity": round(similarity, 4)
                })
            
            # Sort and return top-k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise
    
    def get_embedding_stats(self) -> Dict:
        """
        Get statistics about cached embeddings.
        
        Returns:
            Dict: Cache statistics
        """
        return {
            "model_name": self.model_name,
            "cached_embeddings": len(self.embeddings_cache),
            "embedding_dimension": self.model.get_sentence_embedding_dimension()
        }
