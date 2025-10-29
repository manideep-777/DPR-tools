# -*- coding: utf-8 -*-
"""
Manual Test Script for User Forms List Endpoint (Task 11)
Tests the GET /api/form/user/forms endpoint
"""
import requests
import json
from datetime import datetime
import sys
import io

# Fix Windows console encoding for UTF-8 characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response, title="API Response"):
    """Print formatted API response with full JSON content"""
    print(f"\n--- {title} ---")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

def main():
    print_section("TASK 11: User Forms List - Manual Test")
    
    # Step 1: Register a new user
    print_section("Step 1: Register Test User")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    register_data = {
        "email": f"formlist_{timestamp}@test.com",
        "password": "TestPass123!",
        "full_name": "Form List Tester",
        "phone": "9988776655"
    }
    
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        headers=HEADERS,
        json=register_data
    )
    print_response(register_response, "Registration Response")
    
    if register_response.status_code != 201:
        print("❌ Registration failed!")
        return
    
    # Step 2: Login to get token
    print_section("Step 2: Login User")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        headers=HEADERS,
        json=login_data
    )
    print_response(login_response, "Login Response")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()["access_token"]
    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    # Step 3: Check forms list (should be empty)
    print_section("Step 3: Get User Forms (Empty List)")
    forms_response_1 = requests.get(
        f"{BASE_URL}/form/user/forms",
        headers=auth_headers
    )
    print_response(forms_response_1, "Empty Forms List Response")
    
    if forms_response_1.status_code != 200:
        print("❌ Failed to get forms list!")
        return
    
    forms_data_1 = forms_response_1.json()
    if forms_data_1["total_forms"] != 0:
        print("❌ Expected empty forms list!")
        return
    
    print("✅ Empty forms list verified")
    
    # Step 4: Create first form
    print_section("Step 4: Create First Form (Tech Startup)")
    form1_data = {"business_name": "Tech Startup DPR"}
    form1_response = requests.post(
        f"{BASE_URL}/form/create",
        headers=auth_headers,
        json=form1_data
    )
    print_response(form1_response, "First Form Creation Response")
    
    if form1_response.status_code != 201:
        print("❌ Failed to create first form!")
        return
    
    form1_id = form1_response.json()["form_id"]
    print(f"✅ First form created with ID: {form1_id}")
    
    # Step 5: Create second form
    print_section("Step 5: Create Second Form (Retail Store)")
    form2_data = {"business_name": "Retail Store Expansion"}
    form2_response = requests.post(
        f"{BASE_URL}/form/create",
        headers=auth_headers,
        json=form2_data
    )
    print_response(form2_response, "Second Form Creation Response")
    
    if form2_response.status_code != 201:
        print("❌ Failed to create second form!")
        return
    
    form2_id = form2_response.json()["form_id"]
    print(f"✅ Second form created with ID: {form2_id}")
    
    # Step 6: Create third form
    print_section("Step 6: Create Third Form (Manufacturing Unit)")
    form3_data = {"business_name": "Manufacturing Unit Setup"}
    form3_response = requests.post(
        f"{BASE_URL}/form/create",
        headers=auth_headers,
        json=form3_data
    )
    print_response(form3_response, "Third Form Creation Response")
    
    if form3_response.status_code != 201:
        print("❌ Failed to create third form!")
        return
    
    form3_id = form3_response.json()["form_id"]
    print(f"✅ Third form created with ID: {form3_id}")
    
    # Step 7: Update first form to add some completion
    print_section("Step 7: Update First Form - Add Business Details")
    business_section_data = {
        "business_name": "Tech Startup DPR",
        "sector": "Software Development",
        "legal_structure": "Pvt Ltd",
        "location": "Bangalore",
        "address": "123 Tech Park, Bangalore, Karnataka"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/form/{form1_id}/section/business_details",
        headers=auth_headers,
        json=business_section_data
    )
    print_response(update_response, "Business Details Update Response")
    
    if update_response.status_code != 200:
        print("❌ Failed to update business details!")
        return
    
    print("✅ Business details added (12.5% completion)")
    
    # Step 8: Update second form status
    print_section("Step 8: Update Second Form Status to 'generating'")
    status_update_data = {
        "business_name": "Retail Store Expansion",
        "status": "generating"
    }
    
    status_response = requests.put(
        f"{BASE_URL}/form/{form2_id}",
        headers=auth_headers,
        json=status_update_data
    )
    print_response(status_response, "Status Update Response")
    
    if status_response.status_code != 200:
        print("❌ Failed to update form status!")
        return
    
    print("✅ Form status updated to 'generating'")
    
    # Step 9: Get updated forms list
    print_section("Step 9: Get User Forms (Should Show 3 Forms)")
    forms_response_2 = requests.get(
        f"{BASE_URL}/form/user/forms",
        headers=auth_headers
    )
    print_response(forms_response_2, "Updated Forms List Response")
    
    if forms_response_2.status_code != 200:
        print("❌ Failed to get forms list!")
        return
    
    forms_data_2 = forms_response_2.json()
    
    # Step 10: Verify results
    print_section("Step 10: Verification")
    
    print(f"Total Forms: {forms_data_2['total_forms']}")
    
    if forms_data_2["total_forms"] != 3:
        print(f"❌ Expected 3 forms, got {forms_data_2['total_forms']}")
        return
    
    print("✅ Correct number of forms (3)")
    
    # Check ordering (most recent first - form3 should be first)
    forms = forms_data_2["forms"]
    print(f"\nForms Ordering (by last_modified descending):")
    for i, form in enumerate(forms, 1):
        print(f"  {i}. ID: {form['id']}, Name: {form['business_name']}")
        print(f"     Status: {form['status']}, Completion: {form['completion_percentage']}%")
        print(f"     Last Modified: {form['last_modified']}")
    
    # Verify form 2 or 1 is first (last modified due to updates)
    if forms[0]["id"] not in [form1_id, form2_id]:
        print("❌ Ordering issue - most recently modified form not first!")
        return
    
    print("\n✅ Forms ordered correctly by last_modified")
    
    # Verify completion percentages
    print("\nCompletion Percentages:")
    for form in forms:
        if form["id"] == form1_id:
            if form["completion_percentage"] != 12:  # 1 section out of 8 = 12.5% (rounded to 12)
                print(f"❌ Form 1 completion incorrect: {form['completion_percentage']}%")
                return
            print(f"  ✅ Form 1: {form['completion_percentage']}% (correct)")
        else:
            if form["completion_percentage"] != 0:
                print(f"❌ Form {form['id']} should have 0% completion")
                return
            print(f"  ✅ Form {form['id']}: {form['completion_percentage']}% (correct)")
    
    # Verify statuses
    print("\nForm Statuses:")
    for form in forms:
        if form["id"] == form2_id:
            if form["status"] != "generating":
                print(f"❌ Form 2 status incorrect: {form['status']}")
                return
            print(f"  ✅ Form 2: {form['status']} (correct)")
        else:
            if form["status"] != "draft":
                print(f"❌ Form {form['id']} status incorrect: {form['status']}")
                return
            print(f"  ✅ Form {form['id']}: {form['status']} (correct)")
    
    # Step 11: Test unauthorized access
    print_section("Step 11: Test Unauthorized Access")
    unauth_response = requests.get(
        f"{BASE_URL}/form/user/forms",
        headers=HEADERS  # No token
    )
    print_response(unauth_response, "Unauthorized Access Response")
    
    if unauth_response.status_code != 403:
        print(f"❌ Should return 403 for unauthorized access! Got {unauth_response.status_code}")
        return
    
    print("✅ Unauthorized access correctly blocked (403 Forbidden)")
    
    # Final Summary
    print_section("✅ ALL TESTS PASSED!")
    print("Summary:")
    print(f"  • Empty list verified")
    print(f"  • Created 3 forms successfully")
    print(f"  • Updated form completion (12%)")
    print(f"  • Updated form status (generating)")
    print(f"  • Forms list shows all 3 forms")
    print(f"  • Ordering by last_modified works correctly")
    print(f"  • Completion percentages accurate")
    print(f"  • Form statuses accurate")
    print(f"  • Unauthorized access blocked")
    print("\n✨ Task 11 GET /api/form/user/forms endpoint working perfectly!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
