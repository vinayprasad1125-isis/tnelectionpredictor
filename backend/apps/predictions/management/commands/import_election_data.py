import os
import pandas as pd
from django.core.management.base import BaseCommand
from apps.elections.models import Election, ElectionResult
from apps.constituencies.models import Constituency
from apps.parties.models import Party
from apps.candidates.models import Candidate

class Command(BaseCommand):
    help = 'Import election data from a cleaned CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the cleaned CSV file', required=True)

    def handle(self, *args, **kwargs):
        filepath = kwargs['file']
        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'File "{filepath}" does not exist.'))
            return

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to read CSV: {e}'))
            return
            
        # 1. Validate the CSV
        required_cols = ['election_year', 'constituency_number', 'constituency_name', 
                         'candidate_name', 'party', 'total_votes', 'vote_percentage']
        for col in required_cols:
            if col not in df.columns:
                self.stderr.write(self.style.ERROR(f'Missing required column: {col}'))
                return
                
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(df)} rows. Starting import...'))
        
        # Calculate winners and margins per constituency
        df = df.sort_values(by=['election_year', 'constituency_number', 'total_votes'], ascending=[True, True, False])
        
        for (year, const_num), group in df.groupby(['election_year', 'constituency_number']):
            group = group.reset_index(drop=True)
            
            # Create/update election
            election, _ = Election.objects.get_or_create(
                year=year,
                election_type='ASSEMBLY',
                state='Tamil Nadu'
            )

            # Create/update constituency
            const_name = group.iloc[0]['constituency_name'].title()
            constituency, _ = Constituency.objects.get_or_create(
                number=const_num,
                name=const_name,
                defaults={
                    'district': 'Unknown',
                    'type': group.iloc[0].get('category', 'GEN')
                }
            )

            # Calculate margins
            winning_votes = group.iloc[0]['total_votes']
            runner_up_votes = group.iloc[1]['total_votes'] if len(group) > 1 else 0
            margin = winning_votes - runner_up_votes

            for index, row in group.iterrows():
                is_winner = (index == 0)
                current_margin = margin if is_winner else 0

                # Create/update party
                party_name = str(row['party']).strip()
                party, _ = Party.objects.get_or_create(
                    name=party_name,
                    defaults={'abbreviation': party_name}
                )

                # Create candidate
                cand_name = str(row['candidate_name']).title().strip()
                candidate, _ = Candidate.objects.get_or_create(
                    name=cand_name
                )

                # Insert election results
                try:
                    ElectionResult.objects.update_or_create(
                        election=election,
                        constituency=constituency,
                        candidate=candidate,
                        defaults={
                            'party': party,
                            'votes_received': row['total_votes'],
                            'vote_percentage': row['vote_percentage'],
                            'is_winner': is_winner,
                            'winning_margin': current_margin,
                        }
                    )
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Failed to insert result for {cand_name} in {const_name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully imported all election data.'))
