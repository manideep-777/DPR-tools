"""
Tests for User Profile API endpoints
Tests GET and PUT operations for /api/user/profile
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app
from prisma import Prisma
from utils.auth_utils import create_access_token
import asyncio

client = TestClient(app)
prisma = Prisma()


@pytest.fixture(scope="module")
def event_loop():
    """Create an event loop for the test module"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    """Setup and teardown database connection"""
    await prisma.connect()
    yield
    await prisma.disconnect()


@pytest_asyncio.fixture
async def test_user():
    """Create a test user for profile testing"""
    # Create test user
    user = await prisma.user.create(
        data={
            "email": f"profiletest_{asyncio.get_event_loop().time()}@test.com",
            "hashedPassword": "hashed_password_123",
            "fullName": "Profile Test User",
            "phone": "9876543210",
            "businessType": "manufacturing",
            "state": "Telangana"
        }
    )
    
    yield user
    
    # Cleanup: delete user and cascade will delete profile
    await prisma.user.delete(where={"id": user.id})


@pytest.mark.asyncio
async def test_get_profile_creates_empty_profile(test_user):
    """Test that GET /api/user/profile creates an empty profile if none exists"""
    # Generate JWT token for test user
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Make GET request
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify profile data
    assert data["user_id"] == test_user.id
    assert data["address"] is None
    assert data["aadhar_number"] is None
    assert data["pan_number"] is None
    assert data["years_in_business"] is None
    assert data["bio"] is None
    
    # Verify profile was created in database
    profile = await prisma.userprofile.find_unique(where={"userId": test_user.id})
    assert profile is not None


@pytest.mark.asyncio
async def test_get_profile_without_auth():
    """Test that GET /api/user/profile requires authentication"""
    response = client.get("/api/user/profile")
    assert response.status_code == 403  # No credentials provided


@pytest.mark.asyncio
async def test_update_profile_all_fields(test_user):
    """Test updating all profile fields"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Update profile with all fields
    profile_data = {
        "address": "123 Test Street, Hyderabad, Telangana",
        "aadhar_number": "123456789012",
        "pan_number": "ABCDE1234F",
        "years_in_business": 5,
        "bio": "Test bio for profile testing"
    }
    
    response = client.put(
        "/api/user/profile",
        json=profile_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response
    assert data["success"] is True
    assert data["message"] == "Profile updated successfully"
    assert data["profile"]["address"] == profile_data["address"]
    assert data["profile"]["aadhar_number"] == profile_data["aadhar_number"]
    assert data["profile"]["pan_number"] == profile_data["pan_number"]
    assert data["profile"]["years_in_business"] == profile_data["years_in_business"]
    assert data["profile"]["bio"] == profile_data["bio"]
    
    # Verify in database
    profile = await prisma.userprofile.find_unique(where={"userId": test_user.id})
    assert profile.address == profile_data["address"]
    assert profile.aadharNumber == profile_data["aadhar_number"]


@pytest.mark.asyncio
async def test_update_profile_partial_fields(test_user):
    """Test updating only some profile fields"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # First create a profile with some data
    await client.put(
        "/api/user/profile",
        json={"address": "Old Address", "bio": "Old Bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Update only bio
    response = client.put(
        "/api/user/profile",
        json={"bio": "Updated Bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify bio was updated but address remains
    assert data["profile"]["bio"] == "Updated Bio"
    assert data["profile"]["address"] == "Old Address"


@pytest.mark.asyncio
async def test_update_profile_invalid_aadhar(test_user):
    """Test that invalid Aadhar number is rejected"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Try to update with invalid Aadhar (not 12 digits)
    response = client.put(
        "/api/user/profile",
        json={"aadhar_number": "12345"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("aadhar_number" in str(error).lower() for error in errors)


@pytest.mark.asyncio
async def test_update_profile_invalid_pan(test_user):
    """Test that invalid PAN number is rejected"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Try to update with invalid PAN format
    response = client.put(
        "/api/user/profile",
        json={"pan_number": "INVALID123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_profile_after_update(test_user):
    """Test that GET returns the updated profile data"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Update profile
    update_data = {
        "address": "456 Updated Street",
        "years_in_business": 3
    }
    
    await client.put(
        "/api/user/profile",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get profile
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == update_data["address"]
    assert data["years_in_business"] == update_data["years_in_business"]


@pytest.mark.asyncio
async def test_update_profile_without_auth():
    """Test that PUT /api/user/profile requires authentication"""
    response = client.put(
        "/api/user/profile",
        json={"bio": "Test"}
    )
    assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
