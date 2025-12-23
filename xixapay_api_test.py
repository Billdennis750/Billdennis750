#!/usr/bin/env python3
"""
Direct Xixapay API Testing to verify endpoints and credentials
"""

import asyncio
import httpx
import json
import os
from pathlib import Path

# Load environment variables
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_xixapay_api():
    """Test Xixapay API directly to verify endpoints and credentials"""
    settings = get_settings()
    
    print("🔍 Testing Xixapay API Directly")
    print("=" * 50)
    
    # Test configuration
    base_url = settings.xixapay_base_url
    api_key = settings.xixapay_api_key
    public_key = settings.xixapay_public_key
    merchant_id = settings.xixapay_merchant_id
    
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")
    print(f"Public Key: {public_key[:20]}...")
    print(f"Merchant ID: {merchant_id[:10]}...")
    print()
    
    headers = {
        "api-key": api_key,
        "Authorization": f"Bearer {public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Check if base URL is accessible
        print("1. Testing base URL accessibility...")
        try:
            response = await client.get(base_url)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # Test 2: Try the payment initiate endpoint
        print("2. Testing payment initiate endpoint...")
        try:
            test_payload = {
                "merchantId": merchant_id,
                "merchantTransactionId": "TEST-TXN-123",
                "amount": 2500,
                "currency": "NGN",
                "description": "Test Payment",
                "customer": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
            
            response = await client.post(
                f"{base_url}/api/v1/payment/initiate",
                headers=headers,
                json=test_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # Test 3: Try alternative endpoints that might exist
        alternative_endpoints = [
            "/api/payment/initiate",
            "/api/v1/transactions/create",
            "/api/transactions/initiate",
            "/api/v1/checkout/create"
        ]
        
        print("3. Testing alternative endpoints...")
        for endpoint in alternative_endpoints:
            try:
                response = await client.post(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    json={"test": "data"}
                )
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code != 404:
                    print(f"      Response: {response.text[:200]}...")
            except Exception as e:
                print(f"   {endpoint}: Error - {str(e)}")
        print()
        
        # Test 4: Check documented endpoints
        documented_endpoints = [
            "/api/customer/create",
            "/api/identity/verify"
        ]
        
        print("4. Testing documented endpoints...")
        for endpoint in documented_endpoints:
            try:
                response = await client.get(f"{base_url}{endpoint}", headers=headers)
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code not in [404, 405]:
                    print(f"      Response: {response.text[:200]}...")
            except Exception as e:
                print(f"   {endpoint}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_xixapay_api())