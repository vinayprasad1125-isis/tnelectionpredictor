import pandas as pd
import logging
from typing import List, Dict, Union

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Loads raw election data from CSV files and standardizes column names.
    """
    
    EXPECTED_COLUMNS = [
        'year', 'election_type', 'state', 'constituency_number', 'constituency_name', 
        'constituency_type', 'district', 'candidate_name', 'party_name', 'party_abbreviation', 
        'votes_received', 'vote_percentage'
    ]

    def __init__(self, column_mapping: Dict[str, str] = None):
        """
        Initialize the loader with an optional column mapping.
        If the raw CSV has different column names, this mapping translates them to EXPECTED_COLUMNS.
        """
        self.column_mapping = column_mapping or {}

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Loads the CSV and standardizes columns.
        """
        logger.info(f"Loading data from {filepath}")
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise

        if self.column_mapping:
            df = df.rename(columns=self.column_mapping)

        missing_cols = set(self.EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            error_msg = f"Missing critical columns in dataset: {missing_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return df
