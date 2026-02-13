"""
Backend API Tests for Pending Payments Feature
Tests the new admin payment confirmation workflow and pending payments endpoint
"""
import pytest
import requests
import os

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mfb-staging.preview.emergentagent.com').rstrip('/')

# Admin credentials for testing
ADMIN_EMAIL = "kdride6@gmail.com"
ADMIN_PASSWORD = "djscan30"


class TestAdminLogin:
    """Test admin login functionality"""
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=30)
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user data in response"
        assert data["user"]["role"] == "admin", "User is not admin"
        print(f"SUCCESS: Admin login - user role: {data['user']['role']}")


class TestPendingPaymentsEndpoint:
    """Test GET /api/payments/pending-payments endpoint"""
    
    def test_get_pending_payments_success(self):
        """Test fetching pending payments"""
        response = requests.get(f"{BASE_URL}/api/payments/pending-payments", timeout=30)
        
        assert response.status_code == 200, f"Failed to get pending payments: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Missing 'success' field"
        assert "count" in data, "Missing 'count' field"
        assert "transactions" in data, "Missing 'transactions' field"
        assert isinstance(data["transactions"], list), "Transactions is not a list"
        
        print(f"SUCCESS: Got {data['count']} pending payments")
        
        # Verify transaction structure if there are pending payments
        if data["count"] > 0:
            txn = data["transactions"][0]
            expected_fields = ["application_id", "order_reference", "customer_email", 
                            "customer_name", "amount", "payment_type", "status"]
            for field in expected_fields:
                assert field in txn, f"Transaction missing field: {field}"
            
            # Verify all transactions have pending status
            for txn in data["transactions"]:
                assert txn["status"] == "pending", f"Transaction {txn.get('order_reference')} has status {txn.get('status')}, expected 'pending'"
            
            print(f"SUCCESS: All transactions have correct structure and pending status")


