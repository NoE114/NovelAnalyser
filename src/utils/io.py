"""
Safe I/O utilities
Blezecon's responsibility
"""
import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Dict


def safe_write_json(data: Dict, filepath: str):
    """
    Safely write JSON file
    
    Args:
        data: Data to write
        filepath: Output path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def safe_write_pickle(data: Any, filepath: str):
    """
    Safely write pickle file
    
    Args:
        data: Data to write
        filepath: Output path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def hash_file(filepath: str) -> str:
    """
    Create hash of file for reproducibility
    
    Args:
        filepath: File to hash
        
    Returns:
        SHA256 hash
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    
    return hashlib.sha256(content).hexdigest()


def create_manifest(
    story_id: str,
    input_hash: str,
    output_hash: str,
    config: dict,
    output_path: str
):
    """
    Create reproducibility manifest
    
    Args:
        story_id: Story identifier
        input_hash: Hash of input file
        output_hash: Hash of output
        config: Pipeline config
        output_path: Where to save manifest
    """
    manifest = {
        'story_id': story_id,
        'input_hash': input_hash,
        'output_hash': output_hash,
        'config': config,
        'pipeline_version': '1.0'
    }
    
    safe_write_json(manifest, output_path)