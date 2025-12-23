#!/usr/bin/env python3
"""
Test Xixapay Virtual Account and Transaction APIs
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_xixapay_virtual_accounts():
    """Test Xixapay virtual account creation which might be the payment method"""
    settings = get_settings()
    
    print("🏦 Testing Xixapay Virtual Account APIs")
    print("=" * 50)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test virtual account creation
        print("1. Testing virtual account creation...")
        try:
            va_payload = {
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "amount": 2500,
                "description": "Loan Processing Fee",
                "reference": "TEST-REF-123"
            }
            
            response = await client.post(
                f"{settings.xixapay_base_url}/api/virtual-account/create",
                headers=headers,
                json=va_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success! Virtual account created")
                return data
                
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # Test customer creation first
        print("2. Testing customer creation...")
        try:
            customer_payload = {
                "name": "Test Customer",
                "email": "test@example.com",
                "phone": "+2348012345678"
            }
            
            response = await client.post(
                f"{settings.xixapay_base_url}/api/customer/create",
                headers=headers,
                json=customer_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}...")
            
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # Test different virtual account endpoints
        va_endpoints = [
            "/api/virtual-account/create",
            "/api/v1/virtual-account/create", 
            "/api/virtual-account/dynamic/create",
            "/api/virtual-account/static/create"
        ]
        
        print("3. Testing virtual account endpoints...")
        for endpoint in va_endpoints:
            try:
                response = await client.post(
                    f"{settings.xixapay_base_url}{endpoint}",
                    headers=headers,
                    json={"test": "data"}
                )
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code not in [404, 405]:
                    print(f"      Response: {response.text[:200]}...")
            except Exception as e:
                print(f"   {endpoint}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_xixapay_virtual_accounts())