"""
Quick test to verify /api prefix is working
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import httpx
from multiprocessing import Process
import uvicorn


def run_server():
    """Run the server"""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="error")


async def quick_test():
    """Quick test of /api prefix"""
    print("\n🔍 Testing /api prefix...\n")
    
    await asyncio.sleep(2)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test health endpoint
            resp = await client.get("http://127.0.0.1:8000/api/auth/health")
            print(f"✅ GET /api/auth/health - Status: {resp.status_code}")
            
            # Test register endpoint
            data = {
                "email": "apitest@test.com",
                "password": "Test1234",
                "full_name": "API Test",
                "phone": "1234567890"
            }
            resp = await client.post("http://127.0.0.1:8000/api/auth/register", json=data)
            print(f"✅ POST /api/auth/register - Status: {resp.status_code}")
            
            # Test login endpoint  
            login = {"email": data["email"], "password": data["password"]}
            resp = await client.post("http://127.0.0.1:8000/api/auth/login", json=login)
            print(f"✅ POST /api/auth/login - Status: {resp.status_code}")
            
            print("\n✅ All endpoints working with /api prefix!\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    server = Process(target=run_server)
    server.start()
    
    try:
        await quick_test()
    finally:
        server.terminate()
        server.join()


if __name__ == "__main__":
    asyncio.run(main())
