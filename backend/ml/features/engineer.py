import pandas as pd
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Creates predictive features based strictly on historical data to prevent data leakage.
    If predicting for year Y, only data from year < Y is used to construct features.
    """
    
    def __init__(self, df: pd.DataFrame):
        # Ensure data is sorted chronologically
        self.df = df.sort_values(by=['year', 'constituency_name', 'votes_received'], ascending=[True, True, False])
        
        # Calculate state total votes per year for vote share calculations
        self.state_totals = self.df.groupby('year')['votes_received'].sum().to_dict()

    def engineer_features(self) -> pd.DataFrame:
        logger.info("Starting feature engineering process (Strict chronological order)")
        features_list = []

        years = sorted(self.df['year'].unique())
        
        # We can only predict for years that have at least one prior year of data
        if len(years) < 2:
            logger.warning("Not enough historical years to engineer features without leakage.")
            return self.df

        for target_year in years[1:]:
            # Slice historical data strictly strictly BEFORE the target year
            hist_df = self.df[self.df['year'] < target_year].copy()
            target_df = self.df[self.df['year'] == target_year].copy()

            # Generate Party Historical Features up to target_year
            party_features = self._build_party_features(hist_df)
            
            # Generate Constituency Historical Features up to target_year
            constituency_features = self._build_constituency_features(hist_df)
            
            # Merge features into target_df
            target_df = target_df.merge(party_features, on='party_abbreviation', how='left')
            target_df = target_df.merge(constituency_features, on=['constituency_name', 'party_abbreviation'], how='left')
            
            # Fill missing historical features (for new parties/candidates)
            cols_to_fill = [c for c in target_df.columns if c.startswith('hist_')]
            target_df[cols_to_fill] = target_df[cols_to_fill].fillna(0)

            features_list.append(target_df)

        # Concatenate all featured data
        final_df = pd.concat(features_list, ignore_index=True)
        return final_df

    def _build_party_features(self, hist_df: pd.DataFrame) -> pd.DataFrame:
        """
        Features: prev_election_vote_share, prev_election_seats
        Uses the most recent election in hist_df for 'previous' features.
        """
        if hist_df.empty:
            return pd.DataFrame()
            
        last_year = hist_df['year'].max()
        last_election_df = hist_df[hist_df['year'] == last_year]
        
        # Previous Seats
        prev_seats = last_election_df[last_election_df['is_winner'] == True].groupby('party_abbreviation').size().reset_index(name='hist_prev_seats')
        
        # Previous Vote Share
        state_total = self.state_totals[last_year]
        prev_votes = last_election_df.groupby('party_abbreviation')['votes_received'].sum().reset_index()
        prev_votes['hist_prev_vote_share'] = (prev_votes['votes_received'] / state_total) * 100
        prev_votes = prev_votes.drop(columns=['votes_received'])
        
        features = prev_seats.merge(prev_votes, on='party_abbreviation', how='outer').fillna(0)
        return features

    def _build_constituency_features(self, hist_df: pd.DataFrame) -> pd.DataFrame:
        """
        Features: prev_constituency_vote_share, prev_is_winner
        """
        if hist_df.empty:
            return pd.DataFrame()
            
        last_year = hist_df['year'].max()
        last_election_df = hist_df[hist_df['year'] == last_year]
        
        # Calculate total votes in each constituency for the last year
        const_totals = last_election_df.groupby('constituency_name')['votes_received'].sum().reset_index(name='const_total')
        last_election_df = last_election_df.merge(const_totals, on='constituency_name')
        
        # Vote share in that constituency
        last_election_df['hist_prev_const_vote_share'] = (last_election_df['votes_received'] / last_election_df['const_total']) * 100
        
        features = last_election_df[['constituency_name', 'party_abbreviation', 'hist_prev_const_vote_share', 'is_winner']]
        features = features.rename(columns={'is_winner': 'hist_prev_is_winner'})
        
        # If a party had multiple candidates in same constituency (rare but possible), take max
        features = features.groupby(['constituency_name', 'party_abbreviation']).max().reset_index()
        
        return features
