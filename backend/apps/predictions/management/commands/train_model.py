import os
import pandas as pd
from django.core.management.base import BaseCommand
from ml.training.trainer import MLTrainer
from django.conf import settings

class Command(BaseCommand):
    help = 'Trains the Election Prediction ML Models using historical data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Model Training Process...'))
        
        data_path = os.path.join(settings.BASE_DIR, 'ml', 'data', 'processed', 'final_features.csv')
        models_dir = os.path.join(settings.BASE_DIR, 'ml', 'models')
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'Data file not found at {data_path}. Run the data pipeline first.'))
            return
            
        try:
            df = pd.read_csv(data_path)
            trainer = MLTrainer(df, models_dir)
            
            self.stdout.write('Training Classification Models (Winning Party)...')
            trainer.train_classification()
            
            self.stdout.write('Training Regression Models (Vote Share)...')
            trainer.train_regression()
            
            self.stdout.write(self.style.SUCCESS('Model Training Completed Successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Training failed: {e}'))
