import io

# WINDOWS COMPATIBILITY LAYER
# We define a dummy decorator if Pathway's one fails or is missing
try:
    import pathway as pw
    udf_decorator = pw.dspy.udf
except (ImportError, AttributeError):
    print("⚠️  WINDOWS MODE: Using Mock UDF Decorator")
    def udf_decorator(func):
        return func

# ==============================================================================
# FILE PARSING UDF (TXT & CSV ONLY)
# ==============================================================================
@udf_decorator
def parse_file_content(data: bytes, path: str) -> str:
    """
    Parses file content. Supports .txt and .csv.
    """
    import io
    ext = path.lower().split('.')[-1]
    
    # CSV Handling
    if ext == 'csv':
        try:
            import pandas as pd
            # Read CSV and dump to string (primitive ingestion)
            df = pd.read_csv(io.BytesIO(data))
            return df.to_string(index=False)
        except Exception:
            return ""
    
    # TXT Handling
    elif ext == 'txt':
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1', errors='replace')
    
    return "" 


# ==============================================================================
# CHUNKING UDF
# ==============================================================================
@udf_decorator
def chunk_text(content: str, story_id: str, chunk_size: int = 500) -> list:
    """
    Splits text into chunks.
    """
    chunks = []
    
    paragraphs = content.split('\n\n')
    current_chunk = []
    current_word_count = 0
    chapter_idx = 1
    para_idx = 0
    
    for para in paragraphs:
        # Crude chapter detection
        if "chapter" in para.lower()[:20]:
            if current_chunk:
                _commit_chunk(chunks, current_chunk, story_id, chapter_idx, para_idx, current_word_count)
                current_chunk = []
                current_word_count = 0
                para_idx = 0
            chapter_idx += 1

        words = para.split()
        if not words: continue
        
        if current_word_count + len(words) > chunk_size:
            _commit_chunk(chunks, current_chunk, story_id, chapter_idx, para_idx, current_word_count)
            current_chunk = []
            current_word_count = 0
            para_idx += 1
        
        current_chunk.append(para)
        current_word_count += len(words)
    
    # Final chunk
    if current_chunk:
         _commit_chunk(chunks, current_chunk, story_id, chapter_idx, para_idx, current_word_count)
    
    return chunks

def _commit_chunk(chunks, content_list, story_id, ch_idx, p_idx, w_count):
    text = "\n\n".join(content_list)
    chunks.append({
        "chunk_id": f"{story_id}_ch{ch_idx}_p{p_idx}",
        "story_id": story_id,
        "chapter": int(ch_idx),
        "para_idx": int(p_idx),
        "text": text,
        "word_count": w_count,
        "char_position": 0 # Placeholder
    })
