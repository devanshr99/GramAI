"""
GramAI - Vector Store Service (FAISS + Sentence-Transformers)
Performs local semantic search over the knowledge base with automatic caching.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

from config import DATA_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Category mapped keywords for intelligent filtering/intent hints
EN_CATEGORY_HINTS = {
    'crop': 'कृषि', 'crops': 'कृषि', 'farming': 'कृषि', 'agriculture': 'कृषि',
    'grow': 'कृषि', 'growing': 'कृषि', 'plant': 'कृषि', 'seed': 'कृषि',
    'wheat': 'कृषि', 'rice': 'कृषि', 'potato': 'कृषि', 'vegetable': 'कृषि',
    'soil': 'कृषि', 'irrigation': 'कृषि', 'fertilizer': 'कृषि', 'organic': 'कृषि',
    'pest': 'कृषि', 'cow': 'कृषि', 'dairy': 'कृषि', 'cattle': 'कृषि',
    'health': 'स्वास्थ्य', 'fever': 'स्वास्थ्य', 'disease': 'स्वास्थ्य',
    'medicine': 'स्वास्थ्य', 'doctor': 'स्वास्थ्य', 'hospital': 'स्वास्थ्य',
    'treatment': 'स्वास्थ्य', 'malaria': 'स्वास्थ्य', 'dengue': 'स्वास्थ्य',
    'vaccine': 'स्वास्थ्य', 'pregnancy': 'स्वास्थ्य',
    'education': 'शिक्षा', 'school': 'शिक्षा', 'college': 'शिक्षा',
    'scholarship': 'शिक्षा', 'exam': 'शिक्षा', 'admission': 'शिक्षा',
    'scheme': 'सरकारी योजना', 'government': 'सरकारी योजना', 'pension': 'सरकारी योजना',
    'insurance': 'सरकारी योजना', 'pm': 'सरकारी योजना', 'kisan': 'सरकारी योजना',
    'ayushman': 'सरकारी योजना',
}


class VectorStoreService:
    """Semantic vector search using Sentence-Transformers and FAISS."""

    def __init__(self):
        self.documents: List[Dict] = []
        self.index = None
        self.embedder = None
        self._initialized = False
        self.cache_dir = DATA_DIR / "faiss_index"

    def initialize(self):
        if self._initialized:
            return
        logger.info("Initializing FAISS Vector Store...")
        
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        index_path = self.cache_dir / "index.faiss"
        docs_path = self.cache_dir / "documents.json"

        # Load SentenceTransformer first
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise e

        # Check if cached index exists
        if index_path.exists() and docs_path.exists():
            try:
                import faiss
                self.index = faiss.read_index(str(index_path))
                with open(docs_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                self._initialized = True
                logger.info(f"Loaded FAISS index from cache with {len(self.documents)} documents.")
                return
            except Exception as e:
                logger.warning(f"Failed to load cached index: {e}. Rebuilding index...")

        # Rebuild if cache missed or failed
        self._load_all_data()
        self._build_index()
        self._initialized = True

    def _load_all_data(self):
        self.documents = []
        data_files = {
            "agriculture.json": "कृषि",
            "education.json": "शिक्षा",
            "health.json": "स्वास्थ्य",
            "schemes.json": "सरकारी योजना",
            "science.json": "शिक्षा",
            "mathematics.json": "शिक्षा",
            "history_geography.json": "शिक्षा"
        }
        for filename, category in data_files.items():
            filepath = DATA_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data:
                        self.documents.append({
                            "id": item.get("id", ""),
                            "category": item.get("category", category),
                            "subcategory": item.get("subcategory", ""),
                            "title": item.get("title", ""),
                            "content": item.get("content", ""),
                            "keywords": item.get("keywords", []),
                            "full_text": f"{item.get('title', '')}: {item.get('content', '')} {' '.join(item.get('keywords', []))}"
                        })
                    logger.info(f"Loaded {len(data)} documents from {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filepath}: {e}")

    def _build_index(self):
        if not self.documents:
            logger.warning("No documents loaded to build index.")
            return

        import faiss
        logger.info("Generating embeddings for documents...")
        texts = [doc["full_text"] for doc in self.documents]
        
        # Compute embeddings
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        # Cache FAISS index and documents list
        try:
            faiss.write_index(self.index, str(self.cache_dir / "index.faiss"))
            with open(self.cache_dir / "documents.json", "w", encoding="utf-8") as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logger.info("Saved FAISS index cache.")
        except Exception as e:
            logger.error(f"Error saving FAISS cache: {e}")

    def _detect_category_hint(self, query: str) -> Optional[str]:
        """Detect likely category from query terms."""
        tokens = re.findall(r'\w+', query.lower())
        for token in tokens:
            cat = EN_CATEGORY_HINTS.get(token)
            if cat:
                return cat
        return None

    def search(self, query: str, n_results: int = 3, category: Optional[str] = None) -> List[Dict]:
        if not self._initialized:
            self.initialize()

        if not self.documents or self.index is None:
            return []

        # Encode query
        query_embedding = self.embedder.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # Retrieve candidates (fetch more candidates to filter by category)
        import faiss
        search_k = min(len(self.documents), n_results * 5)
        distances, indices = self.index.search(query_embedding, search_k)

        effective_category = category or self._detect_category_hint(query)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            
            # Apply category filtering if set
            if effective_category and doc["category"] != effective_category:
                continue

            # Calculate a normalized relevance score from L2 distance (L2 distance near 0 means high similarity)
            # Normalization helper: score = 1 / (1 + distance)
            relevance = float(1.0 / (1.0 + float(dist)))

            results.append({
                "content": f"{doc['title']}. {doc['content']}",
                "metadata": {
                    "category": doc["category"],
                    "subcategory": doc["subcategory"],
                    "title": doc["title"],
                },
                "relevance_score": round(relevance, 3)
            })

            if len(results) >= n_results:
                break

        # Fallback: if category filter yielded no results, return top matches without category filter
        if not results:
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1 or idx >= len(self.documents):
                    continue
                doc = self.documents[idx]
                relevance = float(1.0 / (1.0 + float(dist)))
                results.append({
                    "content": f"{doc['title']}. {doc['content']}",
                    "metadata": {
                        "category": doc["category"],
                        "subcategory": doc["subcategory"],
                        "title": doc["title"],
                    },
                    "relevance_score": round(relevance, 3)
                })
                if len(results) >= n_results:
                    break

        return results

    def count(self) -> int:
        return len(self.documents)

    def get_categories(self) -> List[str]:
        return ["कृषि", "शिक्षा", "स्वास्थ्य", "सरकारी योजना"]


vector_store = VectorStoreService()
