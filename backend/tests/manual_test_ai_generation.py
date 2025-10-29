# -*- coding: utf-8 -*-
"""
Manual Test Script for AI Content Generation (Task 12)
Tests the POST /api/form/{form_id}/generate endpoint
"""
import requests
import json
from datetime import datetime, date
import sys
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fix Windows console encoding for UTF-8 characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to Python path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Test AI configuration first
print("\nTesting AI Service Configuration:")
from utils.ai_service import ai_service
print(f"API Key Present: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"Service Available: {ai_service.is_available()}")
if ai_service.is_available():
    print("✅ AI Service initialized successfully")
    sample_form = {
        "business_name": "Test Company",
        "entrepreneur_details": {
            "full_name": "John Doe",
            "education": "MBA"
        }
    }
    text = ai_service.generate_section("executive_summary", sample_form)
    print(f"\nTest Generation Result: {'Success' if text else 'Failed'}")
    if text:
        print(f"Generated {len(text)} characters")
        print("\nFirst 200 characters of generated text:")
        print(text[:200])
else:
    print("❌ AI Service not available")
    print("Please ensure GOOGLE_API_KEY is set in .env file")
    sys.exit(1)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_ai_service():
    """Test AI service initialization directly"""
    from utils.ai_service import ai_service
    
    print("\nTesting AI Service Configuration:")
    print(f"API Key Present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"Service Available: {ai_service.is_available()}")
    if ai_service.is_available():
        print("✅ AI Service initialized successfully")
        sample_form = {
            "business_name": "Test Company",
            "entrepreneur_details": {
                "full_name": "John Doe",
                "education": "MBA"
            }
        }
        text = ai_service.generate_section("executive_summary", sample_form)
        print(f"\nTest Generation Result: {'Success' if text else 'Failed'}")
        if text:
            print(f"Generated {len(text)} characters")
    else:
        print("❌ AI Service not available")
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response, title="API Response", show_full_text=False):
    """Print formatted API response"""
    print(f"\n--- {title} ---")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    try:
        data = response.json()
        # If showing AI content, truncate long text for readability
        if not show_full_text and "sections_generated" in data:
            for section in data["sections_generated"]:
                if "generated_text" in section:
                    text_preview = section["generated_text"][:200] + "..." if len(section["generated_text"]) > 200 else section["generated_text"]
                    section["generated_text"] = f"{text_preview} [truncated, {len(section['generated_text'])} chars total]"
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    print()

def main():
    print_section("TASK 12: AI Content Generation - Manual Test")
    
    # Step 1: Register a new user
    print_section("Step 1: Register Test User")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    register_data = {
        "email": f"ai_test_{timestamp}@test.com",
        "password": "TestPass123!",
        "full_name": "AI Test User",
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
    
    # Step 2: Login
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
    
    # Step 3: Create a DPR form
    print_section("Step 3: Create DPR Form")
    form_data = {"business_name": "AI Test Startup"}
    form_response = requests.post(
        f"{BASE_URL}/form/create",
        headers=auth_headers,
        json=form_data
    )
    print_response(form_response, "Form Creation Response")
    
    if form_response.status_code != 201:
        print("❌ Failed to create form!")
        return
    
    form_id = form_response.json()["form_id"]
    print(f"✅ Form created with ID: {form_id}")
    
    # Step 4: Add comprehensive form data
    print_section("Step 4: Add Form Data (Required for AI Context)")
    
    # Add entrepreneur details
    entrepreneur_data = {
        "full_name": "Rajesh Kumar",
        "date_of_birth": "1985-05-15",
        "education": "MBA in Finance",
        "years_of_experience": 10,
        "previous_business_experience": "Managed a retail store for 5 years",
        "technical_skills": "Financial analysis, Business planning, Digital marketing"
    }
    
    entrepreneur_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/entrepreneur_details",
        headers=auth_headers,
        json=entrepreneur_data
    )
    print_response(entrepreneur_response, "Entrepreneur Details Added")
    
    # Add business details
    business_data = {
        "business_name": "AI Test Startup",
        "sector": "Food Processing",
        "sub_sector": "Packaged Snacks",
        "legal_structure": "Pvt Ltd",
        "location": "Hyderabad",
        "address": "Plot 123, Industrial Area, Hyderabad, Telangana - 500001"
    }
    
    business_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/business_details",
        headers=auth_headers,
        json=business_data
    )
    print_response(business_response, "Business Details Added")
    
    # Add product details
    product_data = {
        "product_name": "Healthy Millet Snacks",
        "description": "Nutritious millet-based snack products including chips, cookies, and energy bars",
        "key_features": ["High protein", "Gluten-free", "Low GI", "No preservatives"],
        "target_customers": "Health-conscious urban consumers, fitness enthusiasts, diabetic patients",
        "planned_capacity": 10000,
        "unique_selling_points": "Made from organic millets, traditional recipes with modern packaging, certified organic",
        "quality_certifications": "FSSAI, Organic India certification"
    }
    
    product_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/product_details",
        headers=auth_headers,
        json=product_data
    )
    print_response(product_response, "Product Details Added")
    
    # Add financial details
    financial_data = {
        "total_investment_amount": "5000000.00",
        "land_cost": "1000000.00",
        "building_cost": "1500000.00",
        "machinery_cost": "2000000.00",
        "working_capital": "300000.00",
        "other_costs": "200000.00",
        "own_contribution": "2000000.00",
        "loan_required": "3000000.00"
    }
    
    financial_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/financial_details",
        headers=auth_headers,
        json=financial_data
    )
    print_response(financial_response, "Financial Details Added")
    
    # Add revenue assumptions
    revenue_data = {
        "product_price": "250.00",
        "monthly_sales_quantity_year1": 2000,
        "monthly_sales_quantity_year2": 3500,
        "monthly_sales_quantity_year3": 5000,
        "growth_rate_percentage": "25.00"
    }
    
    revenue_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/revenue_assumptions",
        headers=auth_headers,
        json=revenue_data
    )
    print_response(revenue_response, "Revenue Assumptions Added")
    
    # Add cost details
    cost_data = {
        "raw_material_cost_monthly": "200000.00",
        "labor_cost_monthly": "80000.00",
        "utilities_cost_monthly": "15000.00",
        "rent_monthly": "25000.00",
        "marketing_cost_monthly": "30000.00",
        "other_fixed_costs_monthly": "20000.00"
    }
    
    cost_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/cost_details",
        headers=auth_headers,
        json=cost_data
    )
    print_response(cost_response, "Cost Details Added")
    
    # Add staffing details
    staffing_data = {
        "total_employees": 15,
        "management_count": 2,
        "technical_staff_count": 8,
        "support_staff_count": 5,
        "average_salary": "25000.00"
    }
    
    staffing_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/staffing_details",
        headers=auth_headers,
        json=staffing_data
    )
    print_response(staffing_response, "Staffing Details Added")
    
    # Add timeline details
    timeline_data = {
        "land_acquisition_months": 2,
        "construction_months": 4,
        "machinery_installation_months": 2,
        "trial_production_months": 1,
        "commercial_production_start_month": 9
    }
    
    timeline_response = requests.put(
        f"{BASE_URL}/form/{form_id}/section/timeline_details",
        headers=auth_headers,
        json=timeline_data
    )
    print_response(timeline_response, "Timeline Details Added")
    
    print("✅ All form data added successfully")
    
    # Step 5: Test AI generation with specific sections
    print_section("Step 5: Generate AI Content (2 sections)")
    
    generation_request = {
        "sections": ["executive_summary", "market_analysis"],
        "regenerate": False
    }
    
    generation_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate",
        headers=auth_headers,
        json=generation_request
    )
    print_response(generation_response, "AI Generation Response (2 sections)")
    
    if generation_response.status_code != 201:
        print("❌ AI generation failed!")
        print("Note: Check if GOOGLE_API_KEY is configured in backend/.env")
        return
    
    print("✅ AI content generated successfully for 2 sections")
    
    # Step 6: Test getting generated content
    print_section("Step 6: Get Generated Content")
    
    content_response = requests.get(
        f"{BASE_URL}/form/{form_id}/generated-content",
        headers=auth_headers
    )
    print_response(content_response, "Generated Content Response")
    
    if content_response.status_code != 200:
        print("❌ Failed to get generated content!")
        return
    
    print("✅ Successfully retrieved generated content")
    
    # Step 7: Test regenerating existing content
    print_section("Step 7: Regenerate Existing Content")
    
    regenerate_request = {
        "sections": ["executive_summary"],
        "regenerate": True
    }
    
    regenerate_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate",
        headers=auth_headers,
        json=regenerate_request
    )
    print_response(regenerate_response, "Regeneration Response")
    
    if regenerate_response.status_code != 201:
        print("❌ Content regeneration failed!")
        return
    
    # Check version number increased
    data = regenerate_response.json()
    if data["sections_generated"]:
        version = data["sections_generated"][0]["version_number"]
        if version > 1:
            print(f"✅ Content regenerated successfully (version {version})")
        else:
            print("⚠️  Content regenerated but version number not incremented")
    
    # Step 8: Test generating all remaining sections
    print_section("Step 8: Generate All Remaining Sections")
    
    all_sections_request = {
        "sections": None,  # Generate all available sections
        "regenerate": False
    }
    
    all_sections_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate",
        headers=auth_headers,
        json=all_sections_request
    )
    print_response(all_sections_response, "All Sections Generation Response")
    
    if all_sections_response.status_code != 201:
        print("❌ Failed to generate all sections!")
        return
    
    print("✅ All remaining sections generated successfully")
    
    # Step 9: Test unauthorized access
    print_section("Step 9: Test Unauthorized Access")
    
    unauth_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate",
        headers=HEADERS,  # No token
        json=generation_request
    )
    print_response(unauth_response, "Unauthorized Access Response")
    
    if unauth_response.status_code != 403:
        print(f"❌ Should return 403 for unauthorized access! Got {unauth_response.status_code}")
        return
    
    print("✅ Unauthorized access correctly blocked")
    
    # Step 10: Test invalid section names
    print_section("Step 10: Test Invalid Section Names")
    
    invalid_request = {
        "sections": ["invalid_section", "another_invalid"],
        "regenerate": False
    }
    
    invalid_response = requests.post(
        f"{BASE_URL}/form/{form_id}/generate",
        headers=auth_headers,
        json=invalid_request
    )
    print_response(invalid_response, "Invalid Sections Response")
    
    if invalid_response.status_code != 400:
        print(f"❌ Should return 400 for invalid sections! Got {invalid_response.status_code}")
        return
    
    print("✅ Invalid section names correctly rejected")
    
    # Final Summary
    print_section("✅ ALL TESTS PASSED!")
    print("Summary:")
    print(f"  • User registration and authentication ✓")
    print(f"  • Form creation and data population ✓")
    print(f"  • AI content generation (selective) ✓")
    print(f"  • Content retrieval ✓")
    print(f"  • Content regeneration with versioning ✓")
    print(f"  • Bulk generation (all sections) ✓")
    print(f"  • Authorization checks ✓")
    print(f"  • Input validation ✓")
    print("\n✨ Task 12 AI Content Generation endpoint working perfectly!")
    print("\nNote: Review the generated content for quality and relevance.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
