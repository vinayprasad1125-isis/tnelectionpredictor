import os
import pandas as pd
import random
from pathlib import Path

def generate_mock_data(output_filepath: str):
    """
    Generates a synthetic dataset for testing the pipeline and APIs.
    Simulates 3 elections across 2 constituencies with 3 parties.
    """
    years = [2011, 2016, 2021]
    constituencies = [
        {'name': 'Chennai North', 'number': 1},
        {'name': 'Madurai Central', 'number': 2}
    ]
    parties = [
        {'name': 'Party A', 'abbr': 'PA'},
        {'name': 'Party B', 'abbr': 'PB'},
        {'name': 'Party C', 'abbr': 'PC'}
    ]

    records = []
    
    for year in years:
        for const in constituencies:
            # Randomly assign a base vote pool for this constituency in this year
            base_votes = random.randint(150000, 200000)
            
            # Party A and B are strong, C is weak
            shares = [random.uniform(0.35, 0.50), random.uniform(0.35, 0.50), random.uniform(0.05, 0.15)]
            
            # Normalize shares
            total_share = sum(shares)
            shares = [s / total_share for s in shares]
            
            for i, party in enumerate(parties):
                votes = int(base_votes * shares[i])
                candidate_name = f"Candidate {party['abbr']} {year}"
                
                records.append({
                    'year': year,
                    'election_type': 'ASSEMBLY',
                    'state': 'Tamil Nadu',
                    'constituency_number': const['number'],
                    'constituency_name': const['name'],
                    'constituency_type': 'GEN',
                    'district': 'Mock District',
                    'candidate_name': candidate_name,
                    'party_name': party['name'],
                    'party_abbreviation': party['abbr'],
                    'votes_received': votes,
                    'vote_percentage': round(shares[i] * 100, 2)
                })

    df = pd.DataFrame(records)
    
    # Intentionally add a duplicate to test cleaner
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    
    # Ensure directory exists
    Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_filepath, index=False)
    print(f"Mock data generated at {output_filepath}")

if __name__ == '__main__':
    # Generates raw data in the expected directory
    raw_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'data', 'raw', 'mock_elections.csv')
    generate_mock_data(raw_path)
