import pathway as pw
from dataclasses import dataclass
from typing import Optional

# ============= PATHWAY SCHEMAS =============

class RawNovelSchema(pw.Schema):
    """Schema for raw novel input"""
    story_id: str
    filepath: str
    content: bytes
    

class NovelMetadataSchema(pw.Schema):
    """Schema for novel-level metadata"""
    story_id: str
    title: str
    total_chapters: int
    total_paragraphs: int
    total_words: int
    total_chars: int
    processed_timestamp: str


class NovelChunkSchema(pw.Schema):
    """
    Schema for processed chunks
    
    Player 3 responsibility
    """
    chunk_id: str           # Format: "{story_id}_chunk_{idx}"
    story_id: str           # Novel identifier
    chapter: int            # Chapter number
    para_idx: int           # Paragraph index within chapter
    text: str               # Actual chunk content
    word_count: int         # Words in this chunk
    char_position: int      # Starting char position in novel
    embedding: list         # Vector embedding (768-dim)


# ============= PYTHON DATACLASSES (for internal use) =============

@dataclass
class ChunkMetadata:
    """Metadata for a single chunk"""
    chunk_id: str
    story_id: str
    chapter: int
    para_idx: int
    word_count: int
    char_position: int


@dataclass
class NovelMetadata:
    """Metadata for a complete novel"""
    story_id: str
    title: str
    total_chapters: int
    total_paragraphs: int
    total_words: int
    total_chars: int
    num_chunks: int
    processed_timestamp: str


@dataclass
class IndexMetadata:
    """Metadata for vector index"""
    story_id: str
    num_chunks: int
    embedding_model: str
    embedding_dim: int
    index_version: str
    created_at: str