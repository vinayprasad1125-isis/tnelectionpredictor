import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.data.builder import DatasetBuilder

def main():
    raw_csv_path = os.path.join('ml', 'data', 'raw', 'elections.csv')
    output_dir = os.path.join('ml', 'data', 'processed')
    
    if not os.path.exists(raw_csv_path):
        print(f"Error: {raw_csv_path} not found. Run clean_eci_data.py first.")
        return

    builder = DatasetBuilder(raw_filepath=raw_csv_path, output_dir=output_dir)
    try:
        clean_csv, processed_file = builder.run_pipeline()
        print(f"Pipeline finished successfully. Features saved to {processed_file}")
        
        # Ingest into Django DB using the cleaned (but not dropped) dataset
        builder.ingest_to_db(clean_csv)
        
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == '__main__':
    main()
