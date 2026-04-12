"""
GramAI - Chat API Tests
Tests for the query processing and RAG pipeline.
"""

import pytest
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestKnowledgeBase:
    """Test knowledge base data files."""

    DATA_DIR = Path(__file__).parent.parent / "backend" / "data"

    def test_agriculture_data_exists(self):
        """Agriculture data file should exist."""
        assert (self.DATA_DIR / "agriculture.json").exists()

    def test_education_data_exists(self):
        """Education data file should exist."""
        assert (self.DATA_DIR / "education.json").exists()

    def test_health_data_exists(self):
        """Health data file should exist."""
        assert (self.DATA_DIR / "health.json").exists()

    def test_schemes_data_exists(self):
        """Government schemes data file should exist."""
        assert (self.DATA_DIR / "schemes.json").exists()

    def test_agriculture_data_valid_json(self):
        """Agriculture data should be valid JSON."""
        with open(self.DATA_DIR / "agriculture.json", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_data_has_required_fields(self):
        """Each data entry should have required fields."""
        for filename in ["agriculture.json", "education.json", "health.json", "schemes.json"]:
            with open(self.DATA_DIR / filename, encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                assert "id" in item, f"Missing 'id' in {filename}"
                assert "category" in item, f"Missing 'category' in {filename}"
                assert "title" in item, f"Missing 'title' in {filename}"
                assert "content" in item, f"Missing 'content' in {filename}"
                assert "keywords" in item, f"Missing 'keywords' in {filename}"
                assert isinstance(item["keywords"], list), f"'keywords' should be list in {filename}"

    def test_data_has_hindi_content(self):
        """Data should contain Hindi content (Devanagari script)."""
        with open(self.DATA_DIR / "agriculture.json", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            # Check if content has Devanagari characters (Unicode range 0900-097F)
            has_hindi = any('\u0900' <= char <= '\u097F' for char in item["content"])
            assert has_hindi, f"Item {item['id']} should have Hindi content"

    def test_unique_ids(self):
        """All IDs across all files should be unique."""
        all_ids = set()
        for filename in ["agriculture.json", "education.json", "health.json", "schemes.json"]:
            with open(self.DATA_DIR / filename, encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                assert item["id"] not in all_ids, f"Duplicate ID: {item['id']}"
                all_ids.add(item["id"])


class TestConfiguration:
    """Test configuration values."""

    def test_config_imports(self):
        """Config module should import without errors."""
        from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT
        assert OLLAMA_BASE_URL
        assert OLLAMA_MODEL
        assert SYSTEM_PROMPT

    def test_system_prompt_has_hindi(self):
        """System prompt should contain Hindi instructions."""
        from config import SYSTEM_PROMPT
        has_hindi = any('\u0900' <= char <= '\u097F' for char in SYSTEM_PROMPT)
        assert has_hindi, "System prompt should have Hindi text"


class TestFrontendFiles:
    """Test frontend files exist and are valid."""

    FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

    def test_index_html_exists(self):
        """index.html should exist."""
        assert (self.FRONTEND_DIR / "index.html").exists()

    def test_css_exists(self):
        """CSS file should exist."""
        assert (self.FRONTEND_DIR / "css" / "style.css").exists()

    def test_js_exists(self):
        """JavaScript file should exist."""
        assert (self.FRONTEND_DIR / "js" / "app.js").exists()

    def test_html_has_hindi_content(self):
        """HTML should have Hindi UI text."""
        html = (self.FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        assert "ग्रामAI" in html
        assert "हिंदी" in html or "सवाल" in html

    def test_html_is_mobile_friendly(self):
        """HTML should have mobile viewport meta tag."""
        html = (self.FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        assert "viewport" in html
        assert "width=device-width" in html

    def test_html_has_manifest(self):
        """HTML should link to PWA manifest."""
        html = (self.FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        assert "manifest" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
