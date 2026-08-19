from rest_framework.views import APIView
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .services import PredictionAPIService
from .models import PredictionHistory
from .serializers import PredictionHistorySerializer

class PredictionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredictionHistory.objects.all().order_by('-prediction_timestamp')
    serializer_class = PredictionHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['constituency_name', 'election_year', 'model_version']
    search_fields = ['constituency_name', 'predicted_winner_party']
    ordering_fields = ['prediction_timestamp', 'election_year']

class ModelsInfoView(APIView):
    def get(self, request):
        data = PredictionAPIService.get_models_info()
        return Response(data, status=status.HTTP_200_OK)

class ModelDetailView(APIView):
    def get(self, request, model_id):
        # We assume model_id is either 'classification' or 'regression' or the version string
        data = PredictionAPIService.get_models_info()
        if model_id in data:
            return Response(data[model_id], status=status.HTTP_200_OK)
        return Response({"error": "Model not found."}, status=status.HTTP_404_NOT_FOUND)

class ModelMetricsView(APIView):
    def get(self, request, model_id):
        data = PredictionAPIService.get_models_info()
        if model_id in data:
            return Response({
                "model_name": data[model_id].get('model_name'),
                "version": data[model_id].get('model_version'),
                "metrics": data[model_id].get('metrics', {}),
                "feature_importance": data[model_id].get('feature_importance', {})
            }, status=status.HTTP_200_OK)
        return Response({"error": "Model not found."}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.throttling import ScopedRateThrottle

class ConstituencyPredictionView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'prediction'

    def get(self, request, constituency_name):
        year = request.query_params.get('year', 2026) # Default to future prediction
        try:
            year = int(year)
            data = PredictionAPIService.predict_constituency(constituency_name, year)
            if "error" in data:
                return Response(data, status=status.HTTP_404_NOT_FOUND)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
