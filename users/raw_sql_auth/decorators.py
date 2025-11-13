"""
Authentication decorators for protecting views
Uses raw SQL to validate tokens
"""
import sqlite3
from functools import wraps
from django.http import JsonResponse

from .db_schema import get_db_connection
from .auth_utils import is_token_expired


def token_required(view_func):
    """
    Decorator to require token authentication for a view

    Usage:
        @token_required
        def my_protected_view(request):
            user_id = request.user_id  # Access authenticated user ID
            ...

    The decorator validates the token and attaches user_id to the request object
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return JsonResponse(
                {'error': 'Authentication required. Please provide Authorization header.'},
                status=401
            )

        # Check header format
        if not auth_header.startswith('Token '):
            return JsonResponse(
                {'error': 'Invalid authorization header format. Use: Authorization: Token <your-token>'},
                status=401
            )

        # Extract token
        token = auth_header.replace('Token ', '', 1).strip()

        if not token:
            return JsonResponse(
                {'error': 'Token is required'},
                status=401
            )

        # Validate token using raw SQL
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get token info with user info in single query (using parameterized query)
            cursor.execute(
                """
                SELECT
                    t.user_id,
                    t.expires_at,
                    t.is_active,
                    u.is_active as user_is_active,
                    u.email,
                    u.full_name
                FROM auth_tokens t
                INNER JOIN auth_users u ON t.user_id = u.id
                WHERE t.token = ?
                """,
                (token,)
            )

            result = cursor.fetchone()

            if not result:
                return JsonResponse(
                    {'error': 'Invalid token'},
                    status=401
                )

            user_id, expires_at, token_is_active, user_is_active, email, full_name = result

            # Check if token is active
            if not token_is_active:
                return JsonResponse(
                    {'error': 'Token has been deactivated. Please login again.'},
                    status=401
                )

            # Check if user is active
            if not user_is_active:
                return JsonResponse(
                    {'error': 'User account is inactive'},
                    status=403
                )

            # Check if token has expired
            if is_token_expired(expires_at):
                # Deactivate expired token
                cursor.execute(
                    "UPDATE auth_tokens SET is_active = 0 WHERE token = ?",
                    (token,)
                )
                conn.commit()

                return JsonResponse(
                    {'error': 'Token has expired. Please login again.'},
                    status=401
                )

            # Attach user information to request object
            request.user_id = user_id
            request.user_email = email
            request.user_full_name = full_name

            # Call the actual view function
            return view_func(request, *args, **kwargs)

        except sqlite3.Error as e:
            return JsonResponse(
                {'error': f'Database error: {str(e)}'},
                status=500
            )
        finally:
            cursor.close()
            conn.close()

    return wrapper


def optional_token_auth(view_func):
    """
    Decorator for optional token authentication

    Usage:
        @optional_token_auth
        def my_view(request):
            if hasattr(request, 'user_id'):
                # User is authenticated
                user_id = request.user_id
            else:
                # User is not authenticated (anonymous)
                ...

    The decorator validates the token if provided, but doesn't require it
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        # If no auth header, continue without authentication
        if not auth_header:
            return view_func(request, *args, **kwargs)

        # If header exists but format is invalid, continue without authentication
        if not auth_header.startswith('Token '):
            return view_func(request, *args, **kwargs)

        # Extract token
        token = auth_header.replace('Token ', '', 1).strip()

        if not token:
            return view_func(request, *args, **kwargs)

        # Validate token using raw SQL
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get token info with user info (using parameterized query)
            cursor.execute(
                """
                SELECT
                    t.user_id,
                    t.expires_at,
                    t.is_active,
                    u.is_active as user_is_active,
                    u.email,
                    u.full_name
                FROM auth_tokens t
                INNER JOIN auth_users u ON t.user_id = u.id
                WHERE t.token = ?
                """,
                (token,)
            )

            result = cursor.fetchone()

            # If valid token found and not expired, attach user info
            if result:
                user_id, expires_at, token_is_active, user_is_active, email, full_name = result

                if token_is_active and user_is_active and not is_token_expired(expires_at):
                    request.user_id = user_id
                    request.user_email = email
                    request.user_full_name = full_name

            # Call the actual view function (whether authenticated or not)
            return view_func(request, *args, **kwargs)

        except sqlite3.Error:
            # On database error, continue without authentication
            return view_func(request, *args, **kwargs)
        finally:
            cursor.close()
            conn.close()

    return wrapper
