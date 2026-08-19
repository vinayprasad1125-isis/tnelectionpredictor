import unittest
import pandas as pd
from ml.training.split import TemporalSplitter

class TestMLLeakage(unittest.TestCase):
    def setUp(self):
        # Create a dummy dataframe spanning 3 elections
        data = {
            'year': [2011, 2011, 2016, 2016, 2021, 2021],
            'constituency_name': ['A', 'B', 'A', 'B', 'A', 'B'],
            'votes': [100, 200, 150, 250, 300, 400]
        }
        self.df = pd.DataFrame(data)

    def test_temporal_splitter_no_leakage(self):
        """
        Ensures that for any split, the maximum year in the training set
        is STRICTLY LESS THAN the minimum year in the testing set.
        This guarantees future information cannot leak into the past.
        """
        splitter = TemporalSplitter(self.df, time_col='year')
        splits = splitter.get_expanding_windows()
        
        for train_df, test_df in splits:
            max_train_year = train_df['year'].max()
            min_test_year = test_df['year'].min()
            self.assertTrue(max_train_year < min_test_year, 
                            f"LEAKAGE DETECTED: Train max year ({max_train_year}) >= Test min year ({min_test_year})")

    def test_temporal_splitter_final_split(self):
        """
        Ensures the final split uses the very last year as test,
        and all preceding years as train.
        """
        splitter = TemporalSplitter(self.df, time_col='year')
        train_df, test_df = splitter.get_final_train_test()
        
        self.assertEqual(test_df['year'].unique()[0], 2021)
        self.assertTrue(2011 in train_df['year'].values)
        self.assertTrue(2016 in train_df['year'].values)
        self.assertFalse(2021 in train_df['year'].values)

if __name__ == '__main__':
    unittest.main()
