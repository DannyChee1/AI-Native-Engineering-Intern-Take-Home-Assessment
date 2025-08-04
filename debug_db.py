#!/usr/bin/env python3
"""Debug script to test database functionality."""

import tempfile
import os
import sqlite3
from database import DatabaseManager

def test_database():
    """Test basic database operations."""
    print("Testing Database Operations")
    print("=" * 40)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        print(f"Creating database at: {db_path}")
        db = DatabaseManager(db_path, enable_logging=False)
        
        # Test database initialization
        print("\n0. Testing database initialization...")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"Database file exists, size: {size} bytes")
        else:
            print("Database file does not exist!")
            return
        
        # Test table creation
        print("\n0.1. Testing table creation...")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            # Check users table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print(f"Users table columns: {[col[1] for col in columns]}")
        
        # Test validation directly
        print("\n1. Testing validation...")
        validation_result = db._validate_user_input('testuser', 'SecurePass123!')
        print(f"Validation result: {validation_result.success}, {validation_result.message}")
        
        # Test user creation
        print("\n2. Testing user creation...")
        user_data = {
            'username': 'testuser',
            'password': 'SecurePass123!',
            'created_at': '2024-01-15T10:00:00'
        }
        
        result = db.create_user(user_data)
        print(f"Create result: {result}")
        
        # Test user existence
        print(f"User exists: {db.user_exists('testuser')}")
        print(f"User count: {db.get_user_count()}")
        
        # Test get user
        user = db.get_user('testuser')
        print(f"Retrieved user: {user is not None}")
        if user:
            print(f"Username: {user.get('username')}")
            print(f"Has password_hash: {'password_hash' in user}")
        
        # Test get all users
        all_users = db.get_all_users()
        print(f"All users count: {len(all_users)}")
        
        # Test update
        print("\n3. Testing user update...")
        update_result = db.update_user('testuser', {'email': 'test@example.com'})
        print(f"Update result: {update_result}")
        
        updated_user = db.get_user('testuser')
        if updated_user:
            print(f"Updated user email: {updated_user.get('email')}")
        
        # Test delete
        print("\n4. Testing user deletion...")
        delete_result = db.delete_user('testuser')
        print(f"Delete result: {delete_result}")
        print(f"User exists after delete: {db.user_exists('testuser')}")
        print(f"User count after delete: {db.get_user_count()}")
        
        # Test database file size
        print(f"\n5. Database file info:")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"Database file size: {size} bytes")
        else:
            print("Database file does not exist!")
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\nCleaned up database file: {db_path}")

if __name__ == '__main__':
    test_database() 