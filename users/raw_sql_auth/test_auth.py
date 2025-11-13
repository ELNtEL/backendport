"""
Test script for raw SQL authentication system
Run this independently to test the authentication logic
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')

# Test utilities without Django
from auth_utils import (
    hash_password,
    verify_password,
    generate_token,
    get_token_expiry,
    validate_email,
    validate_password,
    is_token_expired
)


def test_password_hashing():
    """Test password hashing and verification"""
    print("\n=== Testing Password Hashing ===")

    password = "TestPass123"
    hashed = hash_password(password)

    print(f"Password: {password}")
    print(f"Hashed: {hashed[:50]}...")  # Show first 50 chars

    # Test correct password
    assert verify_password(password, hashed), "✗ Password verification failed"
    print("✓ Correct password verified successfully")

    # Test wrong password
    assert not verify_password("WrongPass123", hashed), "✗ Wrong password accepted"
    print("✓ Wrong password correctly rejected")


def test_token_generation():
    """Test token generation"""
    print("\n=== Testing Token Generation ===")

    token1 = generate_token()
    token2 = generate_token()

    print(f"Token 1: {token1[:30]}...")
    print(f"Token 2: {token2[:30]}...")

    assert len(token1) == 64, "✗ Token length incorrect"
    print(f"✓ Token length correct: {len(token1)} characters")

    assert token1 != token2, "✗ Tokens not unique"
    print("✓ Tokens are unique")


def test_email_validation():
    """Test email validation"""
    print("\n=== Testing Email Validation ===")

    valid_emails = [
        "user@example.com",
        "test.user@company.co.uk",
        "admin+tag@site.org"
    ]

    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com"
    ]

    for email in valid_emails:
        assert validate_email(email), f"✗ Valid email rejected: {email}"
    print(f"✓ All {len(valid_emails)} valid emails accepted")

    for email in invalid_emails:
        assert not validate_email(email), f"✗ Invalid email accepted: {email}"
    print(f"✓ All {len(invalid_emails)} invalid emails rejected")


def test_password_validation():
    """Test password validation"""
    print("\n=== Testing Password Validation ===")

    # Valid password
    valid, msg = validate_password("SecurePass123")
    assert valid, f"✗ Valid password rejected: {msg}"
    print("✓ Valid password accepted")

    # Test various invalid passwords
    tests = [
        ("short", "too short"),
        ("nouppercase123", "no uppercase"),
        ("NOLOWERCASE123", "no lowercase"),
        ("NoDigitsHere", "no digits")
    ]

    for password, reason in tests:
        valid, msg = validate_password(password)
        assert not valid, f"✗ Invalid password accepted: {reason}"
        print(f"✓ Invalid password rejected: {reason}")


def test_token_expiry():
    """Test token expiration"""
    print("\n=== Testing Token Expiration ===")

    # Future expiry (not expired)
    future_expiry = get_token_expiry(days=30)
    assert not is_token_expired(future_expiry), "✗ Future token marked as expired"
    print(f"✓ Future token correctly marked as not expired")
    print(f"  Expires at: {future_expiry}")

    # Past expiry (expired)
    past_expiry = "2020-01-01T00:00:00"
    assert is_token_expired(past_expiry), "✗ Past token marked as not expired"
    print("✓ Past token correctly marked as expired")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RAW SQL AUTHENTICATION SYSTEM - UNIT TESTS")
    print("=" * 60)

    try:
        test_password_hashing()
        test_token_generation()
        test_email_validation()
        test_password_validation()
        test_token_expiry()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
