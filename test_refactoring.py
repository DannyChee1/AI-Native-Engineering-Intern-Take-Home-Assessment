#!/usr/bin/env python3
"""
Comprehensive test suite for SQLite-only user authentication system.
Tests data persistence, CRUD operations, and authentication flows.
"""

import os
import tempfile
import shutil
from database import DatabaseManager
from auth import AuthManager


def test_sqlite_storage_basic():
    """Test basic SQLite storage functionality."""
    print("Testing SQLite Storage - Basic Operations...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        auth = AuthManager(storage)
        
        # Test user registration
        result = auth.register_user("testuser", "SecurePass123")
        assert result.success, f"Registration failed: {result.message}"
        print("✓ User registration works")
        
        # Test user login
        result = auth.login_user("testuser", "SecurePass123")
        assert result.success, f"Login failed: {result.message}"
        print("✓ User login works")
        
        # Test user existence
        assert storage.user_exists("testuser"), "User existence check failed"
        print("✓ User existence check works")
        
        # Test get user data
        user_data = storage.get_user("testuser")
        assert user_data is not None, "Get user data failed"
        assert user_data['username'] == "testuser", "User data mismatch"
        print("✓ Get user data works")
        
        # Test get all users
        all_users = storage.get_all_users()
        assert len(all_users) == 1, f"Expected 1 user, got {len(all_users)}"
        print("✓ Get all users works")
        
        # Test user count
        assert storage.get_user_count() == 1, "User count mismatch"
        print("✓ User count works")
        
        # Test update user
        update_data = {'email': 'test@example.com'}
        assert storage.update_user("testuser", update_data), "Update user failed"
        print("✓ Update user works")
        
        # Test delete user
        assert storage.delete_user("testuser"), "Delete user failed"
        print("✓ Delete user works")
        
        print("✅ SQLite Storage - Basic Operations: All tests passed!\n")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def test_sqlite_persistence():
    """Test data persistence across 'app restarts'."""
    print("Testing SQLite Storage - Data Persistence...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        # First "app session" - register users
        print("  Session 1: Registering users...")
        storage1 = DatabaseManager(test_db, enable_logging=False)
        auth1 = AuthManager(storage1)
        
        # Register multiple users
        users = [
            ("alice", "AlicePass123"),
            ("bob", "BobPass456"),
            ("charlie", "CharliePass789")
        ]
        
        for username, password in users:
            result = auth1.register_user(username, password)
            assert result.success, f"Registration failed for {username}: {result.message}"
            print(f"    ✓ Registered {username}")
        
        # Verify users exist in first session
        assert storage1.get_user_count() == 3, f"Expected 3 users, got {storage1.get_user_count()}"
        print("    ✓ All users registered successfully")
        
        # "Restart app" - create new storage manager with same database
        print("  Session 2: Verifying persistence...")
        storage2 = DatabaseManager(test_db, enable_logging=False)
        auth2 = AuthManager(storage2)
        
        # Verify all users still exist
        assert storage2.get_user_count() == 3, f"Expected 3 users after restart, got {storage2.get_user_count()}"
        print("    ✓ User count persisted")
        
        # Test login for all users
        for username, password in users:
            result = auth2.login_user(username, password)
            assert result.success, f"Login failed for {username}: {result.message}"
            print(f"    ✓ {username} can login")
        
        # Test user data retrieval
        for username, _ in users:
            user_data = storage2.get_user(username)
            assert user_data is not None, f"User data not found for {username}"
            assert user_data['username'] == username, f"Username mismatch for {username}"
            print(f"    ✓ {username} data retrieved")
        
        print("✅ SQLite Storage - Data Persistence: All tests passed!\n")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def test_sqlite_crud_operations():
    """Test comprehensive CRUD operations with SQLite."""
    print("Testing SQLite Storage - CRUD Operations...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        auth = AuthManager(storage)
        
        # CREATE - Register multiple users
        print("  Testing CREATE operations...")
        test_users = [
            ("user1", "Pass123"),
            ("user2", "Pass456"),
            ("user3", "Pass789")
        ]
        
        for username, password in test_users:
            result = auth.register_user(username, password)
            assert result.success, f"Failed to create user {username}"
            print(f"    ✓ Created user {username}")
        
        # READ - Test various read operations
        print("  Testing READ operations...")
        
        # Test get_user
        for username, _ in test_users:
            user_data = storage.get_user(username)
            assert user_data is not None, f"Failed to read user {username}"
            assert user_data['username'] == username, f"Username mismatch for {username}"
            print(f"    ✓ Read user {username}")
        
        # Test user_exists
        for username, _ in test_users:
            assert storage.user_exists(username), f"User existence check failed for {username}"
            print(f"    ✓ Verified {username} exists")
        
        # Test get_all_users
        all_users = storage.get_all_users()
        assert len(all_users) == 3, f"Expected 3 users, got {len(all_users)}"
        usernames = [user['username'] for user in all_users]
        for username, _ in test_users:
            assert username in usernames, f"User {username} not in all_users list"
        print("    ✓ Retrieved all users")
        
        # Test get_user_count
        assert storage.get_user_count() == 3, f"Expected 3 users, got {storage.get_user_count()}"
        print("    ✓ User count correct")
        
        # UPDATE - Test update operations
        print("  Testing UPDATE operations...")
        
        # Update user with additional data
        update_data = {
            'email': 'user1@example.com',
            'last_login': '2024-01-15T10:00:00'
        }
        assert storage.update_user("user1", update_data), "Failed to update user1"
        print("    ✓ Updated user1")
        
        # Verify update
        updated_user = storage.get_user("user1")
        assert updated_user is not None, "Failed to retrieve updated user"
        assert updated_user.get('email') == 'user1@example.com', "Email not updated"
        print("    ✓ Verified user1 update")
        
        # DELETE - Test delete operations
        print("  Testing DELETE operations...")
        
        # Delete one user
        assert storage.delete_user("user2"), "Failed to delete user2"
        print("    ✓ Deleted user2")
        
        # Verify deletion
        assert not storage.user_exists("user2"), "User2 still exists after deletion"
        assert storage.get_user("user2") is None, "User2 data still retrievable after deletion"
        print("    ✓ Verified user2 deletion")
        
        # Verify other users still exist
        assert storage.user_exists("user1"), "User1 missing after user2 deletion"
        assert storage.user_exists("user3"), "User3 missing after user2 deletion"
        assert storage.get_user_count() == 2, f"Expected 2 users after deletion, got {storage.get_user_count()}"
        print("    ✓ Verified other users unaffected")
        
        print("✅ SQLite Storage - CRUD Operations: All tests passed!\n")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def test_sqlite_authentication_flows():
    """Test comprehensive authentication flows with SQLite."""
    print("Testing SQLite Storage - Authentication Flows...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        auth = AuthManager(storage)
        
        # Test registration with various password strengths
        print("  Testing password validation...")
        
        # Valid password
        result = auth.register_user("strong_user", "StrongPass123")
        assert result.success, f"Strong password registration failed: {result.message}"
        print("    ✓ Strong password accepted")
        
        # Weak password
        result = auth.register_user("weak_user", "weak")
        assert not result.success, "Weak password should be rejected"
        assert result.result_type.value == "weak_password", "Expected weak password error"
        print("    ✓ Weak password rejected")
        
        # Test username validation
        print("  Testing username validation...")
        
        # Valid username
        result = auth.register_user("valid_user", "ValidPass123")
        assert result.success, f"Valid username registration failed: {result.message}"
        print("    ✓ Valid username accepted")
        
        # Invalid username (too short)
        result = auth.register_user("ab", "ValidPass123")
        assert not result.success, "Short username should be rejected"
        print("    ✓ Short username rejected")
        
        # Test duplicate registration
        print("  Testing duplicate registration...")
        result = auth.register_user("valid_user", "AnotherPass123")
        assert not result.success, "Duplicate registration should be rejected"
        assert result.result_type.value == "user_exists", "Expected user exists error"
        print("    ✓ Duplicate registration rejected")
        
        # Test login flows
        print("  Testing login flows...")
        
        # Valid login
        result = auth.login_user("strong_user", "StrongPass123")
        assert result.success, f"Valid login failed: {result.message}"
        print("    ✓ Valid login successful")
        
        # Invalid password
        result = auth.login_user("strong_user", "WrongPassword123")
        assert not result.success, "Invalid password should be rejected"
        assert result.result_type.value == "invalid_credentials", "Expected invalid credentials error"
        print("    ✓ Invalid password rejected")
        
        # Non-existent user
        result = auth.login_user("nonexistent", "AnyPassword123")
        assert not result.success, "Non-existent user should be rejected"
        assert result.result_type.value == "user_not_found", "Expected user not found error"
        print("    ✓ Non-existent user rejected")
        
        # Test user data retrieval
        print("  Testing user data retrieval...")
        
        # Valid user
        result = auth.get_user_data("strong_user")
        assert result.success, f"User data retrieval failed: {result.message}"
        assert result.user_data is not None, "User data should be returned"
        assert result.user_data['username'] == "strong_user", "Username mismatch"
        print("    ✓ Valid user data retrieved")
        
        # Non-existent user
        result = auth.get_user_data("nonexistent")
        assert not result.success, "Non-existent user data should be rejected"
        assert result.result_type.value == "user_not_found", "Expected user not found error"
        print("    ✓ Non-existent user data rejected")
        
        print("✅ SQLite Storage - Authentication Flows: All tests passed!\n")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def test_sqlite_interface_consistency():
    """Test that DatabaseManager implements all required interface methods."""
    print("Testing SQLite Storage - Interface Consistency...")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        
        # Test that all required methods exist
        required_methods = [
            'create_user',
            'get_user', 
            'user_exists',
            'update_user',
            'delete_user',
            'get_all_users',
            'get_user_count'
        ]
        
        for method in required_methods:
            assert hasattr(storage, method), f"DatabaseManager missing {method}"
            print(f"    ✓ Method {method} exists")
        
        # Test method signatures and basic functionality
        test_user_data = {
            'username': 'testuser',
            'password_hash': 'test_hash',
            'salt': 'test_salt',
            'created_at': '2024-01-15T10:00:00'
        }
        
        # Test create_user
        assert storage.create_user(test_user_data), "create_user should return True for valid data"
        print("    ✓ create_user works")
        
        # Test user_exists
        assert storage.user_exists('testuser'), "user_exists should return True for existing user"
        print("    ✓ user_exists works")
        
        # Test get_user
        user_data = storage.get_user('testuser')
        assert user_data is not None, "get_user should return data for existing user"
        print("    ✓ get_user works")
        
        # Test get_user_count
        assert storage.get_user_count() >= 1, "get_user_count should return at least 1"
        print("    ✓ get_user_count works")
        
        # Test get_all_users
        all_users = storage.get_all_users()
        assert isinstance(all_users, list), "get_all_users should return a list"
        assert len(all_users) >= 1, "get_all_users should return at least 1 user"
        print("    ✓ get_all_users works")
        
        # Test update_user
        update_data = {'email': 'test@example.com'}
        assert storage.update_user('testuser', update_data), "update_user should return True for valid update"
        print("    ✓ update_user works")
        
        # Test delete_user
        assert storage.delete_user('testuser'), "delete_user should return True for valid deletion"
        print("    ✓ delete_user works")
        
        print("✅ SQLite Storage - Interface Consistency: All tests passed!\n")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def main():
    """Run all SQLite storage tests."""
    print("🚀 Starting SQLite-Only Authentication System Tests")
    print("=" * 60)
    
    try:
        test_sqlite_storage_basic()
        test_sqlite_persistence()
        test_sqlite_crud_operations()
        test_sqlite_authentication_flows()
        test_sqlite_interface_consistency()
        
        print("=" * 60)
        print("✅ All SQLite tests passed successfully!")
        print("📋 Test Summary:")
        print("   - Basic SQLite operations: ✅")
        print("   - Data persistence: ✅")
        print("   - CRUD operations: ✅")
        print("   - Authentication flows: ✅")
        print("   - Interface consistency: ✅")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main() 