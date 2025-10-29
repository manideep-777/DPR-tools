"""
Tests for DPR Form API endpoints
Tests POST /api/form/create and GET /api/form/{form_id}
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
    """Create a test user for form testing"""
    # Create test user
    user = await prisma.user.create(
        data={
            "email": f"formtest_{asyncio.get_event_loop().time()}@test.com",
            "hashedPassword": "hashed_password_123",
            "fullName": "Form Test User",
            "phone": "9876543210",
            "businessType": "manufacturing",
            "state": "Telangana"
        }
    )
    
    yield user
    
    # Cleanup: delete user and cascade will delete forms
    await prisma.user.delete(where={"id": user.id})


@pytest_asyncio.fixture
async def test_user2():
    """Create a second test user for authorization testing"""
    user = await prisma.user.create(
        data={
            "email": f"formtest2_{asyncio.get_event_loop().time()}@test.com",
            "hashedPassword": "hashed_password_456",
            "fullName": "Form Test User 2",
            "phone": "9876543211",
            "businessType": "services",
            "state": "Karnataka"
        }
    )
    
    yield user
    
    # Cleanup
    await prisma.user.delete(where={"id": user.id})


@pytest.mark.asyncio
async def test_create_form_success(test_user):
    """Test successful form creation"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    form_data = {
        "business_name": "Test Manufacturing Unit"
    }
    
    response = client.post(
        "/api/form/create",
        json=form_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert data["success"] is True
    assert data["message"] == "DPR form created successfully"
    assert data["form_id"] > 0
    assert data["business_name"] == form_data["business_name"]
    assert data["status"] == "draft"
    assert "created_at" in data
    
    # Verify in database
    form = await prisma.dprform.find_unique(where={"id": data["form_id"]})
    assert form is not None
    assert form.userId == test_user.id
    assert form.businessName == form_data["business_name"]
    assert form.status == "draft"
    assert form.completionPercentage == 0


@pytest.mark.asyncio
async def test_create_form_without_auth():
    """Test that form creation requires authentication"""
    form_data = {
        "business_name": "Test Business"
    }
    
    response = client.post("/api/form/create", json=form_data)
    assert response.status_code == 403  # No credentials


@pytest.mark.asyncio
async def test_create_form_empty_business_name(test_user):
    """Test that empty business name is rejected"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    form_data = {
        "business_name": ""
    }
    
    response = client.post(
        "/api/form/create",
        json=form_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_form_missing_business_name(test_user):
    """Test that missing business name is rejected"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    form_data = {}
    
    response = client.post(
        "/api/form/create",
        json=form_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_multiple_forms(test_user):
    """Test that a user can create multiple forms"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Create first form
    response1 = client.post(
        "/api/form/create",
        json={"business_name": "Business 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Create second form
    response2 = client.post(
        "/api/form/create",
        json={"business_name": "Business 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    form_id_1 = response1.json()["form_id"]
    form_id_2 = response2.json()["form_id"]
    
    assert form_id_1 != form_id_2


@pytest.mark.asyncio
async def test_get_form_success(test_user):
    """Test retrieving a form by ID"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    # Create a form first
    create_response = client.post(
        "/api/form/create",
        json={"business_name": "Test Business"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    form_id = create_response.json()["form_id"]
    
    # Retrieve the form
    get_response = client.get(
        f"/api/form/{form_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 200
    data = get_response.json()
    
    assert data["id"] == form_id
    assert data["user_id"] == test_user.id
    assert data["business_name"] == "Test Business"
    assert data["status"] == "draft"
    assert data["completion_percentage"] == 0


@pytest.mark.asyncio
async def test_get_form_not_found(test_user):
    """Test retrieving a non-existent form"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    
    response = client.get(
        "/api/form/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_form_unauthorized(test_user, test_user2):
    """Test that users can't access other users' forms"""
    # User 1 creates a form
    token1 = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    create_response = client.post(
        "/api/form/create",
        json={"business_name": "User 1 Business"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    form_id = create_response.json()["form_id"]
    
    # User 2 tries to access User 1's form
    token2 = create_access_token({"sub": test_user2.email, "user_id": test_user2.id})
    get_response = client.get(
        f"/api/form/{form_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert get_response.status_code == 403


@pytest.mark.asyncio
async def test_get_form_without_auth():
    """Test that form retrieval requires authentication"""
    response = client.get("/api/form/1")
    assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
