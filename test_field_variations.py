#!/usr/bin/env python3
"""
Test different field variations for Xixapay customer creation
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_field_variations():
    """Test different field name variations"""
    settings = get_settings()
    
    print("🔍 Testing Xixapay Field Variations")
    print("=" * 40)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    # Different payload variations to try
    payloads = [
        {
            "name": "Customer Creation v1",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "+2348012345678"
            }
        },
        {
            "name": "Customer Creation v2", 
            "data": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phoneNumber": "+2348012345678"
            }
        },
        {
            "name": "Customer Creation v3",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+2348012345678",
                "phone_number": "+2348012345678"
            }
        },
        {
            "name": "Customer Creation v4",
            "data": {
                "name": "John Doe",
                "email": "john.doe@example.com", 
                "phone": "+2348012345678"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        for payload_info in payloads:
            print(f"\n{payload_info['name']}:")
            try:
                response = await client.post(
                    f"{settings.xixapay_base_url}/api/customer/create",
                    headers=headers,
                    json=payload_info['data']
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"   ✅ Success with {payload_info['name']}!")
                    return response.json()
                    
            except Exception as e:
                print(f"   Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_field_variations())