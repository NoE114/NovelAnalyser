# Systems Reasoning with NLP: Codebase Walkthrough Script

**Cast:**
*   **A (Raj)**: System Lead & Architect. Focuses on the "Why" and Governance.
*   **B (Dipendu)**: Pathway Engineer. Focuses on the "How" – Ingestion and Compatibility.
*   **C (Gopal)**: Reasoning Specialist. Focuses on the "Logic" – LLM Validation and Binary Output.

---

### **Intro & The "Why"**

**A (Raj)**: "Hi everyone! We are presenting our solution for the 'Systems Reasoning' track: the **Novel Analyser**. We set out to solve a specific problem: LLMs hallucinate when analyzing long texts. Our goal was to build a **Deterministic Reasoning Engine** that verifies claims with true/false binary precision, regardless of the platform."

**A (Raj)**: "As the System Lead, I defined a strict governance architecture. We prioritized flexibility. Whether you are on Linux or Windows, the system must enforce the same rigorous logic. If the AI can't quote the text verbatim, the system outputs '0' (False). Correctness > Consistency."

### **The Data Backbone (The "How")**

**B (Dipendu)**: "Exactly. I built the data nervous system. Let me walk you through `src/pathway_pipeline`."

**B (Dipendu)**: "First, for **Ingestion**, I built a **Universal Text Ingestor** in `app.py`. It monitors our `data/raw` folder. It automatically detects `.txt` and `.csv` files. Crucially, I implemented a **Windows Compatibility Shim**. If the Pathway engine detects it's running on a Windows local machine, it switches to a native Python mode, ensuring the pipeline runs anywhere without complex Docker setups."

**B (Dipendu)**: "For **Chunking**, I used `udfs.py` to create 400-600 word semantic chunks. Even in 'Windows Mode', we preserve strict paragraph boundaries to ensure causal chains aren't broken."

**B (Dipendu)**: "Finally, for **Retrieval**, my module in `retrieval.py` enforces a 'Diversity Filter'. We ensure evidence comes from at least 3 distinct chapters, preventing the model from fixating on a single scene."

### **Reasoning & Validation (The "Logic")**

**C (Gopal)**: "Right, and once Dipendu's pipeline hands me those verified chunks, my **Reasoning Module** takes over. My job is to verify specific claims from `test.csv`."

**C (Gopal)**: "In `reasoner.py`, I use the Groq API driving Llama-3, wrapped in strict **Pydantic Schemas**. The model must output a `ReasoningTrace` with specific `EvidenceSpan` citations. It can't just say 'Yes'; it must prove it."

**C (Gopal)**: "Then comes the **Validation Layer**. In `validation.py`, I code-check those quotes against the original text. If the quote isn't exact, or confidence < 0.4, we reject the claim. In our final `generate_predictions.py` script, this rejection is converted to a simple '0', and a valid verification is a '1'. This gives us the clean binary CSV output required."

### **Conclusion**

**A (Raj)**: "So, to wrap up: We combined **Universal Data Handling** (Dipendu) with a rigorous **Verification Layer** (Gopal). The result is a robust system that runs natively on your machine and outputs verified 1s and 0s based on hard evidence. Thanks for listening!"
