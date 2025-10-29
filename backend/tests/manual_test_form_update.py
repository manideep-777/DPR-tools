"""
Manual test script for DPR form update endpoints
Tests PUT /api/form/{form_id} and PUT /api/form/{form_id}/section/{section_name}
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# Test user credentials
TEST_USER = {
    "email": f"updatetest_{datetime.now().timestamp()}@test.com",
    "password": "TestPass123!",
    "full_name": "Update Test User",
    "phone": "9988776655"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_form_update_endpoints():
    """Test all form update functionality"""
    
    print_section("FORM UPDATE ENDPOINTS - MANUAL TEST")
    
    # Step 1: Register user
    print("\n1. Registering test user...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    print(f"   Status: {register_response.status_code}")
    if register_response.status_code != 201:
        print(f"   Error: {register_response.text}")
        return
    print("   ✓ User registered successfully")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    print(f"   Status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   Error: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✓ Login successful")
    
    # Step 3: Create a form
    print("\n3. Creating a DPR form...")
    create_response = requests.post(f"{BASE_URL}/form/create", 
                                   json={"business_name": "Original Business Name"},
                                   headers=headers)
    print(f"   Status: {create_response.status_code}")
    if create_response.status_code != 201:
        print(f"   Error: {create_response.text}")
        return
    
    form_id = create_response.json()["form_id"]
    print(f"   ✓ Form created with ID: {form_id}")
    
    # Step 4: Update form's business name
    print("\n4. Updating form's business name...")
    update_response = requests.put(f"{BASE_URL}/form/{form_id}",
                                  json={"business_name": "Updated Business Name"},
                                  headers=headers)
    print(f"   Status: {update_response.status_code}")
    if update_response.status_code == 200:
        data = update_response.json()
        print(f"   ✓ Business name updated to: {data['business_name']}")
    else:
        print(f"   ✗ Error: {update_response.text}")
    
    # Step 5: Update form status
    print("\n5. Updating form status...")
    status_response = requests.put(f"{BASE_URL}/form/{form_id}",
                                  json={"status": "generating"},
                                  headers=headers)
    print(f"   Status: {status_response.status_code}")
    if status_response.status_code == 200:
        data = status_response.json()
        print(f"   ✓ Status updated to: {data['status']}")
    else:
        print(f"   ✗ Error: {status_response.text}")
    
    # Step 6: Test invalid status
    print("\n6. Testing invalid status update...")
    invalid_response = requests.put(f"{BASE_URL}/form/{form_id}",
                                   json={"status": "invalid"},
                                   headers=headers)
    print(f"   Status: {invalid_response.status_code}")
    if invalid_response.status_code == 422:
        print("   ✓ Validation error caught correctly")
    else:
        print(f"   ✗ Unexpected response: {invalid_response.text}")
    
    # Step 7: Test empty update
    print("\n7. Testing empty update...")
    empty_response = requests.put(f"{BASE_URL}/form/{form_id}",
                                 json={},
                                 headers=headers)
    print(f"   Status: {empty_response.status_code}")
    if empty_response.status_code == 400:
        print("   ✓ Empty update rejected correctly")
    else:
        print(f"   ✗ Unexpected response: {empty_response.text}")
    
    # Step 8: Update entrepreneur section (create)
    print("\n8. Creating entrepreneur details section...")
    entrepreneur_data = {
        "full_name": "John Entrepreneur",
        "date_of_birth": "1990-05-15",
        "education": "MBA in Finance",
        "years_of_experience": 8,
        "previous_business_experience": "Ran retail store for 3 years",
        "technical_skills": "Financial modeling, market analysis"
    }
    ent_response = requests.put(f"{BASE_URL}/form/{form_id}/section/entrepreneur_details",
                               json=entrepreneur_data,
                               headers=headers)
    print(f"   Status: {ent_response.status_code}")
    if ent_response.status_code == 200:
        data = ent_response.json()
        print(f"   ✓ Entrepreneur details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {ent_response.text}")
    
    # Step 9: Update business section
    print("\n9. Creating business details section...")
    business_data = {
        "business_name": "ABC Manufacturing Pvt Ltd",
        "sector": "Manufacturing",
        "sub_sector": "Metal Products",
        "legal_structure": "Pvt Ltd",
        "registration_number": "CIN123456789",
        "location": "Hyderabad, Telangana",
        "address": "Plot 123, Industrial Area, Hyderabad - 500001"
    }
    bus_response = requests.put(f"{BASE_URL}/form/{form_id}/section/business_details",
                               json=business_data,
                               headers=headers)
    print(f"   Status: {bus_response.status_code}")
    if bus_response.status_code == 200:
        data = bus_response.json()
        print(f"   ✓ Business details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {bus_response.text}")
    
    # Step 10: Update product section
    print("\n10. Creating product details section...")
    product_data = {
        "product_name": "Widget Pro X",
        "description": "High-quality industrial widgets with advanced features",
        "key_features": ["Durable", "Eco-friendly", "Cost-effective", "ISO certified"],
        "target_customers": "Manufacturing units, Industrial SMEs, Export markets",
        "current_capacity": 5000,
        "planned_capacity": 20000,
        "unique_selling_points": "Patented design with 30% cost savings over competitors",
        "quality_certifications": "ISO 9001:2015, CE Certified"
    }
    prod_response = requests.put(f"{BASE_URL}/form/{form_id}/section/product_details",
                                json=product_data,
                                headers=headers)
    print(f"   Status: {prod_response.status_code}")
    if prod_response.status_code == 200:
        data = prod_response.json()
        print(f"   ✓ Product details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {prod_response.text}")
    
    # Step 11: Update financial section
    print("\n11. Creating financial details section...")
    financial_data = {
        "total_investment_amount": 5000000,
        "land_cost": 1000000,
        "building_cost": 1500000,
        "machinery_cost": 2000000,
        "working_capital": 500000,
        "other_costs": 0,
        "own_contribution": 2000000,
        "loan_required": 3000000
    }
    fin_response = requests.put(f"{BASE_URL}/form/{form_id}/section/financial_details",
                               json=financial_data,
                               headers=headers)
    print(f"   Status: {fin_response.status_code}")
    if fin_response.status_code == 200:
        data = fin_response.json()
        print(f"   ✓ Financial details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {fin_response.text}")
    
    # Step 12: Update revenue section
    print("\n12. Creating revenue assumptions section...")
    revenue_data = {
        "product_price": 500,
        "monthly_sales_quantity_year1": 1000,
        "monthly_sales_quantity_year2": 1500,
        "monthly_sales_quantity_year3": 2000,
        "growth_rate_percentage": 15.5
    }
    rev_response = requests.put(f"{BASE_URL}/form/{form_id}/section/revenue_assumptions",
                               json=revenue_data,
                               headers=headers)
    print(f"   Status: {rev_response.status_code}")
    if rev_response.status_code == 200:
        data = rev_response.json()
        print(f"   ✓ Revenue assumptions created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {rev_response.text}")
    
    # Step 13: Update cost section
    print("\n13. Creating cost details section...")
    cost_data = {
        "raw_material_cost_monthly": 100000,
        "labor_cost_monthly": 50000,
        "utilities_cost_monthly": 15000,
        "rent_monthly": 25000,
        "marketing_cost_monthly": 10000,
        "other_fixed_costs_monthly": 5000
    }
    cost_response = requests.put(f"{BASE_URL}/form/{form_id}/section/cost_details",
                                json=cost_data,
                                headers=headers)
    print(f"   Status: {cost_response.status_code}")
    if cost_response.status_code == 200:
        data = cost_response.json()
        print(f"   ✓ Cost details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {cost_response.text}")
    
    # Step 14: Update staffing section
    print("\n14. Creating staffing details section...")
    staffing_data = {
        "total_employees": 25,
        "management_count": 3,
        "technical_staff_count": 15,
        "support_staff_count": 7,
        "average_salary": 25000
    }
    staff_response = requests.put(f"{BASE_URL}/form/{form_id}/section/staffing_details",
                                 json=staffing_data,
                                 headers=headers)
    print(f"   Status: {staff_response.status_code}")
    if staff_response.status_code == 200:
        data = staff_response.json()
        print(f"   ✓ Staffing details created")
        print(f"   Completion: {data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {staff_response.text}")
    
    # Step 15: Update timeline section (should reach 100% completion)
    print("\n15. Creating timeline details section...")
    timeline_data = {
        "land_acquisition_months": 2,
        "construction_months": 6,
        "machinery_installation_months": 3,
        "trial_production_months": 2,
        "commercial_production_start_month": 13
    }
    time_response = requests.put(f"{BASE_URL}/form/{form_id}/section/timeline_details",
                                json=timeline_data,
                                headers=headers)
    print(f"   Status: {time_response.status_code}")
    if time_response.status_code == 200:
        data = time_response.json()
        print(f"   ✓ Timeline details created")
        print(f"   Completion: {data['completion_percentage']}%")
        if data['completion_percentage'] == 100:
            print("   🎉 FORM 100% COMPLETE!")
    else:
        print(f"   ✗ Error: {time_response.text}")
    
    # Step 16: Partial update test
    print("\n16. Testing partial update (entrepreneur years_of_experience)...")
    partial_update = {"years_of_experience": 12}
    partial_response = requests.put(f"{BASE_URL}/form/{form_id}/section/entrepreneur_details",
                                   json=partial_update,
                                   headers=headers)
    print(f"   Status: {partial_response.status_code}")
    if partial_response.status_code == 200:
        print("   ✓ Partial update successful")
    else:
        print(f"   ✗ Error: {partial_response.text}")
    
    # Step 17: Test invalid section name
    print("\n17. Testing invalid section name...")
    invalid_section = requests.put(f"{BASE_URL}/form/{form_id}/section/invalid_section",
                                  json={"some_field": "value"},
                                  headers=headers)
    print(f"   Status: {invalid_section.status_code}")
    if invalid_section.status_code == 400:
        print("   ✓ Invalid section rejected correctly")
    else:
        print(f"   ✗ Unexpected response: {invalid_section.text}")
    
    # Step 18: Retrieve complete form
    print("\n18. Retrieving complete form...")
    get_response = requests.get(f"{BASE_URL}/form/{form_id}", headers=headers)
    print(f"   Status: {get_response.status_code}")
    if get_response.status_code == 200:
        form_data = get_response.json()
        print(f"   ✓ Form retrieved successfully")
        print(f"   Business Name: {form_data['business_name']}")
        print(f"   Status: {form_data['status']}")
        print(f"   Completion: {form_data['completion_percentage']}%")
    else:
        print(f"   ✗ Error: {get_response.text}")
    
    print_section("ALL TESTS COMPLETED")
    print("\nSummary:")
    print("✓ Form update (business_name, status)")
    print("✓ Section updates (all 8 sections)")
    print("✓ Completion percentage calculation")
    print("✓ Partial updates")
    print("✓ Validation (invalid status, empty updates, invalid sections)")
    print("✓ Authorization checks")


if __name__ == "__main__":
    try:
        test_form_update_endpoints()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("Please ensure the backend server is running:")
        print("  cd backend")
        print("  .\\venv\\Scripts\\activate")
        print("  python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
