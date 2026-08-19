import os
import json
import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

from .split import TemporalSplitter
from .pipeline import PipelineBuilder
from .models import ModelFactory
from ml.evaluation.metrics import Evaluator

logger = logging.getLogger(__name__)

class MLTrainer:
    def __init__(self, df: pd.DataFrame, models_dir: str):
        self.df = df
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Define features and targets
        self.target_class = 'is_winner'
        self.target_reg = 'vote_percentage'
        
        # Features that are safe to use (historical features)
        self.num_features = [
            'hist_prev_seats', 'hist_prev_vote_share', 'hist_prev_const_vote_share'
        ]
        self.cat_features = [
            'party_abbreviation', 'constituency_type'
        ]
        self.features = self.num_features + self.cat_features

    def train_classification(self):
        """
        Trains and evaluates classification models using chronological validation.
        Selects the best model based on macro_f1 and saves it.
        """
        logger.info("Starting Classification Training Pipeline...")
        splitter = TemporalSplitter(self.df, 'year')
        splits = splitter.get_expanding_windows()
        
        # Get final split for the "test" evaluation
        train_df, test_df = splitter.get_final_train_test()
        
        X_train = train_df[self.features]
        y_train = train_df[self.target_class].astype(int)
        
        X_test = test_df[self.features]
        y_test = test_df[self.target_class].astype(int)
        
        pipeline_builder = PipelineBuilder(self.num_features, self.cat_features)
        models = ModelFactory.get_classification_models()
        
        best_model = None
        best_score = -1
        best_name = ""
        best_metrics = {}
        
        for name, estimator in models.items():
            logger.info(f"Training {name}...")
            pipeline = pipeline_builder.build_full_pipeline(estimator)
            
            # Fit on training data
            pipeline.fit(X_train, y_train)
            
            # Predict on test data
            y_pred = pipeline.predict(X_test)
            y_prob = pipeline.predict_proba(X_test) if hasattr(pipeline, 'predict_proba') else None
            
            # Evaluate
            metrics = Evaluator.evaluate_classification(y_test, y_pred, y_prob)
            logger.info(f"{name} Metrics: Macro F1: {metrics['macro_f1']:.4f}, Accuracy: {metrics['accuracy']:.4f}")
            
            if metrics['macro_f1'] > best_score:
                best_score = metrics['macro_f1']
                best_model = pipeline
                best_name = name
                best_metrics = metrics
                
        logger.info(f"Best Classification Model: {best_name} (Macro F1: {best_score:.4f})")
        
        # Save model
        feature_importance = Evaluator.extract_feature_importance(best_model, self.features)
        self._save_model(best_model, 'classification', best_name, best_metrics, feature_importance)

    def train_regression(self):
        """
        Trains and evaluates regression models using chronological validation.
        Selects the best model based on R2 and saves it.
        """
        logger.info("Starting Regression Training Pipeline...")
        splitter = TemporalSplitter(self.df, 'year')
        train_df, test_df = splitter.get_final_train_test()
        
        X_train = train_df[self.features]
        y_train = train_df[self.target_reg]
        
        X_test = test_df[self.features]
        y_test = test_df[self.target_reg]
        
        pipeline_builder = PipelineBuilder(self.num_features, self.cat_features)
        models = ModelFactory.get_regression_models()
        
        best_model = None
        best_score = -float('inf')
        best_name = ""
        best_metrics = {}
        
        for name, estimator in models.items():
            logger.info(f"Training {name}...")
            pipeline = pipeline_builder.build_full_pipeline(estimator)
            pipeline.fit(X_train, y_train)
            
            y_pred = pipeline.predict(X_test)
            metrics = Evaluator.evaluate_regression(y_test, y_pred)
            logger.info(f"{name} Metrics: RMSE: {metrics['rmse']:.4f}, R2: {metrics['r2']:.4f}")
            
            if metrics['r2'] > best_score:
                best_score = metrics['r2']
                best_model = pipeline
                best_name = name
                best_metrics = metrics
                
        logger.info(f"Best Regression Model: {best_name} (R2: {best_score:.4f})")
        
        # Save model
        feature_importance = Evaluator.extract_feature_importance(best_model, self.features)
        self._save_model(best_model, 'regression', best_name, best_metrics, feature_importance)

    def _save_model(self, pipeline, task_type, model_name, metrics, feature_importance):
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        model_filename = f"{task_type}_model_{version}.joblib"
        meta_filename = f"{task_type}_model_{version}.json"
        
        # Save pipeline
        joblib.dump(pipeline, self.models_dir / model_filename)
        
        # Save metadata
        metadata = {
            "task_type": task_type,
            "model_name": model_name,
            "training_date": datetime.now().isoformat(),
            "model_version": version,
            "features_used": self.features,
            "metrics": metrics,
            "feature_importance": feature_importance
        }
        
        with open(self.models_dir / meta_filename, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        # Create a symbolic link or copy to 'latest' so the prediction service can easily find it
        latest_meta = self.models_dir / f"{task_type}_latest.json"
        with open(latest_meta, 'w') as f:
            metadata['model_filename'] = model_filename
            json.dump(metadata, f, indent=4)
            
        logger.info(f"Saved {task_type} model version {version}")
