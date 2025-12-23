#!/usr/bin/env python3
"""
Test Xixapay with all required fields including address
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_with_address():
    """Test with all required fields"""
    settings = get_settings()
    
    print("🏠 Testing Xixapay with Address Field")
    print("=" * 40)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("1. Creating customer with all required fields...")
        try:
            customer_payload = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "08012345678",
                "address": "123 Test Street, Lagos, Nigeria"
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
                print(f"   Full response: {json.dumps(customer_data, indent=2)}")
                return customer_data
                
            else:
                print(f"   ❌ Still failed: {response.text}")
                
        except Exception as e:
            print(f"   Error: {str(e)}")

if __name__ == "__main__":
    result = asyncio.run(test_with_address())
    if result:
        print("\n🎉 SUCCESS! Customer creation working!")
    else:
        print("\n❌ Customer creation still not working")