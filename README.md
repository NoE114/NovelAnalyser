# Repository File Structure aligned to the 4-Player plan

This layout enforces orthogonal lanes that integrate cleanly. Each Player owns a directory with clear deliverables. The orchestrator ties them together under Player 1’s authority.

```text
novel-retrieval-system/
├─ README.md                               # quick start, constraints, lane ownership
├─ pyproject.toml                          # package + tooling config (prefer Poetry or PDM)
├─ requirements.txt                        # pinned deps (Pathway, embeddings, LLM SDK)
├─ .pre-commit-config.yaml                 # lint/format/type checks for determinism
├─ .env.example                            # environment variables template
├─ Makefile                                # reproducible targets (setup, index, query, evaluate)

├─ configs/                                # single source of truth for knobs (no hardcoding)
│  ├─ system_rules.yaml                    # Player 1: chunking + retrieval + reasoning rules
│  ├─ pathway.yaml                         # Player 2: ingestion paths, schema, index params
│  ├─ retrieval.yaml                       # Player 3: top-k, chapter diversity, tie-breakers
│  └─ models.yaml                          # Player 4: model choices, temperature, limits

├─ docs/                                   # judge-facing explanations and artifacts
│  ├─ system_overview.md                   # Player 1: architecture + justification
│  ├─ judges_explanation.md                # Player 1: final narrative + evidence of rigor
│  └─ system_diagram.png                   # Player 1: diagram (data spine → retrieval → LLM)

├─ data/                                   # deterministic, versioned data areas (no ad-hoc writes)
│  ├─ raw/                                 # input novels (text + metadata CSV/JSON)
│  ├─ processed/                           # Player 3: 400–600 word chunks w/ chapter + paragraph
│  ├─ index/                               # Player 2: Pathway-managed vector indexes
│  └─ samples/                             # small fixtures for CI tests and demos

├─ src/                                    # production code, orthogonal lanes
│  ├─ orchestration/                       # Player 1: integrates lanes, enforces rules
│  │  ├─ integrate.py                      # end-to-end pipeline runner (strict sequence 1→5)
│  │  └─ policies.py                       # guardrails: allowed LLM actions vs Python checks
│  │
│  ├─ pathway_pipeline/                    # Player 2: data spine + index inside Pathway
│  │  ├─ ingestion.py                      # load novels + metadata into Pathway
│  │  ├─ schema.py                         # typed records: chapter, para_idx, text, ids
│  │  ├─ vector_index.py                   # Pathway embeddings + index build/search
│  │  └─ determinism.py                    # reproducibility hooks (seeds, hashes, manifests)
│  │
│  ├─ chunking_retrieval/                  # Player 3: long-context chunking + retrieval logic
│  │  ├─ chunker.py                        # 400–600 word chunks, preserve boundaries/context
│  │  ├─ boundaries.py                     # paragraph/chapter boundary handling + fallbacks
│  │  ├─ retrieval.py                      # top-k, chapter diversity enforcement, ranking
│  │  └─ evidence_grouping.py              # grouped evidence sets (not just top similarity)
│  │
│  ├─ reasoning_validation/                # Player 4: LLM prompts + Python validators
│  │  ├─ prompts/
│  │  │  ├─ base_prompt.md                 # strict reasoning template: quotes, alts, confidence
│  │  │  └─ verification_prompt.md         # optional sequential verification / cross-check
│  │  ├─ reasoner.py                       # call LLM(s), produce constrained JSON
│  │  ├─ validation.py                     # Python checks: min evidence, contradictions, rejects
│  │  └─ outputs.py                        # JSON schema + serialization utilities
│  │
│  └─ utils/                               # shared utilities (thin; no lane leakage)
│     ├─ logging.py                        # structured logs for pipeline + retrieval + LLM
│     ├─ io.py                             # file manifests, content hashing, safe writes
│     └─ types.py                          # dataclasses/pydantic models for strong typing

├─ schemas/                                # explicit contracts for I/O and LLM outputs
│  └─ answer.schema.json                   # Player 4: output schema (quotes, alts, confidence)

├─ scripts/                                # CLI entrypoints (deterministic order; no notebooks)
│  ├─ build_index.py                       # 2: ingest → chunk (optional pre) → index build
│  ├─ query.py                             # 3→4: retrieve evidence → reason → validate → JSON
│  └─ evaluate.py                          # reproducible eval over samples; exports metrics

└─ tests/                                  # CI tests aligned to failure conditions
   ├─ test_pipeline.py                     # Player 2: ingestion correctness, schema fidelity
   ├─ test_chunking.py                     # Player 3: boundaries preserved, target lengths
   ├─ test_retrieval.py                    # diversity enforced, stable top-k, ranking sanity
   └─ test_validation.py                   # Player 4: rejects weak answers, contradiction flags
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
