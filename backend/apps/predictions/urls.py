from django.urls import path
from .views import ModelsInfoView, ModelDetailView, ModelMetricsView, ConstituencyPredictionView

urlpatterns = [
    path('models/', ModelsInfoView.as_view(), name='models-info'),
    path('models/<str:model_id>/', ModelDetailView.as_view(), name='model-detail'),
    path('models/<str:model_id>/metrics/', ModelMetricsView.as_view(), name='model-metrics'),
    path('constituency/<str:constituency_name>/', ConstituencyPredictionView.as_view(), name='constituency-prediction'),
]
