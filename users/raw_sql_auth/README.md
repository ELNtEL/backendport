# Raw SQL Token Authentication System

A complete Django authentication system using **raw SQL queries** with **parameterized statements** for protection against SQL injection attacks. This implementation does **not use Django ORM**.

## Features

- **User Registration** with password validation and hashing
- **User Login** with token generation
- **Token-based Authentication** for protected routes
- **Password Security** using SHA-256 with salt
- **SQL Injection Protection** using parameterized queries
- **Token Expiration** management (30-day default)
- **Optional Authentication** decorator for mixed public/private views
- **No Django ORM** - pure SQL implementation

## Architecture

### Database Tables

#### `auth_users`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- email: TEXT UNIQUE NOT NULL
- password_hash: TEXT NOT NULL (format: "salt$hash")
- full_name: TEXT NOT NULL
- is_active: INTEGER DEFAULT 1
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### `auth_tokens`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- user_id: INTEGER NOT NULL (FK to auth_users.id)
- token: TEXT UNIQUE NOT NULL (64-char hex)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- expires_at: TIMESTAMP NOT NULL
- is_active: INTEGER DEFAULT 1
```

### Security Features

1. **Password Hashing**: SHA-256 with random 32-byte salt
2. **SQL Injection Protection**: All queries use parameterized statements (`?` placeholders)
3. **Timing Attack Prevention**: Constant-time password comparison
4. **Token Security**: Cryptographically secure 64-character tokens
5. **Token Expiration**: Automatic expiration after 30 days (configurable)

## Installation & Setup

### 1. Initialize Database Tables

Run the management command to create the authentication tables:

```bash
python manage.py init_raw_sql_auth
```

Or use Python directly:

```bash
python -c "from users.raw_sql_auth.db_schema import init_auth_tables; init_auth_tables()"
```

### 2. URL Configuration

The URLs are already configured in `users/urls.py`. All raw SQL auth endpoints are available under `/api/users/auth/`:

```
POST   /api/users/auth/register/          - User registration
POST   /api/users/auth/login/             - User login
POST   /api/users/auth/logout/            - User logout
GET    /api/users/auth/me/                - Get current user info
GET    /api/users/auth/protected/         - Example protected endpoint
GET    /api/users/auth/optional/          - Example optional auth endpoint
POST   /api/users/auth/protected-action/  - Example protected POST endpoint
```

## API Usage

### 1. User Registration

**Endpoint**: `POST /api/users/auth/register/`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Success Response** (201):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00"
  },
  "token": "a1b2c3d4e5f6...",
  "expires_at": "2025-02-14T10:30:00"
}
```

**Error Response** (400):
```json
{
  "error": "Password must be at least 8 characters long"
}
```

### 2. User Login

**Endpoint**: `POST /api/users/auth/login/`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200):
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00"
  },
  "token": "x9y8z7w6v5u4...",
  "expires_at": "2025-02-14T11:00:00"
}
```

**Error Response** (401):
```json
{
  "error": "Invalid email or password"
}
```

### 3. User Logout

**Endpoint**: `POST /api/users/auth/logout/`

**Headers**:
```
Authorization: Token a1b2c3d4e5f6...
```

**Success Response** (200):
```json
{
  "message": "Logout successful"
}
```

### 4. Get Current User Info

**Endpoint**: `GET /api/users/auth/me/`

**Headers**:
```
Authorization: Token a1b2c3d4e5f6...
```

**Success Response** (200):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00"
  }
}
```

## Using Authentication in Your Views

### Protected View (Authentication Required)

```python
from users.raw_sql_auth.decorators import token_required
from django.http import JsonResponse

@token_required
def my_protected_view(request):
    # Authentication is guaranteed
    # User info is attached to request object
    user_id = request.user_id
    user_email = request.user_email
    user_full_name = request.user_full_name

    return JsonResponse({
        'message': f'Hello, {user_full_name}!',
        'user_id': user_id
    })
```

