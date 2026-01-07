# Pathway Pipeline: Novel Analyzer

## Overview

The `pathway_pipeline` folder contains the **CORE data processing pipeline** for the Novel Analyzer system. It uses **Pathway**, a real-time data processing framework, to orchestrate the complete consistency checking workflow for novels.

This is the **SPINE** of the entire system that wires together all components: ingestion → chunking → indexing → retrieval → reasoning → validation.

---

## Architecture

### Data Flow Pipeline

```
┌─────────────────────┐
│  1. INGESTION       │  Read novels from disk
│  (YOUR CODE)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. CHUNKING        │  Split into manageable chunks
│  (Sarvan)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. EMBEDDINGS      │  Create vector representations
│  (YOUR CODE)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. INDEXING        │  Build searchable index
│  (YOUR CODE)        │
└──────────┬──────────┘
           │
           ├──────────────────────────────────────┐
           │                                      │
           │    Query                             │
           │    (from external system)            │
           │                                      │
           ▼                                      ▼
┌─────────────────────────────────────────────────────────┐
│  5. RETRIEVAL        │  Find relevant evidence chunks    │
│  (Sarvan)            │  (Uses vector similarity search)  │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  6. REASONING       │  LLM analyzes consistency
│  (Gopal)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  7. VALIDATION      │  Verify reasoning quality
│  (Gopal)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RESULT             │  Decision + reasoning
│                     │
└─────────────────────┘
```

---

## Module Breakdown

### 1. **app.py** - Main Orchestrator
**Responsibility:** Blezecon (Pipeline Orchestration)

The central hub that wires all components together.

**Key Classes:**
- `NovelAnalyzerApp`: Main Pathway application

**Key Methods:**
- `__init(config_path)`: Initialize with configuration
- `build_pipeline()`: Build the complete dataflow pipeline (steps 1-4)
- `ingest_novels()`: Read novels using Pathway file connector
- `query(story_id, backstory)`: Execute a consistency check (steps 5-7)
- `run_service()`: Run as REST API (optional)
- `save_snapshot()`: Save Pathway state for reproducibility

**Responsibilities:**
- Load configuration from `configs/pathway.yaml`
- Call chunking, embedding, and indexing functions in sequence
- Handle query execution through the pipeline
- Integrate all team members' modules

**Entry Point:**
```python
from src.pathway_pipeline.app import run_app

app = run_app(config_path="configs/pathway.yaml")
```

---

### 2. **index.py** - Vector Indexing
**Responsibility:** Blezecon (Vector Operations)

Manages embeddings and similarity search.

**Key Classes:**
- `PathwayVectorIndex`: Vector index operations

**Key Methods:**
- `__init(config)`: Load embedding model (e.g., SentenceTransformer)
- `embed_chunks(chunks)`: Convert text chunks to embeddings
- `build_index(chunks_with_embeddings)`: Create searchable index
- `search(query, indexed_chunks, top_k)`: Find similar chunks

**What It Does:**
1. Loads a pre-trained embedding model (configured in `configs/pathway.yaml`)
2. Converts all novel chunks into 768-dimensional vectors
3. Provides similarity search functionality for queries
4. Uses cosine similarity to rank chunks by relevance

**Configuration (from configs/pathway.yaml):**
```yaml
embeddings:
  model: "all-MiniLM-L6-v2"  # SentenceTransformer model
  dimension: 384              # Embedding vector dimension
  batch_size: 32              # Batch size for embedding
```

---

### 3. **schema.py** - Data Schemas
**No Single Owner** (Defines data structures for entire team)

Defines Pathway table schemas that represent data at each pipeline stage.

**Schemas:**

| Schema | Purpose | Created By | Used By |
|--------|---------|-----------|---------|
| `RawNovelSchema` | Raw novel input (bytes) | Ingestion | - |
| `NovelSchema` | Parsed novel text | Chunking | - |
| `ChunkSchema` | Individual text chunks | Chunking (Sarvan) | Embedding, Indexing |
| `ChunkWithEmbeddingSchema` | Chunks + 768-dim vectors | Embedding | Indexing, Retrieval |
| `RetrievalResultSchema` | Retrieved evidence | Retrieval (Sarvan) | Reasoning (Gopal) |
| `ReasoningResultSchema` | LLM output | Reasoning (Gopal) | API responses |

