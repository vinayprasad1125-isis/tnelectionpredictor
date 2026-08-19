import os
import json
import joblib
import pandas as pd
from pathlib import Path

class PredictionService:
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.clf_model, self.clf_meta = self._load_model('classification')
        self.reg_model, self.reg_meta = self._load_model('regression')

    def _load_model(self, task_type: str):
        meta_path = self.models_dir / f"{task_type}_latest.json"
        if not meta_path.exists():
            return None, None
            
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            
        model_path = self.models_dir / meta['model_filename']
        if not model_path.exists():
            return None, meta
            
        model = joblib.load(model_path)
        return model, meta

    def get_models_info(self):
        return {
            "classification": self.clf_meta,
            "regression": self.reg_meta
        }

    def predict_constituency(self, constituency_df: pd.DataFrame, task_type: str = 'classification'):
        """
        Takes a dataframe containing the historical features for a constituency
        and returns the model estimates.
        """
        if task_type == 'classification':
            if not self.clf_model:
                raise ValueError("Classification model not trained yet.")
                
            features = self.clf_meta['features_used']
            X = constituency_df[features]
            
            predictions = self.clf_model.predict(X)
            probabilities = self.clf_model.predict_proba(X) if hasattr(self.clf_model, 'predict_proba') else None
            
            results = []
            for idx, (_, row) in enumerate(constituency_df.iterrows()):
                party = row.get('party_abbreviation', 'Unknown')
                res = {
                    "party": party,
                    "model_estimated_winner": bool(predictions[idx]),
                }
                if probabilities is not None:
                    # Depending on binary classification, index 1 is usually 'True'
                    res["model_estimated_win_probability"] = round(float(probabilities[idx][1]), 4)
                results.append(res)
                
            return {
                "prediction_type": "classification",
                "model_version": self.clf_meta['model_version'],
                "predictions": results
            }
            
        elif task_type == 'regression':
            if not self.reg_model:
                raise ValueError("Regression model not trained yet.")
                
            features = self.reg_meta['features_used']
            X = constituency_df[features]
            
            predictions = self.reg_model.predict(X)
            
            results = []
            for idx, (_, row) in enumerate(constituency_df.iterrows()):
                party = row.get('party_abbreviation', 'Unknown')
                # Constrain regression output between 0 and 100
                pred_share = max(0.0, min(100.0, float(predictions[idx])))
                res = {
                    "party": party,
                    "model_estimated_vote_share": round(pred_share, 2),
                }
                results.append(res)
                
            return {
                "prediction_type": "regression",
                "model_version": self.reg_meta['model_version'],
                "predictions": results
            }
        else:
            raise ValueError("Invalid task type.")
