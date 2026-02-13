#!/usr/bin/env python3
"""
Focused Backend API Testing for Payment Status Update & Loan Disbursement Workflow
Tests the endpoints that are accessible and validates the new functionality
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "https://mfb-staging.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials for testing
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30Z@"

class FocusedDisbursementTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_results = []
        
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
        if details:
            print(f"   Details: {details}")
    
    async def admin_login(self):
        """Login as admin to get authentication token"""
        try:
            login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                await self.log_result("Admin Login", True, "Admin logged in successfully")
                return True
            else:
                await self.log_result("Admin Login", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            await self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin authentication"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.admin_token}"
        }
    
    async def test_health_check(self):
        """Test if backend is running"""
        try:
            response = await self.client.get(f"{API_BASE}/health")
            if response.status_code == 200:
                await self.log_result("Health Check", True, "Backend is running")
                return True
            else:
                await self.log_result("Health Check", False, f"Backend returned {response.status_code}")
                return False
        except Exception as e:
            await self.log_result("Health Check", False, f"Backend not accessible: {str(e)}")
            return False
    
    async def test_admin_endpoints(self):
        """Test admin endpoints with authentication"""
        if not self.admin_token:
            await self.log_result("Admin Endpoints", False, "No admin token available")
            return False
            
        try:
            # Test admin users endpoint
            response = await self.client.get(
                f"{API_BASE}/admin/users",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                await self.log_result(
                    "Admin Users Endpoint", 
                    True, 
                    f"Retrieved {len(users)} users"
                )
            else:
                await self.log_result(
                    "Admin Users Endpoint", 
                    False, 
                    f"Failed: {response.status_code}",
                    response.text
                )
                return False
            
            # Test applications list endpoint
            response = await self.client.get(
                f"{API_BASE}/applications/",
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                applications = data.get("applications", [])
                await self.log_result(
                    "Applications List Endpoint", 
                    True, 
                    f"Retrieved {len(applications)} applications"
                )
                return True
            else:
                await self.log_result(
                    "Applications List Endpoint", 
                    False, 
                    f"Failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Admin Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_disbursement_endpoint_validation(self):
        """Test disbursement endpoint validation and error handling"""
        if not self.admin_token:
            await self.log_result("Disbursement Endpoint Validation", False, "No admin token")
            return False
            
        try:
            # Test 1: Invalid application ID
            invalid_payload = {
                "decision": "approve"
            }
            
            response = await self.client.post(
                f"{API_BASE}/admin/applications/INVALID-APP-ID/disbursement",
                json=invalid_payload,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 404:
                await self.log_result(
                    "Invalid Application ID Test", 
                    True, 
                    "Correctly rejected invalid application ID"
                )
            else:
                await self.log_result("Invalid Application ID Test", False, f"Expected 404, got {response.status_code}")
                return False
            
            # Test 2: Invalid decision value
            invalid_decision_payload = {
                "decision": "invalid_decision"
            }
            
            # Use an existing application ID
            response = await self.client.post(
                f"{API_BASE}/admin/applications/LOAN-2025-001/disbursement",
                json=invalid_decision_payload,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 400:
                await self.log_result(
                    "Invalid Decision Test", 
                    True, 
                    "Correctly rejected invalid decision"
                )
            else:
                await self.log_result("Invalid Decision Test", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test 3: Valid decision but wrong application status
            valid_payload = {
                "decision": "approve"
            }
            
            response = await self.client.post(
                f"{API_BASE}/admin/applications/LOAN-2025-001/disbursement",
                json=valid_payload,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 400:
                response_data = response.json()
                if "deposit_paid" in response_data.get("detail", ""):
                    await self.log_result(
                        "Application Status Validation", 
                        True, 
                        "Correctly validates application must be in deposit_paid status",
                        response_data.get("detail")
                    )
                    return True
                else:
                    await self.log_result("Application Status Validation", False, "Unexpected error message", response_data)
                    return False
            else:
                await self.log_result("Application Status Validation", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_result("Disbursement Endpoint Validation", False, f"Error: {str(e)}")
            return False
    
    async def test_payment_webhook_endpoint(self):
        """Test payment webhook endpoint accessibility and basic handling"""
        try:
            # Test webhook endpoint with valid structure but non-existent transaction
            webhook_payload = {
                "externalReference": f"CASHFLOW-TEST-{int(datetime.now().timestamp())}",
                "notification_status": "payment_successful",
                "transaction_id": f"TXN_TEST_{int(datetime.now().timestamp())}",
                "amount": 2500,
                "amount_paid": 2500
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/webhook",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" or data.get("status") == "ok":
                    await self.log_result(
                        "Payment Webhook Endpoint", 
                        True, 
                        "Webhook endpoint accessible and processing requests",
                        f"Response: {data.get('message', 'Webhook processed')}"
                    )
                    return True
                else:
                    await self.log_result("Payment Webhook Endpoint", False, "Unexpected webhook response", str(data))
                    return False
            else:
                await self.log_result("Payment Webhook Endpoint", False, f"Webhook failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            await self.log_result("Payment Webhook Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_disbursement_endpoint_structure(self):
        """Test that the disbursement endpoint exists and has correct structure"""
        if not self.admin_token:
            await self.log_result("Disbursement Endpoint Structure", False, "No admin token")
            return False
            
        try:
            # Test with missing decision field
            empty_payload = {}
            
            response = await self.client.post(
                f"{API_BASE}/admin/applications/LOAN-2025-001/disbursement",
                json=empty_payload,
                headers=self.get_admin_headers()
            )
            
            # Should get validation error for missing decision field
            if response.status_code == 422:
                await self.log_result(
                    "Disbursement Endpoint Structure", 
                    True, 
                    "Endpoint correctly validates required fields"
                )
                return True
            elif response.status_code == 400:
                # Might get 400 if it validates decision field first
                await self.log_result(
                    "Disbursement Endpoint Structure", 
                    True, 
                    "Endpoint exists and validates input"
                )
                return True
            else:
                await self.log_result("Disbursement Endpoint Structure", False, f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_result("Disbursement Endpoint Structure", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 Starting Focused Payment Status Update & Loan Disbursement Workflow Tests")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.admin_login,
            self.test_admin_endpoints,
            self.test_disbursement_endpoint_structure,
            self.test_disbursement_endpoint_validation,
            self.test_payment_webhook_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                await self.log_result(test.__name__, False, f"Test crashed: {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        # Show successful tests
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            print("\n✅ Successful Tests:")
            for test in successful_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        await self.client.aclose()
        return passed, total, self.test_results

async def main():
    """Main test runner"""
    tester = FocusedDisbursementTester()
    passed, total, results = await tester.run_all_tests()
    
    # Write results to file
    with open('/app/test_results_focused_disbursement.json', 'w') as f:
        json.dump({
            'summary': {'passed': passed, 'total': total},
            'results': results
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)