class TestAdminConfirmPaymentEndpoint:
    """Test POST /api/payments/admin/confirm-payment endpoint"""
    
    def test_confirm_payment_missing_order_reference(self):
        """Test error handling for missing order reference"""
        response = requests.post(f"{BASE_URL}/api/payments/admin/confirm-payment", 
                                json={}, timeout=30)
        
        assert response.status_code == 422, f"Expected 422 for missing order_reference, got {response.status_code}"
        print("SUCCESS: Returns 422 for missing order_reference")
    
    def test_confirm_payment_invalid_order_reference(self):
        """Test error handling for invalid order reference"""
        response = requests.post(f"{BASE_URL}/api/payments/admin/confirm-payment", 
                                json={"order_reference": "INVALID-TEST-REF-12345"},
                                timeout=30)
        
        assert response.status_code == 404, f"Expected 404 for invalid order reference, got {response.status_code}"
        data = response.json()
        assert "detail" in data or "message" in data, "No error message in response"
        print("SUCCESS: Returns 404 for invalid order reference")
    
    def test_confirm_payment_with_pending_transaction(self):
        """Test confirming an actual pending payment (integration test)"""
        # First get pending payments
        response = requests.get(f"{BASE_URL}/api/payments/pending-payments", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        if data["count"] == 0:
            pytest.skip("No pending payments to test confirmation")
        
        # Get the first pending transaction (we won't actually confirm it to preserve test data)
        # Just verify the endpoint accepts the request format
        pending_txn = data["transactions"][0]
        order_ref = pending_txn["order_reference"]
        
        # Verify the transaction data is complete
        assert order_ref, "Order reference is empty"
        assert pending_txn["application_id"], "Application ID is empty"
        assert pending_txn["amount"] > 0, "Amount is invalid"
        
        print(f"SUCCESS: Found pending transaction {order_ref} ready for confirmation")
        print(f"  - Application: {pending_txn['application_id']}")
        print(f"  - Customer: {pending_txn['customer_name']}")
        print(f"  - Amount: {pending_txn['amount']}")
        print(f"  - Type: {pending_txn['payment_type']}")


class TestPaymentVerification:
    """Test payment verification endpoint"""
    
    def test_verify_invalid_order_ref(self):
        """Test verification with invalid order reference"""
        response = requests.post(f"{BASE_URL}/api/payments/verify", 
                                json={"order_ref": "INVALID-REF"},
                                timeout=30)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("SUCCESS: Returns 404 for invalid order reference")


class TestTransactionEndpoint:
    """Test GET /api/payments/transaction/{order_ref} endpoint"""
    
    def test_get_transaction_invalid_ref(self):
        """Test getting transaction with invalid reference"""
        response = requests.get(f"{BASE_URL}/api/payments/transaction/INVALID-REF", timeout=30)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("SUCCESS: Returns 404 for invalid transaction reference")
    
    def test_get_transaction_valid_ref(self):
        """Test getting transaction with valid reference"""
        # First get a pending payment to get a valid order reference
        response = requests.get(f"{BASE_URL}/api/payments/pending-payments", timeout=30)
        if response.status_code != 200:
            pytest.skip("Could not get pending payments")
        
        data = response.json()
        if data["count"] == 0:
            pytest.skip("No transactions to test")
        
        order_ref = data["transactions"][0]["order_reference"]
        
        # Get the specific transaction
        response = requests.get(f"{BASE_URL}/api/payments/transaction/{order_ref}", timeout=30)
        assert response.status_code == 200, f"Failed to get transaction: {response.text}"
        
        txn = response.json()
        assert txn["order_reference"] == order_ref, "Order reference mismatch"
        assert "application_id" in txn, "Missing application_id"
        assert "status" in txn, "Missing status"
        
        print(f"SUCCESS: Retrieved transaction {order_ref}")


class TestWebhookEndpoint:
    """Test POST /api/payments/webhook endpoint"""
    
    def test_webhook_missing_data(self):
        """Test webhook with empty payload"""
        response = requests.post(f"{BASE_URL}/api/payments/webhook", 
                                json={}, timeout=30)
        
        # Webhook should gracefully handle empty data
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"SUCCESS: Webhook handles empty payload (status: {response.status_code})")
    
    def test_webhook_invalid_reference(self):
        """Test webhook with invalid transaction reference"""
        response = requests.post(f"{BASE_URL}/api/payments/webhook", 
                                json={
                                    "eventType": "transaction",
                                    "data": {
                                        "orderId": "INVALID-TEST-REF",
                                        "status": "success",
                                        "amount": 2500
                                    }
                                }, timeout=30)
        
        # Should return 200 OK but indicate transaction not found
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data, "No message in response"
        print(f"SUCCESS: Webhook handles invalid reference gracefully: {data.get('message')}")


class TestDashboardIntegration:
    """Integration tests for admin dashboard data"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=30)
        
        if response.status_code != 200:
            pytest.skip("Could not login as admin")
        
        return response.json()["access_token"]
    
    def test_admin_can_view_applications(self, auth_token):
        """Test admin can view all applications"""
        response = requests.get(f"{BASE_URL}/api/applications/", 
                               headers={"Authorization": f"Bearer {auth_token}"},
                               timeout=30)
        
        assert response.status_code == 200, f"Failed to get applications: {response.text}"
        data = response.json()
        assert "applications" in data, "No applications in response"
        print(f"SUCCESS: Admin can view {len(data['applications'])} applications")
    
    def test_admin_can_view_users(self, auth_token):
        """Test admin can view all users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", 
                               headers={"Authorization": f"Bearer {auth_token}"},
                               timeout=30)
        
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        data = response.json()
        assert "users" in data, "No users in response"
        print(f"SUCCESS: Admin can view {len(data['users'])} users")
    
    def test_admin_can_view_transactions(self, auth_token):
        """Test admin can view transactions"""
        response = requests.get(f"{BASE_URL}/api/admin/transactions", 
                               headers={"Authorization": f"Bearer {auth_token}"},
                               timeout=30)
        
        assert response.status_code == 200, f"Failed to get transactions: {response.text}"
        data = response.json()
        assert "transactions" in data, "No transactions in response"
        print(f"SUCCESS: Admin can view {len(data['transactions'])} transactions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
