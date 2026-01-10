# Systems Reasoning with NLP: Narrative Classification & Analysis

> **Track A: Systems Reasoning with NLP & Generative AI**
> *Built with Pathway, Groq, and Deterministic Logic*

## 📖 Project Overview
This repository hosts a **Logic-First Narrative Analysis System** designed to classify long-context literary works (**TXT or CSV**) based on character motivation and causal attribution.

Unlike standard RAG pipelines that "guess" answers, this system prioritizes **correctness, evidence, and rejection**. It includes a **Windows Native Compatibility Layer** that bypasses the need for Linux/Docker, running purely on Python/Pandas while mimicking the Pathway dataflow.

### 🎯 Key Objectives
1.  **Evidence-Grounded Reasoning**: No hallucination. Every claim must be backed by verbatim quotes from the text.
2.  **Long-Context Management**: Handling full novels via boundary-aware chunking and diversity-enforced retrieval.
3.  **Strict Governance**: Automated validation layers that reject low-confidence or contradictory outputs.

---

## 🏗️ System Architecture

The system follows a strict **Governance-First Architecture**:

```mermaid
graph TD
    A[Raw Novels (TXT/CSV)] -->|Ingestion Shim| B(Boundary-Aware Chunking)
    B -->|Embeddings| C{Vector Index}
    D[User Query] -->|Deterministic Retrieval| C
    C -->|Evidence Groups| E[Reasoning Engine]
    E -->|Hypothesis Comparison| F(LLM - Groq)
    F -->|JSON Output| G{Validation Layer}
    G -- Pass --> H[Final Classification]
    G -- Fail --> I[Rejection / Feedback]
    
    subgraph "Owned by Dipendu"
    A
    B
    C
    D
    end
    
    subgraph "Owned by Gopal"
    E
    F
    G
    end
    
    subgraph "Owned by Raj"
    H
    I
    end
```

### Core Components
1.  **Data Pipeline** (`src/pathway_pipeline/`):
    - **Universal Ingestion**: Automatically detects `.txt` and `.csv`.
    - **Windows Compatibility**: Uses a native Python shim if Pathway is not installed (Windows).
    - **Likely Function**: `app.ingest_novels` manages the flow.

2.  **Reasoning & Validation** (`src/reasoning_validation/`):
    - **Validator**: Python logic that vetoes LLM outputs if confidence < 0.4 or evidence is insufficient.

---

## 👥 Team & Responsibilities

| Player | Role | Responsibility | Key Files |
| :--- | :--- | :--- | :--- |
| **Raj Dey** | **System Lead** | Global Architecture, Governance Rules | `configs/system_rules.yaml`, `src/pathway_pipeline/app.py` |
| **Dipendu** | **Pathway Engineer** | Data Ingestion (TXT/CSV), Vector Indexing | `src/pathway_pipeline/udfs.py`, `src/pathway_pipeline/retrieval.py` |
| **Gopal Paul** | **Reasoning Logic** | Constraint Prompts, Schema Validation | `src/pathway_pipeline/reasoner.py`, `src/reasoning_validation/` |

---

## 🚀 How to Run (Windows Native)

### 1. Prerequisites
```bash
pip install pathway pydantic groq sentence-transformers pyyaml pandas
export GROQ_API_KEY="your_api_key_here"
```

### 2. Build the Index (Ingest Novels)
Place your files (**.txt** or **.csv**) in `data/raw/` and run:
```bash
python scripts/build_index.py
```
*(Note: on Windows, this will print a "Windows Mode" warning. This is normal.)*

### 3. Generate Predictions (Binary Output)
Process the `data/raw/test.csv` file to verify claims against the indexed novels.
```bash
python scripts/generate_predictions.py
```
*   **Input**: `data/raw/test.csv` (Claims to verify)
*   **Output**: `output.csv` (Columns: `id`, `prediction` [0 or 1])

### 4. Verify Logic (Governance Tests)
Run the isolated logic tests to prove rejection capabilities.
```bash
python tests/verify_logic.py
```
