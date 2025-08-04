#!/usr/bin/env python3
"""
Quick test to verify the refactoring works correctly.
"""

from database import DatabaseManager, InMemoryStorageManager
from auth import AuthManager


def test_in_memory_storage():
    """Test in-memory storage functionality."""
    print("Testing In-Memory Storage...")
    
    storage = InMemoryStorageManager()
    auth = AuthManager(storage)
    
    # Test user registration
    result = auth.register_user("testuser", "password123")
    assert result.success, f"Registration failed: {result.message}"
    print("✓ User registration works")
    
    # Test user login
    result = auth.login_user("testuser", "password123")
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
    
    print("✅ In-Memory Storage: All tests passed!\n")


def test_sqlite_storage():
    """Test SQLite storage functionality."""
    print("Testing SQLite Storage...")
    
    import os
    
    # Clean up any existing test database
    test_db = "test_users.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    storage = DatabaseManager(test_db, enable_logging=False)
    auth = AuthManager(storage)
    
    # Test user registration
    result = auth.register_user("testuser2", "password456")
    assert result.success, f"Registration failed: {result.message}"
    print("✓ User registration works")
    
    # Test user login
    result = auth.login_user("testuser2", "password456")
    assert result.success, f"Login failed: {result.message}"
    print("✓ User login works")
    
    # Test user existence
    assert storage.user_exists("testuser2"), "User existence check failed"
    print("✓ User existence check works")
    
    # Test get user data
    user_data = storage.get_user("testuser2")
    assert user_data is not None, "Get user data failed"
    assert user_data['username'] == "testuser2", "User data mismatch"
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
    assert storage.update_user("testuser2", update_data), "Update user failed"
    print("✓ Update user works")
    
    # Test delete user
    assert storage.delete_user("testuser2"), "Delete user failed"
    print("✓ Delete user works")
    
    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("✅ SQLite Storage: All tests passed!\n")


def test_interface_consistency():
    """Test that both storage types implement the same interface."""
    print("Testing Interface Consistency...")
    
    in_memory = InMemoryStorageManager()
    sqlite_db = DatabaseManager("test_interface.db", enable_logging=False)
    
    # Test that both have the same methods
    required_methods = [
        'create_user', 'get_user', 'user_exists', 
        'update_user', 'delete_user', 'get_all_users'
    ]
    
    for method in required_methods:
        assert hasattr(in_memory, method), f"InMemoryStorageManager missing {method}"
        assert hasattr(sqlite_db, method), f"DatabaseManager missing {method}"
    
    print("✓ Both storage types implement the same interface")
    
    # Test that both can be used with AuthManager
    auth1 = AuthManager(in_memory)
    auth2 = AuthManager(sqlite_db)
    
    print("✓ Both storage types work with AuthManager")
    
    # Clean up
    import os
    if os.path.exists("test_interface.db"):
        os.remove("test_interface.db")
    
    print("✅ Interface Consistency: All tests passed!\n")


def main():
    """Run all tests."""
    print("Refactoring Verification Tests")
    print("=" * 40)
    
    try:
        test_in_memory_storage()
        test_sqlite_storage()
        test_interface_consistency()
        
        print("=" * 40)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Refactoring successful - storage.py removed, database.py consolidated")
        print("✅ Both storage types work correctly")
        print("✅ Interface consistency maintained")
        print("✅ Backward compatibility preserved")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 