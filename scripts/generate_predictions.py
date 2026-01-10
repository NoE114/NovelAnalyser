import sys
import os
import csv
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pathway_pipeline.app import run_app

def main():
    print("="*60)
    print("🚀 GENERATING BINARY PREDICTIONS")
    print("="*60)
    
    # 1. Initialize App (computes index if not cached, or loads it)
    # Note: In a real Pathway app, we might connect to a running service.
    # Here we instantiate the app which loads the index.
    app = run_app(config_path="configs/system_rules.yaml")
    
    # 2. Read Test Data
    test_file = "data/raw/test.csv"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
        
    df = pd.read_csv(test_file)
    print(f"📄 Loaded {len(df)} rows from {test_file}")
    
    results = []
    
    # 3. Process Each Row
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        row_id = row['id']
        book_name = row['book_name']
        character = row['char']
        content = row['content']
        
        # Clean story_id (assuming filename matches book_name exactly without extension)
        # Note: In ingestion we might have stripped .txt. Ensure consistency.
        # Filename: "The Count of Monte Cristo.txt" -> story_id: "The Count of Monte Cristo"
        story_id = book_name.strip()
        
        # Formulate Query
        # We want to verify if the content is TRUE or FALSE based on the text.
        # The existing reasoner classifies. If it finds evidence -> True (1). 
        # If Rejection/Contradiction -> False (0).
        query_text = f"Verify claim: {content}"
        
        try:
            result = app.query(story_id=story_id, backstory=query_text)
            
            # Map to 0 or 1
            if result['status'] == 'SUCCESS':
                prediction = 1
            else:
                prediction = 0
                
            # Optional: Log reason for debugging (not in final CSV)
            # print(f"ID {row_id}: {result['status']} - {result.get('rejection_reason', '')}")
            
        except Exception as e:
            print(f"⚠️ Error processing ID {row_id}: {e}")
            prediction = 0 # Fail safe to 0
            
        results.append({'id': row_id, 'prediction': prediction})
        
    # 4. Save Output
    output_path = "output.csv"
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)
    
    print("\n" + "="*60)
    print(f"✅ DONE! Results saved to {output_path}")
    print("Check output.csv for 0/1 predictions.")
    print("="*60)

if __name__ == "__main__":
    main()
