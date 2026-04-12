"""
GramAI - RAG Pipeline Tests
Tests for vector store and RAG integration.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestVectorStore:
    """Test ChromaDB vector store operations."""

    def test_vector_store_import(self):
        """Vector store should import without errors."""
        from services.vector_store import vector_store
        assert vector_store is not None

    def test_get_categories(self):
        """Should return all 4 knowledge categories."""
        from services.vector_store import vector_store
        categories = vector_store.get_categories()
        assert "कृषि" in categories
        assert "शिक्षा" in categories
        assert "स्वास्थ्य" in categories
        assert "सरकारी योजना" in categories


class TestRAGService:
    """Test RAG pipeline."""

    def test_rag_import(self):
        """RAG service should import without errors."""
        from services.rag_service import rag_service
        assert rag_service is not None

    def test_categories(self):
        """RAG should expose knowledge categories."""
        from services.rag_service import rag_service
        cats = rag_service.get_categories()
        assert len(cats) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
