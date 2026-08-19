import unittest
import numpy as np
import pandas as pd
from apps.ml.pipeline import DataPreprocessor
from apps.ml.models.classification import XGBoostElectionsClassifier

class TestMLPipelineConsistency(unittest.TestCase):
    def setUp(self):
        # Create a mock training dataframe with some missing/messy data
        self.train_data = pd.DataFrame({
            'constituency_name': ['A', 'B', 'A', 'B', 'C', 'Unknown'],
            'district': ['D1', 'D1', 'D1', 'D1', 'D2', None],
            'candidate_name': ['C1', 'C2', 'C1', 'C3', 'C4', 'C5'],
            'party': ['P1', 'P2', 'P1', 'P2', 'P3', 'P1'],
            'votes_received': [1000, 2000, 1500, 1800, 3000, 100],
            'turnout_percentage': [60.5, 60.5, 62.0, 62.0, 70.0, None],
            'is_winner': [False, True, False, True, True, False]
        })
        
        self.inference_data = pd.DataFrame({
            'constituency_name': ['A', 'NewConst'], # One seen, one unseen
            'district': ['D1', 'D3'], # D3 unseen
            'candidate_name': ['C1', 'NewCand'],
            'party': ['P1', 'P4'], # P4 unseen
            'votes_received': [1200, 500],
            'turnout_percentage': [61.0, 65.0],
            'is_winner': [False, False]
        })

    def test_preprocessing_consistency(self):
        """
        Verify that inference data is transformed to the exact same feature space as training data
        (same columns, same ordering, handling missing values and unseen categories).
        """
        preprocessor = DataPreprocessor()
        X_train, y_train = preprocessor.fit_transform(self.train_data, target_col='is_winner')
        
        X_infer = preprocessor.transform(self.inference_data)
        
        # 1. Feature columns must perfectly match
        self.assertListEqual(list(X_train.columns), list(X_infer.columns))
        
        # 2. No NaN values after transformation
        self.assertFalse(X_train.isnull().any().any())
        self.assertFalse(X_infer.isnull().any().any())
        
        # 3. Target is separated properly in training
        self.assertEqual(len(y_train), len(X_train))

    def test_model_probability_structure(self):
        """
        Verify that probability outputs sum to 1.0 and are correctly mapped to party labels.
        """
        preprocessor = DataPreprocessor()
        X_train, y_train = preprocessor.fit_transform(self.train_data, target_col='party')
        
        model = XGBoostElectionsClassifier()
        model.fit(X_train, y_train)
        
        X_infer = preprocessor.transform(self.inference_data)
        probas = model.predict_proba(X_infer)
        
        # 1. Output must be a list of dicts mapped to party labels
        self.assertEqual(len(probas), len(X_infer))
        self.assertIsInstance(probas[0], dict)
        
        # 2. Each probability distribution must sum to approximately 1.0
        for prob_dist in probas:
            total_prob = sum(prob_dist.values())
            self.assertAlmostEqual(total_prob, 1.0, places=5)
            
            # 3. All probabilities must be between 0 and 1
            for p in prob_dist.values():
                self.assertTrue(0.0 <= p <= 1.0)
                
if __name__ == '__main__':
    unittest.main()
