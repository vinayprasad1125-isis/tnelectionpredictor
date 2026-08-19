from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Election, ElectionResult
from .serializers import ElectionSerializer, ElectionResultSerializer, ElectionResultDetailSerializer

class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'election_type', 'state']
    search_fields = ['state']
    ordering_fields = ['year']

class ElectionResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ElectionResult.objects.all().select_related('election', 'constituency', 'candidate', 'party')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['election', 'constituency', 'candidate', 'party', 'is_winner']
    ordering_fields = ['votes_received', 'vote_percentage']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ElectionResultDetailSerializer
        return ElectionResultSerializer
