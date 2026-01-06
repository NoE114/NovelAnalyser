import pathway as pw
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

from .schema import RawNovelSchema, NovelMetadataSchema, NovelMetadata


class PathwayNovelIngestion:
    """
    Handles novel loading and metadata extraction using Pathway
    """
    
    def __init__(self, config: dict):
        self.input_folder = config['input_folder']
        self.metadata_folder = config['metadata_folder']
        os.makedirs(self.metadata_folder, exist_ok=True)
    
    def load_novels(self) -> pw.Table:
        """
        Load novels using Pathway file connector
        
        Returns:
            Pathway table with novels
        """
        print(f"📚 Loading novels from {self.input_folder}...")
        
        # Use Pathway to read novels
        novels = pw.io.fs.read(
            path=self.input_folder,
            format='binary',
            mode='static',  # Batch processing
            with_metadata=True
        )
        
        print(f"✅ Novels loaded via Pathway")
        return novels
    
    def extract_metadata(self, text: str, story_id: str) -> NovelMetadata:
        """
        Extract metadata from novel text
        
        Args:
            text: Full novel text
            story_id: Story identifier
            
        Returns:
            NovelMetadata object
        """
        # Detect chapters
        # Common patterns: "Chapter 1", "CHAPTER ONE", "Chapter I"
        chapter_markers = [
            line for line in text.split('\n') 
            if 'chapter' in line.lower() and len(line) < 100
        ]
        total_chapters = max(1, len(chapter_markers))
        
        # Count paragraphs (split by double newline)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        total_paragraphs = len(paragraphs)
        
        # Count words and chars
        words = text.split()
        total_words = len(words)
        total_chars = len(text)
        
        metadata = NovelMetadata(
            story_id=story_id,
            title=f"Novel_{story_id}",
            total_chapters=total_chapters,
            total_paragraphs=total_paragraphs,
            total_words=total_words,
            total_chars=total_chars,
            num_chunks=0,  # Will be updated after chunking
            processed_timestamp=datetime.now().isoformat()
        )
        
        return metadata
    
    def save_metadata(self, metadata: NovelMetadata):
        """Save metadata to JSON"""
        output_path = f"{self.metadata_folder}/novel_{metadata.story_id}_metadata.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.__dict__, f, indent=2)
        
        print(f"  💾 Metadata saved: {output_path}")
    
    def process_all_novels(self) -> List[NovelMetadata]:
        """
        Process all novels and extract metadata
        
        Returns:
            List of NovelMetadata objects
        """
        all_metadata = []
        
        # Get all novel files
        novel_files = sorted([
            f for f in os.listdir(self.input_folder) 
            if f.endswith('.txt')
        ])
        
        for novel_file in novel_files:
            # Extract story ID from filename
            story_id = novel_file.replace('novel_', '').replace('.txt', '')
            
            print(f"\n📖 Processing Novel {story_id}...")
            
            # Read novel
            filepath = f"{self.input_folder}/{novel_file}"
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract and save metadata
            metadata = self.extract_metadata(text, story_id)
            self.save_metadata(metadata)
            
            all_metadata.append(metadata)
            
            print(f"  ✅ Novel {story_id}: {metadata.total_words} words, "
                  f"{metadata.total_chapters} chapters, "
                  f"{metadata.total_paragraphs} paragraphs")
        
        return all_metadata