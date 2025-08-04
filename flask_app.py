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
from database import DatabaseManager

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

# Global storage and auth managers (will be initialized)
storage_manager = None
auth_manager = None


def initialize_managers(db_path: str = "users.db"):
    """Initialize storage and auth managers with specified database path."""
    global storage_manager, auth_manager
    storage_manager = DatabaseManager(db_path=db_path)
    auth_manager = AuthManager(storage_manager)


# Initialize with default database for production
initialize_managers()


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
        Decorated function
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
                    'error': 'MISSING_FIELDS'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/register', methods=['POST'])
@validate_json_request(['username', 'password'])
def register():
    """
    Register a new user.
    
    Expected JSON:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
        JSON response with success status and message
    """
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        # Attempt to register user
        result = auth_manager.register_user(username, password)
        
        if result.success:
            logger.info(f"User '{username}' registered successfully")
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'username': username
                }
            }), 201
        else:
            # Handle different failure types
            if result.result_type == AuthResultType.USER_EXISTS:
                logger.warning(f"Registration failed: User '{username}' already exists")
                return jsonify({
                    'success': False,
                    'message': 'User already exists',
                    'error': 'USER_EXISTS'
                }), 409
            elif result.result_type == AuthResultType.INVALID_USERNAME:
                logger.warning(f"Registration failed: Invalid username '{username}'")
                return jsonify({
                    'success': False,
                    'message': result.message,
                    'error': 'INVALID_USERNAME'
                }), 400
            elif result.result_type == AuthResultType.WEAK_PASSWORD:
                logger.warning(f"Registration failed: Weak password for user '{username}'")
                return jsonify({
                    'success': False,
                    'message': result.message,
                    'error': 'WEAK_PASSWORD'
                }), 400
            else:
                logger.error(f"Registration failed for user '{username}': {result.message}")
                return jsonify({
                    'success': False,
                    'message': 'Registration failed',
                    'error': 'REGISTRATION_FAILED'
                }), 400
                
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/login', methods=['POST'])
@validate_json_request(['username', 'password'])
def login():
    """
    Authenticate user and return JWT token.
    
    Expected JSON:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
        JSON response with JWT token on success
    """
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        # Attempt to authenticate user
        result = auth_manager.login_user(username, password)
        
        if result.success:
            # Generate JWT token
            token = generate_jwt_token({'username': username})
            
            logger.info(f"User '{username}' logged in successfully")
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'data': {
                    'username': username
                }
            }), 200
        else:
            # Handle different failure types
            if result.result_type == AuthResultType.USER_NOT_FOUND:
                logger.warning(f"Login failed: User '{username}' not found")
                return jsonify({
                    'success': False,
                    'message': 'User not found',
                    'error': 'USER_NOT_FOUND'
                }), 404
            elif result.result_type == AuthResultType.INVALID_CREDENTIALS:
                logger.warning(f"Login failed: Invalid credentials for user '{username}'")
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials',
                    'error': 'INVALID_CREDENTIALS'
                }), 401
            else:
                logger.error(f"Login failed for user '{username}': {result.message}")
                return jsonify({
                    'success': False,
                    'message': 'Login failed',
                    'error': 'LOGIN_FAILED'
                }), 400
                
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/get_user', methods=['GET'])
@require_auth
def get_user():
    """
    Get current user data (requires authentication).
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        JSON response with user data
    """
    try:
        username = request.user['username']
        
        # Get user data
        result = auth_manager.get_user_data(username)
        
        if result.success:
            logger.info(f"User data retrieved for '{username}'")
            return jsonify({
                'success': True,
                'message': 'User data retrieved successfully',
                'user': result.user_data
            }), 200
        else:
            logger.error(f"Failed to retrieve user data for '{username}': {result.message}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve user data',
                'error': 'USER_DATA_ERROR'
            }), 500
                
    except Exception as e:
        logger.error(f"Unexpected error retrieving user data: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'INTERNAL_ERROR'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    try:
        return jsonify({
            'success': True,
            'message': 'Service is healthy',
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Service is unhealthy',
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Error handlers
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
    app.run(debug=True, host='0.0.0.0', port=5000) 