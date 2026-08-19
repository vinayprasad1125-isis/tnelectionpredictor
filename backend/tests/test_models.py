from django.test import TestCase
from apps.elections.models import Election, ElectionResult
from apps.constituencies.models import Constituency
from apps.parties.models import Party
from apps.candidates.models import Candidate

class ElectionModelsTest(TestCase):
    def setUp(self):
        self.election = Election.objects.create(year=2021, election_type='ASSEMBLY', state='Tamil Nadu')
        self.constituency = Constituency.objects.create(number=1, name='Chennai North', district='Chennai', type='GEN')
        self.party = Party.objects.create(name='Mock Party', abbreviation='MP')
        self.candidate = Candidate.objects.create(name='John Doe')
        
        self.result = ElectionResult.objects.create(
            election=self.election,
            constituency=self.constituency,
            candidate=self.candidate,
            party=self.party,
            votes_received=50000,
            vote_percentage=45.5,
            is_winner=True,
            winning_margin=10000
        )

    def test_election_creation(self):
        self.assertEqual(self.election.year, 2021)
        self.assertEqual(str(self.election), "2021 State Assembly - Tamil Nadu")

    def test_result_creation(self):
        self.assertEqual(self.result.votes_received, 50000)
        self.assertTrue(self.result.is_winner)
        self.assertEqual(self.result.party.abbreviation, 'MP')
