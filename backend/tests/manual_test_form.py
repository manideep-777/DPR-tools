"""
Manual test script for DPR form endpoints
Run this after starting the backend server: python main.py
Then in another terminal: python tests/manual_test_form.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Register and login to get token
print("=" * 60)
print("1. Creating test user and logging in...")
register_data = {
    "email": "form_manual_test@test.com",
    "password": "Test@123456",
    "full_name": "Form Manual Test",
    "phone": "9876543210",
    "business_type": "manufacturing",
    "state": "Telangana"
}

# Try to register (may already exist)
register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
if register_response.status_code == 201:
    print("✅ User registered successfully")
else:
    print("⚠️  User already exists, logging in...")

# Login
login_data = {
    "email": "form_manual_test@test.com",
    "password": "Test@123456"
}

login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login Status: {login_response.status_code}")
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create a DPR form
print("\n" + "=" * 60)
print("2. Creating a new DPR form...")
form_data = {
    "business_name": "ABC Manufacturing Unit"
}

create_response = requests.post(f"{BASE_URL}/form/create", json=form_data, headers=headers)
print(f"Status: {create_response.status_code}")
print(f"Response: {json.dumps(create_response.json(), indent=2)}")

form_id = create_response.json()["form_id"]

# Retrieve the form
print("\n" + "=" * 60)
print(f"3. Retrieving form {form_id}...")
get_response = requests.get(f"{BASE_URL}/form/{form_id}", headers=headers)
print(f"Status: {get_response.status_code}")
print(f"Response: {json.dumps(get_response.json(), indent=2)}")

# Create another form
print("\n" + "=" * 60)
print("4. Creating a second DPR form...")
form_data2 = {
    "business_name": "XYZ Services Pvt Ltd"
}

create_response2 = requests.post(f"{BASE_URL}/form/create", json=form_data2, headers=headers)
print(f"Status: {create_response2.status_code}")
print(f"Response: {json.dumps(create_response2.json(), indent=2)}")

# Test validation: empty business name
print("\n" + "=" * 60)
print("5. Testing validation: empty business name (should fail)...")
invalid_data = {
    "business_name": ""
}

invalid_response = requests.post(f"{BASE_URL}/form/create", json=invalid_data, headers=headers)
print(f"Status: {invalid_response.status_code}")
if invalid_response.status_code == 422:
    print("✅ Validation worked correctly!")
else:
    print(f"Response: {json.dumps(invalid_response.json(), indent=2)}")

# Test validation: missing business name
print("\n" + "=" * 60)
print("6. Testing validation: missing business name (should fail)...")
invalid_data2 = {}

invalid_response2 = requests.post(f"{BASE_URL}/form/create", json=invalid_data2, headers=headers)
print(f"Status: {invalid_response2.status_code}")
if invalid_response2.status_code == 422:
    print("✅ Validation worked correctly!")
else:
    print(f"Response: {json.dumps(invalid_response2.json(), indent=2)}")

# Test authorization: try to access form without token
print("\n" + "=" * 60)
print("7. Testing authorization: access without token (should fail)...")
unauth_response = requests.post(f"{BASE_URL}/form/create", json=form_data)
print(f"Status: {unauth_response.status_code}")
if unauth_response.status_code == 403:
    print("✅ Authorization check worked correctly!")

# Test GET without auth
print("\n" + "=" * 60)
print("8. Testing GET without auth (should fail)...")
unauth_get = requests.get(f"{BASE_URL}/form/{form_id}")
print(f"Status: {unauth_get.status_code}")
if unauth_get.status_code == 403:
    print("✅ Authorization check worked correctly!")

# Test GET non-existent form
print("\n" + "=" * 60)
print("9. Testing GET non-existent form (should return 404)...")
notfound_response = requests.get(f"{BASE_URL}/form/99999", headers=headers)
print(f"Status: {notfound_response.status_code}")
if notfound_response.status_code == 404:
    print("✅ Not found handling worked correctly!")

print("\n" + "=" * 60)
print("✅ All manual tests completed!")
print("=" * 60)
