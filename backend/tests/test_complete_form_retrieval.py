"""
Test suite for complete DPR form retrieval endpoint
Tests GET /api/form/{form_id}/complete
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test fixtures
TEST_USER = {
    "email": "complete_form@test.com",
    "password": "TestPass123!",
    "full_name": "Complete Form Tester",
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
def test_form_with_all_sections(auth_headers):
    """Create a form with all sections filled"""
    # Create form
    create_resp = client.post("/api/form/create", 
                             json={"business_name": "Complete Test Business"},
                             headers=auth_headers)
    form_id = create_resp.json()["form_id"]
    
    # Fill all 8 sections
    
    # 1. Entrepreneur details
    client.put(f"/api/form/{form_id}/section/entrepreneur_details", json={
        "full_name": "John Entrepreneur",
        "date_of_birth": "1990-05-15",
        "education": "MBA in Finance",
        "years_of_experience": 8,
        "previous_business_experience": "Ran retail store",
        "technical_skills": "Financial modeling"
    }, headers=auth_headers)
    
    # 2. Business details
    client.put(f"/api/form/{form_id}/section/business_details", json={
        "business_name": "ABC Manufacturing",
        "sector": "Manufacturing",
        "sub_sector": "Metal Products",
        "legal_structure": "Pvt Ltd",
        "registration_number": "CIN123456789",
        "location": "Hyderabad",
        "address": "Plot 123, Industrial Area"
    }, headers=auth_headers)
    
    # 3. Product details
    client.put(f"/api/form/{form_id}/section/product_details", json={
        "product_name": "Widget Pro",
        "description": "High-quality widgets",
        "key_features": ["Durable", "Eco-friendly"],
        "target_customers": "Manufacturing units",
        "current_capacity": 5000,
        "planned_capacity": 20000,
        "unique_selling_points": "Patented design",
        "quality_certifications": "ISO 9001:2015"
    }, headers=auth_headers)
    
    # 4. Financial details
    client.put(f"/api/form/{form_id}/section/financial_details", json={
        "total_investment_amount": 5000000,
        "land_cost": 1000000,
        "building_cost": 1500000,
        "machinery_cost": 2000000,
        "working_capital": 500000,
        "other_costs": 0,
        "own_contribution": 2000000,
        "loan_required": 3000000
    }, headers=auth_headers)
    
    # 5. Revenue assumptions
    client.put(f"/api/form/{form_id}/section/revenue_assumptions", json={
        "product_price": 500,
        "monthly_sales_quantity_year1": 1000,
        "monthly_sales_quantity_year2": 1500,
        "monthly_sales_quantity_year3": 2000,
        "growth_rate_percentage": 15.5
    }, headers=auth_headers)
    
    # 6. Cost details
    client.put(f"/api/form/{form_id}/section/cost_details", json={
        "raw_material_cost_monthly": 100000,
        "labor_cost_monthly": 50000,
        "utilities_cost_monthly": 15000,
        "rent_monthly": 25000,
        "marketing_cost_monthly": 10000,
        "other_fixed_costs_monthly": 5000
    }, headers=auth_headers)
    
    # 7. Staffing details
    client.put(f"/api/form/{form_id}/section/staffing_details", json={
        "total_employees": 25,
        "management_count": 3,
        "technical_staff_count": 15,
        "support_staff_count": 7,
        "average_salary": 25000
    }, headers=auth_headers)
    
    # 8. Timeline details
    client.put(f"/api/form/{form_id}/section/timeline_details", json={
        "land_acquisition_months": 2,
        "construction_months": 6,
        "machinery_installation_months": 3,
        "trial_production_months": 2,
        "commercial_production_start_month": 13
    }, headers=auth_headers)
    
    return form_id


@pytest.fixture
def test_form_partial(auth_headers):
    """Create a form with only some sections filled"""
    # Create form
    create_resp = client.post("/api/form/create", 
                             json={"business_name": "Partial Test Business"},
                             headers=auth_headers)
    form_id = create_resp.json()["form_id"]
    
    # Fill only 3 sections
    client.put(f"/api/form/{form_id}/section/entrepreneur_details", json={
        "full_name": "Jane Doe",
        "date_of_birth": "1985-03-20",
        "education": "B.Tech",
        "years_of_experience": 5
    }, headers=auth_headers)
    
    client.put(f"/api/form/{form_id}/section/business_details", json={
        "business_name": "XYZ Services",
        "sector": "Services",
        "legal_structure": "partnership",
        "location": "Mumbai",
        "address": "456 Business Park"
    }, headers=auth_headers)
    
    client.put(f"/api/form/{form_id}/section/financial_details", json={
        "total_investment_amount": 2000000,
        "land_cost": 0,
        "building_cost": 500000,
        "machinery_cost": 800000,
        "working_capital": 700000,
        "other_costs": 0,
        "own_contribution": 1000000,
        "loan_required": 1000000
    }, headers=auth_headers)
    
    return form_id


# Tests for GET /api/form/{form_id}/complete

def test_get_complete_form_all_sections(auth_headers, test_form_with_all_sections):
    """Test retrieving form with all sections filled"""
    form_id = test_form_with_all_sections
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify main form data
    assert data["id"] == form_id
    assert data["business_name"] == "Complete Test Business"
    assert data["status"] == "draft"
    assert data["completion_percentage"] == 100
    
    # Verify all sections are present
    assert data["entrepreneur_details"] is not None
    assert data["business_details"] is not None
    assert data["product_details"] is not None
    assert data["financial_details"] is not None
    assert data["revenue_assumptions"] is not None
    assert data["cost_details"] is not None
    assert data["staffing_details"] is not None
    assert data["timeline_details"] is not None
    
    # Verify entrepreneur details
    assert data["entrepreneur_details"]["full_name"] == "John Entrepreneur"
    assert data["entrepreneur_details"]["education"] == "MBA in Finance"
    assert data["entrepreneur_details"]["years_of_experience"] == 8
    
    # Verify business details
    assert data["business_details"]["business_name"] == "ABC Manufacturing"
    assert data["business_details"]["sector"] == "Manufacturing"
    assert data["business_details"]["legal_structure"] == "Pvt Ltd"
    
    # Verify product details
    assert data["product_details"]["product_name"] == "Widget Pro"
    assert len(data["product_details"]["key_features"]) == 2
    assert data["product_details"]["planned_capacity"] == 20000
    
    # Verify financial details
    assert float(data["financial_details"]["total_investment_amount"]) == 5000000
    assert float(data["financial_details"]["loan_required"]) == 3000000
    
    # Verify revenue assumptions
    assert float(data["revenue_assumptions"]["product_price"]) == 500
    assert data["revenue_assumptions"]["monthly_sales_quantity_year1"] == 1000
    
    # Verify cost details
    assert float(data["cost_details"]["raw_material_cost_monthly"]) == 100000
    assert float(data["cost_details"]["labor_cost_monthly"]) == 50000
    
    # Verify staffing details
    assert data["staffing_details"]["total_employees"] == 25
    assert data["staffing_details"]["management_count"] == 3
    
    # Verify timeline details
    assert data["timeline_details"]["construction_months"] == 6
    assert data["timeline_details"]["commercial_production_start_month"] == 13


def test_get_complete_form_partial_sections(auth_headers, test_form_partial):
    """Test retrieving form with only some sections filled"""
    form_id = test_form_partial
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify main form data
    assert data["id"] == form_id
    assert data["business_name"] == "Partial Test Business"
    assert data["completion_percentage"] == 37  # 3 out of 8 sections
    
    # Verify filled sections are present
    assert data["entrepreneur_details"] is not None
    assert data["business_details"] is not None
    assert data["financial_details"] is not None
    
    # Verify unfilled sections are None
    assert data["product_details"] is None
    assert data["revenue_assumptions"] is None
    assert data["cost_details"] is None
    assert data["staffing_details"] is None
    assert data["timeline_details"] is None


def test_get_complete_form_empty_sections(auth_headers):
    """Test retrieving form with no sections filled"""
    # Create form without filling sections
    create_resp = client.post("/api/form/create", 
                             json={"business_name": "Empty Form"},
                             headers=auth_headers)
    form_id = create_resp.json()["form_id"]
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify main form data
    assert data["id"] == form_id
    assert data["business_name"] == "Empty Form"
    assert data["completion_percentage"] == 0
    
    # Verify all sections are None
    assert data["entrepreneur_details"] is None
    assert data["business_details"] is None
    assert data["product_details"] is None
    assert data["financial_details"] is None
    assert data["revenue_assumptions"] is None
    assert data["cost_details"] is None
    assert data["staffing_details"] is None
    assert data["timeline_details"] is None


def test_get_complete_form_not_found(auth_headers):
    """Test retrieving non-existent form"""
    response = client.get("/api/form/99999/complete", headers=auth_headers)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_complete_form_unauthorized():
    """Test retrieving form without authentication"""
    response = client.get("/api/form/1/complete")
    
    assert response.status_code == 401


def test_get_complete_form_wrong_owner(auth_headers, test_form_with_all_sections):
    """Test retrieving form owned by different user"""
    form_id = test_form_with_all_sections
    
    # Create another user
    other_user = {
        "email": "other_complete@test.com",
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
    
    # Try to access first user's form
    response = client.get(f"/api/form/{form_id}/complete", headers=other_headers)
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_get_complete_form_decimal_precision(auth_headers, test_form_with_all_sections):
    """Test that decimal values are returned correctly"""
    form_id = test_form_with_all_sections
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check decimal precision
    assert data["financial_details"]["total_investment_amount"] == "5000000.00"
    assert data["revenue_assumptions"]["growth_rate_percentage"] == "15.50"
    assert data["staffing_details"]["average_salary"] == "25000.00"


def test_get_complete_form_date_format(auth_headers, test_form_with_all_sections):
    """Test that dates are formatted correctly"""
    form_id = test_form_with_all_sections
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check date format (should be YYYY-MM-DD)
    assert data["entrepreneur_details"]["date_of_birth"] == "1990-05-15"
    
    # Check datetime format (should include time)
    assert "T" in data["created_at"]
    assert "T" in data["last_modified"]


def test_get_complete_form_array_fields(auth_headers, test_form_with_all_sections):
    """Test that array fields are returned correctly"""
    form_id = test_form_with_all_sections
    
    response = client.get(f"/api/form/{form_id}/complete", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check key_features array
    assert isinstance(data["product_details"]["key_features"], list)
    assert "Durable" in data["product_details"]["key_features"]
    assert "Eco-friendly" in data["product_details"]["key_features"]


if __name__ == "__main__":
    print("Run tests with: pytest backend/tests/test_complete_form_retrieval.py -v")
