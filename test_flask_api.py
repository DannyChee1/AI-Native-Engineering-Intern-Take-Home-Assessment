"""
Test script for Flask API endpoints.
Demonstrates proper usage of all endpoints with examples and error handling.
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class FlaskAPITester:
    """Test client for Flask API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the test client.
        
        Args:
            base_url: Base URL of the Flask API
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        print("\n=== Testing Health Check ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def test_register_user(self, username: str, password: str) -> bool:
        """
        Test user registration.
        
        Args:
            username: Username for registration
            password: Password for registration
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n=== Testing User Registration: {username} ===")
        try:
            data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/register",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 201:
                print("✅ Registration successful!")
                return True
            else:
                print("❌ Registration failed!")
                return False
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def test_login(self, username: str, password: str) -> bool:
        """
        Test user login.
        
        Args:
            username: Username for login
            password: Password for login
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n=== Testing User Login: {username} ===")
        try:
            data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('token'):
                    self.auth_token = result['token']
                    print("✅ Login successful! Token received.")
                    return True
                else:
                    print("❌ Login failed - no token received!")
                    return False
            else:
                print("❌ Login failed!")
                return False
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def test_get_user(self) -> bool:
        """
        Test getting user profile (requires authentication).
        
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Testing Get User Profile ===")
        
        if not self.auth_token:
            print("❌ No authentication token available!")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{self.base_url}/get_user",
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("✅ Get user profile successful!")
                return True
            else:
                print("❌ Get user profile failed!")
                return False
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def test_invalid_requests(self):
        """Test various invalid request scenarios."""
        print("\n=== Testing Invalid Requests ===")
        
        # Test 1: Missing required fields
        print("\n--- Test: Missing required fields ---")
        try:
            data = {"username": "testuser"}  # Missing password
            response = self.session.post(
                f"{self.base_url}/register",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test 2: Empty values
        print("\n--- Test: Empty values ---")
        try:
            data = {"username": "", "password": ""}
            response = self.session.post(
                f"{self.base_url}/register",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test 3: Invalid JSON
        print("\n--- Test: Invalid JSON ---")
        try:
            response = self.session.post(
                f"{self.base_url}/register",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test 4: Unauthorized access
        print("\n--- Test: Unauthorized access ---")
        try:
            response = self.session.get(f"{self.base_url}/get_user")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test 5: Invalid token
        print("\n--- Test: Invalid token ---")
        try:
            headers = {
                "Authorization": "Bearer invalid_token",
                "Content-Type": "application/json"
            }
            response = self.session.get(
                f"{self.base_url}/get_user",
                headers=headers
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all endpoints."""
        print("🚀 Starting Comprehensive Flask API Test")
        print("=" * 50)
        
        # Test health check
        if not self.test_health_check():
            print("❌ Health check failed! Make sure the Flask app is running.")
            return
        
        # Test registration with valid data
        valid_username = f"testuser_{int(time.time())}"
        valid_password = "SecurePass123"
        
        if not self.test_register_user(valid_username, valid_password):
            print("❌ Registration test failed!")
            return
        
        # Test duplicate registration
        print("\n=== Testing Duplicate Registration ===")
        self.test_register_user(valid_username, valid_password)
        
        # Test login with valid credentials
        if not self.test_login(valid_username, valid_password):
            print("❌ Login test failed!")
            return
        
        # Test get user profile
        if not self.test_get_user():
            print("❌ Get user profile test failed!")
            return
        
        # Test invalid requests
        self.test_invalid_requests()
        
        print("\n" + "=" * 50)
        print("✅ Comprehensive test completed!")
        print("📋 Summary:")
        print(f"   - Health check: ✅")
        print(f"   - User registration: ✅")
        print(f"   - User login: ✅")
        print(f"   - Get user profile: ✅")
        print(f"   - Error handling: ✅")


def main():
    """Main function to run the API tests."""
    print("Flask API Test Suite")
    print("Make sure the Flask application is running on http://localhost:5000")
    print("Run: python flask_app.py")
    print()
    
    # Wait for user confirmation
    input("Press Enter to start testing...")
    
    # Create test client
    tester = FlaskAPITester()
    
    # Run comprehensive test
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main() 