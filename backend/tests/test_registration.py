"""
Test file for User Registration API endpoint
Tests registration functionality, validation, and error handling
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma import Prisma
from utils.auth_utils import hash_password, verify_password
from models.auth_models import UserRegisterRequest
import json


async def test_password_hashing():
    """Test password hashing and verification"""
    print("\n" + "="*60)
    print("🔐 Testing Password Hashing...")
    print("="*60 + "\n")
    
    password = "TestPassword123"
    
    # Test hashing
    hashed = hash_password(password)
    print(f"✅ Password hashed successfully")
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    
    # Test verification - correct password
    is_valid = verify_password(password, hashed)
    if is_valid:
        print(f"✅ Password verification successful (correct password)")
    else:
        print(f"❌ Password verification failed (correct password)")
    
    # Test verification - wrong password
    is_invalid = verify_password("WrongPassword123", hashed)
    if not is_invalid:
        print(f"✅ Password verification correctly rejected wrong password")
    else:
        print(f"❌ Password verification incorrectly accepted wrong password")


async def test_user_registration():
    """Test user registration with valid data"""
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("\n" + "="*60)
        print("👤 Testing User Registration...")
        print("="*60 + "\n")
        
        # Test data
        test_user = {
            "email": "testuser@example.com",
            "password": "SecurePass123",
            "fullName": "Test User",
            "phone": "9876543210",
            "businessType": "Manufacturing",
            "state": "Andhra Pradesh"
        }
        
        # Check if user already exists (cleanup from previous tests)
        existing = await prisma.user.find_unique(where={"email": test_user["email"]})
        if existing:
            await prisma.user.delete(where={"id": existing.id})
            print(f"🧹 Cleaned up existing test user")
        
        # Hash password
        hashed_password = hash_password(test_user["password"])
        
        # Create user
        new_user = await prisma.user.create(
            data={
                "email": test_user["email"],
                "hashedPassword": hashed_password,
                "fullName": test_user["fullName"],
                "phone": test_user["phone"],
                "businessType": test_user["businessType"],
                "state": test_user["state"]
            }
        )
        
        print(f"✅ User created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Name: {new_user.fullName}")
        print(f"   Phone: {new_user.phone}")
        print(f"   Business Type: {new_user.businessType}")
        print(f"   State: {new_user.state}")
        
        # Verify password was hashed correctly
        is_password_valid = verify_password(test_user["password"], new_user.hashedPassword)
        if is_password_valid:
            print(f"✅ Password hashing verified")
        else:
            print(f"❌ Password hashing verification failed")
        
        # Test duplicate email
        try:
            duplicate_user = await prisma.user.create(
                data={
                    "email": test_user["email"],
                    "hashedPassword": hashed_password,
                    "fullName": "Duplicate User",
                    "phone": "1234567890"
                }
            )
            print(f"❌ Duplicate email check failed - should have raised error")
        except Exception as e:
            print(f"✅ Duplicate email correctly rejected")
        
        # Cleanup
        await prisma.user.delete(where={"id": new_user.id})
        print(f"\n🧹 Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
    finally:
        await prisma.disconnect()


async def test_validation():
    """Test input validation"""
    print("\n" + "="*60)
    print("✅ Testing Input Validation...")
    print("="*60 + "\n")
    
    # Test valid data
    try:
        valid_data = UserRegisterRequest(
            email="valid@example.com",
            password="ValidPass123",
            full_name="Valid User",
            phone="9876543210",
            business_type="Services",
            state="Telangana"
        )
        print(f"✅ Valid data accepted:")
        print(f"   Email: {valid_data.email}")
        print(f"   Phone: {valid_data.phone}")
    except Exception as e:
        print(f"❌ Valid data rejected: {e}")
    
    # Test invalid email
    try:
        invalid_email = UserRegisterRequest(
            email="invalid-email",
            password="ValidPass123",
            full_name="Test User",
            phone="9876543210"
        )
        print(f"❌ Invalid email accepted (should have failed)")
    except Exception as e:
        print(f"✅ Invalid email rejected: {str(e)[:80]}...")
    
    # Test weak password (no uppercase)
    try:
        weak_password = UserRegisterRequest(
            email="test@example.com",
            password="weakpass123",
            full_name="Test User",
            phone="9876543210"
        )
        print(f"❌ Weak password accepted (should have failed)")
    except Exception as e:
        print(f"✅ Weak password rejected: {str(e)[:80]}...")
    
    # Test short password
    try:
        short_password = UserRegisterRequest(
            email="test@example.com",
            password="Short1",
            full_name="Test User",
            phone="9876543210"
        )
        print(f"❌ Short password accepted (should have failed)")
    except Exception as e:
        print(f"✅ Short password rejected: {str(e)[:80]}...")
    
    # Test invalid phone
    try:
        invalid_phone = UserRegisterRequest(
            email="test@example.com",
            password="ValidPass123",
            full_name="Test User",
            phone="123"  # Too short
        )
        print(f"❌ Invalid phone accepted (should have failed)")
    except Exception as e:
        print(f"✅ Invalid phone rejected: {str(e)[:80]}...")


async def run_all_tests():
    """Run all registration tests"""
    print("\n" + "="*60)
    print("  User Registration API - Test Suite")
    print("="*60)
    
    await test_password_hashing()
    await test_validation()
    await test_user_registration()
    
    print("\n" + "="*60)
    print("  ✅ All Registration Tests Completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
