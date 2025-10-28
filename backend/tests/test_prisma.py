"""
Simple test script to verify Prisma connection
"""
import asyncio
from prisma import Prisma


async def main():
    prisma = Prisma()
    
    try:
        # Connect to database
        print("🔄 Connecting to PostgreSQL...")
        await prisma.connect()
        print("✅ Successfully connected to PostgreSQL database!")
        
        # Test query - count users
        user_count = await prisma.user.count()
        print(f"📊 Current user count: {user_count}")
        
        print("\n✅ Prisma ORM is working correctly!")
        print("✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Disconnect from database
        await prisma.disconnect()
        print("👋 Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main())
