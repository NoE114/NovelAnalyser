# Pathway table schemas
import pathway as pw


class RawNovelSchema(pw.Schema):
    """Raw novel input"""
    story_id: str
    content: bytes


class NovelSchema(pw.Schema):
    """Parsed novel"""
    story_id: str
    text: str
    total_words: int
    total_chapters: int


class ChunkSchema(pw.Schema):
    """
    Chunk schema
    
    Raj creates these, but you define the structure!
    """
    chunk_id: str
    story_id: str
    chapter: int
    para_idx: int
    text: str
    word_count: int
    char_position: int


class ChunkWithEmbeddingSchema(pw.Schema):
    """Chunk with embedding"""
    chunk_id: str
    story_id: str
    chapter: int
    para_idx: int
    text: str
    word_count: int
    char_position: int
    embedding: list  # 768-dim vector


class RetrievalResultSchema(pw.Schema):
    """Retrieved evidence"""
    chunk_id: str
    story_id: str
    text: str
    similarity_score: float
    chapter: int


class ReasoningResultSchema(pw.Schema):
    """LLM reasoning output"""
    story_id: str
    decision: int  # 0 or 1
    reasoning: str
    confidence: float
    evidence_used: list