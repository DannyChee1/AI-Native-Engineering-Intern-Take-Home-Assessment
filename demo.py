"""
Demo application showcasing the SQLite-only authentication system.
Demonstrates data persistence, security best practices, and comprehensive testing.
"""

import os
import tempfile
from auth import AuthManager, AuthResultType
from database import DatabaseManager


def demo_sqlite_storage():
    """
    Demo SQLite storage functionality with persistence testing.
    """
    print("=== SQLite-Only Authentication System Demo ===\n")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        # Initialize storage and authentication managers
        storage = DatabaseManager(test_db, enable_logging=False)
        auth_manager = AuthManager(storage)
        
        # Demo: User registration
        print("1. Testing User Registration:")
        print("-" * 30)
        
        # Test valid registration
        result = auth_manager.register_user("alice", "SecurePass123!")
        print(f"Register 'alice': {result.message}")
        print(f"Success: {result.success}")
        print(f"Result Type: {result.result_type}")
        
        # Test duplicate registration
        result = auth_manager.register_user("alice", "AnotherPass456!")
        print(f"Register 'alice' again: {result.message}")
        
        # Test invalid password
        result = auth_manager.register_user("bob", "weak")
        print(f"Register 'bob' with weak password: {result.message}")
        
        # Test invalid username
        result = auth_manager.register_user("a", "ValidPass123!")
        print(f"Register with short username: {result.message}")
        
        print("\n" + "=" * 50 + "\n")
        
        # Demo: User login
        print("2. Testing User Login:")
        print("-" * 30)
        
        # Test valid login
        result = auth_manager.login_user("alice", "SecurePass123!")
        print(f"Login 'alice' with correct password: {result.message}")
        print(f"Success: {result.success}")
        
        # Test invalid password
        result = auth_manager.login_user("alice", "WrongPassword123!")
        print(f"Login 'alice' with wrong password: {result.message}")
        
        # Test non-existent user
        result = auth_manager.login_user("nonexistent", "AnyPassword123!")
        print(f"Login non-existent user: {result.message}")
        
        print("\n" + "=" * 50 + "\n")
        
        # Demo: Get user data
        print("3. Testing User Data Retrieval:")
        print("-" * 30)
        
        # Test valid user data retrieval
        result = auth_manager.get_user_data("alice")
        print(f"Get data for 'alice': {result.message}")
        if result.success and result.user_data:
            print(f"User data: {result.user_data}")
        
        # Test non-existent user
        result = auth_manager.get_user_data("nonexistent")
        print(f"Get data for non-existent user: {result.message}")
        
        print("\n" + "=" * 50 + "\n")
        
        # Demo: Storage statistics
        print("4. Storage Statistics:")
        print("-" * 30)
        print(f"Total users: {storage.get_user_count()}")
        print(f"All users: {storage.get_all_users()}")
        
        print("\n" + "=" * 50 + "\n")
        
        # Demo: Data persistence testing
        print("5. Testing Data Persistence:")
        print("-" * 30)
        
        # Register additional users for persistence test
        auth_manager.register_user("bob", "BobPass456!")
        auth_manager.register_user("charlie", "CharliePass789!")
        
        print(f"Before 'restart': {storage.get_user_count()} users")
        print(f"Users: {[user['username'] for user in storage.get_all_users()]}")
        
        # Simulate "app restart" - create new storage manager with same database
        print("\nSimulating application restart...")
        storage2 = DatabaseManager(test_db, enable_logging=False)
        auth_manager2 = AuthManager(storage2)
        
        print(f"After 'restart': {storage2.get_user_count()} users")
        print(f"Users: {[user['username'] for user in storage2.get_all_users()]}")
        
        # Test login after "restart"
        result = auth_manager2.login_user("alice", "SecurePass123!")
        print(f"Alice login after restart: {result.message}")
        
        result = auth_manager2.login_user("bob", "BobPass456!")
        print(f"Bob login after restart: {result.message}")
        
        result = auth_manager2.login_user("charlie", "CharliePass789!")
        print(f"Charlie login after restart: {result.message}")
        
        print("\n" + "=" * 50 + "\n")
        
        # Demo: CRUD operations
        print("6. Testing CRUD Operations:")
        print("-" * 30)
        
        # Test UPDATE operation
        update_data = {'email': 'alice@example.com', 'last_login': '2024-01-15T10:00:00'}
        success = storage2.update_user("alice", update_data)
        print(f"Update alice with email: {'Success' if success else 'Failed'}")
        
        # Verify update
        user_data = storage2.get_user("alice")
        if user_data and user_data.get('email'):
            print(f"Alice email: {user_data['email']}")
        
        # Test DELETE operation
        success = storage2.delete_user("charlie")
        print(f"Delete charlie: {'Success' if success else 'Failed'}")
        
        # Verify deletion
        user_exists = storage2.user_exists("charlie")
        print(f"Charlie still exists: {user_exists}")
        print(f"Total users after deletion: {storage2.get_user_count()}")
        
        print("\n" + "=" * 50 + "\n")
        
        print("✅ SQLite-Only Demo Completed Successfully!")
        print("📋 Demo Summary:")
        print("   - User registration with validation: ✅")
        print("   - User authentication: ✅")
        print("   - Data persistence across restarts: ✅")
        print("   - CRUD operations: ✅")
        print("   - Error handling: ✅")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def main():
    """
    Main demo function showcasing the SQLite-only authentication system.
    """
    demo_sqlite_storage()


if __name__ == "__main__":
    main() 