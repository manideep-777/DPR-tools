"""
Test suite for DPR form update endpoints
Tests PUT /api/form/{form_id} and PUT /api/form/{form_id}/section/{section_name}
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import date

client = TestClient(app)

# Test fixtures
TEST_USER = {
    "email": "formupdate@test.com",
    "password": "TestPass123!",
    "full_name": "Form Update Tester",
    "phone": "9876543210"
}

@pytest.fixture
def auth_headers():
    """Register a user and return auth headers"""
    # Register
    client.post("/api/auth/register", json=TEST_USER)
    
    # Login
    login_response = client.post("/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_form(auth_headers):
    """Create a test form and return its ID"""
    response = client.post("/api/form/create", 
                          json={"business_name": "Test Business"},
                          headers=auth_headers)
    return response.json()["form_id"]


# Tests for PUT /api/form/{form_id}

def test_update_form_business_name(auth_headers, test_form):
    """Test updating form's business name"""
    response = client.put(f"/api/form/{test_form}",
                         json={"business_name": "Updated Business Name"},
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["business_name"] == "Updated Business Name"
    assert data["form_id"] == test_form


def test_update_form_status(auth_headers, test_form):
    """Test updating form's status"""
    response = client.put(f"/api/form/{test_form}",
                         json={"status": "completed"},
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "completed"


def test_update_form_both_fields(auth_headers, test_form):
    """Test updating both business_name and status"""
    response = client.put(f"/api/form/{test_form}",
                         json={
                             "business_name": "Another Update",
                             "status": "generating"
                         },
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Another Update"
    assert data["status"] == "generating"


def test_update_form_invalid_status(auth_headers, test_form):
    """Test updating form with invalid status"""
    response = client.put(f"/api/form/{test_form}",
                         json={"status": "invalid_status"},
                         headers=auth_headers)
    
    assert response.status_code == 422


def test_update_form_no_fields(auth_headers, test_form):
    """Test updating form with no fields"""
    response = client.put(f"/api/form/{test_form}",
                         json={},
                         headers=auth_headers)
    
    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]


def test_update_form_not_found(auth_headers):
    """Test updating non-existent form"""
    response = client.put("/api/form/99999",
                         json={"business_name": "Test"},
                         headers=auth_headers)
    
    assert response.status_code == 404


def test_update_form_unauthorized():
    """Test updating form without auth"""
    response = client.put("/api/form/1",
                         json={"business_name": "Test"})
    
    assert response.status_code == 401


def test_update_form_wrong_owner(auth_headers, test_form):
    """Test updating form owned by different user"""
    # Create another user
    other_user = {
        "email": "other@test.com",
        "password": "TestPass123!",
        "full_name": "Other User",
        "phone": "8888888888"
    }
    client.post("/api/auth/register", json=other_user)
    login_resp = client.post("/api/auth/login", json={
        "email": other_user["email"],
        "password": other_user["password"]
    })
    other_token = login_resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to update first user's form
    response = client.put(f"/api/form/{test_form}",
                         json={"business_name": "Hacked"},
                         headers=other_headers)
    
    assert response.status_code == 403


# Tests for PUT /api/form/{form_id}/section/{section_name}

def test_update_entrepreneur_section_create(auth_headers, test_form):
    """Test creating entrepreneur details section"""
    section_data = {
        "full_name": "John Entrepreneur",
        "date_of_birth": "1990-05-15",
        "education": "MBA in Finance",
        "years_of_experience": 8,
        "previous_business_experience": "Ran a retail store for 3 years",
        "technical_skills": "Financial modeling, market analysis"
    }
    
    response = client.put(f"/api/form/{test_form}/section/entrepreneur_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["section_name"] == "entrepreneur_details"
    assert data["completion_percentage"] > 0  # Should increase


def test_update_entrepreneur_section_partial(auth_headers, test_form):
    """Test partial update of entrepreneur section (after creation)"""
    # First create full section
    section_data = {
        "full_name": "John Doe",
        "date_of_birth": "1990-01-01",
        "education": "MBA",
        "years_of_experience": 5
    }
    client.put(f"/api/form/{test_form}/section/entrepreneur_details",
              json=section_data,
              headers=auth_headers)
    
    # Then partial update
    update_data = {"years_of_experience": 10}
    response = client.put(f"/api/form/{test_form}/section/entrepreneur_details",
                         json=update_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_business_section(auth_headers, test_form):
    """Test creating business details section"""
    section_data = {
        "business_name": "ABC Manufacturing",
        "sector": "Manufacturing",
        "sub_sector": "Metal Products",
        "legal_structure": "Pvt Ltd",
        "registration_number": "CIN123456789",
        "location": "Hyderabad",
        "address": "Plot 123, Industrial Area, Hyderabad - 500001"
    }
    
    response = client.put(f"/api/form/{test_form}/section/business_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["section_name"] == "business_details"


def test_update_product_section(auth_headers, test_form):
    """Test creating product details section"""
    section_data = {
        "product_name": "Widget Pro X",
        "description": "High-quality widgets for industrial use",
        "key_features": ["Durable", "Eco-friendly", "Cost-effective"],
        "target_customers": "Manufacturing units, SMEs",
        "current_capacity": 5000,
        "planned_capacity": 20000,
        "unique_selling_points": "Patented design with 30% cost savings",
        "quality_certifications": "ISO 9001:2015, CE Certified"
    }
    
    response = client.put(f"/api/form/{test_form}/section/product_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_financial_section(auth_headers, test_form):
    """Test creating financial details section"""
    section_data = {
        "total_investment_amount": 5000000,
        "land_cost": 1000000,
        "building_cost": 1500000,
        "machinery_cost": 2000000,
        "working_capital": 500000,
        "other_costs": 0,
        "own_contribution": 2000000,
        "loan_required": 3000000
    }
    
    response = client.put(f"/api/form/{test_form}/section/financial_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_revenue_section(auth_headers, test_form):
    """Test creating revenue assumptions section"""
    section_data = {
        "product_price": 500,
        "monthly_sales_quantity_year1": 1000,
        "monthly_sales_quantity_year2": 1500,
        "monthly_sales_quantity_year3": 2000,
        "growth_rate_percentage": 15.5
    }
    
    response = client.put(f"/api/form/{test_form}/section/revenue_assumptions",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_cost_section(auth_headers, test_form):
    """Test creating cost details section"""
    section_data = {
        "raw_material_cost_monthly": 100000,
        "labor_cost_monthly": 50000,
        "utilities_cost_monthly": 15000,
        "rent_monthly": 25000,
        "marketing_cost_monthly": 10000,
        "other_fixed_costs_monthly": 5000
    }
    
    response = client.put(f"/api/form/{test_form}/section/cost_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_staffing_section(auth_headers, test_form):
    """Test creating staffing details section"""
    section_data = {
        "total_employees": 25,
        "management_count": 3,
        "technical_staff_count": 15,
        "support_staff_count": 7,
        "average_salary": 25000
    }
    
    response = client.put(f"/api/form/{test_form}/section/staffing_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_timeline_section(auth_headers, test_form):
    """Test creating timeline details section"""
    section_data = {
        "land_acquisition_months": 2,
        "construction_months": 6,
        "machinery_installation_months": 3,
        "trial_production_months": 2,
        "commercial_production_start_month": 13
    }
    
    response = client.put(f"/api/form/{test_form}/section/timeline_details",
                         json=section_data,
                         headers=auth_headers)
    
    assert response.status_code == 200


def test_update_section_invalid_name(auth_headers, test_form):
    """Test updating with invalid section name"""
    response = client.put(f"/api/form/{test_form}/section/invalid_section",
                         json={"some_field": "value"},
                         headers=auth_headers)
    
    assert response.status_code == 400
    assert "Invalid section name" in response.json()["detail"]


def test_update_section_no_fields(auth_headers, test_form):
    """Test updating section with no fields"""
    # First create the section
    section_data = {
        "full_name": "John Doe",
        "date_of_birth": "1990-01-01",
        "education": "MBA",
        "years_of_experience": 5
    }
    client.put(f"/api/form/{test_form}/section/entrepreneur_details",
              json=section_data,
              headers=auth_headers)
    
    # Try empty update
    response = client.put(f"/api/form/{test_form}/section/entrepreneur_details",
                         json={},
                         headers=auth_headers)
    
    assert response.status_code == 400


def test_update_section_incomplete_creation(auth_headers, test_form):
    """Test creating section without required fields"""
    # Try to create entrepreneur section with missing required fields
    incomplete_data = {
        "full_name": "John Doe"
        # Missing: date_of_birth, education, years_of_experience
    }
    
    response = client.put(f"/api/form/{test_form}/section/entrepreneur_details",
                         json=incomplete_data,
                         headers=auth_headers)
    
    assert response.status_code == 400
    assert "requires" in response.json()["detail"].lower()


def test_update_all_sections_completion_percentage(auth_headers, test_form):
    """Test that completion percentage reaches 100% when all sections filled"""
    
    # 1. Entrepreneur details
    client.put(f"/api/form/{test_form}/section/entrepreneur_details", json={
        "full_name": "John Doe", "date_of_birth": "1990-01-01",
        "education": "MBA", "years_of_experience": 5
    }, headers=auth_headers)
    
    # 2. Business details
    client.put(f"/api/form/{test_form}/section/business_details", json={
        "business_name": "ABC Corp", "sector": "Manufacturing",
        "legal_structure": "Pvt Ltd", "location": "Hyderabad",
        "address": "123 Street"
    }, headers=auth_headers)
    
    # 3. Product details
    client.put(f"/api/form/{test_form}/section/product_details", json={
        "product_name": "Widget", "description": "Test product",
        "key_features": ["Feature1"], "target_customers": "SMEs",
        "planned_capacity": 1000, "unique_selling_points": "Unique"
    }, headers=auth_headers)
    
    # 4. Financial details
    client.put(f"/api/form/{test_form}/section/financial_details", json={
        "total_investment_amount": 1000000, "land_cost": 100000,
        "building_cost": 200000, "machinery_cost": 300000,
        "working_capital": 100000, "other_costs": 0,
        "own_contribution": 500000, "loan_required": 500000
    }, headers=auth_headers)
    
    # 5. Revenue assumptions
    client.put(f"/api/form/{test_form}/section/revenue_assumptions", json={
        "product_price": 500, "monthly_sales_quantity_year1": 100,
        "monthly_sales_quantity_year2": 150, "monthly_sales_quantity_year3": 200,
        "growth_rate_percentage": 10
    }, headers=auth_headers)
    
    # 6. Cost details
    client.put(f"/api/form/{test_form}/section/cost_details", json={
        "raw_material_cost_monthly": 10000, "labor_cost_monthly": 5000,
        "utilities_cost_monthly": 2000, "rent_monthly": 3000,
        "marketing_cost_monthly": 1000, "other_fixed_costs_monthly": 500
    }, headers=auth_headers)
    
    # 7. Staffing details
    client.put(f"/api/form/{test_form}/section/staffing_details", json={
        "total_employees": 10, "management_count": 2,
        "technical_staff_count": 5, "support_staff_count": 3,
        "average_salary": 20000
    }, headers=auth_headers)
    
    # 8. Timeline details
    response = client.put(f"/api/form/{test_form}/section/timeline_details", json={
        "land_acquisition_months": 1, "construction_months": 3,
        "machinery_installation_months": 2, "trial_production_months": 1,
        "commercial_production_start_month": 7
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["completion_percentage"] == 100


def test_update_section_unauthorized():
    """Test updating section without auth"""
    response = client.put("/api/form/1/section/entrepreneur_details",
                         json={"full_name": "Test"})
    
    assert response.status_code == 401


def test_update_section_wrong_owner(auth_headers, test_form):
    """Test updating section of form owned by different user"""
    # Create another user
    other_user = {
        "email": "othersection@test.com",
        "password": "TestPass123!",
        "full_name": "Other User",
        "phone": "7777777777"
    }
    client.post("/api/auth/register", json=other_user)
    login_resp = client.post("/api/auth/login", json={
        "email": other_user["email"],
        "password": other_user["password"]
    })
    other_token = login_resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to update first user's form section
    response = client.put(f"/api/form/{test_form}/section/entrepreneur_details",
                         json={
                             "full_name": "Hacker",
                             "date_of_birth": "1990-01-01",
                             "education": "Hacking",
                             "years_of_experience": 0
                         },
                         headers=other_headers)
    
    assert response.status_code == 403


if __name__ == "__main__":
    print("Run tests with: pytest backend/tests/test_form_update.py -v")
