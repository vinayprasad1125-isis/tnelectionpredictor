# pyrefly: ignore [missing-import]
from rest_framework.decorators import api_view, permission_classes
# pyrefly: ignore [missing-import]
from rest_framework.permissions import AllowAny
# pyrefly: ignore [missing-import]
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify the API is running.
    """
    return Response({"status": "ok"})
