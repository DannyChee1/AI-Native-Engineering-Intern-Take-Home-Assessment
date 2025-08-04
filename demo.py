"""
Demo application showcasing the modernized authentication system.
Demonstrates the separation of concerns and security best practices.
"""

from auth import AuthManager, AuthResultType
from storage import InMemoryStorageManager, SQLiteStorageManager


def main():
    """
    Main demo function showcasing the modernized authentication system.
    """
    print("=== Modernized Authentication System Demo ===\n")
    
    # Initialize storage and authentication managers
    # For development/testing, use InMemoryStorageManager
    # For production, use SQLiteStorageManager
    storage = InMemoryStorageManager()
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


if __name__ == "__main__":
    main() 