### Optional Authentication

```python
from users.raw_sql_auth.decorators import optional_token_auth
from django.http import JsonResponse

@optional_token_auth
def my_optional_view(request):
    if hasattr(request, 'user_id'):
        # User is authenticated
        return JsonResponse({
            'message': f'Welcome back, {request.user_full_name}!'
        })
    else:
        # Anonymous user
        return JsonResponse({
            'message': 'Welcome, guest!'
        })
```

## Testing with cURL

### Register a new user
```bash
curl -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Access protected endpoint
```bash
# Save the token from login response
TOKEN="your-token-here"

curl -X GET http://localhost:8000/api/users/auth/me/ \
  -H "Authorization: Token $TOKEN"
```

### Logout
```bash
curl -X POST http://localhost:8000/api/users/auth/logout/ \
  -H "Authorization: Token $TOKEN"
```

## SQL Injection Protection Examples

All queries use parameterized statements to prevent SQL injection:

### ✅ SAFE (Parameterized Query)
```python
cursor.execute(
    "SELECT * FROM auth_users WHERE email = ?",
    (email,)  # Parameters passed separately
)
```

### ❌ UNSAFE (String Interpolation)
```python
# DON'T DO THIS!
cursor.execute(f"SELECT * FROM auth_users WHERE email = '{email}'")
```

## File Structure

```
users/raw_sql_auth/
├── __init__.py
├── README.md                 # This file
├── db_schema.py             # Database table definitions
├── auth_utils.py            # Password hashing, token generation
├── views.py                 # Registration, login, logout endpoints
├── decorators.py            # @token_required, @optional_token_auth
├── examples.py              # Example protected views
└── urls.py                  # URL routing
```

## Customization

### Change Token Expiration

Edit `auth_utils.py`:

```python
def get_token_expiry(days=30):  # Change default here
    expiry = datetime.now() + timedelta(days=days)
    return expiry.isoformat()
```

Or pass custom value when calling:
```python
expires_at = get_token_expiry(days=7)  # 7-day expiration
```

### Change Password Requirements

Edit `auth_utils.py`, modify `validate_password()` function.

### Use Different Hashing Algorithm

Edit `auth_utils.py`:

```python
def hash_password(password):
    salt = secrets.token_hex(32)
    # Change to bcrypt, argon2, etc.
    pwd_hash = hashlib.sha512((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"
```

## Database Management

### Drop Tables (Careful!)
```python
from users.raw_sql_auth.db_schema import drop_auth_tables
drop_auth_tables()
```

### Query Database Directly
```python
from users.raw_sql_auth.db_schema import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM auth_users")
users = cursor.fetchall()
cursor.close()
conn.close()
```

## Troubleshooting

### Error: "table auth_users already exists"
The tables are already created. No action needed.

### Error: "no such table: auth_users"
Run the initialization command:
```bash
python manage.py init_raw_sql_auth
```

### Error: "Invalid token"
- Check that the token is correct
- Verify token hasn't expired
- Ensure token is active (not logged out)

### Error: "Authentication required"
- Include the Authorization header
- Use format: `Authorization: Token <your-token>`
- Check that the token is valid

## Security Best Practices

1. **Always use HTTPS** in production to prevent token interception
2. **Store tokens securely** on the client side (httpOnly cookies recommended)
3. **Implement token refresh** for long-lived sessions
4. **Rate limit** login endpoints to prevent brute force attacks
5. **Log authentication attempts** for security monitoring
6. **Use environment variables** for sensitive configuration
7. **Regularly rotate tokens** for active users
8. **Implement account lockout** after failed login attempts

## Migration from ORM-based Auth

This system runs alongside the existing Django ORM authentication. To migrate:

1. Export users from Django's User model
2. Insert into `auth_users` table with password re-hashing
3. Update client applications to use new endpoints
4. Disable old authentication endpoints

## License

Part of the Django backend portfolio project.
