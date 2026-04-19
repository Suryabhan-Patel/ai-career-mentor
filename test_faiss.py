"""Test script for FAISS initialization"""

from app.services.embedding_utils import EmbeddingModel
from app.services.faiss_index import FAISSIndexManager
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("Loading embedding model...")
embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
print(f"✓ Model loaded. Embedding dim: {embedding_model.embedding_dim}")

print("\nInitializing FAISS index...")
role_descriptions = {
    "Data Scientist": "Data scientist with expertise in machine learning, statistical analysis, Python programming",
    "ML Engineer": "Machine learning engineer who develops and deploys ML models",
    "Backend Developer": "Backend developer building APIs, managing databases, SQL"
}

faiss_manager = FAISSIndexManager(embedding_model)
if faiss_manager.build_index(role_descriptions):
    print("✓ FAISS index built successfully!")
    stats = faiss_manager.get_index_stats()
    print(f"  Indexed roles: {stats['num_roles']}")
    print(f"  Is trained: {stats['is_trained']}")
    
    # Test search
    print("\nTesting FAISS search with sample resume text...")
    result = faiss_manager.search("I know Python, SQL, and machine learning")
    print(f"✓ Search returned {len(result)} results:")
    for r in result:
        print(f"  - {r['role']}: {r['match_percentage']:.2f}%")
else:
    print("✗ Failed to build FAISS index")
