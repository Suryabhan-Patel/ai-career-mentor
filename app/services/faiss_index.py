"""
FAISS Index Manager for semantic similarity search.
Manages role embeddings and performs fast similarity search.
"""

import numpy as np
import logging
from typing import List, Dict, Tuple
import json

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from app.services.embedding_utils import EmbeddingModel, encode_text_batch

logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """
    Manages FAISS index for role embeddings.
    Handles index creation, adding embeddings, and similarity search.
    """
    
    def __init__(self, embedding_model: EmbeddingModel):
        """
        Initialize FAISS Index Manager.
        
        Args:
            embedding_model: EmbeddingModel instance for encoding texts
        """
        self.embedding_model = embedding_model
        self.index = None
        self.roles = []
        self.role_descriptions = {}
        self.embedding_dim = embedding_model.embedding_dim
        self.is_trained = False
        
        if not HAS_FAISS:
            logger.error("✗ FAISS not installed. Install with: pip install faiss-cpu")
        else:
            logger.info("✓ FAISS available for semantic search")
    
    def build_index(self, roles: Dict[str, str]) -> bool:
        """
        Build FAISS index from role descriptions.
        
        Args:
            roles: Dictionary mapping role name to description
                   Example: {"Data Analyst": "Analyzes data...", ...}
                   
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_FAISS:
            logger.error("FAISS not available")
            return False
        
        try:
            # Store roles
            self.roles = list(roles.keys())
            self.role_descriptions = roles
            
            # Create role description texts for embedding
            role_texts = list(roles.values())
            
            logger.info(f"Encoding {len(self.roles)} role descriptions...")
            # Encode all role descriptions
            role_embeddings = encode_text_batch(role_texts, self.embedding_model)
            
            # Create FAISS index
            # Using IndexFlatIP (Inner Product) for normalized vectors
            # This gives us cosine similarity scores directly
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Add embeddings to index
            self.index.add(role_embeddings.astype(np.float32))
            self.is_trained = True
            
            logger.info(f"✓ FAISS index built with {len(self.roles)} roles")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error building FAISS index: {str(e)}")
            return False
    
    def search(self, query_text: str, k: int = 3) -> List[Dict]:
        """
        Search for similar roles using FAISS.
        
        Args:
            query_text: Resume text or query embedding
            k: Number of top results to return
            
        Returns:
            List of dicts with role, score, and description
        """
        if not self.is_trained or self.index is None:
            logger.warning("FAISS index not trained yet")
            return []
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode(query_text, normalize=True)
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            
            # Search in FAISS index
            # Returns distances and indices
            distances, indices = self.index.search(query_embedding, min(k, len(self.roles)))
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx >= 0:  # Valid index
                    role = self.roles[idx]
                    # Convert distance to similarity score (0-1)
                    # For normalized vectors, IP distance is already in range [0, 1]
                    score = float(distance)
                    
                    results.append({
                        "role": role,
                        "role_name": role,
                        "similarity_score": score,
                        "match_percentage": score * 100,
                        "description": self.role_descriptions.get(role, ""),
                        "required_skills": self._get_role_skills(role)
                    })
            
            logger.info(f"FAISS search completed: {len(results)} results for query")
            return results
            
        except Exception as e:
            logger.error(f"✗ Error during FAISS search: {str(e)}")
            return []
    
    def search_batch(self, query_texts: List[str], k: int = 3) -> List[List[Dict]]:
        """
        Search for multiple queries at once.
        
        Args:
            query_texts: List of query texts
            k: Number of top results per query
            
        Returns:
            List of lists, each containing top-k results
        """
        if not self.is_trained or self.index is None:
            return [[] for _ in query_texts]
        
        try:
            # Encode all queries
            query_embeddings = encode_text_batch(query_texts, self.embedding_model)
            query_embeddings = query_embeddings.astype(np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embeddings, min(k, len(self.roles)))
            
            results = []
            for dist_row, idx_row in zip(distances, indices):
                query_results = []
                for distance, idx in zip(dist_row, idx_row):
                    if idx >= 0:
                        role = self.roles[idx]
                        score = float(distance)
                        query_results.append({
                            "role": role,
                            "role_name": role,
                            "similarity_score": score,
                            "match_percentage": score * 100,
                            "description": self.role_descriptions.get(role, ""),
                            "required_skills": self._get_role_skills(role)
                        })
                results.append(query_results)
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Error during batch FAISS search: {str(e)}")
            return [[] for _ in query_texts]
    
    def _get_role_skills(self, role: str) -> List[str]:
        """
        Get required skills for a role.
        Maps role to predefined skill sets.
        
        Args:
            role: Role name
            
        Returns:
            List of required skills
        """
        role_skills_map = {
            "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL", "TensorFlow", "Pandas"],
            "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics"],
            "ML Engineer": ["Python", "ML Frameworks", "Deep Learning", "PyTorch", "Scikit-learn", "Production ML"],
            "Backend Developer": ["Python", "APIs", "Databases", "SQL", "REST", "Microservices"],
            "Frontend Developer": ["JavaScript", "React", "HTML/CSS", "TypeScript", "UI/UX", "Web Dev"],
            "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS/Cloud", "Infrastructure"],
            "AI Engineer": ["Python", "NLP", "Deep Learning", "LLMs", "Transformers", "Hugging Face"],
            "Full Stack Developer": ["Python", "JavaScript", "React", "Databases", "APIs", "Web Dev"]
        }
        return role_skills_map.get(role, [])
    
    def save_index(self, filepath: str) -> bool:
        """
        Save FAISS index to disk.
        
        Args:
            filepath: Path to save index file
            
        Returns:
            bool: True if successful
        """
        if not self.is_trained or self.index is None:
            logger.warning("No trained index to save")
            return False
        
        try:
            # Save index
            faiss.write_index(self.index, filepath)
            
            # Save metadata (roles and descriptions)
            metadata = {
                "roles": self.roles,
                "descriptions": self.role_descriptions,
                "embedding_dim": self.embedding_dim
            }
            
            metadata_path = filepath.replace(".index", ".meta.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✓ FAISS index saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error saving FAISS index: {str(e)}")
            return False
    
    def load_index(self, filepath: str) -> bool:
        """
        Load FAISS index from disk.
        
        Args:
            filepath: Path to saved index file
            
        Returns:
            bool: True if successful
        """
        try:
            # Load index
            self.index = faiss.read_index(filepath)
            
            # Load metadata
            metadata_path = filepath.replace(".index", ".meta.json")
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            self.roles = metadata["roles"]
            self.role_descriptions = metadata["descriptions"]
            self.embedding_dim = metadata["embedding_dim"]
            self.is_trained = True
            
            logger.info(f"✓ FAISS index loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error loading FAISS index: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the current index."""
        return {
            "is_trained": self.is_trained,
            "num_roles": len(self.roles),
            "embedding_dim": self.embedding_dim,
            "roles": self.roles if self.is_trained else []
        }
