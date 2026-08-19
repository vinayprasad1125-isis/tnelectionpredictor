import pandas as pd
import re
import argparse
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_and_merge_datasets(files: List[Tuple[str, int]], output_path: str):
    all_mapped_dfs = []

    for input_path, year in files:
        logger.info(f"Reading raw ECI data from {input_path} for year {year}")
        
        # ECI detailed results usually have 4 lines of junk at the top.
        # The actual headers are on row 5 (index 4).
        try:
            df = pd.read_csv(input_path, skiprows=3) # Let's read and check headers
            if 'STATE/UT NAME' not in df.columns:
                 df = pd.read_csv(input_path, skiprows=4)
        except Exception as e:
            logger.error(f"Failed to read {input_path}: {e}")
            continue
            
        # Drop summary "TURN OUT" rows where 'STATE/UT NAME' is "TURN OUT"
        if 'STATE/UT NAME' in df.columns:
            df = df[df['STATE/UT NAME'] != 'TURN OUT']
        
        # Drop rows that are completely empty or NA in critical columns
        df = df.dropna(subset=['AC NO.', 'AC NAME', 'CANDIDATE NAME', 'PARTY'])
        
        # Ensure AC NO is numeric
        df = df[pd.to_numeric(df['AC NO.'], errors='coerce').notnull()]
        
        # Strip leading numbers from Candidate Names (e.g., "1 S.vijayakumar" -> "S.vijayakumar")
        df['CANDIDATE NAME'] = df['CANDIDATE NAME'].astype(str).apply(lambda x: re.sub(r'^\d+\s+', '', x).strip())
        
        # Reset index to prevent alignment issues when assigning to new DataFrame
        df = df.reset_index(drop=True)
        
        # Map columns to match what the ML Pipeline expects
        mapped_df = pd.DataFrame()
        mapped_df['year'] = [year] * len(df)
        mapped_df['election_type'] = 'ASSEMBLY'
        mapped_df['state'] = df['STATE/UT NAME'].str.title()
        mapped_df['constituency_number'] = df['AC NO.']
        mapped_df['constituency_name'] = df['AC NAME'].str.title()
        mapped_df['constituency_type'] = 'GEN' # Fallback default
        mapped_df['district'] = 'Unknown' # Fallback default
        mapped_df['candidate_name'] = df['CANDIDATE NAME'].str.title()
        mapped_df['party_abbreviation'] = df['PARTY']
        mapped_df['party_name'] = df['PARTY'] # ECI data only provides the abbreviation usually
        mapped_df['votes_received'] = pd.to_numeric(df['TOTAL'], errors='coerce').fillna(0).astype(int)
        
        # Handle differing column names for vote percentage
        if 'OVER VALID VOTES + NOTA' in df.columns:
            mapped_df['vote_percentage'] = pd.to_numeric(df['OVER VALID VOTES + NOTA'], errors='coerce').fillna(0.0)
        elif '% VOTES POLLED' in df.columns:
            mapped_df['vote_percentage'] = pd.to_numeric(df['% VOTES POLLED'], errors='coerce').fillna(0.0)
        else:
            mapped_df['vote_percentage'] = 0.0

        all_mapped_dfs.append(mapped_df)

    if not all_mapped_dfs:
        logger.error("No valid datasets were processed.")
        return

    final_df = pd.concat(all_mapped_dfs, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    logger.info(f"Successfully cleaned and merged data. Saved {len(final_df)} rows to {output_path}")

if __name__ == '__main__':
    # Define the datasets to merge
    datasets = [
        ('ml/data/raw/10- Detailed Results.csv', 2021),
        ('ml/data/raw/10-Detailed_Results_1778165153.csv', 2026)
    ]
    output_csv = 'ml/data/raw/elections.csv'
    
    clean_and_merge_datasets(datasets, output_csv)
