import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, log_loss
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class Evaluator:
    @staticmethod
    def evaluate_classification(y_true, y_pred, y_prob=None):
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='binary', zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average='binary', zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, average='binary', zero_division=0)),
            "macro_f1": float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
        if y_prob is not None:
            try:
                metrics["log_loss"] = float(log_loss(y_true, y_prob))
            except Exception:
                pass
        return metrics

    @staticmethod
    def evaluate_regression(y_true, y_pred):
        return {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred))
        }

    @staticmethod
    def extract_feature_importance(pipeline, feature_names):
        """
        Extracts feature importances if the model is tree-based.
        """
        model = pipeline.named_steps.get('model')
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Try to get the feature names after one-hot encoding
            try:
                preprocessor = pipeline.named_steps.get('preprocessor')
                cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
                cat_features = cat_encoder.get_feature_names_out()
                num_features = preprocessor.transformers_[0][2] # numerical col names
                all_features = list(num_features) + list(cat_features)
            except Exception:
                all_features = feature_names

            # Make sure lengths match just in case
            if len(all_features) == len(importances):
                feat_dict = dict(zip(all_features, importances))
                # Sort by importance
                return {k: float(v) for k, v in sorted(feat_dict.items(), key=lambda item: item[1], reverse=True)}
        
        return {}
