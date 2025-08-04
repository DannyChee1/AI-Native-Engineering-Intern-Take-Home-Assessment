#!/usr/bin/env python3
"""
Demo script for the refactored user management system.
Shows how the consolidated database.py module works with both in-memory and SQLite storage.
"""

from database import DatabaseManager, InMemoryStorageManager
from auth import AuthManager
import os


def demo_in_memory_storage():
    """Demonstrate in-memory storage functionality."""
    print("=== In-Memory Storage Demo ===")
    
    # Create in-memory storage manager
    storage = InMemoryStorageManager()
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


def demo_sqlite_storage():
    """Demonstrate SQLite storage functionality."""
    print("\n=== SQLite Storage Demo ===")
    
    # Remove existing database file for clean demo
    db_file = "demo_users.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Create SQLite storage manager
    storage = DatabaseManager(db_file, enable_logging=False)
    auth_manager = AuthManager(storage)
    
    # Register users
    print("\n1. Registering users...")
    result1 = auth_manager.register_user("charlie", "securepass789")
    print(f"Charlie registration: {result1.message}")
    
    result2 = auth_manager.register_user("diana", "mypassword101")
    print(f"Diana registration: {result2.message}")
    
    # Try to register duplicate user
    result3 = auth_manager.register_user("charlie", "anotherpass")
    print(f"Duplicate Charlie registration: {result3.message}")
    
    # Login users
    print("\n2. Testing login...")
    login1 = auth_manager.login_user("charlie", "securepass789")
    print(f"Charlie login: {login1.message}")
    
    login2 = auth_manager.login_user("diana", "wrongpassword")
    print(f"Diana wrong password: {login2.message}")
    
    # Get user data
    print("\n3. Getting user data...")
    user_data = auth_manager.get_user_data("charlie")
    print(f"Charlie data: {user_data.message}")
    
    # List all users
    print("\n4. All users:")
    all_users = storage.get_all_users()
    for user in all_users:
        print(f"  - {user['username']} (created: {user['created_at']})")
    
    print(f"\nTotal users: {storage.get_user_count()}")
    
    # Test advanced database features
    print("\n5. Testing advanced features...")
    
    # Update user
    update_data = {'email': 'charlie@example.com'}
    if storage.update_user("charlie", update_data):
        print("Charlie email updated successfully")
    
    # Get updated user data
    updated_user = storage.get_user("charlie")
    if updated_user:
        print(f"Charlie's email: {updated_user.get('email', 'Not set')}")
    
    # Delete user
    if storage.delete_user("diana"):
        print("Diana deleted successfully")
    
    print(f"Final user count: {storage.get_user_count()}")


def demo_storage_interface():
    """Demonstrate the unified storage interface."""
    print("\n=== Storage Interface Demo ===")
    
    # Both storage managers implement the same interface
    in_memory = InMemoryStorageManager()
    sqlite_db = DatabaseManager("interface_demo.db", enable_logging=False)
    
    # Test with in-memory storage
    print("\n1. Testing with In-Memory Storage:")
    test_storage_operations(in_memory)
    
    # Test with SQLite storage
    print("\n2. Testing with SQLite Storage:")
    test_storage_operations(sqlite_db)
    
    # Clean up
    if os.path.exists("interface_demo.db"):
        os.remove("interface_demo.db")


def test_storage_operations(storage):
    """Test basic storage operations on any storage manager."""
    # Create user
    user_data = {
        'username': 'testuser',
        'password': 'testpass123',
        'created_at': '2024-01-01 12:00:00'
    }
    
    if storage.create_user(user_data):
        print("  ✓ User created")
    else:
        print("  ✗ User creation failed")
    
    # Check if user exists
    if storage.user_exists('testuser'):
        print("  ✓ User exists")
    else:
        print("  ✗ User not found")
    
    # Get user data
    user = storage.get_user('testuser')
    if user:
        print(f"  ✓ User retrieved: {user['username']}")
    else:
        print("  ✗ User retrieval failed")
    
    # Get all users
    all_users = storage.get_all_users()
    print(f"  ✓ Retrieved {len(all_users)} users")
    
    # Delete user
    if storage.delete_user('testuser'):
        print("  ✓ User deleted")
    else:
        print("  ✗ User deletion failed")


def main():
    """Run all demos."""
    print("Refactored User Management System Demo")
    print("=" * 50)
    print("This demo shows the consolidated system using only database.py")
    print("(storage.py has been removed and functionality consolidated)")
    print()
    
    try:
        # Demo in-memory storage
        demo_in_memory_storage()
        
        # Demo SQLite storage
        demo_sqlite_storage()
        
        # Demo storage interface
        demo_storage_interface()
        
        print("\n" + "=" * 50)
        print("✅ All demos completed successfully!")
        print("✅ System successfully refactored to use only database.py")
        print("✅ Redundancies removed (storage.py deleted)")
        print("✅ Both in-memory and SQLite storage work seamlessly")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 