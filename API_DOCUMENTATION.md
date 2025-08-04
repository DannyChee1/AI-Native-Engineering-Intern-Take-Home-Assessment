# Flask RESTful API Documentation

A comprehensive Flask RESTful API for user authentication with JWT tokens, secure password handling, and comprehensive error handling.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)
- [Testing](#testing)

## Overview

This Flask API provides secure user authentication with the following features:

- **RESTful Design**: Follows REST conventions with proper HTTP methods and status codes
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Detailed error responses with appropriate HTTP status codes
- **Password Security**: Secure password hashing with salt
- **CORS Support**: Cross-origin request support

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python flask_app.py
   ```

3. **Test the API**:
   ```bash
   python test_unittest.py
   ```

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response**:
```json
{
  "success": true,
  "message": "Service is healthy",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

**Status Code**: `200 OK`

---

### 2. User Registration

**POST** `/register`

Register a new user account.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Validation Rules**:
- Username: 3-50 characters, letters, numbers, and underscores only
- Password: 8-128 characters, must contain uppercase, lowercase, and number

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "username": "john_doe"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input (weak password, invalid username)
- `409 Conflict`: User already exists

---

### 3. User Login

**POST** `/login`

Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "username": "john_doe"
  },
  "expires_in": 3600
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input format
- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found

---

### 4. Get User Profile

**GET** `/get_user`

Retrieve user profile (requires authentication).

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "User data retrieved successfully",
  "user": {
    "username": "john_doe",
    "created_at": "2024-01-15T10:30:00.000000"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found

## Authentication

### JWT Token Format

The API uses JWT (JSON Web Tokens) for authentication:

1. **Token Structure**: `Bearer <token>`
2. **Expiration**: 1 hour from creation
3. **Algorithm**: HS256

### Using Authentication

Include the JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
     http://localhost:5000/get_user
```

## Error Handling

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET requests |
| 201 | Created | Successful POST requests (registration) |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Authentication failed, missing/invalid token |
| 404 | Not Found | User not found, endpoint not found |
| 405 | Method Not Allowed | Wrong HTTP method |
| 409 | Conflict | User already exists |
| 500 | Internal Server Error | Server-side errors |

### Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "message": "Human-readable error message",
  "error": "ERROR_CODE"
}
```

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `MISSING_FIELDS` | Required fields missing |
| `EMPTY_FIELDS` | Required fields are empty |
| `INVALID_JSON` | Malformed JSON data |
| `INVALID_CONTENT_TYPE` | Wrong Content-Type header |
| `MISSING_AUTH_HEADER` | Authorization header missing |
| `INVALID_AUTH_FORMAT` | Wrong Authorization header format |
| `INVALID_TOKEN` | JWT token is invalid or expired |
| `USER_EXISTS` | Username already taken |
| `USER_NOT_FOUND` | User doesn't exist |
| `INVALID_CREDENTIALS` | Wrong username/password |
| `WEAK_PASSWORD` | Password doesn't meet requirements |
| `INVALID_USERNAME` | Username format is invalid |

## Usage Examples

### 1. Register a New User

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

### 3. Get User Profile (Authenticated)

```bash
curl -X GET http://localhost:5000/get_user \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 4. Check API Health

```bash
curl -X GET http://localhost:5000/health
```

## Testing

### Automated Testing

Run the comprehensive test suite:

```bash
python test_unittest.py
```

This will test:
- ✅ Health check endpoint
- ✅ User registration (valid and invalid)
- ✅ User login
- ✅ Protected endpoint access
- ✅ Error handling scenarios

### Manual Testing with curl

1. **Start the server**:
   ```bash
   python flask_app.py
   ```

2. **Test registration**:
   ```bash
   curl -X POST http://localhost:5000/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "TestPass123"}'
   ```

3. **Test login**:
   ```bash
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "TestPass123"}'
   ```

4. **Test protected endpoint**:
   ```bash
   curl -X GET http://localhost:5000/get_user \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Security Features

- **Password Hashing**: SHA-256 with salt
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **CORS Support**: Configurable cross-origin requests
- **Error Handling**: No sensitive information in error messages

## Configuration

### Environment Variables

Set these environment variables for production:

```bash
export SECRET_KEY="your-secret-key-change-in-production"
export JWT_SECRET_KEY="your-jwt-secret-key-change-in-production"
```

### Database Configuration

The API uses SQLite database for all operations:

- **Database**: SQLite database (`users.db`)
- **Persistence**: All data is persisted to disk
- **Testing**: Uses temporary database files for testing

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin request support
- **PyJWT**: JWT token handling
- **Werkzeug**: WSGI utilities

## File Structure

```
├── flask_app.py          # Main Flask application (SQLite-only)
├── auth.py              # Authentication module
├── database.py          # SQLite database operations
├── test_unittest.py     # Comprehensive test suite (database, auth, API)
├── demo.py              # SQLite demo with persistence
├── demo_refactored.py   # Comprehensive SQLite demo
├── requirements.txt     # Python dependencies
└── API_DOCUMENTATION.md # This documentation
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `flask_app.py`
2. **Database errors**: Check file permissions for `users.db`
3. **Import errors**: Install dependencies with `pip install -r requirements.txt`
4. **CORS issues**: Configure CORS settings in `flask_app.py`

### Logs

The application logs to console with INFO level. Check for:
- Authentication attempts
- Database operations
- Error details

## Contributing

1. Follow RESTful conventions
2. Add comprehensive error handling
3. Include input validation
4. Write tests for new endpoints
5. Update documentation

## License

This project is for demonstration purposes. 