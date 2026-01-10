"""
Build index script
    Calls Blezecon's Pathway app
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pathway_pipeline.app import run_app


def main():
    """Build vector index for all novels"""
    print("="*60)
    print("🚀 BUILDING INDEX VIA PATHWAY APP")
    print("="*60)
    
    # Run Blezecon's Pathway app
    app = run_app(config_path="configs/system_rules.yaml")
    
    print("\n✅ Index build complete!")
    print("📁 Outputs in data/index/")


if __name__ == "__main__":
    main()