from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Standardizes all API error responses.
    {
        "success": false,
        "error": {
            "code": "...",
            "message": "..."
        }
    }
    """
    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)

    # If the exception is unhandled by DRF, response will be None.
    if response is None:
        if isinstance(exc, ObjectDoesNotExist):
            return construct_error_response("NOT_FOUND", "Resource does not exist.", 404)
        
        # Log unexpected errors so they aren't lost, but don't expose traceback to user
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return construct_error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred.", 500)

    # Restructure DRF responses
    code = getattr(exc, 'default_code', 'INVALID_REQUEST')
    from django.http import Http404
    if isinstance(exc, Http404):
        code = 'NOT_FOUND'
        
    message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
    
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            message = "Validation Error"
            # Optional: Include validation details safely if needed
            # details = exc.detail
        elif isinstance(exc.detail, list):
             message = exc.detail[0]
         
    return construct_error_response(code.upper(), message, response.status_code)

def construct_error_response(code, message, status_code):
    from rest_framework.response import Response
    return Response({
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }, status=status_code)
