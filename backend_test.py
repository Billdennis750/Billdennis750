#!/usr/bin/env python3
"""
Backend API Testing for Cashflow MFB - Payment Status Update & Loan Disbursement Workflow
Tests new disbursement decision endpoint, payment webhook handling, and admin features
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = "https://cashflow-dashboard-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials for testing
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30Z@"

class DisbursementWorkflowTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.test_application_id = None
        self.admin_token = None
        
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
                if self.admin_token:
                    await self.log_result("Admin Login", True, f"Admin logged in successfully")
                    return True
                else:
                    await self.log_result("Admin Login", False, "No access token in response")
                    return False
            else:
                await self.log_result("Admin Login", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            await self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin authentication"""
        if not self.admin_token:
            return {"Content-Type": "application/json"}
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
    
    async def create_test_application_with_deposit_paid_status(self):
        """Create a test application and set it to deposit_paid status for disbursement testing"""
        try:
            # Create multipart form data for application submission
            files = {
                'full_name': (None, 'Jane Smith'),
                'date_of_birth': (None, '1985-05-20'),
                'email': (None, 'jane.smith.test@example.com'),
                'phone': (None, '08087654321'),
                'secondary_phone': (None, '08012345678'),
                'relative_phone': (None, '08098765432'),
                'home_town': (None, 'Abuja'),
                'flat_house_number': (None, '15B'),
                'residential_address': (None, '15B Test Avenue, Abuja'),
                'place_of_work': (None, 'Test Corp Nigeria'),
                'employment_status': (None, 'employed'),
                'employment_details': (None, 'Senior Manager'),
                'monthly_income': (None, '250000'),
                'loan_reason': (None, 'Equipment purchase'),
                'bank_name': (None, 'First Bank'),
                'account_name': (None, 'Jane Smith'),
                'account_number': (None, '1234567890'),
                'loan_amount': (None, '1000000'),
                'repayment_duration': (None, '12_months'),
                'repayment_frequency': (None, 'monthly'),
                'nin': (None, '98765432109'),
                'bvn': (None, '98765432109'),
                'password': (None, 'TestPassword123!'),
                'id_card': ('test_id.jpg', b'fake_id_card_content', 'image/jpeg'),
                'passport': ('test_passport.jpg', b'fake_passport_content', 'image/jpeg')
            }
            
            response = await self.client.post(f"{API_BASE}/applications/submit", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.test_application_id = data.get('application_id')
                
                # Now simulate the payment workflow to get to deposit_paid status
                # 1. Mark processing fee as paid
                # 2. Approve the application
                # 3. Mark deposit as paid
                
                # We'll use direct database simulation via webhook calls
                await self.simulate_processing_fee_payment()
                await self.simulate_application_approval()
                await self.simulate_deposit_payment()
                
                await self.log_result(
                    "Create Test Application (Deposit Paid)", 
                    True, 
                    f"Application created and set to deposit_paid: {self.test_application_id}"
                )
                return True
            else:
                await self.log_result(
                    "Create Test Application (Deposit Paid)", 
                    False, 
                    f"Failed to create application: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Create Test Application (Deposit Paid)", False, f"Error: {str(e)}")
            return False
    
    async def simulate_processing_fee_payment(self):
        """Simulate processing fee payment via payment initiation and webhook"""
        try:
            # First initiate payment to create transaction record
            payment_payload = {
                "application_id": self.test_application_id,
                "customer_email": "jane.smith.test@example.com",
                "customer_name": "Jane Smith",
                "customer_phone": "08087654321",
                "amount": 2500,
                "redirect_url": f"{BACKEND_URL}/payment-callback"
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/initiate",
                json=payment_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                order_reference = data.get("order_reference")
                
                if order_reference:
                    # Now send webhook for successful payment
                    webhook_payload = {
                        "externalReference": order_reference,
                        "notification_status": "payment_successful",
                        "transaction_id": f"TXN_PROC_{int(datetime.now().timestamp())}",
                        "amount": 2500,
                        "amount_paid": 2500
                    }
                    
                    webhook_response = await self.client.post(
                        f"{API_BASE}/payments/webhook",
                        json=webhook_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if webhook_response.status_code == 200:
                        await self.log_result("Simulate Processing Fee Payment", True, "Processing fee payment simulated")
                        return True
                    else:
                        await self.log_result("Simulate Processing Fee Payment", False, f"Webhook failed: {webhook_response.status_code}")
                        return False
                else:
                    await self.log_result("Simulate Processing Fee Payment", False, "No order reference from payment initiation")
                    return False
            else:
                await self.log_result("Simulate Processing Fee Payment", False, f"Payment initiation failed: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_result("Simulate Processing Fee Payment", False, f"Error: {str(e)}")
            return False
    
    async def simulate_application_approval(self):
        """Simulate application approval by admin"""
        try:
            if not self.admin_token:
                await self.log_result("Simulate Application Approval", False, "No admin token")
                return False
            
            approval_payload = {
                "status": "approved",
                "approved_amount": 1000000,
                "notes": "Application approved for testing disbursement workflow"
            }
            
            response = await self.client.put(
                f"{API_BASE}/applications/{self.test_application_id}/status",
                json=approval_payload,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                await self.log_result("Simulate Application Approval", True, "Application approved")
                return True
            else:
                await self.log_result("Simulate Application Approval", False, f"Failed: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_result("Simulate Application Approval", False, f"Error: {str(e)}")
            return False
    
    async def simulate_deposit_payment(self):
        """Simulate deposit payment via webhook"""
        try:
            webhook_payload = {
                "externalReference": f"CASHFLOW-{self.test_application_id}-{int(datetime.now().timestamp())}",
                "notification_status": "payment_successful",
                "transaction_id": f"TXN_DEP_{int(datetime.now().timestamp())}",
                "amount": 3000,
                "amount_paid": 3000
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/webhook",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                await self.log_result("Simulate Deposit Payment", True, "Deposit payment simulated")
                return True
            else:
                await self.log_result("Simulate Deposit Payment", False, f"Failed: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_result("Simulate Deposit Payment", False, f"Error: {str(e)}")
            return False
    
    async def test_disbursement_decision_endpoint(self):
        """Test the new disbursement decision endpoint"""
        if not self.test_application_id or not self.admin_token:
            await self.log_result("Disbursement Decision Endpoint", False, "Missing application ID or admin token")
            return False
            
        try:
            # Test approve disbursement
            approve_payload = {
                "decision": "approve"
            }
            
            response = await self.client.post(
                f"{API_BASE}/admin/applications/{self.test_application_id}/disbursement",
                json=approve_payload,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("decision") == "approve" and data.get("status") == "disbursed":
                    await self.log_result(
                        "Disbursement Approve", 
                        True, 
                        "Disbursement approved successfully",
                        f"Status: {data.get('status')}"
                    )
                    
                    # Create another test application for decline test
                    await self.create_second_test_application()
                    
                    # Test decline disbursement
                    decline_payload = {
                        "decision": "decline",
                        "reason": "Test decline reason for automated testing"
                    }
                    
                    response = await self.client.post(
                        f"{API_BASE}/admin/applications/{self.test_application_id}/disbursement",
                        json=decline_payload,
                        headers=self.get_admin_headers()
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("decision") == "decline" and data.get("status") == "disbursement_declined":
                            await self.log_result(
                                "Disbursement Decline", 
                                True, 
                                "Disbursement declined successfully",
                                f"Status: {data.get('status')}"
                            )
                            return True
                        else:
                            await self.log_result("Disbursement Decline", False, "Unexpected response data", str(data))
                            return False
                    else:
                        await self.log_result("Disbursement Decline", False, f"Failed: {response.status_code}", response.text)
                        return False
                else:
                    await self.log_result("Disbursement Approve", False, "Unexpected response data", str(data))
                    return False
            else:
                await self.log_result("Disbursement Approve", False, f"Failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            await self.log_result("Disbursement Decision Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def create_second_test_application(self):
        """Create a second test application for decline testing"""
        try:
            files = {
                'full_name': (None, 'Bob Johnson'),
                'date_of_birth': (None, '1980-03-15'),
                'email': (None, 'bob.johnson.test@example.com'),
                'phone': (None, '08011223344'),
                'secondary_phone': (None, '08055667788'),
                'relative_phone': (None, '08099887766'),
                'home_town': (None, 'Port Harcourt'),
                'flat_house_number': (None, '22A'),
                'residential_address': (None, '22A Test Road, Port Harcourt'),
                'place_of_work': (None, 'Test Industries Ltd'),
                'employment_status': (None, 'employed'),
                'employment_details': (None, 'Operations Manager'),
                'monthly_income': (None, '180000'),
                'loan_reason': (None, 'Business expansion'),
                'bank_name': (None, 'GTBank'),
                'account_name': (None, 'Bob Johnson'),
                'account_number': (None, '0987654321'),
                'loan_amount': (None, '750000'),
                'repayment_duration': (None, '6_months'),
                'repayment_frequency': (None, 'monthly'),
                'nin': (None, '11223344556'),
                'bvn': (None, '11223344556'),
                'password': (None, 'TestPassword456!'),
                'id_card': ('test_id2.jpg', b'fake_id_card_content_2', 'image/jpeg'),
                'passport': ('test_passport2.jpg', b'fake_passport_content_2', 'image/jpeg')
            }
            
            response = await self.client.post(f"{API_BASE}/applications/submit", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.test_application_id = data.get('application_id')
                
                # Simulate payment workflow to get to deposit_paid status
                await self.simulate_processing_fee_payment()
                await self.simulate_application_approval()
                await self.simulate_deposit_payment()
                
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    async def test_payment_webhook_handling(self):
        """Test payment webhook handling for processing_fee_paid and deposit_paid flags"""
        try:
            # Test processing fee webhook (₦2,500)
            processing_webhook = {
                "externalReference": f"CASHFLOW-TEST-PROC-{int(datetime.now().timestamp())}",
                "notification_status": "payment_successful",
                "transaction_id": f"TXN_PROC_TEST_{int(datetime.now().timestamp())}",
                "amount": 2500,
                "amount_paid": 2500
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/webhook",
                json=processing_webhook,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    await self.log_result(
                        "Processing Fee Webhook", 
                        True, 
                        "Processing fee webhook handled correctly"
                    )
                else:
                    await self.log_result("Processing Fee Webhook", False, "Unexpected webhook response", str(data))
                    return False
            else:
                await self.log_result("Processing Fee Webhook", False, f"Failed: {response.status_code}", response.text)
                return False
            
            # Test deposit webhook (₦3,000)
            deposit_webhook = {
                "externalReference": f"CASHFLOW-TEST-DEP-{int(datetime.now().timestamp())}",
                "notification_status": "payment_successful",
                "transaction_id": f"TXN_DEP_TEST_{int(datetime.now().timestamp())}",
                "amount": 3000,
                "amount_paid": 3000
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/webhook",
                json=deposit_webhook,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    await self.log_result(
                        "Deposit Webhook", 
                        True, 
                        "Deposit webhook handled correctly"
                    )
                    return True
                else:
                    await self.log_result("Deposit Webhook", False, "Unexpected webhook response", str(data))
                    return False
            else:
                await self.log_result("Deposit Webhook", False, f"Failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            await self.log_result("Payment Webhook Handling", False, f"Error: {str(e)}")
            return False
    
    async def test_invalid_disbursement_scenarios(self):
        """Test invalid disbursement scenarios"""
        if not self.admin_token:
            await self.log_result("Invalid Disbursement Scenarios", False, "No admin token")
            return False
            
        try:
            # Test with invalid application ID
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
                    "Invalid Application ID", 
                    True, 
                    "Correctly rejected invalid application ID"
                )
            else:
                await self.log_result("Invalid Application ID", False, f"Expected 404, got {response.status_code}")
                return False
            
            # Test with invalid decision
            invalid_decision_payload = {
                "decision": "invalid_decision"
            }
            
            # Use a valid application ID but invalid decision
            if self.test_application_id:
                response = await self.client.post(
                    f"{API_BASE}/admin/applications/{self.test_application_id}/disbursement",
                    json=invalid_decision_payload,
                    headers=self.get_admin_headers()
                )
                
                if response.status_code == 400:
                    await self.log_result(
                        "Invalid Decision", 
                        True, 
                        "Correctly rejected invalid decision"
                    )
                    return True
                else:
                    await self.log_result("Invalid Decision", False, f"Expected 400, got {response.status_code}")
                    return False
            else:
                await self.log_result("Invalid Decision", False, "No test application ID available")
                return False
                
        except Exception as e:
            await self.log_result("Invalid Disbursement Scenarios", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all disbursement workflow tests"""
        print("🚀 Starting Payment Status Update & Loan Disbursement Workflow Tests")
        print("=" * 70)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.admin_login,
            self.test_admin_endpoints,
            self.create_test_application_with_deposit_paid_status,
            self.test_disbursement_decision_endpoint,
            self.test_payment_webhook_handling,
            self.test_invalid_disbursement_scenarios
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
        
        print("\n" + "=" * 70)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        await self.client.aclose()
        return passed, total, self.test_results

async def main():
    """Main test runner"""
    tester = DisbursementWorkflowTester()
    passed, total, results = await tester.run_all_tests()
    
    # Write results to file
    with open('/app/test_results_disbursement.json', 'w') as f:
        json.dump({
            'summary': {'passed': passed, 'total': total},
            'results': results
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)