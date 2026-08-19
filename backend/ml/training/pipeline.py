from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class PipelineBuilder:
    """
    Builds Scikit-Learn preprocessing pipelines for Election Data.
    """
    def __init__(self, numerical_cols, categorical_cols):
        self.numerical_cols = numerical_cols
        self.categorical_cols = categorical_cols

    def build_preprocessor(self) -> ColumnTransformer:
        """
        Builds the ColumnTransformer for the features.
        """
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numerical_cols),
                ('cat', categorical_transformer, self.categorical_cols)
            ]
        )
        return preprocessor

    def build_full_pipeline(self, estimator) -> Pipeline:
        """
        Returns a complete inference pipeline.
        """
        return Pipeline(steps=[
            ('preprocessor', self.build_preprocessor()),
            ('model', estimator)
        ])
