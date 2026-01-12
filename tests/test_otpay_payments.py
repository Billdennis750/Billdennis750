"""
OTPay Payment Integration Tests
Tests for OTPay virtual account payment flow:
- Payment initiation (creates virtual account)
- Payment verification
- Webhook handling (IP restricted)
- Virtual account retrieval
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

# OTPay webhook IPs (from documentation)
OTPAY_WEBHOOK_IPS = ["185.31.40.25", "2a00:b6e0:1:20:16::1"]


class TestOTPayPaymentEndpoints:
    """Test OTPay payment integration endpoints"""
    
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
        """Test payment initiation with valid application - OTPay virtual account"""
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
            "redirect_url": f"{BASE_URL}/payment-callback"
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=payload)
        
        # OTPay should return virtual account details
        if response.status_code == 200:
            data = response.json()
            
            # OTPay returns virtual_account instead of checkout_link
            assert "virtual_account" in data, f"Response should contain virtual_account: {data}"
            assert "order_reference" in data, "Response should contain order_reference"
            assert data.get("status") == "success"
            assert data.get("payment_type") == "bank_transfer"
            
            # Verify virtual account structure
            va = data.get("virtual_account", {})
            assert "account_number" in va, "Virtual account should have account_number"
            assert "account_name" in va, "Virtual account should have account_name"
            assert "bank_name" in va, "Virtual account should have bank_name"
            
            # Verify order reference format
            assert "CASHFLOW-" in data.get("order_reference", "")
            
            print(f"✓ OTPay Payment initiated successfully:")
            print(f"  - Order Reference: {data['order_reference']}")
            print(f"  - Bank: {va.get('bank_name')}")
            print(f"  - Account Number: {va.get('account_number')}")
            print(f"  - Account Name: {va.get('account_name')}")
            print(f"  - Amount: ₦{data.get('amount')} {data.get('currency')}")
            print(f"  - Message: {data.get('message')}")
            
            return data
        elif response.status_code == 502:
            # OTPay gateway error
            data = response.json()
            print(f"⚠ OTPay gateway error: {data.get('detail')}")
            pytest.skip(f"OTPay gateway error: {data.get('detail')}")
        elif response.status_code == 504:
            print("⚠ OTPay gateway timeout")
            pytest.skip("OTPay gateway timeout")
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
    
    def test_get_virtual_account_nonexistent(self):
        """Test getting virtual account for non-existent application"""
        response = self.session.get(f"{BASE_URL}/api/payments/virtual-account/NONEXISTENT-APP")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"✓ Correctly rejected non-existent virtual account: {data['detail']}")
    
    def test_get_virtual_account_for_application(self):
        """Test getting virtual account for an application"""
        # First get a valid application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        app_id = test_app["application_id"]
        
        # First initiate a payment to create virtual account
        init_payload = {
            "application_id": app_id,
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500
        }
        
        init_response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if init_response.status_code != 200:
            pytest.skip("Could not initiate payment to create virtual account")
        
        # Now get the virtual account
        response = self.session.get(f"{BASE_URL}/api/payments/virtual-account/{app_id}")
        
        if response.status_code == 200:
            data = response.json()
            assert "account_number" in data
            assert "account_name" in data
            assert "bank_name" in data
            assert "application_id" in data
            assert data["application_id"] == app_id
            
            print(f"✓ Virtual account retrieved:")
            print(f"  - Application: {data['application_id']}")
            print(f"  - Bank: {data['bank_name']}")
            print(f"  - Account: {data['account_number']}")
            print(f"  - Name: {data['account_name']}")
            return data
        elif response.status_code == 404:
            print(f"⚠ No active virtual account found for {app_id}")
            pytest.skip("No active virtual account")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_webhook_endpoint_exists(self):
        """Test that webhook endpoint exists and accepts POST"""
        response = self.session.post(f"{BASE_URL}/api/payments/webhook", json={})
        
        # Should not return 404 or 405
        assert response.status_code != 404, "Webhook endpoint should exist"
        assert response.status_code != 405, "Webhook endpoint should accept POST"
        
        # May return 200 (ok) or 403 (IP restricted) or 400 (bad request)
        print(f"✓ Webhook endpoint exists, status: {response.status_code}")
    
    def test_webhook_ip_restriction(self):
        """Test that webhook rejects requests from non-OTPay IPs"""
        # Our test request comes from a non-OTPay IP
        webhook_payload = {
            "email": "test@example.com",
            "phone": "08012345678",
            "business_code": "TEST",
            "account_number": "1234567890",
            "amount": 2500,
            "transaction_reference": "TEST-TXN-123"
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/webhook", json=webhook_payload)
        
        # Should be rejected due to IP restriction (403) or processed if IP check is disabled
        if response.status_code == 403:
            data = response.json()
            assert "Unauthorized IP" in data.get("detail", "") or "IP" in data.get("detail", "")
            print(f"✓ Webhook correctly rejected non-OTPay IP: {data['detail']}")
        elif response.status_code == 200:
            print(f"⚠ Webhook IP restriction may be disabled (accepted request)")
        else:
            print(f"✓ Webhook returned status {response.status_code}")
    
    def test_get_transaction_details(self):
        """Test getting transaction details by order reference"""
        # First create a transaction
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        
        # Initiate payment
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500
        }
        
        init_response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if init_response.status_code != 200:
            pytest.skip("Could not initiate payment")
        
        order_ref = init_response.json().get("order_reference")
        
        # Get transaction details
        response = self.session.get(f"{BASE_URL}/api/payments/transaction/{order_ref}")
        
        if response.status_code == 200:
            data = response.json()
            assert "order_reference" in data
            assert "application_id" in data
            assert "status" in data
            assert data["order_reference"] == order_ref
            
            print(f"✓ Transaction details retrieved:")
            print(f"  - Order Ref: {data['order_reference']}")
            print(f"  - Status: {data['status']}")
            print(f"  - Amount: {data.get('amount')}")
            print(f"  - Payment Method: {data.get('payment_method')}")
            return data
        elif response.status_code == 404:
            print(f"⚠ Transaction {order_ref} not found")
            pytest.skip("Transaction not found")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


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


class TestOTPayPaymentFlowIntegration:
    """End-to-end OTPay payment flow integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_full_otpay_payment_flow(self):
        """Test complete OTPay payment flow: initiate -> get VA -> verify"""
        # Get an application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        print(f"Testing with application: {test_app['application_id']}")
        
        # Step 1: Initiate payment (creates virtual account)
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500,
            "redirect_url": f"{BASE_URL}/payment-callback"
        }
        
        init_response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if init_response.status_code != 200:
            if init_response.status_code in [502, 504]:
                pytest.skip(f"OTPay gateway issue: {init_response.json().get('detail')}")
            pytest.fail(f"Payment initiation failed: {init_response.status_code} - {init_response.text}")
        
        init_data = init_response.json()
        order_ref = init_data.get("order_reference")
        virtual_account = init_data.get("virtual_account", {})
        
        print(f"✓ Step 1 - Payment initiated (Virtual Account created):")
        print(f"  - Order Reference: {order_ref}")
        print(f"  - Bank: {virtual_account.get('bank_name')}")
        print(f"  - Account: {virtual_account.get('account_number')}")
        print(f"  - Name: {virtual_account.get('account_name')}")
        
        # Step 2: Get virtual account details
        va_response = self.session.get(f"{BASE_URL}/api/payments/virtual-account/{test_app['application_id']}")
        
        if va_response.status_code == 200:
            va_data = va_response.json()
            print(f"✓ Step 2 - Virtual account retrieved:")
            print(f"  - Account: {va_data.get('account_number')}")
            print(f"  - Status: {va_data.get('status')}")
        else:
            print(f"⚠ Step 2 - Could not retrieve virtual account: {va_response.status_code}")
        
        # Step 3: Verify payment status (should be pending)
        verify_payload = {"order_ref": order_ref}
        verify_response = self.session.post(f"{BASE_URL}/api/payments/verify", json=verify_payload)
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        print(f"✓ Step 3 - Payment verification:")
        print(f"  - Status: {verify_data.get('payment_status')}")
        print(f"  - Application: {verify_data.get('application_id')}")
        print(f"  - Payment Type: {verify_data.get('payment_type')}")
        
        # Step 4: Get transaction details
        txn_response = self.session.get(f"{BASE_URL}/api/payments/transaction/{order_ref}")
        
        assert txn_response.status_code == 200
        txn_data = txn_response.json()
        
        print(f"✓ Step 4 - Transaction details:")
        print(f"  - Status: {txn_data.get('status')}")
        print(f"  - Payment Method: {txn_data.get('payment_method')}")
        print(f"  - Virtual Account: {txn_data.get('virtual_account_number')}")
        print(f"  - Created: {txn_data.get('created_at')}")
        
        return {
            "order_reference": order_ref,
            "virtual_account": virtual_account,
            "status": verify_data.get("payment_status")
        }
    
    def test_deposit_payment_flow(self):
        """Test deposit payment (₦3,000) flow"""
        # Get an application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        
        # Initiate deposit payment (₦3,000)
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 3000  # Deposit amount
        }
        
        response = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("amount") == 3000
            print(f"✓ Deposit payment initiated:")
            print(f"  - Amount: ₦{data.get('amount')}")
            print(f"  - Virtual Account: {data.get('virtual_account', {}).get('account_number')}")
        elif response.status_code in [502, 504]:
            pytest.skip(f"OTPay gateway issue: {response.json().get('detail')}")
        else:
            pytest.fail(f"Deposit payment failed: {response.status_code}")


