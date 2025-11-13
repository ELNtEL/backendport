"""
Example protected views demonstrating token authentication
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .decorators import token_required, optional_token_auth


@token_required
@require_http_methods(["GET"])
def protected_view(request):
    """
    Example protected view that requires authentication

    GET /api/auth/protected/
    Headers: {
        "Authorization": "Token <your-token>"
    }

    Returns: {
        "message": "This is a protected resource",
        "user": {...}
    }
    """
    return JsonResponse({
        'message': 'This is a protected resource',
        'user': {
            'id': request.user_id,
            'email': request.user_email,
            'full_name': request.user_full_name
        }
    })


@optional_token_auth
@require_http_methods(["GET"])
def optional_auth_view(request):
    """
    Example view with optional authentication

    GET /api/auth/optional/
    Headers (optional): {
        "Authorization": "Token <your-token>"
    }

    Returns different content based on authentication status
    """
    if hasattr(request, 'user_id'):
        # User is authenticated
        return JsonResponse({
            'message': 'Welcome back!',
            'authenticated': True,
            'user': {
                'id': request.user_id,
                'email': request.user_email,
                'full_name': request.user_full_name
            }
        })
    else:
        # Anonymous user
        return JsonResponse({
            'message': 'Welcome, guest!',
            'authenticated': False,
            'hint': 'Login to see personalized content'
        })


@token_required
@require_http_methods(["POST"])
def protected_post_example(request):
    """
    Example protected POST endpoint

    POST /api/auth/protected-action/
    Headers: {
        "Authorization": "Token <your-token>"
    }
    Body: {
        "action": "some_action",
        "data": {...}
    }

    Returns: {
        "message": "Action performed successfully",
        "performed_by": {...}
    }
    """
    import json

    try:
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action', 'unknown')

        return JsonResponse({
            'message': f'Action "{action}" performed successfully',
            'performed_by': {
                'id': request.user_id,
                'email': request.user_email,
                'full_name': request.user_full_name
            },
            'data_received': data
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
