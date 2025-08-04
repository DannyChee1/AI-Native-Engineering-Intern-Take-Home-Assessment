"""
Authentication module for user management system.
Implements secure authentication with password hashing, input validation, and proper error handling.
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class AuthResultType(Enum):
    """Enumeration for authentication result types."""
    SUCCESS = "success"
    USER_EXISTS = "user_exists"
    USER_NOT_FOUND = "user_not_found"
    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_INPUT = "invalid_input"
    WEAK_PASSWORD = "weak_password"
    INVALID_USERNAME = "invalid_username"


@dataclass
class AuthResult:
    """Result object for authentication operations."""
    success: bool
    message: str
    result_type: AuthResultType
    user_data: Optional[Dict[str, Any]] = None


class AuthManager:
    """
    Authentication manager with secure password handling and input validation.
    
    Responsibilities:
    - User registration with password validation
    - User login with secure password verification
    - Input validation and sanitization
    - Password strength enforcement
    """
    
    def __init__(self, storage_manager):
        """
        Initialize the authentication manager.
        
        Args:
            storage_manager: Storage interface for user data persistence
        """
        self.storage = storage_manager
        self._password_min_length = 8
        self._password_max_length = 128
        self._username_min_length = 3
        self._username_max_length = 50
        
    def register_user(self, username: str, password: str) -> AuthResult:
        """
        Register a new user with secure password hashing.
        
        Args:
            username: User's desired username
            password: User's password (will be hashed)
            
        Returns:
            AuthResult: Result of the registration attempt
        """
        # Input validation
        validation_result = self._validate_registration_input(username, password)
        if not validation_result.success:
            return validation_result
            
        # Check if user already exists
        if self.storage.user_exists(username):
            return AuthResult(
                success=False,
                message="User already exists",
                result_type=AuthResultType.USER_EXISTS
            )
            
        # Hash password with salt
        salt, hashed_password = self._hash_password(password)
        
        # Create user data
        user_data = {
            'username': username,
            'password_hash': hashed_password,
            'salt': salt,
            'created_at': self._get_current_timestamp()
        }
        
        # Store user data
        try:
            self.storage.create_user(user_data)
            return AuthResult(
                success=True,
                message="User registered successfully",
                result_type=AuthResultType.SUCCESS,
                user_data={'username': username}
            )
        except Exception as e:
            return AuthResult(
                success=False,
                message=f"Registration failed: {str(e)}",
                result_type=AuthResultType.INVALID_INPUT
            )
    
    def login_user(self, username: str, password: str) -> AuthResult:
        """
        Authenticate a user with secure password verification.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            AuthResult: Result of the login attempt
        """
        # Input validation
        if not self._validate_login_input(username, password):
            return AuthResult(
                success=False,
                message="Invalid input provided",
                result_type=AuthResultType.INVALID_INPUT
            )
            
        # Get user data
        user_data = self.storage.get_user(username)
        if not user_data:
            return AuthResult(
                success=False,
                message="User not found",
                result_type=AuthResultType.USER_NOT_FOUND
            )
            
        # Verify password
        if self._verify_password(password, user_data['password_hash'], user_data['salt']):
            return AuthResult(
                success=True,
                message="Login successful",
                result_type=AuthResultType.SUCCESS,
                user_data={'username': username}
            )
        else:
            return AuthResult(
                success=False,
                message="Invalid credentials",
                result_type=AuthResultType.INVALID_CREDENTIALS
            )
    
    def get_user_data(self, username: str) -> AuthResult:
        """
        Retrieve user data (excluding sensitive information).
        
        Args:
            username: Username to retrieve data for
            
        Returns:
            AuthResult: Result with user data (password excluded)
        """
        if not self._validate_username(username):
            return AuthResult(
                success=False,
                message="Invalid username format",
                result_type=AuthResultType.INVALID_USERNAME
            )
            
        user_data = self.storage.get_user(username)
        if not user_data:
            return AuthResult(
                success=False,
                message="User not found",
                result_type=AuthResultType.USER_NOT_FOUND
            )
            
        # Return user data without sensitive information
        safe_user_data = {
            'username': user_data['username'],
            'created_at': user_data.get('created_at', 'Unknown')
        }
        
        return AuthResult(
            success=True,
            message="User data retrieved successfully",
            result_type=AuthResultType.SUCCESS,
            user_data=safe_user_data
        )
    
    def _validate_registration_input(self, username: str, password: str) -> AuthResult:
        """Validate registration input parameters."""
        # Username validation
        if not self._validate_username(username):
            return AuthResult(
                success=False,
                message="Username must be 3-50 characters and contain only letters, numbers, and underscores",
                result_type=AuthResultType.INVALID_USERNAME
            )
            
        # Password validation
        password_validation = self._validate_password(password)
        if not password_validation['valid']:
            return AuthResult(
                success=False,
                message=password_validation['message'],
                result_type=AuthResultType.WEAK_PASSWORD
            )
            
        return AuthResult(
            success=True,
            message="Input validation passed",
            result_type=AuthResultType.SUCCESS
        )
    
    def _validate_login_input(self, username: str, password: str) -> bool:
        """Validate login input parameters."""
        return (self._validate_username(username) and 
                self._validate_password(password)['valid'])
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False
            
        if len(username) < self._username_min_length or len(username) > self._username_max_length:
            return False
            
        # Username should contain only letters, numbers, and underscores
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))
    
    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        if not password or not isinstance(password, str):
            return {'valid': False, 'message': 'Password is required'}
            
        if len(password) < self._password_min_length:
            return {
                'valid': False, 
                'message': f'Password must be at least {self._password_min_length} characters long'
            }
            
        if len(password) > self._password_max_length:
            return {
                'valid': False,
                'message': f'Password must be no more than {self._password_max_length} characters long'
            }
            
        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not re.search(r'[A-Z]', password):
            return {'valid': False, 'message': 'Password must contain at least one uppercase letter'}
            
        if not re.search(r'[a-z]', password):
            return {'valid': False, 'message': 'Password must contain at least one lowercase letter'}
            
        if not re.search(r'\d', password):
            return {'valid': False, 'message': 'Password must contain at least one number'}
            
        return {'valid': True, 'message': 'Password is strong'}
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash password with salt using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Tuple of (salt, hashed_password)
        """
        salt = secrets.token_hex(16)  # 32 character hex string
        salted_password = password + salt
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        return salt, hashed
    
    def _verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """
        Verify password against stored hash and salt.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored password hash
            stored_salt: Stored salt
            
        Returns:
            True if password matches, False otherwise
        """
        salted_password = password + stored_salt
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed == stored_hash
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat() 