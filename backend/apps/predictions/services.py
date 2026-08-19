import os
from django.conf import settings
from ml.prediction.service import PredictionService
import pandas as pd

class PredictionAPIService:
    _ml_service = None

    @classmethod
    def get_service(cls):
        if cls._ml_service is None:
            models_dir = os.path.join(settings.BASE_DIR, 'ml', 'models')
            cls._ml_service = PredictionService(models_dir)
        return cls._ml_service

    @classmethod
    def get_models_info(cls):
        return cls.get_service().get_models_info()

    @classmethod
    def predict_constituency(cls, constituency_name, year):
        """
        Fetches the latest featured data for the constituency to run predictions.
        (In a real app, this would extract the features from DB or a Feature Store).
        """
        data_path = os.path.join(settings.BASE_DIR, 'ml', 'data', 'processed', 'final_features.csv')
        if not os.path.exists(data_path):
            return {"error": "Feature dataset not available."}
            
        df = pd.read_csv(data_path)
        # Filter for the specific constituency and the target year
        # For a truly future prediction, we would use the most recent historical features 
        # and set the year to the future year. 
        # For simplicity here, we grab the row that matches the constituency.
        
        search_name = str(constituency_name).strip().lower()
        max_year = df['year'].max()
        
        if year <= max_year:
            const_df = df[(df['constituency_name'].str.lower() == search_name) & (df['year'] == year)]
        else:
            # Dynamically simulate future year by using latest raw data as historical context
            raw_path = os.path.join(settings.BASE_DIR, 'ml', 'data', 'raw', 'elections.csv')
            if not os.path.exists(raw_path):
                return {"error": "Raw dataset not available to simulate future predictions."}
                
            raw_df = pd.read_csv(raw_path)
            
            from ml.preprocessing.cleaner import DataCleaner
            cleaner = DataCleaner()
            clean_df = cleaner.clean(raw_df)
            
            from ml.features.engineer import FeatureEngineer
            engineer = FeatureEngineer(clean_df)
            
            # Assume same candidates/parties run as in the latest election for this constituency
            target_df = clean_df[(clean_df['constituency_name'].str.lower() == search_name) & (clean_df['year'] == clean_df['year'].max())].copy()
            target_df['year'] = year # Set to future target year
            
            party_features = engineer._build_party_features(clean_df)
            constituency_features = engineer._build_constituency_features(clean_df)
            
            target_df = target_df.merge(party_features, on='party_abbreviation', how='left')
            target_df = target_df.merge(constituency_features, on=['constituency_name', 'party_abbreviation'], how='left')
            
            cols_to_fill = [c for c in target_df.columns if c.startswith('hist_')]
            target_df[cols_to_fill] = target_df[cols_to_fill].fillna(0)
            
            const_df = target_df
            
        if const_df.empty:
            return {"error": f"No feature data available for constituency {constituency_name} in year {year}"}
            
        clf_result = cls.get_service().predict_constituency(const_df, 'classification')
        
        # Format the response as requested
        preds = clf_result.get('predictions', [])
        winner = None
        probabilities = {}
        highest_prob = -1
        
        for p in preds:
            party = p['party']
            prob = p.get('model_estimated_win_probability', 0)
            probabilities[party] = prob
            if prob > highest_prob:
                highest_prob = prob
                winner = party
                
        # Get Model info
        models_info = cls.get_models_info()
        clf_meta = models_info.get('classification', {})
        
        response_data = {
            "constituency": constituency_name,
            "election_year": year,
            "prediction": {
                "winner": winner,
                "probabilities": probabilities
            },
            "model": {
                "name": clf_meta.get('model_name'),
                "version": clf_meta.get('model_version'),
                "validation_metric": f"Macro F1: {clf_meta.get('metrics', {}).get('macro_f1', 0):.4f}"
            }
        }
        
        # Save to PredictionHistory
        from .models import PredictionHistory
        PredictionHistory.objects.create(
            constituency_name=constituency_name,
            election_year=year,
            predicted_winner_party=winner,
            probabilities=probabilities,
            model_version=clf_meta.get('model_version', 'unknown')
        )
        
        return response_data
