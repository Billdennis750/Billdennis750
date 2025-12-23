#!/usr/bin/env python3
"""
Test Xixapay Customer Creation with proper parameters
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_customer_creation():
    """Test proper customer creation"""
    settings = get_settings()
    
    print("👤 Testing Xixapay Customer Creation")
    print("=" * 40)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test with proper customer data
        print("1. Testing customer creation with proper fields...")
        try:
            customer_payload = {
                "first_name": "John",
                "last_name": "Doe", 
                "email": "john.doe@example.com",
                "phone": "+2348012345678"
            }
            
            response = await client.post(
                f"{settings.xixapay_base_url}/api/customer/create",
                headers=headers,
                json=customer_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                customer_data = response.json()
                print("   ✅ Customer created successfully!")
                
                # Now try to create a virtual account for this customer
                print("\n2. Testing virtual account creation for customer...")
                
                va_payload = {
                    "customer_id": customer_data.get("data", {}).get("id"),
                    "amount": 2500,
                    "description": "Loan Processing Fee",
                    "reference": "CASHFLOW-TEST-123"
                }
                
                # Try different virtual account endpoints
                va_endpoints = [
                    "/api/virtual-account/create",
                    "/api/virtual-account/dynamic/create"
                ]
                
                for endpoint in va_endpoints:
                    try:
                        va_response = await client.post(
                            f"{settings.xixapay_base_url}{endpoint}",
                            headers=headers,
                            json=va_payload
                        )
                        print(f"   {endpoint}: {va_response.status_code}")
                        print(f"   Response: {va_response.text[:300]}...")
                        
                        if va_response.status_code == 200:
                            print(f"   ✅ Virtual account created via {endpoint}!")
                            return va_response.json()
                            
                    except Exception as e:
                        print(f"   {endpoint}: Error - {str(e)}")
                
            else:
                print(f"   ❌ Customer creation failed: {response.text}")
                
        except Exception as e:
            print(f"   Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_customer_creation())