---

### 4. **service.py** - REST API (Optional)
**Responsibility:** Blezecon (REST Service - Optional)

Exposes the Pathway pipeline as an HTTP REST API for external systems.

**Key Components:**
- `QueryRequest`: Input model for consistency checks
- `QueryResponse`: Output model with results
- `HealthResponse`: Service health status
- FastAPI application with endpoints

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/query` | Submit consistency check query |
| GET | `/stories` | List available stories |
| GET | `/story/{story_id}/metadata` | Get story metadata |

**Usage Example:**
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "1",
    "backstory": "Character grew up in Chicago...",
    "top_k": 15
  }'
```

**Running the Service:**
```python
from src.pathway_pipeline.service import create_pathway_service

create_pathway_service(host="0.0.0.0", port=8080)
```

---

### 5. **Missing Modules** (To Be Implemented by Team)

The following modules are imported in `app.py` but not yet created:

#### **chunking.py** - Text Chunking
**Owner:** Sarvan

**Expected Function:**
```python
def chunk_novels(novels: pw.Table, chunk_size: int) -> pw.Table:
    """
    Split novels into overlapping chunks
    
    Input: RawNovelSchema or NovelSchema
    Output: ChunkSchema (with chunk_id, story_id, chapter, para_idx, text, word_count, char_position)
    """
```

**Configuration:**
```yaml
chunking:
  chunk_size: 512  # Tokens per chunk
  overlap: 50      # Overlap between chunks
```

---

#### **retrieval.py** - Evidence Retrieval
**Owner:** Sarvan

**Expected Function:**
```python
def retrieve_evidence(
    query: str,
    indexed_chunks: pw.Table,
    story_id: str,
    top_k: int = 15
) -> List[dict]:
    """
    Find most relevant chunks for a query using vector similarity
    
    Input: Query text, indexed chunks
    Output: List of top-k RetrievalResultSchema
    """
```

Uses the `PathwayVectorIndex.search()` method internally.

---

#### **reasoner.py** - LLM Reasoning
**Owner:** Gopal

**Expected Function:**
```python
def reason_with_llm(
    backstory: str,
    evidence: List[dict],
    config: dict
) -> dict:
    """
    Use LLM to reason about consistency
    
    Input: Hypothetical backstory, retrieved evidence chunks
    Output: ReasoningResultSchema with decision, reasoning, confidence
    
    Returns:
        {
            "decision": 1 or 0,  # 1=consistent, 0=inconsistent
            "reasoning": "...",
            "confidence": 0.85,
            "evidence_used": [...]
        }
    """
```

**Configuration:**
```yaml
reasoning:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 1000
```

---

#### **validation.py** - Output Validation
**Owner:** Gopal

**Expected Function:**
```python
def validate_output(
    reasoning_result: dict,
    min_evidence: int = 3
) -> dict:
    """
    Validate LLM reasoning quality
    
    Input: ReasoningResultSchema
    Output: Validated result
    
    Checks:
    - Sufficient evidence chunks used
    - Reasoning quality
    - Confidence score validity
    """
```

**Configuration:**
```yaml
validation:
  min_evidence: 3      # Minimum chunks for valid result
  min_confidence: 0.5  # Minimum confidence score
```

---

## Configuration File

The pipeline is configured via `configs/pathway.yaml`:

```yaml
pathway:
  input_folder: "data/raw/"
  output_folder: "data/output/"

embeddings:
  model: "all-MiniLM-L6-v2"
  dimension: 384
  batch_size: 32

chunking:
  chunk_size: 512
  overlap: 50

retrieval:
  top_k: 15
  similarity_threshold: 0.3

reasoning:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 1000

validation:
  min_evidence: 3
  min_confidence: 0.5
```

---

## How It All Works

### **Phase 1: Build Pipeline (Offline)**

```python
from src.pathway_pipeline.app import run_app

# 1. Initialize
app = NovelAnalyzerApp(config_path="configs/pathway.yaml")

# 2. Build pipeline (processes all novels once)
indexed_chunks = app.build_pipeline()
#
# This executes:
# - Load novels from data/raw/
# - Chunk into smaller pieces (Sarvan's code)
# - Create embeddings for each chunk
# - Build searchable index
# - Save indexed data for queries
```

