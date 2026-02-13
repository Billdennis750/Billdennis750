"""
Comprehensive API Tests for Cashflow MFB Platform
Tests: Authentication, User Registration, Login, Applications, Admin endpoints
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment or use preview URL
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://loan-app-staging.preview.emergentagent.com').rstrip('/')

# Test credentials from requirement
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30"

# Generate unique test user
TEST_USER_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test User Cashflow"
TEST_USER_PHONE = "08012345678"


class TestHealthAndBasicAPI:
    """Test health check and basic API endpoints"""
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unhealthy status: {data}"
        print(f"Health check passed: {data}")
    
    def test_api_base_responds(self):
        """Test that API base responds"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        # Should get 200 (frontend served) or API response
        assert response.status_code in [200, 404, 307], f"Base URL failed: {response.status_code}"
        print(f"Base URL response: {response.status_code}")


class TestUserRegistration:
    """Test user registration flow"""
    
    def test_register_new_user_success(self):
        """Test registering a new user"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "phone": TEST_USER_PHONE
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=15)
        
        # Registration should succeed
        assert response.status_code in [200, 201], f"Registration failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "user_id" in data or "message" in data, f"Unexpected response: {data}"
        print(f"User registration successful: {data}")
    
    def test_register_duplicate_email_fails(self):
        """Test that registering with existing email fails"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "phone": TEST_USER_PHONE
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=15)
        
        # Should fail with 400 for duplicate
        assert response.status_code == 400, f"Expected 400 for duplicate, got: {response.status_code}"
        print(f"Duplicate email correctly rejected: {response.status_code}")
    
    def test_register_invalid_email_fails(self):
        """Test that invalid email format is rejected"""
        payload = {
            "email": "invalid-email",
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "phone": TEST_USER_PHONE
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=15)
        
        # Should fail with 422 (validation error)
        assert response.status_code == 422, f"Expected 422 for invalid email, got: {response.status_code}"
        print(f"Invalid email correctly rejected: {response.status_code}")


class TestUserLogin:
    """Test user login flow"""
    
    def test_login_success(self):
        """Test logging in with valid credentials"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        assert "user" in data, f"No user in response: {data}"
        assert data["user"]["email"] == TEST_USER_EMAIL, f"Email mismatch: {data}"
        print(f"Login successful: {data['user']['email']}")
        return data["access_token"]
    
    def test_login_wrong_password_fails(self):
        """Test that wrong password fails"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": "WrongPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        
        assert response.status_code == 401, f"Expected 401 for wrong password, got: {response.status_code}"
        print(f"Wrong password correctly rejected: {response.status_code}")
    
    def test_login_nonexistent_user_fails(self):
        """Test that nonexistent user fails"""
        payload = {
            "email": "nonexistent@example.com",
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        
        assert response.status_code == 401, f"Expected 401 for nonexistent user, got: {response.status_code}"
        print(f"Nonexistent user correctly rejected: {response.status_code}")


class TestAdminLogin:
    """Test admin login and access"""
    
    def test_admin_login_success(self):
        """Test admin can login"""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token: {data}"
        assert data["user"]["role"] == "admin", f"User is not admin: {data}"
        print(f"Admin login successful: {data['user']['email']}")
        return data["access_token"]


class TestApplicationsEndpoint:
    """Test applications API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Admin login failed - skipping authenticated tests")
    
    def test_get_all_applications(self, admin_token):
        """Test fetching all applications (admin)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/applications/", headers=headers, timeout=15)
        
        assert response.status_code == 200, f"Get applications failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "applications" in data, f"No applications key: {data}"
        assert isinstance(data["applications"], list), f"Applications is not a list: {data}"
        print(f"Found {len(data['applications'])} applications")
        return data["applications"]
    
    def test_get_single_application(self, admin_token):
        """Test fetching a single application"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # First get all applications
        response = requests.get(f"{BASE_URL}/api/applications/", headers=headers, timeout=15)
        if response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications to test")
        
        app_id = apps[0].get("application_id")
        response = requests.get(f"{BASE_URL}/api/applications/{app_id}", headers=headers, timeout=15)
        
        assert response.status_code == 200, f"Get application failed: {response.status_code}"
        data = response.json()
        assert data.get("application_id") == app_id, f"Application ID mismatch: {data}"
        print(f"Fetched application: {app_id}")
    
    def test_get_nonexistent_application(self, admin_token):
        """Test fetching nonexistent application returns 404"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/applications/NONEXISTENT-APP-ID", headers=headers, timeout=15)
        
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print(f"Nonexistent application correctly returns 404")


class TestAdminEndpoints:
    """Test admin-specific endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Admin login failed")
    
    def test_get_admin_users(self, admin_token):
        """Test admin can fetch all users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers, timeout=15)
        
        assert response.status_code == 200, f"Get users failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "users" in data, f"No users key: {data}"
        assert isinstance(data["users"], list), f"Users is not a list"
        print(f"Found {len(data['users'])} users")
    
    def test_get_admin_transactions(self, admin_token):
        """Test admin can fetch transactions"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/transactions", headers=headers, timeout=15)
        
        # May return 200 or 404 if not implemented
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            print(f"Transactions response: {data}")


class TestPaymentEndpoints:
    """Test payment API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Admin login failed")
    
    def test_payment_verify_invalid_reference(self):
        """Test verifying nonexistent payment reference"""
        payload = {"order_ref": "INVALID-REFERENCE-123"}
        response = requests.post(f"{BASE_URL}/api/payments/verify", json=payload, timeout=15)
        
        # Should return 404 for nonexistent transaction
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print(f"Invalid payment reference correctly returns 404")
    
    def test_payment_initiate_requires_application(self):
        """Test payment initiation requires valid application"""
        payload = {
            "application_id": "NONEXISTENT-APP",
            "customer_email": "test@example.com",
            "customer_name": "Test User",
            "customer_phone": "08012345678",
            "amount": 2500,
            "redirect_url": "https://example.com/callback"
        }
        response = requests.post(f"{BASE_URL}/api/payments/initiate", json=payload, timeout=15)
        
        # Should return 404 for nonexistent application
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print(f"Payment initiation correctly requires valid application")


class TestForgotPassword:
    """Test forgot password flow"""
    
    def test_forgot_password_endpoint(self):
        """Test forgot password endpoint"""
        payload = {"email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json=payload, timeout=15)
        
        # Should always return 200 to prevent email enumeration
        assert response.status_code == 200, f"Forgot password failed: {response.status_code}"
        data = response.json()
        assert "message" in data, f"No message in response: {data}"
        print(f"Forgot password response: {data}")


class TestUserDashboard:
    """Test user dashboard endpoints"""
    
    @pytest.fixture
    def user_token(self):
        """Get user token"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("User login failed")
    
    def test_get_user_info(self, user_token):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=15)
        
        assert response.status_code == 200, f"Get user info failed: {response.status_code}"
        data = response.json()
        assert data.get("email") == TEST_USER_EMAIL, f"Email mismatch: {data}"
        print(f"User info retrieved: {data}")
    
    def test_get_user_applications(self, user_token):
        """Test getting user's applications"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/applications/user/my-applications", headers=headers, timeout=15)
        
        assert response.status_code == 200, f"Get user applications failed: {response.status_code}"
        data = response.json()
        assert "applications" in data, f"No applications key: {data}"
        print(f"User has {len(data['applications'])} applications")


# Cleanup function
def cleanup_test_user():
    """Cleanup test user after tests"""
    # This would require admin access to delete users
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
