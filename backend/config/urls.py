from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.elections.views import ElectionViewSet, ElectionResultViewSet
from apps.constituencies.views import ConstituencyViewSet
from apps.parties.views import PartyViewSet
from apps.candidates.views import CandidateViewSet
from apps.predictions.views import PredictionHistoryViewSet
from config.views import health_check

router = DefaultRouter()
router.register(r'elections', ElectionViewSet, basename='election')
router.register(r'results', ElectionResultViewSet, basename='result')
router.register(r'constituencies', ConstituencyViewSet, basename='constituency')
router.register(r'parties', PartyViewSet, basename='party')
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'prediction-history', PredictionHistoryViewSet, basename='predictionhistory')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health Check
    path('api/health/', health_check, name='health_check'),
    
    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/', include(router.urls)),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/predictions/', include('apps.predictions.urls')),
]
