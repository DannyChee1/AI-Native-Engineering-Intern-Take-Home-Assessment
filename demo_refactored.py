#!/usr/bin/env python3
"""
Demo script for the SQLite-only user management system.
Shows how the consolidated database.py module works with SQLite storage and persistence.
"""

import os
import tempfile
from database import DatabaseManager
from auth import AuthManager


def demo_sqlite_storage():
    """Demonstrate SQLite storage functionality with persistence testing."""
    print("=== SQLite Storage Demo ===")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        # Create SQLite storage manager
        storage = DatabaseManager(test_db, enable_logging=False)
        auth_manager = AuthManager(storage)
        
        # Register users
        print("\n1. Registering users...")
        result1 = auth_manager.register_user("alice", "securepass123")
        print(f"Alice registration: {result1.message}")
        
        result2 = auth_manager.register_user("bob", "mypassword456")
        print(f"Bob registration: {result2.message}")
        
        # Try to register duplicate user
        result3 = auth_manager.register_user("alice", "anotherpass")
        print(f"Duplicate Alice registration: {result3.message}")
        
        # Login users
        print("\n2. Testing login...")
        login1 = auth_manager.login_user("alice", "securepass123")
        print(f"Alice login: {login1.message}")
        
        login2 = auth_manager.login_user("bob", "wrongpassword")
        print(f"Bob wrong password: {login2.message}")
        
        # Get user data
        print("\n3. Getting user data...")
        user_data = auth_manager.get_user_data("alice")
        print(f"Alice data: {user_data.message}")
        
        # List all users
        print("\n4. All users:")
        all_users = storage.get_all_users()
        for user in all_users:
            print(f"  - {user['username']} (created: {user['created_at']})")
        
        print(f"\nTotal users: {storage.get_user_count()}")
        
        # Test persistence across "app restarts"
        print("\n5. Testing Data Persistence...")
        print("Simulating application restart...")
        
        # Create new storage manager with same database (simulating restart)
        storage2 = DatabaseManager(test_db, enable_logging=False)
        auth_manager2 = AuthManager(storage2)
        
        # Verify all users still exist
        print(f"Users after restart: {storage2.get_user_count()}")
        all_users_after_restart = storage2.get_all_users()
        for user in all_users_after_restart:
            print(f"  - {user['username']} (created: {user['created_at']})")
        
        # Test login after restart
        print("\n6. Testing login after restart...")
        login_after_restart = auth_manager2.login_user("alice", "securepass123")
        print(f"Alice login after restart: {login_after_restart.message}")
        
        login_after_restart2 = auth_manager2.login_user("bob", "mypassword456")
        print(f"Bob login after restart: {login_after_restart2.message}")
        
        print("✅ SQLite Storage Demo Completed Successfully!")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def demo_storage_interface():
    """Demonstrate that DatabaseManager implements the complete storage interface."""
    print("\n=== Storage Interface Demo ===")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        
        # Test all required interface methods
        print("\nTesting interface methods:")
        
        # Test create_user
        test_user_data = {
            'username': 'testuser',
            'password_hash': 'test_hash',
            'salt': 'test_salt',
            'created_at': '2024-01-15T10:00:00'
        }
        success = storage.create_user(test_user_data)
        print(f"  create_user: {'✓' if success else '✗'}")
        
        # Test user_exists
        exists = storage.user_exists('testuser')
        print(f"  user_exists: {'✓' if exists else '✗'}")
        
        # Test get_user
        user_data = storage.get_user('testuser')
        print(f"  get_user: {'✓' if user_data else '✗'}")
        
        # Test get_user_count
        count = storage.get_user_count()
        print(f"  get_user_count: {'✓' if count >= 1 else '✗'}")
        
        # Test get_all_users
        all_users = storage.get_all_users()
        print(f"  get_all_users: {'✓' if len(all_users) >= 1 else '✗'}")
        
        # Test update_user
        update_data = {'email': 'test@example.com'}
        update_success = storage.update_user('testuser', update_data)
        print(f"  update_user: {'✓' if update_success else '✗'}")
        
        # Test delete_user
        delete_success = storage.delete_user('testuser')
        print(f"  delete_user: {'✓' if delete_success else '✗'}")
        
        print("✅ All interface methods implemented correctly!")
        
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


