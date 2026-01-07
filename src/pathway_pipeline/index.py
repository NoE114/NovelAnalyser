"""
Vector index in Pathway
Blezecon's responsibility
"""
import pathway as pw
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

from .schema import ChunkSchema, ChunkWithEmbeddingSchema


class PathwayVectorIndex:
    """
    Vector index using Pathway
    """
    
    def __init__(self, config: dict):
        self.model_name = config['model']
        self.dimension = config['dimension']
        self.batch_size = config['batch_size']
        
        print(f"🔧 Loading embedding model: {self.model_name}...")
        self.embedding_model = SentenceTransformer(self.model_name)
        print(f"  ✅ Model loaded")
    
    def embed_chunks(self, chunks: pw.Table) -> pw.Table:
        """
        Add embeddings to chunks using Pathway
        
        Args:
            chunks: Pathway table with ChunkSchema
            
        Returns:
            Pathway table with ChunkWithEmbeddingSchema
        """
        # Use Pathway's UDF to create embeddings
        def create_embedding(text: str) -> list:
            embedding = self.embedding_model.encode([text])[0]
            return embedding.tolist()
        
        # Apply embedding to each chunk
        chunks_with_embeddings = chunks.select(
            chunk_id=pw.this.chunk_id,
            story_id=pw.this.story_id,
            chapter=pw.this.chapter,
            para_idx=pw.this.para_idx,
            text=pw.this.text,
            word_count=pw.this.word_count,
            char_position=pw.this.char_position,
            embedding=pw.apply(create_embedding, pw.this.text)
        )
        
        return chunks_with_embeddings
    
    def build_index(self, chunks_with_embeddings: pw.Table) -> pw.Table:
        """
        Build searchable vector index
        
        Args:
            chunks_with_embeddings: Pathway table with embeddings
            
        Returns:
            Indexed table ready for search
        """
        # In Pathway, the table IS the index
        # No separate data structure needed!
        
        # Optionally add metadata or optimization here
        
        return chunks_with_embeddings
    
    def search(
        self, 
        query: str, 
        indexed_chunks: pw.Table,
        top_k: int = 15
    ) -> List[dict]:
        """
        Search for similar chunks
        
        Args:
            query: Search query
            indexed_chunks: Indexed Pathway table
            top_k: Number of results
            
        Returns:
            List of top-k chunks
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarities using Pathway
        def compute_similarity(embedding: list) -> float:
            embedding_np = np.array(embedding)
            return float(np.dot(embedding_np, query_embedding))
        
        # Add similarity scores
        scored_chunks = indexed_chunks.select(
            **pw.this.__dict__,
            similarity=pw.apply(compute_similarity, pw.this.embedding)
        )
        
        # Sort by similarity (Pathway will handle this efficiently)
        # For now, we'll extract to Python for simplicity
        # In production, you'd use Pathway's native operations
        
        # TODO: Implement pure Pathway sorting
        
        return scored_chunks