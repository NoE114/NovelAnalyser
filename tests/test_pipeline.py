"""
Tests for Blezecon's pipeline
"""
import pytest
from src.pathway_pipeline.app import NovelAnalyzerApp
from src.pathway_pipeline.schema import ChunkSchema


def test_app_initialization():
    """Test app initializes correctly"""
    app = NovelAnalyzerApp("configs/pathway.yaml")
    assert app.config is not None
    assert app.vector_index is not None


def test_ingestion():
    """Test novel ingestion"""
    app = NovelAnalyzerApp("configs/pathway.yaml")
    novels = app.ingest_novels()
    
    # Verify it's a Pathway table
    assert novels is not None


def test_schema_validation():
    """Test chunk schema"""
    # Verify schema has required fields
    required_fields = ['chunk_id', 'story_id', 'chapter', 'para_idx', 'text']
    
    schema_fields = ChunkSchema.__annotations__.keys()
    
    for field in required_fields:
        assert field in schema_fields