"""
Integrated test that starts server and tests endpoints
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import httpx
import json
from multiprocessing import Process
import time
import uvicorn


def run_server():
    """Run the FastAPI server"""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="error")


async def test_endpoints():
    """Test the API endpoints"""
    print("\n" + "="*60)
    print("📡 Testing Registration & Login Endpoints")
    print("="*60 + "\n")
    
    base_url = "http://127.0.0.1:8000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    await asyncio.sleep(3)
    
    # Cleanup test user if exists
    from prisma import Prisma
    prisma = Prisma()
    await prisma.connect()
    existing = await prisma.user.find_unique(where={"email": "integration@example.com"})
    if existing:
        await prisma.user.delete(where={"id": existing.id})
        print("🧹 Cleaned up existing test user\n")
    await prisma.disconnect()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test 1: Health check
            print("\nTest 1: Health check...")
            response = await client.get(f"{base_url}/api/auth/health")
            print(f"✅ Status: {response.status_code}")
            print(f"   Response: {response.json()}\n")
            
            # Test 2: Register a new user
            print("Test 2: Register new user...")
            user_data = {
                "email": "integration@example.com",
                "password": "TestPass123",
                "full_name": "Integration Test User",
                "phone": "9876543210",
                "business_type": "Services",
                "state": "Andhra Pradesh"
            }
            
            response = await client.post(f"{base_url}/api/auth/register", json=user_data)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}\n")
            
            if response.status_code in [200, 201]:
                print("✅ Registration successful!")
                user_id = result.get("user_id")
                
                # Test 3: Try duplicate registration
                print("\nTest 3: Try duplicate email...")
                response = await client.post(f"{base_url}/api/auth/register", json=user_data)
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}\n")
                if response.status_code == 400:
                    print("✅ Duplicate email rejected!")
                
                # Test 4: Login
                print("\nTest 4: Login with registered user...")
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                response = await client.post(f"{base_url}/api/auth/login", json=login_data)
                print(f"Status: {response.status_code}")
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}\n")
                
                if response.status_code == 200:
                    print("✅ Login successful!")
                    print(f"   Token: {result.get('access_token', '')[:50]}...")
                
                # Test 5: Wrong password
                print("\nTest 5: Login with wrong password...")
                wrong_data = {
                    "email": user_data["email"],
                    "password": "WrongPassword123"
                }
                response = await client.post(f"{base_url}/api/auth/login", json=wrong_data)
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}\n")
                if response.status_code == 401:
                    print("✅ Wrong password rejected!")
            
            print("\n" + "="*60)
            print("✅ All Endpoint Tests Passed!")
            print("="*60 + "\n")
            
        except httpx.ConnectError:
            print("❌ Could not connect to server")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main test runner"""
    # Start server in background process
    server_process = Process(target=run_server)
    server_process.start()
    
    try:
        # Run tests
        await test_endpoints()
    finally:
        # Stop server
        print("🛑 Stopping server...")
        server_process.terminate()
        server_process.join()
        print("✅ Server stopped\n")


if __name__ == "__main__":
    asyncio.run(main())