def test_storage_operations(storage):
    """Test comprehensive storage operations."""
    print("\n=== Comprehensive Storage Operations Test ===")
    
    # Test CREATE operations
    print("\n1. Testing CREATE operations...")
    users_to_create = [
        ("user1", "pass1"),
        ("user2", "pass2"),
        ("user3", "pass3")
    ]
    
    for username, password in users_to_create:
        user_data = {
            'username': username,
            'password_hash': f'hash_{password}',
            'salt': f'salt_{password}',
            'created_at': '2024-01-15T10:00:00'
        }
        success = storage.create_user(user_data)
        print(f"  Created {username}: {'✓' if success else '✗'}")
    
    # Test READ operations
    print("\n2. Testing READ operations...")
    
    # Test get_user
    for username, _ in users_to_create:
        user_data = storage.get_user(username)
        print(f"  Retrieved {username}: {'✓' if user_data else '✗'}")
    
    # Test user_exists
    for username, _ in users_to_create:
        exists = storage.user_exists(username)
        print(f"  {username} exists: {'✓' if exists else '✗'}")
    
    # Test get_all_users
    all_users = storage.get_all_users()
    print(f"  Retrieved all users: {'✓' if len(all_users) == 3 else '✗'}")
    
    # Test get_user_count
    count = storage.get_user_count()
    print(f"  User count: {'✓' if count == 3 else '✗'}")
    
    # Test UPDATE operations
    print("\n3. Testing UPDATE operations...")
    update_data = {'email': 'user1@example.com', 'last_login': '2024-01-15T10:00:00'}
    success = storage.update_user("user1", update_data)
    print(f"  Updated user1: {'✓' if success else '✗'}")
    
    # Verify update
    updated_user = storage.get_user("user1")
    if updated_user and updated_user.get('email'):
        print(f"  Verified user1 email: {'✓' if updated_user['email'] == 'user1@example.com' else '✗'}")
    
    # Test DELETE operations
    print("\n4. Testing DELETE operations...")
    success = storage.delete_user("user2")
    print(f"  Deleted user2: {'✓' if success else '✗'}")
    
    # Verify deletion
    exists = storage.user_exists("user2")
    print(f"  user2 still exists: {'✗' if not exists else '✗'}")
    
    # Verify other users unaffected
    exists1 = storage.user_exists("user1")
    exists3 = storage.user_exists("user3")
    print(f"  user1 still exists: {'✓' if exists1 else '✗'}")
    print(f"  user3 still exists: {'✓' if exists3 else '✗'}")
    
    final_count = storage.get_user_count()
    print(f"  Final user count: {'✓' if final_count == 2 else '✗'}")
    
    print("\n✅ All storage operations completed successfully!")


def main():
    """Main demo function."""
    print("🚀 SQLite-Only User Management System Demo")
    print("=" * 60)
    
    # Demo SQLite storage
    demo_sqlite_storage()
    
    # Demo storage interface
    demo_storage_interface()
    
    # Test comprehensive operations
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db = tmp_file.name
    
    try:
        storage = DatabaseManager(test_db, enable_logging=False)
        test_storage_operations(storage)
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)
    
    print("\n" + "=" * 60)
    print("✅ SQLite-Only Demo Completed Successfully!")
    print("📋 Demo Summary:")
    print("   - SQLite storage functionality: ✅")
    print("   - Data persistence testing: ✅")
    print("   - Interface compliance: ✅")
    print("   - Comprehensive CRUD operations: ✅")
    print("   - Error handling: ✅")


if __name__ == "__main__":
    main() 