"""
Database module for user management system.
Provides SQLite database operations with proper connection management, security, and error handling.
Consolidated storage functionality with support for both in-memory and SQLite storage.
"""

import sqlite3
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List, Tuple, Union
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class DatabaseResultType(Enum):
    """Enumeration for database operation result types."""
    SUCCESS = "success"
    USER_EXISTS = "user_exists"
    USER_NOT_FOUND = "user_not_found"
    DATABASE_ERROR = "database_error"
    CONNECTION_ERROR = "connection_error"
    VALIDATION_ERROR = "validation_error"
    HASHING_ERROR = "hashing_error"


@dataclass
class DatabaseResult:
    """Result object for database operations."""
    success: bool
    message: str
    result_type: DatabaseResultType
    data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None


class StorageManager(ABC):
    """
    Abstract base class for storage managers.
    Defines the interface for user data persistence.
    """
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in storage."""
        pass
    
    @abstractmethod
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data by username."""
        pass
    
    @abstractmethod
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        pass
    
    @abstractmethod
    def update_user(self, username: str, user_data: Dict[str, Any]) -> bool:
        """Update user data."""
        pass
    
    @abstractmethod
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (excluding sensitive data)."""
        pass


class InMemoryStorageManager(StorageManager):
    """
    In-memory storage implementation for development and testing.
    Data is lost when the application restarts.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._users = {}
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in memory storage."""
        try:
            username = user_data['username']
            if username in self._users:
                return False
            self._users[username] = user_data.copy()
            return True
        except KeyError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data by username."""
        return self._users.get(username)
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return username in self._users
    
    def update_user(self, username: str, user_data: Dict[str, Any]) -> bool:
        """Update user data."""
        if username not in self._users:
            return False
        self._users[username] = user_data.copy()
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username not in self._users:
            return False
        del self._users[username]
        return True
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (excluding sensitive data)."""
        users = []
        for username, user_data in self._users.items():
            safe_user_data = {
                'username': user_data['username'],
                'created_at': user_data.get('created_at', 'Unknown')
            }
            users.append(safe_user_data)
        return users
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self._users)


class DatabaseManager(StorageManager):
    """
    SQLite database manager with secure password handling and proper connection management.
    
    Responsibilities:
    - Database connection management with context managers
    - Secure password hashing and verification
    - User data CRUD operations
    - Comprehensive error handling and logging
    - Database schema management
    """
    
    def __init__(self, db_path: str = "users.db", enable_logging: bool = True):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file
            enable_logging: Whether to enable database logging
        """
        self.db_path = Path(db_path)
        self.enable_logging = enable_logging
        
        # Configure logging
        if enable_logging:
            self._setup_logging()
        
        # Initialize database schema
        self._init_database()
    
    def _setup_logging(self) -> None:
        """Configure database logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('database.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self) -> None:
        """Initialize database schema and tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create users table with proper constraints
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        email TEXT UNIQUE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT,
                        last_login TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        failed_login_attempts INTEGER DEFAULT 0,
                        account_locked_until TEXT
                    )
                ''')
                
                # Create user_sessions table for session management
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions (session_token)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)')
                
                conn.commit()
                
                if self.enable_logging:
                    self.logger.info(f"Database initialized successfully at {self.db_path}")
                    
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
            
        Raises:
            DatabaseError: If connection fails
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable row factory for named access
            yield conn
        except sqlite3.Error as e:
            if self.enable_logging:
                self.logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError(f"Connection failed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Create a new user with secure password hashing.
        
        Args:
            user_data: Dictionary containing user data (username, password, email, etc.)
            
        Returns:
            bool: True if user created successfully, False otherwise
        """
        try:
            username = user_data.get('username')
            password = user_data.get('password')
            email = user_data.get('email')
            
            # Input validation
            validation_result = self._validate_user_input(username, password, email)
            if not validation_result.success:
                return False
            
            # Check if user already exists
            if self.user_exists(username):
                return False
            
            # Hash password with salt if not already hashed
            if 'password_hash' not in user_data:
                salt, hashed_password = self._hash_password(password)
                user_data['password_hash'] = hashed_password
                user_data['salt'] = salt
            
            # Ensure required fields
            if 'created_at' not in user_data:
                user_data['created_at'] = self._get_current_timestamp()
            
            # Store user in database
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, salt, email, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_data['username'],
                    user_data['password_hash'],
                    user_data['salt'],
                    user_data.get('email'),
                    user_data['created_at']
                ))
                conn.commit()
                
                if self.enable_logging:
                    self.logger.info(f"User '{username}' created successfully")
                
                return True
                
        except sqlite3.IntegrityError as e:
            if self.enable_logging:
                self.logger.warning(f"Integrity error creating user '{username}': {str(e)}")
            return False
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error creating user '{username}': {str(e)}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> DatabaseResult:
        """
        Authenticate a user with secure password verification.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            DatabaseResult: Result of the authentication attempt
        """
        try:
            # Get user data
            user_data = self.get_user(username)
            if not user_data:
                return DatabaseResult(
                    success=False,
                    message="User not found",
                    result_type=DatabaseResultType.USER_NOT_FOUND
                )
            
            user = user_data
            
            # Check if account is locked
            if user.get('account_locked_until'):
                lock_time = datetime.fromisoformat(user['account_locked_until'])
                if datetime.now() < lock_time:
                    return DatabaseResult(
                        success=False,
                        message="Account is temporarily locked",
                        result_type=DatabaseResultType.VALIDATION_ERROR
                    )
            
            # Verify password
            if self._verify_password(password, user['password_hash'], user['salt']):
                # Reset failed login attempts on successful login
                self._reset_failed_login_attempts(user['id'])
                
                # Update last login time
                self._update_last_login(user['id'])
                
                if self.enable_logging:
                    self.logger.info(f"User '{username}' authenticated successfully")
                
                return DatabaseResult(
                    success=True,
                    message="Authentication successful",
                    result_type=DatabaseResultType.SUCCESS,
                    data={'user_id': user['id'], 'username': user['username']}
                )
            else:
                # Increment failed login attempts
                self._increment_failed_login_attempts(user['id'])
                
                if self.enable_logging:
                    self.logger.warning(f"Failed authentication attempt for user '{username}'")
                
                return DatabaseResult(
                    success=False,
                    message="Invalid credentials",
                    result_type=DatabaseResultType.VALIDATION_ERROR
                )
                
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error authenticating user '{username}': {str(e)}")
            return DatabaseResult(
                success=False,
                message="Authentication failed",
                result_type=DatabaseResultType.DATABASE_ERROR,
                error_details=str(e)
            )
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user data by username.
        
        Args:
            username: Username to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: User data dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, password_hash, salt, email, created_at, updated_at, 
                           last_login, is_active, failed_login_attempts, account_locked_until
                    FROM users WHERE username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'password_hash': row[2],
                        'salt': row[3],
                        'email': row[4],
                        'created_at': row[5],
                        'updated_at': row[6],
                        'last_login': row[7],
                        'is_active': bool(row[8]),
                        'failed_login_attempts': row[9],
                        'account_locked_until': row[10]
                    }
                else:
                    return None
                    
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error retrieving user '{username}': {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: int) -> DatabaseResult:
        """
        Retrieve user data by user ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            DatabaseResult: Result with user data
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, created_at, updated_at, last_login,
                           is_active, failed_login_attempts, account_locked_until
                    FROM users WHERE id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    user_data = dict(row)
                    return DatabaseResult(
                        success=True,
                        message="User retrieved successfully",
                        result_type=DatabaseResultType.SUCCESS,
                        data=user_data
                    )
                else:
                    return DatabaseResult(
                        success=False,
                        message="User not found",
                        result_type=DatabaseResultType.USER_NOT_FOUND
                    )
                    
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error retrieving user ID {user_id}: {str(e)}")
            return DatabaseResult(
                success=False,
                message="Failed to retrieve user",
                result_type=DatabaseResultType.DATABASE_ERROR,
                error_details=str(e)
            )
    
    def update_user(self, username: str, user_data: Dict[str, Any]) -> bool:
        """
        Update user data.
        
        Args:
            username: Username to update
            user_data: Dictionary containing updated user data
            
        Returns:
            bool: True if user updated successfully, False otherwise
        """
        try:
            # Get user ID first
            user = self.get_user(username)
            if not user:
                return False
            
            user_id = user['id']
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for field, value in user_data.items():
                if field in ['email', 'is_active']:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
                elif field == 'password':
                    # Hash new password
                    salt, hashed_password = self._hash_password(value)
                    update_fields.extend(["password_hash = ?", "salt = ?"])
                    update_values.extend([hashed_password, salt])
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = ?")
            update_values.append(self._get_current_timestamp())
            update_values.append(user_id)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                
                if cursor.rowcount > 0:
                    if self.enable_logging:
                        self.logger.info(f"User '{username}' updated successfully")
                    return True
                else:
                    return False
                    
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error updating user '{username}': {str(e)}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user by username.
        
        Args:
            username: Username to delete
            
        Returns:
            bool: True if user deleted successfully, False otherwise
        """
        try:
            # Get user ID first
            user = self.get_user(username)
            if not user:
                return False
            
            user_id = user['id']
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                
                if cursor.rowcount > 0:
                    if self.enable_logging:
                        self.logger.info(f"User '{username}' deleted successfully")
                    return True
                else:
                    return False
                    
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error deleting user '{username}': {str(e)}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retrieve all users (excluding sensitive data).
        
        Returns:
            List[Dict[str, Any]]: List of user data dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, email, created_at, updated_at, last_login,
                           is_active, failed_login_attempts, account_locked_until
                    FROM users
                    ORDER BY created_at DESC
                ''')
                
                rows = cursor.fetchall()
                users = []
                
                for row in rows:
                    user_data = {
                        'username': row[0],
                        'email': row[1],
                        'created_at': row[2],
                        'updated_at': row[3],
                        'last_login': row[4],
                        'is_active': bool(row[5]),
                        'failed_login_attempts': row[6],
                        'account_locked_until': row[7]
                    }
                    users.append(user_data)
                
                return users
                
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error retrieving all users: {str(e)}")
            return []
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
                return cursor.fetchone() is not None
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error checking if user '{username}' exists: {str(e)}")
            return False
    
    def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            int: Total number of users
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                return cursor.fetchone()[0]
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error getting user count: {str(e)}")
            return 0
    
    def _validate_user_input(self, username: str, password: str, email: Optional[str] = None) -> DatabaseResult:
        """Validate user input data."""
        # Username validation
        if not username or len(username) < 3 or len(username) > 50:
            return DatabaseResult(
                success=False,
                message="Username must be 3-50 characters long",
                result_type=DatabaseResultType.VALIDATION_ERROR
            )
        
        # Password validation
        if not password or len(password) < 8:
            return DatabaseResult(
                success=False,
                message="Password must be at least 8 characters long",
                result_type=DatabaseResultType.VALIDATION_ERROR
            )
        
        # Email validation (if provided)
        if email and not self._is_valid_email(email):
            return DatabaseResult(
                success=False,
                message="Invalid email format",
                result_type=DatabaseResultType.VALIDATION_ERROR
            )
        
        return DatabaseResult(
            success=True,
            message="Input validation passed",
            result_type=DatabaseResultType.SUCCESS
        )
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
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
            bool: True if password matches, False otherwise
        """
        salted_password = password + stored_salt
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed == stored_hash
    
    def _increment_failed_login_attempts(self, user_id: int) -> None:
        """Increment failed login attempts for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = failed_login_attempts + 1
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error incrementing failed login attempts for user {user_id}: {str(e)}")
    
    def _reset_failed_login_attempts(self, user_id: int) -> None:
        """Reset failed login attempts for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = 0, account_locked_until = NULL
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error resetting failed login attempts for user {user_id}: {str(e)}")
    
    def _update_last_login(self, user_id: int) -> None:
        """Update last login time for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET last_login = ?
                    WHERE id = ?
                ''', (self._get_current_timestamp(), user_id))
                conn.commit()
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error updating last login for user {user_id}: {str(e)}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO format string."""
        return datetime.now().isoformat()


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass 