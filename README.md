# Repository File Structure aligned to the 4-Player plan

This layout enforces orthogonal lanes that integrate cleanly. Each Player owns a directory with clear deliverables. The orchestrator ties them together under Player 1’s authority.

```text
NovelAnalyzer/
├─ README.md
│   # Raj — System Lead
│   # Project rules, how to run, what is in/out of scope

├─ pyproject.toml
├─ requirements.txt
├─ .env
├─ .pre-commit-config.yaml
├─ Makefile
│   # Raj — enforcement + reproducibility

├─ configs/
│  ├─ system_rules.yaml
│  │   # Raj — GLOBAL AUTHORITY
│  │   # Chunking rules, retrieval rules, reasoning + validation constraints
│  │
│  ├─ pathway.yaml
│  │   # Dipendu — Pathway configuration
│  │   # Tables, connectors, index params, snapshot settings
│  │
│  ├─ retrieval.yaml
│  │   # Sarvan — retrieval knobs
│  │   # top-k, diversity rules, fallback behavior
│  │
│  └─ models.yaml
│      # Gopal — model usage rules
│      # embedding model, LLM provider, temps, rate limits

├─ docs/
│  ├─ system_overview.md
│  │   # Raj — technical explanation for judges
│  │
│  ├─ judges_explanation.md
│  │   # Raj — narrative explanation (non-technical)
│  │
│  └─ system_diagram.png
│      # Raj — visual pipeline (Pathway → retrieval → reasoning)

├─ data/
│  ├─ raw/
│  │   # Dipendu — input novels + metadata (read-only)
│  │
│  ├─ processed/
│  │   # Sarvan — optional debug chunks (not authoritative)
│  │
│  ├─ index/
│  │   # Dipendu — Pathway snapshot / restore state
│  │
│  └─ samples/
│      # Raj — small fixtures for demos/tests

├─ schemas/
│  └─ answer.schema.json
│      # Raj — STRICT output contract
│      # Classification, quotes, alternatives, confidence

├─ src/
│  ├─ orchestration/
│  │  ├─ integrate.py
│  │  │   # Raj — single entrypoint
│  │  │   # Starts Pathway app, enforces execution order
│  │  │
│  │  └─ policies.py
│  │      # Raj — reads system_rules.yaml
│  │      # Guards what LLM + pipeline are allowed to do
│  │
│  ├─ pathway_app/
│  │  ├─ app.py
│  │  │   # Dipendu — CORE Pathway program
│  │  │   # Wires ingestion → chunking → index → retrieval → reasoning
│  │  │
│  │  ├─ schema.py
│  │  │   # Dipendu — Pathway table schemas
│  │  │
│  │  ├─ chunking.py
│  │  │   # Sarvan — chunking + boundary logic (400–600 words)
│  │  │
│  │  ├─ index.py
│  │  │   # Dipendu — embeddings + vector index/search in Pathway
│  │  │
│  │  ├─ retrieval.py
│  │  │   # Sarvan — ranking + diversity enforcement
│  │  │
│  │  ├─ reasoner.py
│  │  │   # Gopal — LLM calls (schema-bound, no free-form)
│  │  │
│  │  ├─ validation.py
│  │  │   # Gopal — Python veto logic
│  │  │   # min evidence, contradictions, schema enforcement
│  │  │
│  │  ├─ service.py
│  │  │   # Dipendu — optional HTTP ingress/egress
│  │  │
│  │  ├─ prompts/
│  │  │  ├─ base_prompt.md
│  │  │  │   # Gopal — primary reasoning prompt
│  │  │  │
│  │  │  └─ verification_prompt.md
│  │  │      # Gopal — optional cross-check prompt
│  │  │
│  │  └─ README.md
│  │      # Raj — explains Pathway dataflow in plain language
│  │
│  └─ utils/
│     ├─ logging.py
│     │   # Raj — structured logs
│     │
│     ├─ io.py
│     │   # Dipendu — safe reads/writes, hashing
│     │
│     └─ types.py
│         # Raj — shared dataclasses / typing

├─ scripts/
│  ├─ build_index.py
│  │   # Dipendu — batch mode (delegates to Pathway app)
│  │
│  ├─ query.py
│  │   # Gopal — run queries (batch or service)
│  │
│  └─ evaluate.py
│      # Raj — lightweight sanity evaluation

└─ tests/
   ├─ test_pipeline.py
   │   # Dipendu — ingestion + schema invariants
   │
   ├─ test_chunking.py
   │   # Sarvan — chunk size + boundary preservation
   │
   ├─ test_retrieval.py
   │   # Sarvan — diversity + ranking stability
   │
   └─ test_validation.py
       # Gopal — rejects weak or invalid outputs

```

## Ownership and Deliverables

- Player 1 — System Lead
  - `configs/system_rules.yaml`, `src/orchestration/`, `docs/*`
  - Deliverables: rules, final explanation, system diagram, integration script.

- Player 2 — Pathway + Data Pipeline
  - `src/pathway_pipeline/`, `configs/pathway.yaml`, `data/index/`
  - Deliverables: working Pathway pipeline, verified vector search, clean schema.

- Player 3 — Chunking + Retrieval
  - `src/chunking_retrieval/`, `configs/retrieval.yaml`, `data/processed/`
  - Deliverables: chunking script, retrieval module, evidence grouping output.

- Player 4 — LLM Reasoning + Validation
  - `src/reasoning_validation/`, `schemas/answer.schema.json`, `configs/models.yaml`
  - Deliverables: strict prompts, validation logic, clean JSON outputs.

## Workflow Enforcement (1 → 5)

- Orchestrated by `src/orchestration/integrate.py`
  1. Load rules (`system_rules.yaml`)
  2. Build data spine (`pathway_pipeline/*`)
  3. Chunk + retrieve (`chunking_retrieval/*`)
  4. Reason + validate (`reasoning_validation/*`)
  5. Freeze artifacts and produce judge-facing docs (`docs/*`)

## Determinism and Compliance

- Configuration-only tuning (no code edits without Player 1 approval).
- Fixed seeds and content hashing in `determinism.py` and `utils/io.py`.
- Pinned dependencies and CI tests aligned to failure conditions.
- No agents, UI, or end-to-end model roulette—only controlled execution paths via scripts.
