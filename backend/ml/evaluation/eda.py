import pandas as pd
from typing import Dict, Any

class EDAAnalyzer:
    """
    Performs Exploratory Data Analysis on the cleaned election dataset.
    Generates meaningful numerical statistics that can be consumed by the API.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
        # Calculate total valid votes per constituency per election if not present
        if 'total_votes' not in self.df.columns:
            self.total_votes_map = self.df.groupby(['year', 'constituency_name'])['votes_received'].sum().reset_index(name='total_valid_votes')
            self.df = self.df.merge(self.total_votes_map, on=['year', 'constituency_name'], how='left')

    def party_level_analysis(self) -> pd.DataFrame:
        """
        Total votes, seats won, and vote share by party per year.
        """
        # Aggregate total votes per party per year
        party_votes = self.df.groupby(['year', 'party_abbreviation'])['votes_received'].sum().reset_index()
        
        # Aggregate total votes in the entire state per year
        total_state_votes = self.df.groupby('year')['votes_received'].sum().reset_index(name='state_total_votes')
        
        # Seats won
        winners = self.df[self.df['is_winner'] == True]
        seats_won = winners.groupby(['year', 'party_abbreviation']).size().reset_index(name='seats_won')
        
        # Merge
        stats = party_votes.merge(total_state_votes, on='year')
        stats = stats.merge(seats_won, on=['year', 'party_abbreviation'], how='left')
        stats['seats_won'] = stats['seats_won'].fillna(0).astype(int)
        
        # Calculate Vote Share
        stats['vote_share'] = (stats['votes_received'] / stats['state_total_votes']) * 100
        
        return stats.sort_values(by=['year', 'seats_won'], ascending=[False, False])

    def constituency_level_analysis(self, constituency_name: str) -> pd.DataFrame:
        """
        Historical winners, vote shares, and margins for a specific constituency.
        """
        const_df = self.df[self.df['constituency_name'] == constituency_name]
        winners = const_df[const_df['is_winner'] == True].copy()
        
        winners['vote_share'] = (winners['votes_received'] / winners['total_valid_votes']) * 100
        
        result = winners[['year', 'candidate_name', 'party_abbreviation', 'votes_received', 'vote_share', 'winning_margin']]
        return result.sort_values(by='year', ascending=False)

    def election_level_analysis(self) -> pd.DataFrame:
        """
        Overall election stats: total seats, total votes
        """
        stats = self.df.groupby('year').agg(
            total_seats=('constituency_name', 'nunique'),
            total_votes=('votes_received', 'sum'),
            total_candidates=('candidate_name', 'count')
        ).reset_index()
        return stats.sort_values(by='year', ascending=False)
