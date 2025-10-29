"""
Automated Tests for User Forms List Endpoint (Task 11)
Tests GET /api/form/user/forms endpoint
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from prisma import Prisma

client = TestClient(app)
prisma = Prisma()

# Test user credentials
TEST_USER_EMAIL = f"formlist_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Forms List Tester"


@pytest.fixture(scope="module")
async def setup_db():
    """Setup database connection"""
    await prisma.connect()
    yield
    await prisma.disconnect()


@pytest.fixture
def auth_token():
    """Register user and return auth token"""
    # Register
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME
        }
    )
    assert register_response.status_code == 201
    print(f"\n✅ User registered: {register_response.json()}")
    
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    print(f"✅ User logged in: {login_data}")
    
    return login_data["access_token"]


def test_empty_forms_list(auth_token):
    """Test getting forms list when user has no forms"""
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n📋 Empty Forms List Response:")
    print(f"   Total Forms: {data['total_forms']}")
    print(f"   Forms: {data['forms']}")
    
    assert data["total_forms"] == 0
    assert data["forms"] == []
    assert "total_forms" in data
    assert "forms" in data


def test_single_form_in_list(auth_token):
    """Test getting forms list with one form"""
    # Create a form
    create_response = client.post(
        "/api/form/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"business_name": "Test Business 1"}
    )
    assert create_response.status_code == 201
    form_id = create_response.json()["form_id"]
    
    print(f"\n✅ Form created: {create_response.json()}")
    
    # Get forms list
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n📋 Single Form List Response:")
    print(f"   Total Forms: {data['total_forms']}")
    print(f"   Forms: {data['forms']}")
    
    assert data["total_forms"] == 1
    assert len(data["forms"]) == 1
    assert data["forms"][0]["id"] == form_id
    assert data["forms"][0]["business_name"] == "Test Business 1"
    assert data["forms"][0]["status"] == "draft"
    assert data["forms"][0]["completion_percentage"] == 0


def test_multiple_forms_ordering(auth_token):
    """Test getting multiple forms ordered by last_modified"""
    # Create three forms
    forms = []
    for i in range(1, 4):
        create_response = client.post(
            "/api/form/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"business_name": f"Business {i}"}
        )
        assert create_response.status_code == 201
        forms.append(create_response.json()["form_id"])
        print(f"✅ Form {i} created: {create_response.json()}")
    
    # Update the first form to change its last_modified
    update_response = client.put(
        f"/api/form/{forms[0]}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"business_name": "Updated Business 1", "status": "in-progress"}
    )
    assert update_response.status_code == 200
    print(f"✅ Form 1 updated: {update_response.json()}")
    
    # Get forms list
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n📋 Multiple Forms List Response:")
    print(f"   Total Forms: {data['total_forms']}")
    for i, form in enumerate(data['forms'], 1):
        print(f"   Form {i}: ID={form['id']}, Name={form['business_name']}, "
              f"Status={form['status']}, Completion={form['completion_percentage']}%")
    
    assert data["total_forms"] == 3
    assert len(data["forms"]) == 3
    
    # First form should be the most recently modified (forms[0])
    assert data["forms"][0]["id"] == forms[0]
    assert data["forms"][0]["business_name"] == "Updated Business 1"
    assert data["forms"][0]["status"] == "in-progress"


def test_forms_with_different_completion(auth_token):
    """Test forms list shows correct completion percentages"""
    # Create a form
    create_response = client.post(
        "/api/form/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"business_name": "Completion Test"}
    )
    form_id = create_response.json()["form_id"]
    
    # Update a section to get 12.5% completion
    section_response = client.put(
        f"/api/form/{form_id}/section/entrepreneur_details",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "John Doe",
            "contact_number": "1234567890",
            "email": "john@example.com",
            "aadhar_number": "123456789012",
            "pan_number": "ABCDE1234F"
        }
    )
    assert section_response.status_code == 200
    print(f"✅ Section updated: {section_response.json()}")
    
    # Get forms list
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    data = response.json()
    
    print(f"\n📋 Completion Test Response:")
    for form in data['forms']:
        if form['id'] == form_id:
            print(f"   Form: {form['business_name']}")
            print(f"   Completion: {form['completion_percentage']}%")
    
    # Find our test form
    test_form = next(f for f in data["forms"] if f["id"] == form_id)
    assert test_form["completion_percentage"] == 12  # 1/8 sections = 12.5% rounded to 12


def test_unauthorized_access():
    """Test that unauthorized requests are rejected"""
    response = client.get("/api/form/user/forms")
    
    assert response.status_code == 401
    print(f"\n🚫 Unauthorized Access Response: {response.json()}")


def test_forms_list_structure(auth_token):
    """Test the structure of forms list response"""
    # Create a form
    client.post(
        "/api/form/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"business_name": "Structure Test"}
    )
    
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    data = response.json()
    
    print(f"\n📋 Response Structure:")
    print(f"   Keys: {list(data.keys())}")
    if data['forms']:
        print(f"   Form Keys: {list(data['forms'][0].keys())}")
    
    # Verify response structure
    assert "total_forms" in data
    assert "forms" in data
    assert isinstance(data["total_forms"], int)
    assert isinstance(data["forms"], list)
    
    if data["forms"]:
        form = data["forms"][0]
        assert "id" in form
        assert "business_name" in form
        assert "status" in form
        assert "completion_percentage" in form
        assert "created_at" in form
        assert "last_modified" in form


def test_forms_list_with_different_statuses(auth_token):
    """Test forms list with various form statuses"""
    statuses = ["draft", "in-progress", "completed"]
    form_ids = []
    
    for status in statuses:
        # Create form
        create_resp = client.post(
            "/api/form/create",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"business_name": f"Business {status}"}
        )
        form_id = create_resp.json()["form_id"]
        form_ids.append(form_id)
        
        # Update status if not draft
        if status != "draft":
            client.put(
                f"/api/form/{form_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"business_name": f"Business {status}", "status": status}
            )
    
    # Get forms list
    response = client.get(
        "/api/form/user/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    data = response.json()
    
    print(f"\n📋 Forms with Different Statuses:")
    for form in data['forms']:
        if form['id'] in form_ids:
            print(f"   {form['business_name']}: {form['status']}")
    
    # Verify all statuses are present
    form_statuses = [f["status"] for f in data["forms"] if f["id"] in form_ids]
    for status in statuses:
        assert status in form_statuses
