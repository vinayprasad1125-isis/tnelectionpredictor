from rest_framework.test import APITestCase
from rest_framework import status
from apps.elections.models import Election, ElectionResult
from apps.constituencies.models import Constituency
from apps.parties.models import Party
from apps.candidates.models import Candidate
from apps.predictions.models import PredictionHistory

class ComprehensiveAPITests(APITestCase):
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
        self.pred_history = PredictionHistory.objects.create(
            constituency_name='Chennai North',
            election_year=2026,
            predicted_winner_party='MP',
            probabilities={'MP': 0.75, 'OTHER': 0.25},
            model_version='1.0'
        )

    def test_elections_api(self):
        response = self.client.get('/api/elections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) > 0)
        self.assertEqual(response.data['results'][0]['year'], 2021)

    def test_constituencies_api(self):
        response = self.client.get('/api/constituencies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Checking if it matches frontend expectations
        first = response.data['results'][0]
        self.assertIn('id', first)
        self.assertIn('name', first)
        self.assertIn('district', first)

    def test_results_api_filter(self):
        response = self.client.get(f'/api/results/?party={self.party.id}&is_winner=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        # Check specific frontend expectation
        res = response.data['results'][0]
        self.assertIn('constituency_name', res)
        self.assertIn('candidate_name', res)
        self.assertIn('election_year', res)
        self.assertEqual(res['votes_received'], 50000)

    def test_prediction_history_api(self):
        response = self.client.get('/api/prediction-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) > 0)
        self.assertEqual(response.data['results'][0]['predicted_winner_party'], 'MP')

    def test_analytics_constituency_api(self):
        response = self.client.get(f'/api/analytics/constituency/{self.constituency.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Analytics returns a list, not paginated
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)
        self.assertIn('party', response.data[0])
        self.assertIn('vote_share', response.data[0])
        self.assertIn('margin', response.data[0])

    def test_api_404_handling(self):
        response = self.client.get('/api/constituencies/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'NOT_FOUND')

    def test_empty_dataset(self):
        # Delete data and query
        ElectionResult.objects.all().delete()
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

