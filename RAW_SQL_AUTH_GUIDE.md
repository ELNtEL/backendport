# Raw SQL Token Authentication - Quick Start Guide

Complete Django authentication system using **pure SQL** (no ORM) with **token-based authentication** and **SQL injection protection**.

## 🚀 Quick Start

### 1. Initialize Database Tables

```bash
# Option 1: Using Django management command
python manage.py init_raw_sql_auth

# Option 2: Using Python directly
python -c "from users.raw_sql_auth.db_schema import init_auth_tables; init_auth_tables()"
```

### 2. Start Django Server

```bash
python manage.py runserver
```

### 3. Test the API

All endpoints are available under `/api/users/auth/`

## 📍 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/auth/register/` | Register new user | No |
| POST | `/api/users/auth/login/` | Login user | No |
| POST | `/api/users/auth/logout/` | Logout user | Yes |
| GET | `/api/users/auth/me/` | Get current user | Yes |
| GET | `/api/users/auth/protected/` | Example protected route | Yes |
| GET | `/api/users/auth/optional/` | Example optional auth | No |

## 🔐 Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00"
  },
  "token": "a1b2c3d4e5f6789...",
  "expires_at": "2025-02-14T10:30:00"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {...},
  "token": "x9y8z7w6v5u4321...",
  "expires_at": "2025-02-14T11:00:00"
}
```

### Access Protected Endpoint

```bash
# Save your token
TOKEN="your-token-from-login-response"

# Use token in Authorization header
curl -X GET http://localhost:8000/api/users/auth/me/ \
  -H "Authorization: Token $TOKEN"
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00"
  }
}
```

### Logout

```bash
curl -X POST http://localhost:8000/api/users/auth/logout/ \
  -H "Authorization: Token $TOKEN"
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

## 🛡️ Security Features

### 1. SQL Injection Protection

All queries use **parameterized statements**:

```python
# ✅ SAFE - Parameters passed separately
cursor.execute(
    "SELECT * FROM auth_users WHERE email = ?",
    (email,)
)

# ❌ UNSAFE - Never do this!
cursor.execute(f"SELECT * FROM auth_users WHERE email = '{email}'")
```

### 2. Password Security

- **SHA-256 hashing** with random 32-byte salt
- **Constant-time comparison** to prevent timing attacks
- **Strong password requirements**:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 digit

### 3. Token Security

- **64-character cryptographically secure tokens**
- **30-day expiration** (configurable)
- **Automatic cleanup** of expired tokens
- **Single active session** per user (old tokens deactivated on new login)

## 💻 Using in Your Views

### Protected View (Required Authentication)

```python
from users.raw_sql_auth.decorators import token_required
from django.http import JsonResponse

@token_required
def my_protected_view(request):
    """Only authenticated users can access this"""
    return JsonResponse({
        'message': f'Hello, {request.user_full_name}!',
        'user_id': request.user_id,
        'user_email': request.user_email
    })
```

### Optional Authentication

```python
from users.raw_sql_auth.decorators import optional_token_auth
from django.http import JsonResponse

@optional_token_auth
def my_public_view(request):
    """Anyone can access, but authenticated users get extra features"""
    if hasattr(request, 'user_id'):
        return JsonResponse({
            'message': f'Welcome back, {request.user_full_name}!',
            'premium_content': 'Special content for logged-in users'
        })
    else:
        return JsonResponse({
            'message': 'Welcome, guest!',
            'hint': 'Login for premium features'
        })
```

## 🗄️ Database Schema

### auth_users Table

```sql
CREATE TABLE auth_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### auth_tokens Table

```sql
CREATE TABLE auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);
```

## 🧪 Testing

Run unit tests to verify everything works:

```bash
cd users/raw_sql_auth
python test_auth.py
```

**Expected output:**
```
============================================================
RAW SQL AUTHENTICATION SYSTEM - UNIT TESTS
============================================================
...
ALL TESTS PASSED! ✓
============================================================
```

## 📁 File Structure

```
users/raw_sql_auth/
├── __init__.py              # Module initialization
├── README.md                # Detailed documentation
├── db_schema.py             # Database table creation
├── auth_utils.py            # Password hashing, token generation
├── views.py                 # Registration, login, logout endpoints
├── decorators.py            # @token_required, @optional_token_auth
├── examples.py              # Example protected views
├── urls.py                  # URL routing
└── test_auth.py             # Unit tests

users/management/commands/
└── init_raw_sql_auth.py     # Django management command
```

## ⚙️ Configuration

### Change Token Expiration

Edit `users/raw_sql_auth/auth_utils.py`:

```python
def get_token_expiry(days=30):  # Change default here
    expiry = datetime.now() + timedelta(days=days)
    return expiry.isoformat()
```

### Customize Password Requirements

Edit `users/raw_sql_auth/auth_utils.py`, modify `validate_password()`:

```python
def validate_password(password):
    if len(password) < 12:  # Change minimum length
        return False, "Password must be at least 12 characters long"
    # Add more rules...
```

## 🔍 Troubleshooting

### "table auth_users already exists"
Tables are already initialized. No action needed.

### "no such table: auth_users"
Run initialization:
```bash
python manage.py init_raw_sql_auth
```

### "Invalid token"
- Check token is correct
- Verify token hasn't expired
- Ensure user hasn't logged out

### "Authentication required"
Add Authorization header:
```
Authorization: Token <your-token>
```

## 🌐 Frontend Integration

### JavaScript/Fetch Example

```javascript
// Register
const register = async (email, password, fullName) => {
  const response = await fetch('/api/users/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
};

// Login
const login = async (email, password) => {
  const response = await fetch('/api/users/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
};

// Authenticated Request
const getProfile = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/users/auth/me/', {
    headers: { 'Authorization': `Token ${token}` }
  });
  return await response.json();
};

// Logout
const logout = async () => {
  const token = localStorage.getItem('token');
  await fetch('/api/users/auth/logout/', {
    method: 'POST',
    headers: { 'Authorization': `Token ${token}` }
  });
  localStorage.removeItem('token');
};
```

## 📚 Additional Resources

- Full documentation: `users/raw_sql_auth/README.md`
- Example views: `users/raw_sql_auth/examples.py`
- Unit tests: `users/raw_sql_auth/test_auth.py`

## ⚠️ Production Checklist

- [ ] Use HTTPS (required for token security)
- [ ] Set `CORS_ALLOW_ALL_ORIGINS = False` in settings
- [ ] Add rate limiting for login/register endpoints
- [ ] Implement account lockout after failed attempts
- [ ] Set up logging for authentication events
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Enable Django's security middleware
- [ ] Implement token refresh mechanism
- [ ] Add CAPTCHA for registration
- [ ] Set up monitoring and alerts

## 🎯 Key Advantages

✅ **No ORM** - Pure SQL implementation
✅ **SQL Injection Safe** - Parameterized queries throughout
✅ **Token-based** - Stateless authentication
✅ **Secure** - Industry-standard password hashing
✅ **Well-tested** - Comprehensive unit tests
✅ **Easy to use** - Simple decorators for protection
✅ **Documented** - Extensive documentation and examples
✅ **Production-ready** - Built with security best practices

---

**Created for Django Backend Portfolio Project**
**License:** MIT
