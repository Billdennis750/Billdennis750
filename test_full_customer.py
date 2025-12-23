#!/usr/bin/env python3
"""
Complete Xixapay customer creation with all fields
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_full_customer():
    """Test with all possible required fields"""
    settings = get_settings()
    
    print("🌟 Complete Xixapay Customer Test")
    print("=" * 35)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("Creating customer with all fields...")
        try:
            customer_payload = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "08012345678",
                "address": "123 Test Street",
                "city": "Lagos",
                "state": "Lagos"
            }
            
            response = await client.post(
                f"{settings.xixapay_base_url}/api/customer/create",
                headers=headers,
                json=customer_payload
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Customer created!")
                return response.json()
            else:
                print(f"❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

if __name__ == "__main__":
    result = asyncio.run(test_full_customer())
    if result:
        print("\n🎉 Xixapay customer creation is working!")
        print("Now we can proceed to test virtual accounts and payments")
    else:
        print("\n❌ Still having issues with customer creation")