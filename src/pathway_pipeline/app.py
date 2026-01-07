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
from .chunking import chunk_novels  # Sarvan writes this
from .retrieval import retrieve_evidence  # Sarvan writes this
from .reasoner import reason_with_llm  # Gopal writes this
from .validation import validate_output  # Gopal writes this


class NovelAnalyzerApp:
    """
    Main Pathway application
    
    This is the CORE data processing pipeline.
    All team members plug their logic into this app.
    """
    
    def __init__(self, config_path: str = "configs/pathway.yaml"):
        """Initialize Pathway app with config"""
        print("🚀 Initializing Novel Analyzer Pathway App...")
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✅ Config loaded from {config_path}")
        
        # Initialize components (your responsibility)
        self.vector_index = PathwayVectorIndex(self.config['embeddings'])
        
        print("✅ Pathway app ready!")
    
    def build_pipeline(self):
        """
        Build the complete Pathway dataflow pipeline
        
        This is where you WIRE everything together!
        
        Flow:
        1. Ingest novels (YOU)
        2. Chunk novels (Sarvan's logic, but YOU call it)
        3. Create embeddings (YOU)
        4. Build vector index (YOU)
        5. Retrieve evidence (Sarvan's logic, but YOU call it)
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
        
        # ========== STEP 2: CHUNKING (SARVAN'S LOGIC) ==========
        print("\n✂️ Step 2: Chunking novels...")
        chunks = chunk_novels(
            novels, 
            chunk_size=self.config['chunking']['chunk_size']
        )
        print(f"  ✅ Chunks created (Sarvan's logic)")
        
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
        Ingest novels using Pathway
        YOUR RESPONSIBILITY
        
        Returns:
            Pathway table with novels
        """
        input_path = self.config['pathway']['input_folder']
        
        # Use Pathway's file connector
        novels = pw.io.fs.read(
            path=input_path,
            format='binary',
            mode='static',
            with_metadata=True
        )
        
        # Transform to your schema
        novels = novels.select(
            story_id=pw.this.path.apply(self._extract_story_id),
            content=pw.this.data
        )
        
        return novels
    
    def _extract_story_id(self, filepath: str) -> str:
        """Extract story ID from filepath"""
        import os
        filename = os.path.basename(filepath)
        return filename.replace('novel_', '').replace('.txt', '')
    
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
        
        # ========== STEP 5: RETRIEVAL (SARVAN'S LOGIC) ==========
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
        validated_result = validate_output(
            reasoning_result,
            min_evidence=self.config['validation']['min_evidence']
        )
        print(f"  ✅ Validation complete")
        
        return validated_result
    
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