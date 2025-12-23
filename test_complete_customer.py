#!/usr/bin/env python3
"""
Final test with all required fields for Xixapay customer creation
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import sys
sys.path.append('/app/backend')
from config import get_settings

async def test_complete_customer():
    """Test with complete customer data"""
    settings = get_settings()
    
    print("🎯 Final Xixapay Customer Creation Test")
    print("=" * 45)
    
    headers = {
        "api-key": settings.xixapay_api_key,
        "Authorization": f"Bearer {settings.xixapay_public_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("1. Creating customer with complete data...")
        try:
            customer_payload = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "08012345678",
                "address": "123 Test Street, Lagos",
                "state": "Lagos"
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
                print(f"   Customer Data: {json.dumps(customer_data, indent=2)}")
                
                # Now test virtual account creation with the customer
                customer_id = customer_data.get("data", {}).get("id") or customer_data.get("customer_id")
                
                print(f"\n2. Testing virtual account creation for customer {customer_id}...")
                
                # Test different virtual account payloads
                va_tests = [
                    {
                        "name": "With customer_id",
                        "payload": {
                            "customer_id": customer_id,
                            "amount": 2500,
                            "description": "Loan Processing Fee",
                            "reference": "CASHFLOW-TEST-001"
                        }
                    },
                    {
                        "name": "With customer details",
                        "payload": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john.doe@example.com",
                            "phone_number": "08012345678",
                            "amount": 2500,
                            "description": "Loan Processing Fee",
                            "reference": "CASHFLOW-TEST-002"
                        }
                    },
                    {
                        "name": "Minimal payload",
                        "payload": {
                            "email": "john.doe@example.com",
                            "amount": 2500,
                            "reference": "CASHFLOW-TEST-003"
                        }
                    }
                ]
                
                va_endpoints = [
                    "/api/virtual-account/create",
                    "/api/virtual-account/dynamic/create"
                ]
                
                for test in va_tests:
                    for endpoint in va_endpoints:
                        try:
                            print(f"\n   Testing {endpoint} - {test['name']}...")
                            va_response = await client.post(
                                f"{settings.xixapay_base_url}{endpoint}",
                                headers=headers,
                                json=test['payload']
                            )
                            print(f"      Status: {va_response.status_code}")
                            print(f"      Response: {va_response.text[:400]}...")
                            
                            if va_response.status_code == 200:
                                print(f"      ✅ Virtual account created successfully!")
                                va_data = va_response.json()
                                print(f"      VA Data: {json.dumps(va_data, indent=2)}")
                                return {"customer": customer_data, "virtual_account": va_data}
                                
                        except Exception as e:
                            print(f"      Error: {str(e)}")
                
                return {"customer": customer_data, "virtual_account": None}
                
            else:
                print(f"   ❌ Customer creation failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"   Error: {str(e)}")
            return None

if __name__ == "__main__":
    result = asyncio.run(test_complete_customer())
    if result and result.get("customer"):
        print("\n🎉 SUCCESS! Customer creation is working!")
        if result.get("virtual_account"):
            print("🎉 BONUS! Virtual account creation also working!")
        else:
            print("⚠️  Virtual account creation needs more investigation")
    else:
        print("\n❌ Customer creation still not working")