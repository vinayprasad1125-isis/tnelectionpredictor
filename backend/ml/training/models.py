from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor

class ModelFactory:
    """
    Returns dictionaries of initialized models for both tasks.
    """
    @staticmethod
    def get_classification_models():
        return {
            'Baseline': DummyClassifier(strategy='prior'),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
            'RandomForest': RandomForestClassifier(random_state=42, class_weight='balanced'),
            'XGBoost': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
        }

    @staticmethod
    def get_regression_models():
        return {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(random_state=42),
            'XGBoost': XGBRegressor(random_state=42)
        }
