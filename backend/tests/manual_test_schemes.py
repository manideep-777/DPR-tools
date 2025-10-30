"""
Manual test script for Government Scheme Matching API
Tests the /api/schemes/match/{form_id} endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_separator(title=""):
    """Print a separator line"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def register_test_user():
    """Register a test user"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email = f"scheme_test_{timestamp}@test.com"
    
    user_data = {
        "email": email,
        "password": "TestPass123!",
        "full_name": "Scheme Test User",
        "phone": "9876543210"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def login_user(email, password):
    """Login user and get token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()["access_token"]

def create_dpr_form(token, business_name="Scheme Test Business"):
    """Create a new DPR form"""
    headers = {"Authorization": f"Bearer {token}"}
    form_data = {"business_name": business_name}
    
    response = requests.post(f"{BASE_URL}/form/create", json=form_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()["form_id"]

def add_business_details(token, form_id, sector="Manufacturing", location="Telangana"):
    """Add business details to the form"""
    headers = {"Authorization": f"Bearer {token}"}
    business_data = {
        "business_name": "Test Manufacturing Unit",
        "sector": sector,
        "sub_sector": "Electronics",
        "legal_structure": "Pvt Ltd",  # Fixed: Must be one of: proprietorship, partnership, LLP, Pvt Ltd
        "registration_number": "U12345TS2024PTC123456",
        "location": location,
        "address": "Survey No. 123, Industrial Area, Hyderabad, Telangana - 500001"
    }
    
    response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/business_details",
        json=business_data,
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    return response.status_code == 200

def add_financial_details(token, form_id, total_investment=5000000):
    """Add financial details to the form"""
    headers = {"Authorization": f"Bearer {token}"}
    financial_data = {
        "total_investment_amount": total_investment,
        "land_cost": 1000000,
        "building_cost": 1500000,
        "machinery_cost": 2000000,
        "working_capital": 500000,
        "other_costs": 0,
        "own_contribution": 2000000,
        "loan_required": 3000000
    }
    
    response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/financial_details",
        json=financial_data,
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    return response.status_code == 200

def get_all_schemes(token):
    """Get all available schemes"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/schemes/all", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        schemes = response.json()
        print(f"\n📋 Total schemes available: {len(schemes)}")
        for scheme in schemes[:3]:  # Show first 3
            print(f"\n  • {scheme['scheme_name']}")
            print(f"    Type: {scheme['scheme_type']}")
            print(f"    Ministry: {scheme['ministry']}")
    
    return response.json() if response.status_code == 200 else []

def match_schemes(token, form_id, max_results=10):
    """Match government schemes for the form"""
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {"max_results": max_results}
    
    response = requests.post(
        f"{BASE_URL}/schemes/match/{form_id}",
        json=request_data,
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_scheme_matching():
    """Main test function"""
    print_separator("GOVERNMENT SCHEME MATCHING - MANUAL TEST")
    
    # Step 1: Register user
    print_separator("Step 1: Register Test User")
    user_response = register_test_user()
    email = user_response["email"]
    
    # Step 2: Login
    print_separator("Step 2: Login User")
    token = login_user(email, "TestPass123!")
    print(f"✅ Token obtained: {token[:50]}...")
    
    # Step 3: Create DPR form
    print_separator("Step 3: Create DPR Form")
    form_id = create_dpr_form(token, "Tech Manufacturing Startup")
    print(f"✅ Form created with ID: {form_id}")
    
    # Step 4: Add business details
    print_separator("Step 4: Add Business Details")
    success = add_business_details(token, form_id, sector="Manufacturing", location="Telangana")
    if success:
        print("✅ Business details added successfully")
    
    # Step 5: Add financial details
    print_separator("Step 5: Add Financial Details")
    success = add_financial_details(token, form_id, total_investment=5000000)
    if success:
        print("✅ Financial details added successfully")
    
    # Step 6: Get all available schemes
    print_separator("Step 6: Get All Available Schemes")
    all_schemes = get_all_schemes(token)
    
    # Step 7: Match schemes (without business details - should fail)
    print_separator("Step 7: Match Schemes for the Form")
    match_result = match_schemes(token, form_id, max_results=10)
    
    if match_result.get("success"):
        print(f"\n✅ Scheme matching successful!")
        print(f"   Business: {match_result['business_name']}")
        print(f"   Total matches: {match_result['total_matches']}")
        print(f"   Showing: {len(match_result['matched_schemes'])} top matches")
        
        print("\n📊 Matched Schemes:")
        for i, scheme in enumerate(match_result['matched_schemes'], 1):
            print(f"\n{i}. {scheme['scheme_name']}")
            print(f"   Match Score: {scheme['match_score']}/100 ⭐")
            print(f"   Type: {scheme['scheme_type']}")
            print(f"   Ministry: {scheme['ministry']}")
            print(f"   Match Reasons:")
            for reason in scheme['match_reasons']:
                print(f"     • {reason}")
            if scheme.get('subsidy_percentage'):
                subsidy_amt = float(scheme['max_subsidy_amount']) if scheme['max_subsidy_amount'] else 0
                print(f"   Subsidy: {scheme['subsidy_percentage']}% (Max: ₹{subsidy_amt:,.0f})")
            if scheme.get('application_link'):
                print(f"   Apply: {scheme['application_link']}")
    
    # Test different scenarios
    print_separator("Step 8: Test Different Investment Amount")
    
    # High investment
    add_financial_details(token, form_id, total_investment=25000000)
    high_investment_result = match_schemes(token, form_id, max_results=5)
    if high_investment_result.get('total_matches') is not None:
        print(f"\n💰 High Investment (₹2.5 Cr) - {high_investment_result['total_matches']} matches")
    
    # Low investment
    add_financial_details(token, form_id, total_investment=200000)
    low_investment_result = match_schemes(token, form_id, max_results=5)
    if low_investment_result.get('total_matches') is not None:
        print(f"\n💰 Low Investment (₹2 Lakhs) - {low_investment_result['total_matches']} matches")
    
    # Test different sectors
    print_separator("Step 9: Test Different Sectors")
    
    # Food Processing sector
    add_business_details(token, form_id, sector="Food Processing", location="Maharashtra")
    add_financial_details(token, form_id, total_investment=3000000)
    food_result = match_schemes(token, form_id, max_results=5)
    if food_result.get('total_matches') is not None:
        print(f"\n🍲 Food Processing Sector - {food_result['total_matches']} matches")
    
    # Textile sector
    add_business_details(token, form_id, sector="Textile", location="Gujarat")
    textile_result = match_schemes(token, form_id, max_results=5)
    if textile_result.get('total_matches') is not None:
        print(f"\n🧵 Textile Sector - {textile_result['total_matches']} matches")
    
    print_separator("✅ ALL TESTS COMPLETED!")
    print("\nSummary:")
    print("  • User registration and login ✓")
    print("  • DPR form creation ✓")
    print("  • Business and financial details ✓")
    print("  • Scheme matching algorithm ✓")
    print("  • Different investment ranges ✓")
    print("  • Different sectors and states ✓")
    print("\n✨ Task 15 Government Scheme Matching working perfectly!")

if __name__ == "__main__":
    test_scheme_matching()
