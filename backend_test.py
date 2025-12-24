#!/usr/bin/env python3
"""
Backend API Testing for Cashflow MFB - Xixapay Payment Integration
Tests payment initiation, verification, and webhook handling
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

class XixapayPaymentTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
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
        if details:
            print(f"   Details: {details}")
    
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
    
    async def create_test_application(self):
        """Create a test application for payment testing"""
        try:
            # Create multipart form data for application submission
            files = {
                'full_name': (None, 'John Doe'),
                'date_of_birth': (None, '1990-01-15'),
                'email': (None, 'john.doe@example.com'),
                'phone': (None, '+2348012345678'),
                'home_town': (None, 'Lagos'),
                'residential_address': (None, '123 Test Street, Lagos'),
                'place_of_work': (None, 'Test Company Ltd'),
                'employment_status': (None, 'employed'),
                'employment_details': (None, 'Software Engineer'),
                'monthly_income': (None, '150000'),
                'loan_amount': (None, '500000'),
                'loan_reason': (None, 'Business expansion'),
                'nin': (None, '12345678901'),
                'bvn': (None, '12345678901'),
                'id_card': ('test_id.jpg', b'fake_id_card_content', 'image/jpeg'),
                'passport': ('test_passport.jpg', b'fake_passport_content', 'image/jpeg')
            }
            
            response = await self.client.post(f"{API_BASE}/applications/submit", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.test_application_id = data.get('application_id')
                await self.log_result(
                    "Create Test Application", 
                    True, 
                    f"Application created: {self.test_application_id}"
                )
                return True
            else:
                await self.log_result(
                    "Create Test Application", 
                    False, 
                    f"Failed to create application: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Create Test Application", False, f"Error: {str(e)}")
            return False
    
    async def test_payment_initiation(self):
        """Test payment initiation with Xixapay"""
        if not self.test_application_id:
            await self.log_result("Payment Initiation", False, "No test application available")
            return False
            
        try:
            payload = {
                "application_id": self.test_application_id,
                "customer_email": "john.doe@example.com",
                "customer_name": "John Doe",
                "amount": 2500,
                "redirect_url": f"{BACKEND_URL}/payment-callback"
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/initiate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                checkout_link = data.get('checkout_link')
                order_reference = data.get('order_reference')
                
                if checkout_link and order_reference:
                    self.order_reference = order_reference
                    await self.log_result(
                        "Payment Initiation", 
                        True, 
                        "Payment initiated successfully",
                        f"Order ref: {order_reference}, Checkout: {checkout_link[:50]}..."
                    )
                    return True
                else:
                    await self.log_result(
                        "Payment Initiation", 
                        False, 
                        "Missing checkout_link or order_reference in response",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Payment Initiation", 
                    False, 
                    f"API returned {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Payment Initiation", False, f"Error: {str(e)}")
            return False
    
    async def test_payment_verification(self):
        """Test payment verification"""
        if not hasattr(self, 'order_reference'):
            await self.log_result("Payment Verification", False, "No order reference available")
            return False
            
        try:
            payload = {
                "order_ref": self.order_reference
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/verify",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                payment_status = data.get('payment_status')
                
                # For testing, we expect 'pending' status since no actual payment was made
                if payment_status in ['pending', 'completed', 'failed']:
                    await self.log_result(
                        "Payment Verification", 
                        True, 
                        f"Verification working, status: {payment_status}",
                        str(data)
                    )
                    return True
                else:
                    await self.log_result(
                        "Payment Verification", 
                        False, 
                        f"Unexpected payment status: {payment_status}",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Payment Verification", 
                    False, 
                    f"API returned {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Payment Verification", False, f"Error: {str(e)}")
            return False
    
    async def test_webhook_handler(self):
        """Test webhook handler with sample payload"""
        if not hasattr(self, 'order_reference'):
            await self.log_result("Webhook Handler", False, "No order reference available")
            return False
            
        try:
            # Sample webhook payload simulating successful payment
            webhook_payload = {
                "merchantTransactionId": self.order_reference,
                "status": "success",
                "transactionId": "TXN_" + str(int(datetime.now().timestamp())),
                "amount": 2500,
                "currency": "NGN",
                "customer": {
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                },
                "metadata": {
                    "application_id": self.test_application_id,
                    "fee_type": "processing_fee"
                }
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/webhook",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    await self.log_result(
                        "Webhook Handler", 
                        True, 
                        "Webhook processed successfully",
                        str(data)
                    )
                    return True
                else:
                    await self.log_result(
                        "Webhook Handler", 
                        False, 
                        f"Webhook returned unexpected status: {data.get('status')}",
                        str(data)
                    )
                    return False
            else:
                await self.log_result(
                    "Webhook Handler", 
                    False, 
                    f"API returned {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Webhook Handler", False, f"Error: {str(e)}")
            return False
    
    async def test_invalid_application_payment(self):
        """Test payment initiation with invalid application ID"""
        try:
            payload = {
                "application_id": "INVALID-APP-ID",
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
            
            if response.status_code == 404:
                await self.log_result(
                    "Invalid Application Payment", 
                    True, 
                    "Correctly rejected invalid application ID"
                )
                return True
            else:
                await self.log_result(
                    "Invalid Application Payment", 
                    False, 
                    f"Expected 404, got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Invalid Application Payment", False, f"Error: {str(e)}")
            return False
    
    async def test_invalid_order_verification(self):
        """Test payment verification with invalid order reference"""
        try:
            payload = {
                "order_ref": "INVALID-ORDER-REF"
            }
            
            response = await self.client.post(
                f"{API_BASE}/payments/verify",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 404:
                await self.log_result(
                    "Invalid Order Verification", 
                    True, 
                    "Correctly rejected invalid order reference"
                )
                return True
            else:
                await self.log_result(
                    "Invalid Order Verification", 
                    False, 
                    f"Expected 404, got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            await self.log_result("Invalid Order Verification", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all payment tests"""
        print("🚀 Starting Xixapay Payment Integration Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.create_test_application,
            self.test_payment_initiation,
            self.test_payment_verification,
            self.test_webhook_handler,
            self.test_invalid_application_payment,
            self.test_invalid_order_verification
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
        
        print("\n" + "=" * 60)
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
    tester = XixapayPaymentTester()
    passed, total, results = await tester.run_all_tests()
    
    # Write results to file
    with open('/app/test_results_payments.json', 'w') as f:
        json.dump({
            'summary': {'passed': passed, 'total': total},
            'results': results
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)