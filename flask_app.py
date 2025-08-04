"""
Flask RESTful API for user authentication system.
Implements secure authentication with JWT tokens, comprehensive error handling, and input validation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import datetime
import os
from typing import Dict, Any, Optional
import logging

# Import existing modules
from auth import AuthManager, AuthResultType
from database import DatabaseManager, InMemoryStorageManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

# Enable CORS for cross-origin requests
CORS(app)

# Initialize storage and auth managers
# Use DatabaseManager for production, InMemoryStorageManager for development
storage_manager = DatabaseManager(db_path="users.db")
auth_manager = AuthManager(storage_manager)


def generate_jwt_token(user_data: Dict[str, Any]) -> str:
    """
    Generate JWT token for authenticated user.
    
    Args:
        user_data: User data to include in token
        
    Returns:
        JWT token string
    """
    payload = {
        'username': user_data['username'],
        'exp': datetime.datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """
    Decorator to require JWT authentication for protected routes.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header missing',
                'error': 'MISSING_AUTH_HEADER'
            }), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'success': False,
                'message': 'Invalid authorization header format',
                'error': 'INVALID_AUTH_FORMAT'
            }), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token',
                'error': 'INVALID_TOKEN'
            }), 401
        
        # Add user info to request context
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def validate_json_request(required_fields: list):
    """
    Decorator to validate JSON request data.
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type must be application/json',
                    'error': 'INVALID_CONTENT_TYPE'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Invalid JSON data',
                    'error': 'INVALID_JSON'
                }), 400
            
            # Check for required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'error': 'MISSING_FIELDS',
                    'missing_fields': missing_fields
                }), 400
            
            # Check for empty string values
            empty_fields = [field for field in required_fields if not data.get(field, '').strip()]
            if empty_fields:
                return jsonify({
                    'success': False,
                    'message': f'Empty values not allowed for fields: {", ".join(empty_fields)}',
                    'error': 'EMPTY_FIELDS',
                    'empty_fields': empty_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/register', methods=['POST'])
@validate_json_request(['username', 'password'])
def register():
    """
    Register a new user.
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        JSON response with registration result
    """
    try:
        data = request.get_json()
        username = data['username'].strip()
        password = data['password']
        
        # Attempt user registration
        result = auth_manager.register_user(username, password)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': result.message,
                'user': result.user_data
            }), 201
        else:
            # Map auth result types to HTTP status codes
            status_code = 400
            if result.result_type == AuthResultType.USER_EXISTS:
                status_code = 409  # Conflict
            elif result.result_type == AuthResultType.WEAK_PASSWORD:
                status_code = 400
            elif result.result_type == AuthResultType.INVALID_USERNAME:
                status_code = 400
            
            return jsonify({
                'success': False,
                'message': result.message,
                'error': result.result_type.value
            }), status_code
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error during registration',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/login', methods=['POST'])
@validate_json_request(['username', 'password'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        JSON response with JWT token
    """
    try:
        data = request.get_json()
        username = data['username'].strip()
        password = data['password']
        
        # Attempt user login
        result = auth_manager.login_user(username, password)
        
        if result.success:
            # Generate JWT token
            token = generate_jwt_token(result.user_data)
            
            return jsonify({
                'success': True,
                'message': result.message,
                'token': token,
                'user': result.user_data,
                'expires_in': app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
            }), 200
        else:
            # Map auth result types to HTTP status codes
            status_code = 401
            if result.result_type == AuthResultType.USER_NOT_FOUND:
                status_code = 404
            elif result.result_type == AuthResultType.INVALID_CREDENTIALS:
                status_code = 401
            elif result.result_type == AuthResultType.INVALID_INPUT:
                status_code = 400
            
            return jsonify({
                'success': False,
                'message': result.message,
                'error': result.result_type.value
            }), status_code
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error during login',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/get_user', methods=['GET'])
@require_auth
def get_user():
    """
    Retrieve user profile (authenticated endpoint).
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        JSON response with user profile data
    """
    try:
        username = request.user['username']
        
        # Get user data
        result = auth_manager.get_user_data(username)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': result.message,
                'user': result.user_data
            }), 200
        else:
            # Map auth result types to HTTP status codes
            status_code = 404
            if result.result_type == AuthResultType.USER_NOT_FOUND:
                status_code = 404
            elif result.result_type == AuthResultType.INVALID_USERNAME:
                status_code = 400
            
            return jsonify({
                'success': False,
                'message': result.message,
                'error': result.result_type.value
            }), status_code
            
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error while retrieving user data',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response indicating service status
    """
    return jsonify({
        'success': True,
        'message': 'Service is healthy',
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found',
        'error': 'NOT_FOUND'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'success': False,
        'message': 'Method not allowed',
        'error': 'METHOD_NOT_ALLOWED'
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': 'INTERNAL_ERROR'
    }), 500


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000) 