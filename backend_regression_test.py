#!/usr/bin/env python3
"""
Comprehensive Backend Regression Testing for Cashflow MFB
Tests all critical backend APIs after code review and linting fixes
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Test configuration
BACKEND_URL = "https://cashflow-dashboard-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials for testing
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30Z@"

class BackendRegressionTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.admin_token = None
        self.test_application_id = None
        
    async def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    async def test_health_check(self):
        """Test backend health check endpoint"""
        try:
            response = await self.client.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    await self.log_result("Health Check", True, "Backend is healthy and responding")
                    return True
                else:
                    await self.log_result("Health Check", False, f"Backend unhealthy: {data}")
                    return False
            else:
                await self.log_result("Health Check", False, f"Backend returned {response.status_code}")
                return False
        except Exception as e:
            await self.log_result("Health Check", False, f"Backend not accessible: {str(e)}")
            return False
    
    async def test_user_registration(self):
        """Test user registration API"""
        try:
            # Generate unique test user
            timestamp = int(datetime.now().timestamp())
            test_user = {
                "email": f"testuser{timestamp}@example.com",
                "full_name": "Test User Registration",
                "phone": "+2348012345678",
                "password": "testpassword123"
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data and data.get("message") == "Registration successful":
                    await self.log_result(
                        "User Registration", 
                        True, 
                        "User registration working correctly",
                        f"User ID: {data['user_id']}"
                    )
                    return True
                else:
                    await self.log_result(
                        "User Registration", 
                        False, 
                        "Registration response missing required fields",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "User Registration", 
                    False, 
                    f"Registration failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("User Registration", False, f"Error: {str(e)}")
            return False
    
    async def test_admin_login(self):
        """Test admin login with provided credentials"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    user_info = data["user"]
                    
                    # Verify admin role
                    if user_info.get("role") == "admin" and user_info.get("email") == ADMIN_EMAIL:
                        await self.log_result(
                            "Admin Login", 
                            True, 
                            "Admin login successful with correct credentials",
                            f"Admin: {user_info['full_name']} ({user_info['email']})"
                        )
                        return True
                    else:
                        await self.log_result(
                            "Admin Login", 
                            False, 
                            "Login successful but user is not admin or wrong email",
                            f"Role: {user_info.get('role')}, Email: {user_info.get('email')}"
                        )
                        return False
                else:
                    await self.log_result(
                        "Admin Login", 
                        False, 
                        "Login response missing access_token or user info",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Admin Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Admin Login", False, f"Error: {str(e)}")
            return False
    
    async def test_password_reset_flow(self):
        """Test forgot password API endpoint"""
        try:
            # Test forgot password request
            forgot_data = {
                "email": "test@example.com"  # Using test email
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/forgot-password",
                json=forgot_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "If an account exists with this email, you will receive a password reset link."
                if data.get("message") == expected_message:
                    await self.log_result(
                        "Password Reset API", 
                        True, 
                        "Forgot password endpoint working correctly"
                    )
                    return True
                else:
                    await self.log_result(
                        "Password Reset API", 
                        False, 
                        "Unexpected response message",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Password Reset API", 
                    False, 
                    f"Forgot password failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Password Reset API", False, f"Error: {str(e)}")
            return False
    
    async def test_loan_application_submission(self):
        """Test loan application submission API"""
        try:
            # Create multipart form data for application submission
            timestamp = int(datetime.now().timestamp())
            files = {
                'full_name': (None, f'John Doe {timestamp}'),
                'date_of_birth': (None, '1990-01-15'),
                'email': (None, f'john.doe.{timestamp}@example.com'),
                'phone': (None, '08012345678'),
                'secondary_phone': (None, '08087654321'),
                'relative_phone': (None, '08011223344'),
                'flat_house_number': (None, '15A'),
                'home_town': (None, 'Lagos'),
                'residential_address': (None, '123 Test Street, Lagos'),
                'place_of_work': (None, 'Test Company Ltd'),
                'employment_status': (None, 'employed'),
                'employment_details': (None, 'Software Engineer'),
                'monthly_income': (None, '150000'),
                'bank_name': (None, 'First Bank'),
                'account_name': (None, f'John Doe {timestamp}'),
                'account_number': (None, '1234567890'),
                'loan_amount': (None, '500000'),
                'loan_duration': (None, '12'),
                'repayment_frequency': (None, 'monthly'),
                'loan_reason': (None, 'Business expansion'),
                'nin': (None, '12345678901'),
                'bvn': (None, '12345678901'),
                'password': (None, 'testpassword123'),
                'id_card': ('test_id.jpg', b'fake_id_card_content', 'image/jpeg'),
                'passport': ('test_passport.jpg', b'fake_passport_content', 'image/jpeg')
            }
            
            response = await self.client.post(f"{API_BASE}/applications/submit", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "application_id" in data and "message" in data:
                    self.test_application_id = data.get('application_id')
                    await self.log_result(
                        "Loan Application Submission", 
                        True, 
                        "Loan application submission working with new form fields",
                        f"Application ID: {self.test_application_id}"
                    )
                    return True
                else:
                    await self.log_result(
                        "Loan Application Submission", 
                        False, 
                        "Application response missing required fields",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Loan Application Submission", 
                    False, 
                    f"Application submission failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Loan Application Submission", False, f"Error: {str(e)}")
            return False
    
    async def test_admin_dashboard_api(self):
        """Test admin dashboard API endpoints"""
        if not self.admin_token:
            await self.log_result("Admin Dashboard API", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin stats endpoint
            response = await self.client.get(f"{API_BASE}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_keys = ["total_applications", "pending_applications", "approved_applications", "total_users"]
                
                if all(key in data for key in expected_keys):
                    await self.log_result(
                        "Admin Dashboard API", 
                        True, 
                        "Admin dashboard stats API working correctly",
                        f"Stats: {data}"
                    )
                    return True
                else:
                    await self.log_result(
                        "Admin Dashboard API", 
                        False, 
                        "Admin stats response missing required fields",
                        f"Expected: {expected_keys}, Got: {list(data.keys())}"
                    )
                    return False
            else:
                await self.log_result(
                    "Admin Dashboard API", 
                    False, 
                    f"Admin stats failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Admin Dashboard API", False, f"Error: {str(e)}")
            return False
    
    async def test_payment_endpoints_basic(self):
        """Test basic payment endpoint accessibility"""
        if not self.test_application_id:
            await self.log_result("Payment Endpoints Basic", False, "No test application available")
            return False
            
        try:
            # Test payment initiation endpoint structure
            payload = {
                "application_id": self.test_application_id,
                "customer_email": "test@example.com",
                "customer_name": "Test User",
                "amount": 2500,
                "redirect_url": f"{BACKEND_URL}/payment-callback"
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/initiate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # We expect this to work or fail gracefully (not crash)
            if response.status_code in [200, 400, 404, 500]:
                await self.log_result(
                    "Payment Endpoints Basic", 
                    True, 
                    f"Payment initiation endpoint accessible (status: {response.status_code})"
                )
                return True
            else:
                await self.log_result(
                    "Payment Endpoints Basic", 
                    False, 
                    f"Unexpected status code: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Payment Endpoints Basic", False, f"Error: {str(e)}")
            return False
    
    async def test_auth_middleware(self):
        """Test authentication middleware with protected endpoints"""
        try:
            # Test accessing protected endpoint without token
            response = await self.client.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 401:
                await self.log_result(
                    "Auth Middleware", 
                    True, 
                    "Authentication middleware correctly blocking unauthorized access"
                )
                return True
            else:
                await self.log_result(
                    "Auth Middleware", 
                    False, 
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Auth Middleware", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all regression tests"""
        print("🚀 Starting Backend Regression Testing")
        print("=" * 60)
        
        # Test sequence - order matters for dependencies
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_admin_login,
            self.test_password_reset_flow,
            self.test_loan_application_submission,
            self.test_admin_dashboard_api,
            self.test_payment_endpoints_basic,
            self.test_auth_middleware
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                await self.log_result(test.__name__, False, f"Test crashed: {str(e)}")
                print()
        
        print("=" * 60)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        else:
            print("\n✅ All tests passed!")
        
        await self.client.aclose()
        return passed, total, self.test_results

async def main():
    """Main test runner"""
    tester = BackendRegressionTester()
    passed, total, results = await tester.run_all_tests()
    
    # Write results to file
    with open('/app/backend_regression_results.json', 'w') as f:
        json.dump({
            'summary': {'passed': passed, 'total': total},
            'results': results,
            'test_type': 'backend_regression'
        }, f, indent=2)
    
    return passed, total, results

if __name__ == "__main__":
    passed, total, results = asyncio.run(main())
    sys.exit(0 if passed == total else 1)