This happens once at startup (called by `scripts/build_index.py`).

---

### **Phase 2: Query Pipeline (Online)**

```python
# External system (Raj's orchestration) calls:
result = app.query(
    story_id="novel_1",
    backstory="Character grew up in Chicago..."
)

# Returns:
{
    "story_id": "novel_1",
    "decision": 1,  # 0=inconsistent, 1=consistent
    "reasoning": "The backstory is consistent with...",
    "confidence": 0.92,
    "evidence_used": [
        {"chunk_id": "...", "text": "...", "chapter": 3},
        ...
    ]
}
```

For each query:
1. **Retrieval** (Sarvan): Find relevant chunks using vector search
2. **Reasoning** (Gopal): Ask LLM if backstory is consistent with evidence
3. **Validation** (Gopal): Verify reasoning quality
4. Return decision to external system

---

## Team Responsibilities

| Team Member | Responsibility | Files |
|-------------|-----------------|-------|
| **Blezecon** | Pipeline orchestration, vector indexing | `app.py`, `index.py`, `service.py` |
| **Sarvan** | Chunking, retrieval | `chunking.py` (create), `retrieval.py` (create) |
| **Gopal** | LLM reasoning, validation | `reasoner.py` (create), `validation.py` (create) |
| **Raj** | External orchestration | (separate repo) |

---

## Key Features

✅ **Streaming-Ready**: Pathway processes data as streams, enabling real-time updates  
✅ **Modular**: Each team member plugs their logic into the pipeline  
✅ **Reproducible**: Pathway snapshots ensure consistent results  
✅ **Scalable**: REST API allows external systems to query  
✅ **Type-Safe**: Strict Pathway schemas prevent data mismatches  
✅ **Traceable**: Each step logs progress for debugging  

---

## Usage Examples

### Run the Complete Pipeline

```bash
python scripts/build_index.py
```

This:
1. Initializes the Pathway app
2. Loads all novels from `data/raw/`
3. Chunks them (Sarvan's logic)
4. Creates embeddings
5. Builds the index
6. Saves indexed data

### Query the Pipeline

```python
from src.pathway_pipeline.app import run_app

app = run_app()
result = app.query(
    story_id="novel_1",
    backstory="Protagonist was born in France"
)

print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

### Run as REST API

```bash
python -m src.pathway_pipeline.service
```

Then make HTTP requests:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"story_id": "1", "backstory": "..."}'
```

---

## Data Directories

| Directory | Purpose |
|-----------|---------|
| `data/raw/` | Input novels (text files) |
| `data/index/` | Indexed chunks (embedding vectors) |
| `data/metadata/` | Novel metadata (chapters, word count, etc.) |

---

## Dependencies

- **pathway**: Real-time data processing framework
- **sentence-transformers**: Embedding model
- **fastapi**: REST API framework (optional, for service.py)
- **pydantic**: Data validation for API requests
- **uvicorn**: ASGI server (optional, for service.py)
- **yaml**: Configuration parsing

Install via: `pip install pathway sentence-transformers fastapi pydantic uvicorn pyyaml`

---

## Notes for Team Members

**For Sarvan (Chunking & Retrieval):**
- Your `chunk_novels()` function receives a Pathway table and returns one with `ChunkSchema`
- Your `retrieve_evidence()` function calls `PathwayVectorIndex.search()` and formats results
- Both functions are called by `app.py`, you don't need to modify it

**For Gopal (Reasoning & Validation):**
- Your `reason_with_llm()` function receives evidence chunks and uses an LLM
- Your `validate_output()` function checks the quality of LLM output
- Both functions are called by `app.py`, you don't need to modify it

**For Blezecon (Pipeline Core):**
- You own the orchestration logic in `app.py`
- You implement embedding and indexing in `index.py`
- Optionally implement the REST service in `service.py`
- The pipeline calls everyone else's functions in the right sequence

---

## Future Enhancements

- [ ] Pure Pathway sorting (currently uses Python extraction in `index.py`)
- [ ] Snapshot saving for reproducibility
- [ ] Story metadata listing endpoint
- [ ] Batch query processing
- [ ] Query result caching
- [ ] Performance monitoring and logging

---

**Last Updated:** January 2026  
**Status:** In Development (chunking, retrieval, reasoner, validation modules pending)
