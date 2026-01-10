"""
CORE PATHWAY APPLICATION
Blezecon's responsibility

This is the SPINE of the entire system.
Wires: ingestion → chunking → index → retrieval → reasoning
"""
import pathway as pw
from typing import Optional
import yaml

from .schema import RawNovelSchema, ChunkSchema, ReasoningResultSchema
from .index import PathwayVectorIndex
from .chunking import chunk_novels
from .retrieval import retrieve_evidence
from .reasoner import reason_with_llm
from src.reasoning_validation.validation import Validator
from src.reasoning_validation.schemas import ClassificationResult


class NovelAnalyzerApp:
    """
    Main Pathway application
    
    This is the CORE data processing pipeline.
    All team members plug their logic into this app.
    """
    
    def __init__(self, config_path: str = "configs/system_rules.yaml"):
        """Initialize Pathway app with config"""
        print("🚀 Initializing Novel Analyzer Pathway App...")
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✅ Config loaded from {config_path}")
        
        # Initialize components
        self.vector_index = PathwayVectorIndex(self.config['retrieval']) # Adjusted config key
        self.validator = Validator(self.config)
        
        print("✅ Pathway app ready!")
    
    def build_pipeline(self):
        """
        Build the complete Pathway dataflow pipeline
        
        This is where you WIRE everything together!
        
        Flow:
        1. Ingest novels (YOU)
        2. Chunk novels (Raj's logic, but YOU call it)
        3. Create embeddings (YOU)
        4. Build vector index (YOU)
        5. Retrieve evidence (Raj's logic, but YOU call it)
        6. Reason with LLM (Gopal's logic, but YOU call it)
        7. Validate output (Gopal's logic, but YOU call it)
        """
        print("\n" + "="*60)
        print("🏗️ BUILDING PATHWAY PIPELINE")
        print("="*60)
        
        # ========== STEP 1: INGESTION (YOUR CODE) ==========
        print("\n📚 Step 1: Ingesting novels...")
        novels = self.ingest_novels()
        print(f"  ✅ Ingested novels via Pathway")
        
        # ========== STEP 2: CHUNKING (Raj'S LOGIC) ==========
        print("\n✂️ Step 2: Chunking novels...")
        chunks = chunk_novels(
            novels, 
            chunk_size=self.config['chunking']['chunk_size']
        )
        print(f"  ✅ Chunks created (Raj's logic)")
        
        # ========== STEP 3: EMBEDDINGS (YOUR CODE) ==========
        print("\n🔢 Step 3: Creating embeddings...")
        chunks_with_embeddings = self.vector_index.embed_chunks(chunks)
        print(f"  ✅ Embeddings created")
        
        # ========== STEP 4: INDEX (YOUR CODE) ==========
        print("\n📇 Step 4: Building vector index...")
        indexed_chunks = self.vector_index.build_index(chunks_with_embeddings)
        print(f"  ✅ Vector index built")
        
        # Store for later use
        self.indexed_chunks = indexed_chunks
        
        print("\n" + "="*60)
        print("✅ PATHWAY PIPELINE BUILT")
        print("="*60)
        
        return indexed_chunks
    
    def ingest_novels(self) -> pw.Table:
        """
        Ingest novels using Pathway (Stub for Windows)
        YOUR RESPONSIBILITY
        
        Returns:
            Pathway table (or Mock) with novels
        """
        input_path = self.config['pathway']['input_folder']
        
        # Check if Pathway is real or stub
        is_windows_mode = False
        try:
            _ = pw.io.fs.read
        except AttributeError:
            is_windows_mode = True
            
        if is_windows_mode:
            print("⚠️  WINDOWS MODE DETECTED: Bypassing Pathway Engine...")
            # Manual Ingestion Logic
            import glob
            import os
            from src.pathway_pipeline.udfs import parse_file_content
            
            data_rows = []
            files = glob.glob(os.path.join(input_path, "*"))
            print(f"  📂 Found {len(files)} files in {input_path}")
            
            for file_path in files:
                fname = os.path.basename(file_path)
                if not (fname.endswith('.txt') or fname.endswith('.csv')): 
                    continue
                    
                story_id = self._extract_story_id(file_path)
                try:
                    with open(file_path, 'rb') as f:
                        raw_bytes = f.read()
                    content_str = parse_file_content(raw_bytes, file_path)
                    data_rows.append({"story_id": story_id, "content": content_str})
                    print(f"    - Ingested: {fname}")
                except Exception as e:
                    print(f"    - Error reading {fname}: {e}")
            
            # Create a Mock Table that behaves like Pathway Table for select/apply
            class MockTable:
                def __init__(self, data): self.data = data
                def select(self, **kwargs): return self # Simplification
                def __iter__(self): return iter(self.data) # Make iterable
                
            return MockTable(data_rows)

        # Standard Pathway Logic (Linux/Docker)
        # Import UDF from global module (pickling safe)
        from src.pathway_pipeline.udfs import parse_file_content

        # Use Pathway's file connector
        novels = pw.io.fs.read(
            path=input_path,
            format='binary',
            mode='static',
            with_metadata=True
        )
        
        # Transform to your schema with Multi-format parsing
        novels = novels.select(
            story_id=pw.this.path.apply(self._extract_story_id),
            content=pw.apply(parse_file_content, pw.this.data, pw.this.path)
        )
        
        return novels
    
    def _extract_story_id(self, filepath: str) -> str:
        """Extract story ID from filepath handling multiple extensions"""
        import os
        filename = os.path.basename(filepath)
        # Remove common extensions
        clean_name = filename.replace('novel_', '')
        for ext in ['.txt', '.pdf', '.csv']:
            clean_name = clean_name.replace(ext, '')
        return clean_name
    
    def query(self, story_id: str, backstory: str) -> dict:
        """
        Query the system for consistency check
        
        This is called by Raj's orchestration layer!
        
        Args:
            story_id: Novel to check
            backstory: Hypothetical backstory
            
        Returns:
            Result dict with decision and reasoning
        """
        print(f"\n🔍 Processing query for story {story_id}...")
        
        # ========== STEP 5: RETRIEVAL (Raj'S LOGIC) ==========
        print("  📖 Retrieving evidence...")
        evidence_chunks = retrieve_evidence(
            query=backstory,
            indexed_chunks=self.indexed_chunks,
            story_id=story_id,
            top_k=self.config['retrieval']['top_k']
        )
        print(f"  ✅ Retrieved {len(evidence_chunks)} chunks")
        
        # ========== STEP 6: REASONING (GOPAL'S LOGIC) ==========
        print("  🧠 Reasoning with LLM...")
        reasoning_result = reason_with_llm(
            backstory=backstory,
            evidence=evidence_chunks,
            config=self.config['reasoning']
        )
        print(f"  ✅ LLM reasoning complete")
        
        # ========== STEP 7: VALIDATION (GOPAL'S LOGIC) ==========
        print("  ✔️ Validating output...")
        validated_result = self.validator.validate_classification(
            reasoning_result,
            retrieved_context=evidence_chunks
        )
        print(f"  ✅ Validation complete. Status: {validated_result.status}")
        
        return validated_result.model_dump()
    
    def run_service(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Run Pathway as a service (optional)
        YOUR RESPONSIBILITY
        """
        print(f"\n🌐 Starting Pathway service on {host}:{port}...")
        
        # Use Pathway's REST connector
        # This allows external systems to query your pipeline
        
        # TODO: Implement REST service if needed
        pass
    
    def save_snapshot(self, output_path: str):
        """
        Save Pathway state for reproducibility
        YOUR RESPONSIBILITY
        
        Args:
            output_path: Where to save snapshot
        """
        print(f"\n💾 Saving Pathway snapshot to {output_path}...")
        
        # Use Pathway's snapshot feature
        # This ensures reproducibility
        
        # TODO: Implement snapshot logic
        pass


# ========== MAIN ENTRYPOINT ==========

def run_app(config_path: str = "configs/pathway.yaml"):
    """
    Run the Pathway application
    
    This is called by scripts/build_index.py
    and by Raj's orchestration layer!
    """
    app = NovelAnalyzerApp(config_path)
    app.build_pipeline()
    return app


if __name__ == "__main__":
    # For testing
    app = run_app()
    print("\n✅ Pathway app running!")