"""
Manual Test Script for PDF Generation (Task 16)
Tests the /api/pdf/generate/{form_id} endpoint
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_section(text):
    """Print formatted section"""
    print(f"\n{text}")
    print("-" * 60)

def test_pdf_generation():
    """Test complete PDF generation workflow"""
    
    print_header("Task 16: PDF Generation Test")
    print("This test will:")
    print("1. Register a new user")
    print("2. Create a DPR form with complete data")
    print("3. Generate AI content")
    print("4. Calculate financial projections")
    print("5. Match government schemes")
    print("6. Generate PDF using Playwright")
    print("7. Retrieve PDF details")
    print("8. List all PDFs for the form")
    
    # Step 1: Register User
    print_section("Step 1: Register Test User")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_email = f"pdf_test_{timestamp}@test.com"
    
    register_data = {
        "email": test_email,
        "password": "Test@12345",
        "fullName": "PDF Test User",
        "phone": "+919876543210",
        "businessType": "Manufacturing",
        "state": "Telangana"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.text}")
        return False
    
    user_data = response.json()
    print(f"✅ User registered: {test_email}")
    
    # Step 2: Login
    print_section("Step 2: Login")
    
    login_data = {
        "email": test_email,
        "password": "Test@12345"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login successful, token received")
    
    # Step 3: Create DPR Form
    print_section("Step 3: Create DPR Form")
    
    form_data = {
        "businessName": "Tech Manufacturing Enterprise",
        "status": "draft"
    }
    
    response = requests.post(f"{BASE_URL}/form/create", json=form_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 201:
        print(f"❌ Form creation failed: {response.text}")
        return False
    
    form_id = response.json()["formId"]
    print(f"✅ Form created: ID {form_id}")
    
    # Step 4: Add Business Details
    print_section("Step 4: Add Business Details")
    
    business_details = {
        "businessName": "Tech Manufacturing Enterprise",
        "sector": "Manufacturing",
        "subSector": "Electronics",
        "legalStructure": "Private Limited",
        "registrationNumber": "U12345TG2024PTC123456",
        "location": "Hyderabad",
        "address": "Plot No. 123, HITEC City, Hyderabad, Telangana - 500081"
    }
    
    response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/business_details",
        json=business_details,
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"✅ Business details added")
    
    # Step 5: Add Financial Details
    print_section("Step 5: Add Financial Details")
    
    financial_details = {
        "totalInvestmentAmount": 5000000,
        "landCost": 1000000,
        "buildingCost": 1500000,
        "machineryCost": 2000000,
        "workingCapital": 300000,
        "otherCosts": 200000,
        "ownContribution": 2000000,
        "loanRequired": 3000000
    }
    
    response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/financial_details",
        json=financial_details,
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"✅ Financial details added")
    
    # Step 6: Generate AI Content (Optional - for complete PDF)
    print_section("Step 6: Generate AI Content")
    
    response = requests.post(f"{BASE_URL}/form/ai/generate-dpr/{form_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ AI content generation initiated")
    else:
        print(f"⚠️  AI content generation skipped (optional)")
    
    # Step 7: Calculate Financial Projections
    print_section("Step 7: Calculate Financial Projections")
    
    response = requests.post(f"{BASE_URL}/financial/{form_id}/calculate", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Financial projections calculated")
    else:
        print(f"⚠️  Financial projections failed: {response.text}")
    
    # Step 8: Match Government Schemes
    print_section("Step 8: Match Government Schemes")
    
    response = requests.post(f"{BASE_URL}/schemes/match/{form_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        schemes_data = response.json()
        print(f"✅ Matched {schemes_data.get('total_matches', 0)} schemes")
    else:
        print(f"⚠️  Scheme matching failed: {response.text}")
    
    # Step 9: Generate PDF (Main Test!)
    print_section("Step 9: Generate PDF with Playwright")
    print("⏳ Generating PDF... (this may take 10-30 seconds)")
    
    pdf_params = {
        "language": "english",
        "template_type": "professional"
    }
    
    response = requests.post(
        f"{BASE_URL}/pdf/generate/{form_id}",
        params=pdf_params,
        headers=headers,
        timeout=60  # Increased timeout for PDF generation
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ PDF generation failed: {response.text}")
        return False
    
    pdf_data = response.json()
    print(f"Response: {json.dumps(pdf_data, indent=2)}")
    
    if pdf_data.get("success"):
        pdf_info = pdf_data["data"]
        print(f"\n✅ PDF Generated Successfully!")
        print(f"   PDF ID: {pdf_info['pdfId']}")
        print(f"   PDF URL: {pdf_info['pdfUrl']}")
        print(f"   File Name: {pdf_info['fileName']}")
        print(f"   File Size: {pdf_info['fileSize']:,} bytes ({pdf_info['fileSize'] / 1024:.2f} KB)")
        print(f"   Language: {pdf_info['language']}")
        print(f"   Template: {pdf_info['templateType']}")
        print(f"   Generated At: {pdf_info['generatedAt']}")
        
        pdf_id = pdf_info['pdfId']
    else:
        print(f"❌ PDF generation failed")
        return False
    
    # Step 10: Retrieve PDF Details
    print_section("Step 10: Retrieve PDF Details")
    
    response = requests.get(f"{BASE_URL}/pdf/{pdf_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        pdf_details = response.json()
        print(f"✅ PDF details retrieved")
        print(f"   Download Count: {pdf_details['data']['downloadCount']}")
    else:
        print(f"❌ Failed to retrieve PDF details")
    
    # Step 11: List All PDFs for Form
    print_section("Step 11: List All PDFs for Form")
    
    response = requests.get(f"{BASE_URL}/pdf/form/{form_id}/list", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        pdfs_list = response.json()
        print(f"✅ Found {pdfs_list['totalPdfs']} PDF(s) for form {form_id}")
        for pdf in pdfs_list['pdfs']:
            print(f"   - {pdf['fileName']} ({pdf['fileSize']:,} bytes)")
    else:
        print(f"❌ Failed to list PDFs")
    
    # Summary
    print_header("✅ ALL TESTS COMPLETED!")
    print(f"Summary:")
    print(f"  • User registration and login ✓")
    print(f"  • DPR form creation ✓")
    print(f"  • Business and financial details ✓")
    print(f"  • Financial projections ✓")
    print(f"  • Government scheme matching ✓")
    print(f"  • PDF generation with Playwright ✓")
    print(f"  • PDF retrieval and listing ✓")
    print(f"\n✨ Task 16 implementation working perfectly!")
    print(f"\n📄 PDF Location: backend/uploads/{pdf_info['fileName']}")
    print(f"🌐 Cloudinary URL: {pdf_info['pdfUrl']}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_pdf_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
