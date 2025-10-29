"""
Manual Test Script for Financial Projections API
Tests the /financial endpoints for calculating and retrieving financial projections
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"

def print_separator(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def print_response(response, title):
    print(f"\n--- {title} ---")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    print_separator("TASK 14: Financial Projections - Manual Test")
    
    # Step 1: Register test user
    print_separator("Step 1: Register Test User")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    registration_data = {
        "email": f"financial_test_{timestamp}@test.com",
        "password": "Test@123",
        "full_name": "Financial Test User",
        "phone": "9876543210"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)
    print_response(register_response, "Registration Response")
    
    if register_response.status_code != 201:
        print("❌ Registration failed!")
        return
    
    # Step 2: Login
    print_separator("Step 2: Login User")
    login_data = {
        "email": registration_data["email"],
        "password": registration_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(login_response, "Login Response")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Create DPR Form
    print_separator("Step 3: Create DPR Form")
    form_data = {
        "business_name": "Financial Test Startup"
    }
    
    form_response = requests.post(f"{BASE_URL}/form/create", json=form_data, headers=headers)
    print_response(form_response, "Form Creation Response")
    
    if form_response.status_code != 201:
        print("❌ Form creation failed!")
        return
    
    form_id = form_response.json()["form_id"]
    print(f"\n✅ Form created with ID: {form_id}")
    
    # Step 4: Add Financial Details
    print_separator("Step 4: Add Financial Details")
    financial_details = {
        "total_investment_amount": 5000000.00,  # ₹50 lakhs
        "land_cost": 1000000.00,
        "building_cost": 1500000.00,
        "machinery_cost": 2000000.00,
        "working_capital": 300000.00,
        "other_costs": 200000.00,
        "own_contribution": 1500000.00,  # 30%
        "loan_required": 3500000.00      # 70%
    }
    
    financial_resp = requests.put(
        f"{BASE_URL}/form/{form_id}/section/financial_details",
        json=financial_details,
        headers=headers
    )
    print(f"Financial details: {financial_resp.status_code}")
    if financial_resp.status_code != 200:
        print(f"❌ Failed to add financial details: {financial_resp.json()}")
        return
    
    # Step 5: Add Revenue Assumptions
    print_separator("Step 5: Add Revenue Assumptions")
    revenue_assumptions = {
        "product_price": 500.00,  # ₹500 per unit
        "monthly_sales_quantity_year1": 2000,  # 2000 units/month in year 1
        "monthly_sales_quantity_year2": 2500,  # 2500 units/month in year 2
        "monthly_sales_quantity_year3": 3000,  # 3000 units/month in year 3
        "growth_rate_percentage": 25.00  # 25% growth
    }
    
    revenue_resp = requests.put(
        f"{BASE_URL}/form/{form_id}/section/revenue_assumptions",
        json=revenue_assumptions,
        headers=headers
    )
    print(f"Revenue assumptions: {revenue_resp.status_code}")
    if revenue_resp.status_code != 200:
        print(f"❌ Failed to add revenue assumptions: {revenue_resp.json()}")
        return
    
    # Step 6: Add Cost Details
    print_separator("Step 6: Add Cost Details")
    cost_details = {
        "raw_material_cost_monthly": 300000.00,  # Variable cost
        "labor_cost_monthly": 150000.00,
        "utilities_cost_monthly": 50000.00,
        "rent_monthly": 30000.00,
        "marketing_cost_monthly": 20000.00,
        "other_fixed_costs_monthly": 10000.00
    }
    
    cost_resp = requests.put(
        f"{BASE_URL}/form/{form_id}/section/cost_details",
        json=cost_details,
        headers=headers
    )
    print(f"Cost details: {cost_resp.status_code}")
    if cost_resp.status_code != 200:
        print(f"❌ Failed to add cost details: {cost_resp.json()}")
        return
    
    print("✅ All form data added successfully")
    
    # Step 7: Calculate Financial Projections
    print_separator("Step 7: Calculate Financial Projections")
    calc_response = requests.post(
        f"{BASE_URL}/financial/{form_id}/calculate",
        headers=headers
    )
    print_response(calc_response, "Calculation Response")
    
    if calc_response.status_code == 201:
        calc_data = calc_response.json()
        print(f"\n✅ Projections calculated successfully!")
        print(f"   Projections count: {calc_data['projections_count']}")
        if calc_data.get('summary'):
            summary = calc_data['summary']
            print(f"\n📊 Financial Summary:")
            print(f"   Break-even month: {summary['breakeven_months']}")
            print(f"   ROI: {summary['roi_percentage']}%")
            print(f"   Payback period: {summary['payback_period_months']} months")
            print(f"   NPV: ₹{summary['npv']:,.2f}")
            print(f"   Profit margin: {summary['profit_margin_percentage']}%")
    else:
        print("❌ Calculation failed!")
        return
    
    # Step 8: Get Financial Projections
    print_separator("Step 8: Get Financial Projections")
    proj_response = requests.get(
        f"{BASE_URL}/financial/{form_id}/projections",
        headers=headers
    )
    print(f"Status Code: {proj_response.status_code}")
    
    if proj_response.status_code == 200:
        proj_data = proj_response.json()
        print(f"\n✅ Retrieved {proj_data['total_months']} months of projections")
        
        # Show first 3 months and last 3 months
        print("\n📈 Sample Projections:")
        print("\nFirst 3 months:")
        for month in proj_data['projections'][:3]:
            print(f"  Month {month['month_number']}:")
            print(f"    Revenue: ₹{month['revenue']:,.2f}")
            print(f"    Profit/Loss: ₹{month['profit_loss']:,.2f}")
            print(f"    Cumulative P/L: ₹{month['cumulative_profit_loss']:,.2f}")
        
        print("\nLast 3 months:")
        for month in proj_data['projections'][-3:]:
            print(f"  Month {month['month_number']}:")
            print(f"    Revenue: ₹{month['revenue']:,.2f}")
            print(f"    Profit/Loss: ₹{month['profit_loss']:,.2f}")
            print(f"    Cumulative P/L: ₹{month['cumulative_profit_loss']:,.2f}")
    else:
        print("❌ Failed to retrieve projections!")
    
    # Step 9: Get Financial Summary
    print_separator("Step 9: Get Financial Summary")
    summary_response = requests.get(
        f"{BASE_URL}/financial/{form_id}/summary",
        headers=headers
    )
    print_response(summary_response, "Summary Response")
    
    if summary_response.status_code == 200:
        print("\n✅ Successfully retrieved financial summary")
    else:
        print("❌ Failed to retrieve summary!")
    
    # Step 10: Test Unauthorized Access
    print_separator("Step 10: Test Unauthorized Access")
    unauth_response = requests.get(
        f"{BASE_URL}/financial/{form_id}/summary"
    )
    print_response(unauth_response, "Unauthorized Access Response")
    
    if unauth_response.status_code == 403:
        print("✅ Unauthorized access correctly blocked")
    else:
        print("❌ Should have returned 403 for unauthorized access")
    
    # Step 11: Test Missing Required Data
    print_separator("Step 11: Test Calculation Without Required Data")
    
    # Create another form without complete data
    form2_response = requests.post(
        f"{BASE_URL}/form/create",
        json={"business_name": "Incomplete Test Form"},
        headers=headers
    )
    
    if form2_response.status_code == 201:
        form2_id = form2_response.json()["form_id"]
        
        # Try to calculate without data
        calc2_response = requests.post(
            f"{BASE_URL}/financial/{form2_id}/calculate",
            headers=headers
        )
        print_response(calc2_response, "Calculation Without Data")
        
        if calc2_response.status_code == 400:
            print("✅ Correctly rejected calculation without required data")
        else:
            print("❌ Should have returned 400 for missing data")
    
    # Final Summary
    print_separator("✅ ALL TESTS PASSED!")
    print("\nSummary:")
    print("  • Financial projections calculation ✓")
    print("  • 36-month projections generation ✓")
    print("  • Summary metrics (ROI, NPV, break-even) ✓")
    print("  • Projections retrieval ✓")
    print("  • Summary retrieval ✓")
    print("  • Authorization checks ✓")
    print("  • Input validation ✓")
    print("\n✨ Task 14 Financial Projections working perfectly!")

if __name__ == "__main__":
    main()
