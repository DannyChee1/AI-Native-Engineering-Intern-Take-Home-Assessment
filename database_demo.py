"""
Demo application showcasing the database module.
Demonstrates SQLite database operations with proper connection management and security.
"""

from database import DatabaseManager, DatabaseResultType
import time


def main():
    """
    Main demo function showcasing the database module features.
    """
    print("=== Database Module Demo ===\n")
    
    # Initialize database manager
    db_manager = DatabaseManager("demo_users.db", enable_logging=True)
    
    # Demo 1: User Creation
    print("1. Testing User Creation:")
    print("-" * 30)
    
    # Create users with different scenarios
    users_to_create = [
        ("alice", "SecurePass123!", "alice@example.com"),
        ("bob", "AnotherSecure456!", "bob@example.com"),
        ("charlie", "CharliePass789!", None),  # No email
        ("admin", "AdminSecurePass!", "admin@example.com")
    ]
    
    for username, password, email in users_to_create:
        result = db_manager.create_user(username, password, email)
        print(f"Create '{username}': {result.message}")
        if result.success:
            print(f"  User ID: {result.data['user_id']}")
        print()
    
    # Demo 2: User Authentication
    print("2. Testing User Authentication:")
    print("-" * 30)
    
    # Test valid authentication
    result = db_manager.authenticate_user("alice", "SecurePass123!")
    print(f"Authenticate 'alice' with correct password: {result.message}")
    if result.success:
        print(f"  User ID: {result.data['user_id']}")
    
    # Test invalid password
    result = db_manager.authenticate_user("alice", "WrongPassword123!")
    print(f"Authenticate 'alice' with wrong password: {result.message}")
    
    # Test non-existent user
    result = db_manager.authenticate_user("nonexistent", "AnyPassword123!")
    print(f"Authenticate non-existent user: {result.message}")
    
    print()
    
    # Demo 3: User Data Retrieval
    print("3. Testing User Data Retrieval:")
    print("-" * 30)
    
    # Get user by username
    result = db_manager.get_user_by_username("bob")
    print(f"Get user 'bob' by username: {result.message}")
    if result.success:
        print(f"  User data: {result.data}")
    
    # Get user by ID
    if result.success:
        user_id = result.data['id']
        result = db_manager.get_user_by_id(user_id)
        print(f"Get user by ID {user_id}: {result.message}")
        if result.success:
            print(f"  User data: {result.data}")
    
    print()
    
    # Demo 4: User Updates
    print("4. Testing User Updates:")
    print("-" * 30)
    
    # Update user email
    result = db_manager.update_user(1, email="alice.updated@example.com")
    print(f"Update user ID 1 email: {result.message}")
    
    # Update user password
    result = db_manager.update_user(1, password="NewSecurePass456!")
    print(f"Update user ID 1 password: {result.message}")
    
    # Verify password change
    result = db_manager.authenticate_user("alice", "NewSecurePass456!")
    print(f"Authenticate with new password: {result.message}")
    
    print()
    
    # Demo 5: User Management
    print("5. Testing User Management:")
    print("-" * 30)
    
    # Get all users
    result = db_manager.get_all_users(limit=10)
    print(f"Get all users: {result.message}")
    if result.success:
        print(f"  Total users: {result.data['count']}")
        for user in result.data['users']:
            print(f"    - {user['username']} (ID: {user['id']})")
    
    # Check user existence
    exists = db_manager.user_exists("alice")
    print(f"User 'alice' exists: {exists}")
    
    exists = db_manager.user_exists("nonexistent")
    print(f"User 'nonexistent' exists: {exists}")
    
    # Get user count
    count = db_manager.get_user_count()
    print(f"Total user count: {count}")
    
    print()
    
    # Demo 6: Error Handling
    print("6. Testing Error Handling:")
    print("-" * 30)
    
    # Try to create duplicate user
    result = db_manager.create_user("alice", "AnotherPassword123!", "duplicate@example.com")
    print(f"Create duplicate user 'alice': {result.message}")
    print(f"  Result type: {result.result_type}")
    
    # Try to create user with invalid data
    result = db_manager.create_user("a", "weak", "invalid-email")
    print(f"Create user with invalid data: {result.message}")
    print(f"  Result type: {result.result_type}")
    
    # Try to get non-existent user
    result = db_manager.get_user_by_id(999)
    print(f"Get non-existent user ID 999: {result.message}")
    print(f"  Result type: {result.result_type}")
    
    print()
    
    # Demo 7: Database Statistics
    print("7. Database Statistics:")
    print("-" * 30)
    
    # Get all users with pagination
    result = db_manager.get_all_users(limit=5, offset=0)
    print(f"First 5 users: {result.message}")
    if result.success:
        for user in result.data['users']:
            print(f"  - {user['username']} (Created: {user['created_at']})")
    
    # Get total count
    total_count = db_manager.get_user_count()
    print(f"Total users in database: {total_count}")
    
    print("\n" + "=" * 50)
    print("Database demo completed successfully!")
    print("Check 'database.log' for detailed operation logs.")


if __name__ == "__main__":
    main() 