from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Party
from .serializers import PartySerializer

class PartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'abbreviation']
    ordering_fields = ['name', 'abbreviation']
