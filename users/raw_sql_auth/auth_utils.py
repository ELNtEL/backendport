"""
Authentication utilities for password hashing and token generation
"""
import hashlib
import secrets
from datetime import datetime, timedelta


def hash_password(password):
    """
    Hash password using SHA-256 with salt

    Args:
        password (str): Plain text password

    Returns:
        str: Hashed password in format 'salt$hash'
    """
    # Generate a random salt
    salt = secrets.token_hex(32)

    # Create hash using salt and password
    pwd_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    # Return salt and hash combined
    return f"{salt}${pwd_hash}"


def verify_password(password, hashed_password):
    """
    Verify password against hashed password

    Args:
        password (str): Plain text password to verify
        hashed_password (str): Stored hashed password in format 'salt$hash'

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Split salt and hash
        salt, pwd_hash = hashed_password.split('$')

        # Hash the provided password with the same salt
        new_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

        # Compare hashes using constant-time comparison to prevent timing attacks
        return secrets.compare_digest(new_hash, pwd_hash)
    except (ValueError, AttributeError):
        return False


def generate_token():
    """
    Generate a secure random token

    Returns:
        str: 64-character hexadecimal token
    """
    return secrets.token_hex(32)


def get_token_expiry(days=30):
    """
    Get token expiration timestamp

    Args:
        days (int): Number of days until token expires (default: 30)

    Returns:
        str: ISO format timestamp
    """
    expiry = datetime.now() + timedelta(days=days)
    return expiry.isoformat()


def is_token_expired(expires_at):
    """
    Check if token has expired

    Args:
        expires_at (str): ISO format timestamp

    Returns:
        bool: True if token has expired, False otherwise
    """
    try:
        expiry_time = datetime.fromisoformat(expires_at)
        return datetime.now() > expiry_time
    except (ValueError, TypeError):
        return True


def validate_email(email):
    """
    Basic email validation

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if email format is valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength

    Args:
        password (str): Password to validate

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, ""
