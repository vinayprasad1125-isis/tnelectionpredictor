import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup Django environment for ingestion
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml.preprocessing.loader import DataLoader
from ml.preprocessing.validator import DataValidator
from ml.preprocessing.cleaner import DataCleaner
from ml.features.engineer import FeatureEngineer

from apps.elections.models import Election, ElectionResult
from apps.constituencies.models import Constituency
from apps.parties.models import Party
from apps.candidates.models import Candidate

logger = logging.getLogger(__name__)

class DatasetBuilder:
    def __init__(self, raw_filepath: str, output_dir: str):
        self.raw_filepath = raw_filepath
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_pipeline(self) -> str:
        """
        Orchestrates the entire ML data pipeline.
        Returns the path to the processed feature dataset.
        """
        logger.info("Starting Dataset Pipeline")

        # 1. Load
        loader = DataLoader()
        raw_df = loader.load_csv(self.raw_filepath)

        # 2. Validate
        validator = DataValidator()
        validation_report = validator.validate(raw_df)
        
        # Save Validation Report
        report_path = self.output_dir.parent / 'metadata' / f'validation_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(validation_report, f, indent=4)
            
        if "FAIL" in validation_report["validation_status"]:
            logger.error(f"Validation Failed! See report at {report_path}")
            raise ValueError(f"Data Validation Failed: {validation_report['validation_status']}")

        # 3. Clean
        cleaner = DataCleaner()
        clean_df = cleaner.clean(raw_df)

        clean_output = self.output_dir / 'clean_data.csv'
        clean_df.to_csv(clean_output, index=False)

        # 4. Feature Engineering
        engineer = FeatureEngineer(clean_df)
        final_df = engineer.engineer_features()

        # 5. Save Processed Dataset
        output_file = self.output_dir / 'final_features.csv'
        final_df.to_csv(output_file, index=False)
        logger.info(f"Successfully created feature dataset at {output_file}")

        return str(clean_output), str(output_file)

    def ingest_to_db(self, clean_csv_path: str):
        """
        Populates the Django Database for the API to consume.
        Requires a cleaned CSV (before or after feature engineering).
        """
        import pandas as pd
        df = pd.read_csv(clean_csv_path)
        logger.info("Starting Database Ingestion...")

        for _, row in df.iterrows():
            # 1. Election
            election, _ = Election.objects.get_or_create(
                year=row['year'],
                election_type=row.get('election_type', 'ASSEMBLY'),
                state=row.get('state', 'Tamil Nadu')
            )

            # 2. Constituency
            constituency, _ = Constituency.objects.get_or_create(
                number=row['constituency_number'],
                name=row['constituency_name'],
                defaults={
                    'district': row.get('district', 'Unknown'),
                    'type': row.get('constituency_type', 'GEN')
                }
            )

            # 3. Party
            party, _ = Party.objects.get_or_create(
                name=row['party_name'],
                defaults={'abbreviation': row['party_abbreviation']}
            )

            # 4. Candidate
            candidate, _ = Candidate.objects.get_or_create(
                name=row['candidate_name']
            )

            # 5. ElectionResult
            ElectionResult.objects.update_or_create(
                election=election,
                constituency=constituency,
                candidate=candidate,
                defaults={
                    'party': party,
                    'votes_received': row['votes_received'],
                    'vote_percentage': row.get('vote_percentage', 0.0),
                    'is_winner': row.get('is_winner', False),
                    'winning_margin': row.get('winning_margin', 0),
                }
            )
        logger.info("Database Ingestion Complete.")

if __name__ == '__main__':
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Example Usage:
    # builder = DatasetBuilder('ml/data/raw/elections.csv', 'ml/data/processed/')
    # processed_file = builder.run_pipeline()
    # builder.ingest_to_db(processed_file)
