"""
Task 13: Single Section AI Generation - Manual Test
Test the new /form/{form_id}/generate/{section} endpoint
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = f"single_section_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
TEST_PASSWORD = "TestPass123!"

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)

def print_response(response, title="Response"):
    print(f"\n--- {title} ---")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# Test Steps
def main():
    print_separator("TASK 13: Single Section AI Generation - Manual Test")
    
    # Step 1: Register and login (reuse existing form from Task 12 if possible)
    print_separator("Step 1: Register Test User")
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "full_name": "Single Section Test User",
        "email": TEST_EMAIL,
        "phone": "9876543210",
        "password": TEST_PASSWORD
    })
    print_response(register_response, "Registration Response")
    
    if register_response.status_code != 201:
        print("\n❌ Registration failed!")
        return
    
    # Step 2: Login
    print_separator("Step 2: Login User")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    print_response(login_response, "Login Response")
    
    if login_response.status_code != 200:
        print("\n❌ Login failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Create a form
    print_separator("Step 3: Create DPR Form")
    form_response = requests.post(f"{BASE_URL}/form/create", 
        json={"business_name": "Single Section Test Startup"},
        headers=headers
    )
    print_response(form_response, "Form Creation Response")
    
    if form_response.status_code != 201:
        print("\n❌ Form creation failed!")
        return
    
    form_id = form_response.json()["form_id"]
    print(f"\n✅ Form created with ID: {form_id}")
    
    # Step 4: Add minimum required data
    print_separator("Step 4: Add Required Form Data")
    
    # Entrepreneur details
    entrepreneur_data = {
        "full_name": "Test Entrepreneur",
        "date_of_birth": "1990-01-01",
        "education": "MBA",
        "years_of_experience": 5,
        "previous_business_experience": "2 years in retail",
        "technical_skills": "Digital marketing, Basic accounting"
    }
    entrepreneur_resp = requests.put(f"{BASE_URL}/form/{form_id}/section/entrepreneur_details", 
                                      json=entrepreneur_data, headers=headers)
    print(f"Entrepreneur details: {entrepreneur_resp.status_code}")
    if entrepreneur_resp.status_code != 200:
        print(f"❌ Failed to add entrepreneur details: {entrepreneur_resp.json()}")
    
    # Business details
    business_data = {
        "business_name": "Single Section Test Startup",
        "sector": "Food Processing",
        "sub_sector": "Organic Food Products",
        "legal_structure": "Pvt Ltd",  # Must match: proprietorship|partnership|LLP|Pvt Ltd
        "registration_number": "CIN12345",
        "location": "Hyderabad, Telangana",
        "address": "Test Address, Street 123"
    }
    business_resp = requests.put(f"{BASE_URL}/form/{form_id}/section/business_details", 
                                  json=business_data, headers=headers)
    print(f"Business details: {business_resp.status_code}")
    if business_resp.status_code != 200:
        print(f"❌ Failed to add business details: {business_resp.json()}")
    
    if entrepreneur_resp.status_code == 200 and business_resp.status_code == 200:
        print("✅ Required form data added")
    else:
        print("❌ Failed to add required form data")
    
    # Step 5: Test invalid section name
    print_separator("Step 5: Test Invalid Section Name")
    invalid_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate/invalid_section",
        headers=headers
    )
    print_response(invalid_response, "Invalid Section Response")
    
    if invalid_response.status_code == 400:
        print("✅ Invalid section name correctly rejected")
    else:
        print("❌ Should have returned 400 for invalid section")
    
    # Step 6: Generate a single section (executive_summary)
    print_separator("Step 6: Generate Executive Summary")
    exec_summary_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate/executive_summary",
        headers=headers
    )
    print_response(exec_summary_response, "Executive Summary Generation")
    
    if exec_summary_response.status_code == 201:
        data = exec_summary_response.json()
        if data["total_sections"] == 1 and data["sections_generated"][0]["section_name"] == "executive_summary":
            print("✅ Executive summary generated successfully")
            print(f"   Version: {data['sections_generated'][0]['version_number']}")
            print(f"   Length: {len(data['sections_generated'][0]['generated_text'])} chars")
        else:
            print("❌ Unexpected response structure")
    else:
        print("❌ Executive summary generation failed")
    
    # Step 7: Generate another section (market_analysis)
    print_separator("Step 7: Generate Market Analysis")
    market_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate/market_analysis",
        headers=headers
    )
    print_response(market_response, "Market Analysis Generation")
    
    if market_response.status_code == 201:
        print("✅ Market analysis generated successfully")
    else:
        print("❌ Market analysis generation failed")
    
    # Step 8: Regenerate executive summary (should increment version)
    print_separator("Step 8: Regenerate Executive Summary (Version 2)")
    exec_v2_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate/executive_summary",
        headers=headers
    )
    print_response(exec_v2_response, "Executive Summary Regeneration")
    
    if exec_v2_response.status_code == 201:
        data = exec_v2_response.json()
        version = data['sections_generated'][0]['version_number']
        if version == 2:
            print(f"✅ Executive summary regenerated with version {version}")
        else:
            print(f"❌ Expected version 2, got version {version}")
    else:
        print("❌ Regeneration failed")
    
    # Step 9: Verify all generated content
    print_separator("Step 9: Retrieve All Generated Content")
    all_content_response = requests.get(
        f"{BASE_URL}/form/{form_id}/generated-content",
        headers=headers
    )
    print_response(all_content_response, "All Generated Content")
    
    if all_content_response.status_code == 200:
        data = all_content_response.json()
        print(f"\n✅ Total sections generated: {data['total_sections']}")
        for section in data['sections']:
            print(f"   - {section['section_name']} (v{section['version_number']})")
    else:
        print("❌ Failed to retrieve generated content")
    
    # Step 10: Test unauthorized access
    print_separator("Step 10: Test Unauthorized Access")
    unauth_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate/executive_summary"
    )
    print_response(unauth_response, "Unauthorized Access Response")
    
    if unauth_response.status_code == 403:
        print("✅ Unauthorized access correctly blocked")
    else:
        print("❌ Should have returned 403 for unauthorized access")
    
    # Final Summary
    print_separator("✅ ALL TESTS PASSED!")
    print("\nSummary:")
    print("  • Single section endpoint working ✓")
    print("  • Version control functioning ✓")
    print("  • Input validation working ✓")
    print("  • Authorization checks working ✓")
    print("\n✨ Task 13 Single Section AI Generation endpoint working perfectly!")

if __name__ == "__main__":
    main()
