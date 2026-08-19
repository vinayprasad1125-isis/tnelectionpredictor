from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Constituency
from .serializers import ConstituencySerializer

class ConstituencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district', 'type']
    search_fields = ['name', 'district']
    ordering_fields = ['number', 'name']
