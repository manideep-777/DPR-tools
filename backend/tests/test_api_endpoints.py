"""
Test API endpoints manually by making HTTP requests
Run this while the server is running
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import httpx
import json


async def test_registration_endpoint():
    """Test POST /api/auth/register endpoint"""
    print("\n" + "="*60)
    print("📡 Testing Registration Endpoint")
    print("="*60 + "\n")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Register a new user
    print("Test 1: Register new user...")
    user_data = {
        "email": "apitest@example.com",
        "password": "TestPass123",
        "full_name": "API Test User",
        "phone": "9876543210",
        "business_type": "Services",
        "state": "Andhra Pradesh"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/api/auth/register",
                json=user_data
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
            
            if response.status_code == 200:
                print("✅ User registration successful!")
                user_id = response.json().get("user_id")
                
                # Test 2: Try duplicate email
                print("\nTest 2: Try duplicate email...")
                response2 = await client.post(
                    f"{base_url}/api/auth/register",
                    json=user_data
                )
                print(f"Status Code: {response2.status_code}")
                print(f"Response: {json.dumps(response2.json(), indent=2)}\n")
                
                if response2.status_code == 400:
                    print("✅ Duplicate email correctly rejected!")
                
                # Test 3: Test with invalid password
                print("\nTest 3: Invalid password (too short)...")
                invalid_data = user_data.copy()
                invalid_data["email"] = "another@example.com"
                invalid_data["password"] = "short"
                
                response3 = await client.post(
                    f"{base_url}/api/auth/register",
                    json=invalid_data
                )
                print(f"Status Code: {response3.status_code}")
                print(f"Response: {json.dumps(response3.json(), indent=2)}\n")
                
                if response3.status_code == 422:
                    print("✅ Weak password correctly rejected!")
                
                # Test 4: Login with the registered user
                print("\nTest 4: Login with registered user...")
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                response4 = await client.post(
                    f"{base_url}/api/auth/login",
                    json=login_data
                )
                print(f"Status Code: {response4.status_code}")
                print(f"Response: {json.dumps(response4.json(), indent=2)}\n")
                
                if response4.status_code == 200:
                    print("✅ Login successful!")
                    token = response4.json().get("access_token")
                    print(f"   Token: {token[:50]}...")
                
                # Test 5: Login with wrong password
                print("\nTest 5: Login with wrong password...")
                wrong_login = {
                    "email": user_data["email"],
                    "password": "WrongPassword123"
                }
                
                response5 = await client.post(
                    f"{base_url}/api/auth/login",
                    json=wrong_login
                )
                print(f"Status Code: {response5.status_code}")
                print(f"Response: {json.dumps(response5.json(), indent=2)}\n")
                
                if response5.status_code == 401:
                    print("✅ Wrong password correctly rejected!")
            
        except httpx.ConnectError:
            print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ API Endpoint Tests Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running: uvicorn main:app --reload")
    asyncio.run(test_registration_endpoint())
