import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Cleans the validated dataframe by standardizing names and fixing missing types.
    """

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data cleaning pipeline")
        cleaned_df = df.copy()

        # 1. Drop complete duplicates
        cleaned_df = cleaned_df.drop_duplicates()

        # 2. Normalize Text Columns (Party, Constituency, Candidate)
        text_cols = ['party_name', 'party_abbreviation', 'constituency_name', 'candidate_name', 'district']
        for col in text_cols:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip().str.upper()

        # 3. Handle Numerical Conversions & Missing values
        cleaned_df['votes_received'] = pd.to_numeric(cleaned_df['votes_received'], errors='coerce').fillna(0).astype(int)
        if 'vote_percentage' in cleaned_df.columns:
            cleaned_df['vote_percentage'] = pd.to_numeric(cleaned_df['vote_percentage'], errors='coerce').fillna(0.0)

        # 4. Determine Winners and Margins
        cleaned_df = self._calculate_winner_and_margin(cleaned_df)

        return cleaned_df

    def _calculate_winner_and_margin(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates is_winner and winning_margin for each candidate in a constituency.
        """
        df = df.sort_values(by=['year', 'constituency_name', 'votes_received'], ascending=[True, True, False])
        
        # Determine winner
        df['rank'] = df.groupby(['year', 'constituency_name'])['votes_received'].rank(method='first', ascending=False)
        df['is_winner'] = df['rank'] == 1

        # Calculate winning margin
        # Margin = (Votes of this candidate) - (Votes of runner up) IF winner
        # IF not winner, Margin = (Votes of this candidate) - (Votes of winner) (Usually negative)
        
        # Get highest and second highest votes per constituency
        top_votes = df[df['rank'] <= 2].groupby(['year', 'constituency_name'])['votes_received'].apply(list).reset_index()
        
        def get_margin(row, top_votes_list):
            if len(top_votes_list) >= 2:
                winner_votes = top_votes_list[0]
                runner_up_votes = top_votes_list[1]
                if row['is_winner']:
                    return winner_votes - runner_up_votes
                else:
                    return row['votes_received'] - winner_votes
            return 0 # Unopposed
            
        top_votes_dict = dict(zip(zip(top_votes['year'], top_votes['constituency_name']), top_votes['votes_received']))
        
        margins = []
        for _, row in df.iterrows():
            key = (row['year'], row['constituency_name'])
            tv_list = top_votes_dict.get(key, [row['votes_received']])
            margins.append(get_margin(row, tv_list))
            
        df['winning_margin'] = margins
        df = df.drop(columns=['rank'])
        
        return df
