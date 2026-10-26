# pyrefly: ignore [missing-import]
from rest_framework.views import APIView
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework import status
from .services import AnalyticsService

class PartyPerformanceView(APIView):
    def get(self, request):
        year = request.query_params.get('year')
        data = AnalyticsService.get_party_performance(year=year)
        return Response(data, status=status.HTTP_200_OK)

class ConstituencyHistoryView(APIView):
    def get(self, request, pk):
        data = AnalyticsService.get_constituency_history(pk)
        return Response(data, status=status.HTTP_200_OK)

class VoteShareTrendView(APIView):
    def get(self, request):
        party = request.query_params.get('party')
        if not party:
            return Response({"error": "party abbreviation is required"}, status=status.HTTP_400_BAD_REQUEST)
        data = AnalyticsService.get_vote_share_trends(party)
        return Response(data, status=status.HTTP_200_OK)

class SeatTrendView(APIView):
    def get(self, request):
        party = request.query_params.get('party')
        if not party:
            return Response({"error": "party abbreviation is required"}, status=status.HTTP_400_BAD_REQUEST)
        data = AnalyticsService.get_seat_trends(party)
        return Response(data, status=status.HTTP_200_OK)

class TurnoutView(APIView):
    def get(self, request):
        data = AnalyticsService.get_turnout()
        return Response(data, status=status.HTTP_200_OK)
