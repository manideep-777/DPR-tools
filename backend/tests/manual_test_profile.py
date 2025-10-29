"""
Manual test script for user profile endpoints
Run this after starting the backend server: python main.py
Then in another terminal: python tests/manual_test_profile.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# First, create a test user (register)
print("=" * 60)
print("1. Creating test user...")
register_data = {
    "email": "profile_manual_test@test.com",
    "password": "Test@123456",
    "full_name": "Profile Manual Test",
    "phone": "9876543210",
    "business_type": "manufacturing",
    "state": "Telangana"
}

register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"Status: {register_response.status_code}")
print(f"Response: {json.dumps(register_response.json(), indent=2)}")

# Login to get token
print("\n" + "=" * 60)
print("2. Logging in...")
login_data = {
    "email": "profile_manual_test@test.com",
    "password": "Test@123456"
}

login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Status: {login_response.status_code}")
login_result = login_response.json()
print(f"Response: {json.dumps(login_result, indent=2)}")

token = login_result["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get profile (should create empty profile)
print("\n" + "=" * 60)
print("3. Getting profile (should create empty profile)...")
get_response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
print(f"Status: {get_response.status_code}")
print(f"Response: {json.dumps(get_response.json(), indent=2)}")

# Update profile with all fields
print("\n" + "=" * 60)
print("4. Updating profile with all fields...")
profile_update = {
    "address": "123 Test Street, Hyderabad, Telangana 500001",
    "aadhar_number": "123456789012",
    "pan_number": "ABCDE1234F",
    "years_in_business": 5,
    "bio": "This is a test bio for manual profile testing"
}

update_response = requests.put(f"{BASE_URL}/user/profile", json=profile_update, headers=headers)
print(f"Status: {update_response.status_code}")
print(f"Response: {json.dumps(update_response.json(), indent=2)}")

# Get profile again to verify update
print("\n" + "=" * 60)
print("5. Getting profile again to verify update...")
get_response2 = requests.get(f"{BASE_URL}/user/profile", headers=headers)
print(f"Status: {get_response2.status_code}")
print(f"Response: {json.dumps(get_response2.json(), indent=2)}")

# Update only bio
print("\n" + "=" * 60)
print("6. Updating only bio (partial update)...")
partial_update = {
    "bio": "Updated bio only - other fields should remain"
}

update_response2 = requests.put(f"{BASE_URL}/user/profile", json=partial_update, headers=headers)
print(f"Status: {update_response2.status_code}")
print(f"Response: {json.dumps(update_response2.json(), indent=2)}")

# Try invalid Aadhar
print("\n" + "=" * 60)
print("7. Testing invalid Aadhar (should return 422)...")
invalid_aadhar = {
    "aadhar_number": "12345"  # Not 12 digits
}

invalid_response = requests.put(f"{BASE_URL}/user/profile", json=invalid_aadhar, headers=headers)
print(f"Status: {invalid_response.status_code}")
if invalid_response.status_code == 422:
    print("✅ Validation worked correctly!")
else:
    print(f"Response: {json.dumps(invalid_response.json(), indent=2)}")

# Try invalid PAN
print("\n" + "=" * 60)
print("8. Testing invalid PAN (should return 422)...")
invalid_pan = {
    "pan_number": "INVALID123"  # Wrong format
}

invalid_response2 = requests.put(f"{BASE_URL}/user/profile", json=invalid_pan, headers=headers)
print(f"Status: {invalid_response2.status_code}")
if invalid_response2.status_code == 422:
    print("✅ Validation worked correctly!")
else:
    print(f"Response: {json.dumps(invalid_response2.json(), indent=2)}")

print("\n" + "=" * 60)
print("✅ All manual tests completed!")
print("=" * 60)
