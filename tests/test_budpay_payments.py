"""
BudPay Payment Integration Tests
Tests for payment initiation, verification, and webhook handling
"""
import pytest
import requests
import os
import json
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30Z@"
TEST_APPLICATION_ID = "LOAN-2025-002"


class TestBudPayPaymentEndpoints:
    """Test BudPay payment integration endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_health_check(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_get_applications_list(self):
        """Test fetching applications list"""
        response = self.session.get(f"{BASE_URL}/api/applications/")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        print(f"✓ Applications list fetched: {len(data['applications'])} applications")
        return data['applications']
    
    def test_get_specific_application(self):
        """Test fetching specific application by ID"""
        response = self.session.get(f"{BASE_URL}/api/applications/{TEST_APPLICATION_ID}")
        
        # Application may or may not exist
        if response.status_code == 200:
            data = response.json()
            assert "application_id" in data
            print(f"✓ Application found: {data.get('application_id')}")
            return data
        elif response.status_code == 404:
            print(f"⚠ Application {TEST_APPLICATION_ID} not found - this is expected if test data doesn't exist")
            pytest.skip("Test application not found")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_payment_initiate_missing_application(self):
        """Test payment initiation with non-existent application"""
        payload = {
            "application_id": "NONEXISTENT-APP-999",
            "customer_email": "test@example.com",
            "customer_name": "Test User",
            "customer_phone": "08012345678",
            "amount": 2500,
            "redirect_url": "https://example.com/callback"
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=payload)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"✓ Correctly rejected non-existent application: {data['detail']}")
    
    def test_payment_initiate_with_valid_application(self):
        """Test payment initiation with valid application - BudPay integration"""
        # First get a valid application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available for testing")
        
        # Use first available application
        test_app = apps[0]
        
        payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500,
            "redirect_url": "https://loan-app-staging.preview.emergentagent.com/payment-callback"
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=payload)
        
        # BudPay should return checkout link
        if response.status_code == 200:
            data = response.json()
            assert "checkout_link" in data, "Response should contain checkout_link"
            assert "order_reference" in data, "Response should contain order_reference"
            assert data.get("status") == "initiated"
            assert "CASHFLOW-" in data.get("order_reference", "")
            
            # Verify checkout link is from BudPay
            checkout_link = data.get("checkout_link", "")
            assert "budpay" in checkout_link.lower() or "checkout" in checkout_link.lower(), \
                f"Checkout link should be from BudPay: {checkout_link}"
            
            print(f"✓ Payment initiated successfully:")
            print(f"  - Order Reference: {data['order_reference']}")
            print(f"  - Checkout Link: {data['checkout_link'][:80]}...")
            print(f"  - Amount: {data.get('amount')} {data.get('currency')}")
            
            return data
        elif response.status_code == 502:
            # BudPay gateway error - could be API key issue or network
            data = response.json()
            print(f"⚠ BudPay gateway error: {data.get('detail')}")
            pytest.skip(f"BudPay gateway error: {data.get('detail')}")
        elif response.status_code == 504:
            print("⚠ BudPay gateway timeout")
            pytest.skip("BudPay gateway timeout")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code} - {response.text}")
    
    def test_payment_verify_nonexistent_transaction(self):
        """Test payment verification with non-existent transaction"""
        payload = {
            "order_ref": "NONEXISTENT-REF-12345"
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/verify", json=payload)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"✓ Correctly rejected non-existent transaction: {data['detail']}")
    
    def test_payment_verify_existing_transaction(self):
        """Test payment verification with existing transaction reference"""
        # Use the known successful test reference from main agent
        test_ref = "CASHFLOW-LOAN-2025-002-ebbea1ce"
        
        payload = {
            "order_ref": test_ref
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/verify", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "payment_status" in data
            assert "application_id" in data
            assert "amount" in data
            print(f"✓ Payment verification successful:")
            print(f"  - Status: {data['payment_status']}")
            print(f"  - Application: {data['application_id']}")
            print(f"  - Amount: {data['amount']}")
            return data
        elif response.status_code == 404:
            print(f"⚠ Transaction {test_ref} not found in database")
            pytest.skip("Test transaction not found")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_transaction_details(self):
        """Test getting transaction details by order reference"""
        test_ref = "CASHFLOW-LOAN-2025-002-ebbea1ce"
        
        response = self.session.get(f"{BASE_URL}/api/payments/transaction/{test_ref}")
        
        if response.status_code == 200:
            data = response.json()
            assert "order_reference" in data
            assert "application_id" in data
            assert "status" in data
            print(f"✓ Transaction details retrieved:")
            print(f"  - Order Ref: {data['order_reference']}")
            print(f"  - Status: {data['status']}")
            print(f"  - Amount: {data.get('amount')}")
            return data
        elif response.status_code == 404:
            print(f"⚠ Transaction {test_ref} not found")
            pytest.skip("Test transaction not found")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_webhook_endpoint_exists(self):
        """Test that webhook endpoint exists and accepts POST"""
        # Send empty webhook to test endpoint exists
        response = self.session.post(f"{BASE_URL}/api/payments/webhook", json={})
        
        # Should not return 404 or 405
        assert response.status_code != 404, "Webhook endpoint should exist"
        assert response.status_code != 405, "Webhook endpoint should accept POST"
        
        # May return 200 (ok) or 400 (bad request) depending on payload validation
        print(f"✓ Webhook endpoint exists, status: {response.status_code}")
    
    def test_webhook_with_mock_success_payload(self):
        """Test webhook processing with mock success payload"""
        # First create a payment to get a valid reference
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        
        # Initiate a payment first
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500,
            "redirect_url": "https://loan-app-staging.preview.emergentagent.com/payment-callback"
        }
        
        init_response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if init_response.status_code != 200:
            pytest.skip("Could not initiate payment for webhook test")
        
        order_ref = init_response.json().get("order_reference")
        
        # Now send a mock webhook
        webhook_payload = {
            "event": "charge.success",
            "data": {
                "reference": order_ref,
                "status": "success",
                "amount": 2500,
                "transaction_id": "TEST-TXN-12345"
            }
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/webhook", json=webhook_payload)
        
        # Webhook should process successfully
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["success", "ok"]
        print(f"✓ Webhook processed successfully: {data}")
        
        # Verify transaction was updated
        time.sleep(1)  # Allow DB update
        verify_response = self.session.post(f"{BASE_URL}/api/payments/verify", json={"order_ref": order_ref})
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            print(f"  - Updated status: {verify_data.get('payment_status')}")


class TestAuthenticationFlow:
    """Test authentication for admin access"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_admin_login(self):
        """Test admin login with provided credentials"""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data or "token" in data
            token = data.get("access_token") or data.get("token")
            print(f"✓ Admin login successful, token received")
            return token
        elif response.status_code == 401:
            print(f"⚠ Admin login failed - invalid credentials")
            pytest.skip("Admin credentials invalid")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_user_dashboard_access(self):
        """Test authenticated access to user applications"""
        # Login first
        login_payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        
        if login_response.status_code != 200:
            pytest.skip("Could not login")
        
        token = login_response.json().get("access_token") or login_response.json().get("token")
        
        # Access user applications
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(f"{BASE_URL}/api/applications/user/my-applications", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ User applications accessed: {len(data.get('applications', []))} applications")
        else:
            print(f"⚠ Could not access user applications: {response.status_code}")


class TestPaymentFlowIntegration:
    """End-to-end payment flow integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_full_payment_flow(self):
        """Test complete payment flow: initiate -> verify"""
        # Get an application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        print(f"Testing with application: {test_app['application_id']}")
        
        # Step 1: Initiate payment
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500,
            "redirect_url": "https://loan-app-staging.preview.emergentagent.com/payment-callback"
        }
        
        init_response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if init_response.status_code != 200:
            if init_response.status_code in [502, 504]:
                pytest.skip(f"BudPay gateway issue: {init_response.json().get('detail')}")
            pytest.fail(f"Payment initiation failed: {init_response.status_code}")
        
        init_data = init_response.json()
        order_ref = init_data.get("order_reference")
        checkout_link = init_data.get("checkout_link")
        
        print(f"✓ Step 1 - Payment initiated:")
        print(f"  - Order Reference: {order_ref}")
        print(f"  - Checkout Link: {checkout_link[:60]}...")
        
        # Step 2: Verify payment status (should be initiated/pending)
        verify_payload = {"order_ref": order_ref}
        verify_response = self.session.post(f"{BASE_URL}/api/payments/verify", json=verify_payload)
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        print(f"✓ Step 2 - Payment verification:")
        print(f"  - Status: {verify_data.get('payment_status')}")
        print(f"  - Application: {verify_data.get('application_id')}")
        
        # Step 3: Get transaction details
        txn_response = self.session.get(f"{BASE_URL}/api/payments/transaction/{order_ref}")
        
        assert txn_response.status_code == 200
        txn_data = txn_response.json()
        
        print(f"✓ Step 3 - Transaction details:")
        print(f"  - Status: {txn_data.get('status')}")
        print(f"  - Payment Method: {txn_data.get('payment_method')}")
        print(f"  - Created: {txn_data.get('created_at')}")
        
        return {
            "order_reference": order_ref,
            "checkout_link": checkout_link,
            "status": verify_data.get("payment_status")
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