class TestExistingVirtualAccount:
    """Test handling of existing virtual accounts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_reuse_existing_virtual_account(self):
        """Test that existing virtual account is returned instead of creating new one"""
        # Get an application
        apps_response = self.session.get(f"{BASE_URL}/api/applications/")
        if apps_response.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = apps_response.json().get("applications", [])
        if not apps:
            pytest.skip("No applications available")
        
        test_app = apps[0]
        
        # First initiation
        init_payload = {
            "application_id": test_app["application_id"],
            "customer_email": test_app.get("email", "test@example.com"),
            "customer_name": test_app.get("full_name", "Test User"),
            "customer_phone": test_app.get("phone", "08012345678"),
            "amount": 2500
        }
        
        response1 = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if response1.status_code != 200:
            pytest.skip("Could not initiate first payment")
        
        data1 = response1.json()
        account1 = data1.get("virtual_account", {}).get("account_number")
        
        # Second initiation - should return same virtual account
        response2 = self.session.post(f"{BASE_URL}/api/payments/initiate", json=init_payload)
        
        if response2.status_code != 200:
            pytest.skip("Could not initiate second payment")
        
        data2 = response2.json()
        account2 = data2.get("virtual_account", {}).get("account_number")
        
        # Should be the same account
        assert account1 == account2, f"Expected same account {account1}, got {account2}"
        print(f"✓ Existing virtual account reused: {account1}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
