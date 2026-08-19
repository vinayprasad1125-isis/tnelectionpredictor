import pandas as pd
from typing import List, Tuple

class TemporalSplitter:
    """
    Handles data splitting while strictly respecting chronological order
    to prevent data leakage.
    """
    def __init__(self, df: pd.DataFrame, time_col: str = 'year'):
        self.df = df.sort_values(by=time_col)
        self.time_col = time_col
        
    def get_expanding_windows(self) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Returns a list of (train_df, test_df) tuples for expanding window cross-validation.
        """
        years = sorted(self.df[self.time_col].unique())
        splits = []
        
        if len(years) < 2:
            # Fallback to random split if only 1 year of features exists
            from sklearn.model_selection import train_test_split
            train_df, test_df = train_test_split(self.df, test_size=0.2, random_state=42)
            splits.append((train_df, test_df))
            return splits
            
        for i in range(1, len(years)):
            train_years = years[:i]
            test_year = years[i]
            
            train_df = self.df[self.df[self.time_col].isin(train_years)]
            test_df = self.df[self.df[self.time_col] == test_year]
            
            splits.append((train_df, test_df))
            
        return splits
        
    def get_final_train_test(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Train: All years except the most recent (or random 80% if 1 year)
        Test: The most recent year (or random 20% if 1 year)
        """
        splits = self.get_expanding_windows()
        return splits[-1]
