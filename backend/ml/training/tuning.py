import numpy as np
from sklearn.model_selection import RandomizedSearchCV
from typing import List, Tuple

class TemporalTuner:
    """
    Performs hyperparameter tuning while strictly respecting temporal splits
    by passing a custom cross-validation iterable to RandomizedSearchCV.
    """
    def __init__(self, n_iter=10):
        self.n_iter = n_iter

    def tune(self, pipeline, param_distributions, df_train, splits: List[Tuple[np.ndarray, np.ndarray]], scoring: str):
        """
        `splits` should be a list of (train_indices, val_indices)
        """
        search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=param_distributions,
            n_iter=self.n_iter,
            cv=splits,
            scoring=scoring,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        return search
