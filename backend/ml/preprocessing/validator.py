import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates the election dataset for logical inconsistencies.
    """

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        report = {
            "rows_processed": len(df),
            "duplicates": 0,
            "missing_values": {},
            "invalid_votes": 0,
            "invalid_percentages": 0,
            "multiple_winners": 0,
            "validation_status": "PASS"
        }

        # 1. Missing Values
        report["missing_values"] = df.isnull().sum().to_dict()
        if any(v > 0 for k, v in report["missing_values"].items() if k in ['year', 'constituency_name', 'candidate_name', 'votes_received']):
            report["validation_status"] = "FAIL - Critical columns have missing values"

        # 2. Duplicate rows
        duplicates = df.duplicated(subset=['year', 'constituency_name', 'candidate_name', 'party_name']).sum()
        report["duplicates"] = int(duplicates)

        # 3. Invalid votes
        invalid_votes = (df['votes_received'] < 0).sum()
        report["invalid_votes"] = int(invalid_votes)

        # 4. Invalid percentages
        if 'vote_percentage' in df.columns:
            invalid_percentages = ((df['vote_percentage'] < 0) | (df['vote_percentage'] > 100)).sum()
            report["invalid_percentages"] = int(invalid_percentages)

        # 5. Multiple winners per constituency validation (by max votes)
        # Find if the top 2 candidates have the exact same votes (tie is possible but usually a data issue)
        max_votes = df.groupby(['year', 'constituency_name'])['votes_received'].transform('max')
        winners = df[df['votes_received'] == max_votes]
        winner_counts = winners.groupby(['year', 'constituency_name']).size()
        multiple_winners = (winner_counts > 1).sum()
        report["multiple_winners"] = int(multiple_winners)

        # Fail status
        if invalid_votes > 0 or invalid_percentages > 0:
            report["validation_status"] = "FAIL - Invalid numeric data found (e.g. negative votes)"
        elif duplicates > 0:
            report["validation_status"] = "WARN - Duplicates found, will be cleaned"

        return report
