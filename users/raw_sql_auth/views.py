"""
Authentication views using raw SQL with parameterized queries
Includes registration, login, logout, and user info endpoints
"""
import json
import sqlite3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .db_schema import get_db_connection
from .auth_utils import (
    hash_password,
    verify_password,
    generate_token,
    get_token_expiry,
    validate_email,
    validate_password,
    is_token_expired
)
from .decorators import token_required


def json_error_response(message, status=400):
    """Helper function to return JSON error response"""
    return JsonResponse({'error': message}, status=status)


def json_success_response(data, status=200):
    """Helper function to return JSON success response"""
    return JsonResponse(data, status=status)


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    """
    User registration endpoint

    POST /api/auth/register/
    Body: {
        "email": "user@example.com",
        "password": "SecurePass123",
        "full_name": "John Doe"
    }

    Returns: {
        "message": "User registered successfully",
        "user": {...},
        "token": "..."
    }
    """
    try:
        # Parse JSON body
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()

        # Validate inputs
        if not email or not password or not full_name:
            return json_error_response("Email, password, and full name are required")

        if not validate_email(email):
            return json_error_response("Invalid email format")

        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return json_error_response(error_msg)

        # Hash password
        password_hash = hash_password(password)

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if user already exists (using parameterized query)
            cursor.execute(
                "SELECT id FROM auth_users WHERE email = ?",
                (email,)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                return json_error_response("User with this email already exists", status=409)

            # Insert new user (using parameterized query to prevent SQL injection)
            cursor.execute(
                """
                INSERT INTO auth_users (email, password_hash, full_name, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (email, password_hash, full_name)
            )

            user_id = cursor.lastrowid

            # Generate authentication token
            token = generate_token()
            expires_at = get_token_expiry(days=30)

            # Insert token (using parameterized query)
            cursor.execute(
                """
                INSERT INTO auth_tokens (user_id, token, expires_at, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (user_id, token, expires_at)
            )

            conn.commit()

            # Get created user info
            cursor.execute(
                """
                SELECT id, email, full_name, is_active, created_at
                FROM auth_users
                WHERE id = ?
                """,
                (user_id,)
            )
            user = cursor.fetchone()

            return json_success_response({
                'message': 'User registered successfully',
                'user': {
                    'id': user[0],
                    'email': user[1],
                    'full_name': user[2],
                    'is_active': bool(user[3]),
                    'created_at': user[4]
                },
                'token': token,
                'expires_at': expires_at
            }, status=201)

        except sqlite3.IntegrityError as e:
            conn.rollback()
            return json_error_response(f"Database integrity error: {str(e)}", status=409)
        except sqlite3.Error as e:
            conn.rollback()
            return json_error_response(f"Database error: {str(e)}", status=500)
        finally:
            cursor.close()
            conn.close()

    except json.JSONDecodeError:
        return json_error_response("Invalid JSON body")
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    User login endpoint

    POST /api/auth/login/
    Body: {
        "email": "user@example.com",
        "password": "SecurePass123"
    }

    Returns: {
        "message": "Login successful",
        "user": {...},
        "token": "..."
    }
    """
    try:
        # Parse JSON body
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Validate inputs
        if not email or not password:
            return json_error_response("Email and password are required")

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get user by email (using parameterized query)
            cursor.execute(
                """
                SELECT id, email, password_hash, full_name, is_active, created_at
                FROM auth_users
                WHERE email = ?
                """,
                (email,)
            )
            user = cursor.fetchone()

            if not user:
                return json_error_response("Invalid email or password", status=401)

            user_id, user_email, password_hash, full_name, is_active, created_at = user

            # Check if user is active
            if not is_active:
                return json_error_response("User account is inactive", status=403)

            # Verify password
            if not verify_password(password, password_hash):
                return json_error_response("Invalid email or password", status=401)

            # Deactivate old tokens for this user (optional: keep only one active token per user)
            cursor.execute(
                """
                UPDATE auth_tokens
                SET is_active = 0
                WHERE user_id = ? AND is_active = 1
                """,
                (user_id,)
            )

            # Generate new authentication token
            token = generate_token()
            expires_at = get_token_expiry(days=30)

            # Insert new token (using parameterized query)
            cursor.execute(
                """
                INSERT INTO auth_tokens (user_id, token, expires_at, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (user_id, token, expires_at)
            )

            conn.commit()

            return json_success_response({
                'message': 'Login successful',
                'user': {
                    'id': user_id,
                    'email': user_email,
                    'full_name': full_name,
                    'is_active': bool(is_active),
                    'created_at': created_at
                },
                'token': token,
                'expires_at': expires_at
            })

        except sqlite3.Error as e:
            conn.rollback()
            return json_error_response(f"Database error: {str(e)}", status=500)
        finally:
            cursor.close()
            conn.close()

    except json.JSONDecodeError:
        return json_error_response("Invalid JSON body")
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """
    User logout endpoint

    POST /api/auth/logout/
    Headers: {
        "Authorization": "Token <token>"
    }

    Returns: {
        "message": "Logout successful"
    }
    """
    try:
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Token '):
            return json_error_response("Invalid authorization header format. Use 'Token <token>'", status=401)

        token = auth_header.replace('Token ', '', 1).strip()

        if not token:
            return json_error_response("Token is required", status=401)

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Deactivate token (using parameterized query)
            cursor.execute(
                """
                UPDATE auth_tokens
                SET is_active = 0
                WHERE token = ? AND is_active = 1
                """,
                (token,)
            )

            if cursor.rowcount == 0:
                return json_error_response("Invalid or already logged out token", status=401)

            conn.commit()

            return json_success_response({'message': 'Logout successful'})

        except sqlite3.Error as e:
            conn.rollback()
            return json_error_response(f"Database error: {str(e)}", status=500)
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@token_required
@require_http_methods(["GET"])
def user_info_view(request):
    """
    Get current user information (requires authentication)

    GET /api/auth/me/
    Headers: {
        "Authorization": "Token <token>"
    }

    Returns: {
        "user": {...}
    }
    """
    # The @token_required decorator attaches user_id to request
    user_id = request.user_id

    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get user info (using parameterized query)
        cursor.execute(
            """
            SELECT id, email, full_name, is_active, created_at, updated_at
            FROM auth_users
            WHERE id = ?
            """,
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            return json_error_response("User not found", status=404)

        return json_success_response({
            'user': {
                'id': user[0],
                'email': user[1],
                'full_name': user[2],
                'is_active': bool(user[3]),
                'created_at': user[4],
                'updated_at': user[5]
            }
        })

    except sqlite3.Error as e:
        return json_error_response(f"Database error: {str(e)}", status=500)
    finally:
        cursor.close()
        conn.close()
