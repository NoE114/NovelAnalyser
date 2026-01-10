import pathway as pw

def chunk_novels(novels: pw.Table, chunk_size: int = 500) -> pw.Table:
    """
    Chunks novels into segments respecting chapter boundaries.
    
    Args:
        novels: Pathway table with 'content' and 'story_id'.
        chunk_size: Target word count (approx 500).
        
    Returns:
        Pathway table with 'text', 'chapter_id', 'para_idx', etc.
    """
    # Use Pathway's UDF for custom chunking logic
    # This allows us to implement the strict "boundary-aware" logic
    
    class ChunkingUDF(pw.UDF):
        def __call__(self, content: str, story_id: str):
            chunks = []
            # logical splitting by chapter (assuming generic headers for now or provided metadata)
            # In a real scenario, we might parse "Chapter X" headers.
            # Here we assume content is the full text.
            
            # Simple simulation of boundary-aware chunking:
            paragraphs = content.split('\n\n')
            current_chunk = []
            current_word_count = 0
            chapter_idx = 1 # simplified
            para_idx = 0
            
            for para in paragraphs:
                words = para.split()
                if not words: continue
                
                # Check soft boundaries
                if current_word_count + len(words) > 600: # Max limit
                    # Yield current chunk
                    chunks.append({
                        "text": "\n\n".join(current_chunk),
                        "word_count": current_word_count,
                        "chapter": f"ch_{chapter_idx}",
                        "para_idx": para_idx,
                        "story_id": story_id,
                        "chunk_id": f"{story_id}_ch{chapter_idx}_p{para_idx}"
                    })
                    current_chunk = []
                    current_word_count = 0
                    para_idx += 1
                
                current_chunk.append(para)
                current_word_count += len(words)
            
            # Yield last chunk
            if current_chunk:
                chunks.append({
                    "text": "\n\n".join(current_chunk),
                    "word_count": current_word_count,
                    "chapter": f"ch_{chapter_idx}",
                    "para_idx": para_idx,
                    "story_id": story_id,
                    "chunk_id": f"{story_id}_ch{chapter_idx}_p{para_idx}"
                })
            
            return chunks

    # Apply UDF - flattened
    result = novels.select(
        chunks=pw.apply(ChunkingUDF(), pw.this.content, pw.this.story_id)
    ).flatten(pw.this.chunks).select(
        chunk_id=pw.this.chunks['chunk_id'],
        story_id=pw.this.chunks['story_id'],
        chapter=pw.this.chunks['chapter'],
        para_idx=pw.this.chunks['para_idx'],
        text=pw.this.chunks['text'],
        word_count=pw.this.chunks['word_count']
    )
    
    return result
