from django.urls import path
from .views import PartyPerformanceView, ConstituencyHistoryView, VoteShareTrendView, SeatTrendView, TurnoutView

urlpatterns = [
    path('party-performance/', PartyPerformanceView.as_view(), name='party-performance'),
    path('constituency/<int:pk>/', ConstituencyHistoryView.as_view(), name='constituency-history'),
    path('vote-share-trends/', VoteShareTrendView.as_view(), name='vote-share-trends'),
    path('seat-trends/', SeatTrendView.as_view(), name='seat-trends'),
    path('turnout/', TurnoutView.as_view(), name='turnout'),
]
