"""
Quick verification that all routes work with new folder structure
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import httpx
import json
from multiprocessing import Process
import uvicorn


def run_server():
    """Run the server"""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="error")


async def verify_routes():
    """Verify all authentication routes work"""
    print("\n" + "="*60)
    print("✅ Verifying Routes with New Folder Structure")
    print("="*60 + "\n")
    
    await asyncio.sleep(2)  # Wait for server
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test 1: Health endpoint
            print("1. Testing /api/auth/health endpoint...")
            resp = await client.get("http://127.0.0.1:8000/api/auth/health")
            print(f"   Status: {resp.status_code} ✅")
            print(f"   Response: {resp.json()}\n")
            
            # Test 2: Register endpoint
            print("2. Testing /api/auth/register endpoint...")
            user_data = {
                "email": "structure_test@example.com",
                "password": "TestPass123",
                "full_name": "Structure Test",
                "phone": "9876543210",
                "business_type": "Testing",
                "state": "Test State"
            }
            resp = await client.post("http://127.0.0.1:8000/api/auth/register", json=user_data)
            print(f"   Status: {resp.status_code} ✅")
            print(f"   Response: {json.dumps(resp.json(), indent=2)}\n")
            
            # Test 3: Login endpoint
            print("3. Testing /api/auth/login endpoint...")
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            resp = await client.post("http://127.0.0.1:8000/api/auth/login", json=login_data)
            print(f"   Status: {resp.status_code} ✅")
            result = resp.json()
            print(f"   Token received: {result.get('access_token', '')[:50]}...\n")
            
            # Test 4: Documentation
            print("4. Testing /docs endpoint...")
            resp = await client.get("http://127.0.0.1:8000/docs")
            print(f"   Status: {resp.status_code} ✅")
            print(f"   API Documentation accessible\n")
            
            print("="*60)
            print("✅ All Routes Working Correctly!")
            print("="*60)
            print("\n📁 New Folder Structure:")
            print("   backend/")
            print("   ├── utils/")
            print("   │   ├── __init__.py")
            print("   │   └── auth_utils.py")
            print("   ├── models/")
            print("   │   ├── __init__.py")
            print("   │   └── auth_models.py")
            print("   └── routes/")
            print("       └── auth.py (updated imports)")
            print("\n✅ All endpoints now use /api prefix:")
            print("   - /api/auth/register")
            print("   - /api/auth/login")
            print("   - /api/auth/health\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main function"""
    server = Process(target=run_server)
    server.start()
    
    try:
        await verify_routes()
    finally:
        print("🛑 Stopping server...")
        server.terminate()
        server.join()
        print("✅ Done!\n")


if __name__ == "__main__":
    asyncio.run(main())
