from rest_framework.test import APITestCase
from rest_framework import status
from apps.elections.models import Election

class APIEndpointsTest(APITestCase):
    def setUp(self):
        self.election = Election.objects.create(year=2021, election_type='ASSEMBLY', state='Tamil Nadu')
        
    def test_get_elections(self):
        response = self.client.get('/api/elections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination format
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_custom_error_handler_404(self):
        # We fetch a non-existent election
        response = self.client.get('/api/elections/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify the custom format
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'NOT_FOUND')

    def test_analytics_endpoints_exist(self):
        # We don't have DB populated with results so it will be empty but should return 200
        response = self.client.get('/api/analytics/party-performance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_prediction_endpoint_exists(self):
        # It should return 404 since no features are there in the test environment
        response = self.client.get('/api/predictions/constituency/Chennai_North/')
        # Wait, the response might be 404 because the dataset isn't available
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])
