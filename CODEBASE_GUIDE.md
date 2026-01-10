# 🗺️ Novel Analyser Codebase Guide

This document maps the entire codebase, explaining the role of each file and its core functions.

---

## 📂 Project Structure

### 1. **Root Directory**
*   **`.env`**: Stores secret keys (e.g., `GROQ_API_KEY`).
*   **`README.md`**: The main entry point for the project, explaining how to run it.
*   **`presentation_script.md`**: A dialogue script for the team to present the solution.
*   **`CODEBASE_GUIDE.md`** (This file): Technical documentation of files and functions.

---

### 2. **Scripts (`scripts/`)**
User-facing entry points to run the system.

*   **`build_index.py`**
    *   **Purpose**: Bootstraps the pipeline to ingest data and build the vector index.
    *   **Key Function**: `main()` - Initializes `NovelAnalyzerApp` and triggers the pipeline build.
*   **`generate_predictions.py`**
    *   **Purpose**: The actual "Exam" script. Reads `test.csv`, queries the system updates `output.csv`.
    *   **Key Function**: `main()` - Iterates through test rows, calls `app.query()`, and results 0 (False) or 1 (True).

---

### 3. **Pathway Pipeline (`src/pathway_pipeline/`)**
The "Nervous System" handling data ingestion and processing. Note: Contains a **Windows Shim** compatibility layer.

*   **`app.py`** (The Orchestrator)
    *   **Role**: Central hub that connects Ingestion → Embedding → Indexing → Retrieval → Reasoning.
    *   **Key Functions**:
        *   `ingest_novels()`: **Crucial**. Detects if running on Windows. If yes, uses a Python Shim to read `.txt/.csv` files using `glob`. If Linux, uses Pathway engine.
        *   `build_pipeline()`: Wires up the dataflow steps.
        *   `query(story_id, backstory)`: The main API called by the prediction script. Triggers retrieval + reasoning + validation.

*   **`udfs.py`** (User Defined Functions)
    *   **Role**: Standalone functions for data processing.
    *   **Key Functions**:
        *   `parse_file_content(data, path)`: Decodes bytes from .txt or .csv files into string variables.
        *   `chunk_text(content, ...)`: Splits long text into 400-600 word semantic chunks.

*   **`index.py`**
    *   **Role**: Manages Vector Embeddings.
    *   **Key Function**: `embed_chunks()` - Uses `SentenceTransformer` to convert text chunks into vector lists.

*   **`retrieval.py`**
    *   **Role**: Logic for finding relevant text.
    *   **Key Function**: `retrieve_evidence(query, top_k)` - Searches the index and enforces "Diversity Rules" (fetching from multiple chapters).

*   **`chunking.py`**
    *   **Role**: Contains the original chunking logic (now wrapped by `udfs.py` for Serialization).

---

### 4. **Reasoning & Validation (`src/reasoning_validation/`)**
The "Brain" and "Judge" of the system.

*   **`reasoner.py`**
    *   **Role**: Interacts with the LLM (Groq/Llama-3).
    *   **Key Function**: `reason_with_llm(backstory, evidence)` - Sends a strictly constrained prompt to the AI, forcing it to output a JSON `ReasoningTrace` citing specific evidence.

*   **`validation.py`**
    *   **Role**: The Governance Layer.
    *   **Key Function**: `Validator.validate_classification()` - Checks the LLM's work.
        *   Verifies quotes exist verbatim in the source text.
        *   Checks confidence score > 0.4.
        *   Returns `SUCCESS` or `REJECT`.

*   **`schemas.py`**
    *   **Role**: Defines strict Data structures.
    *   **Key Classes**: `RawNovelSchema`, `EvidenceSpan`, `ReasoningTrace`. Ensures data integrity passed between modules.

---

### 5. **Configuration (`configs/`)**
*   **`system_rules.yaml`**: The "God Config". Controls every threshold (chunk size, retrieval count, confidence limits) in one place.
