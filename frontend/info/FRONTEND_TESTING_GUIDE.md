# 🧪 Frontend Testing Guide - DPR Form

## Prerequisites ✅

Based on your terminal output, you already have:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running (you mentioned starting it)
- ✅ Database connected and working

## Step-by-Step Testing Instructions

### Step 1: Access the Application

1. **Open your browser** and go to:
   ```
   http://localhost:3000
   ```

2. **First-time users**: You'll need to create an account
   - Click on "Register" or "Sign Up"
   - Fill in your details
   - Create your account

3. **Existing users**: Log in with your credentials

### Step 2: Navigate to Dashboard

After logging in, you should see the **Dashboard** which now has:
- ✅ Your profile information
- ✅ **"Create New DPR"** button (now enabled!)
- ✅ List of your existing DPR projects (if any)

### Step 3: Create a New DPR Form

1. Click the **"Create New DPR"** button
2. A new form will be created automatically
3. You'll be redirected to the form editing page at:
   ```
   http://localhost:3000/form/[form-id]
   ```

### Step 4: Fill Out the Form

You should see **8 TABS** at the top of the form:

#### Tab 1: Entrepreneur Details 👤
Fill in your personal information:
- Full Name (required)
- Date of Birth
- Education background
- Years of Experience
- Previous Business Experience (optional)
- Technical Skills (optional)

Click **"Save Section"** when done.

#### Tab 2: Business Details 🏢
Enter your business information:
- Business Name (required)
- Sector & Sub-sector
- Legal Structure (dropdown: Proprietorship, Partnership, LLP, Private Limited, Public Limited)
- Registration Number (optional)
- Location & Address

Click **"Save Section"** when done.

#### Tab 3: Product Details 📦
Describe your product/service:
- Product/Service Name
- Description
- Key Features
- Target Customers
- Current & Planned Capacity
- Unique Selling Points
- Quality Certifications (optional)

Click **"Save Section"** when done.

#### Tab 4: Financial Details 💰
**This is the most important tab for financial projections!**

Enter investment breakdown:
- Land Cost
- Building Cost
- Machinery Cost
- Working Capital
- Other Costs
- **Total Investment** (auto-calculated or manual entry)

Enter funding structure:
- Own Contribution
- Loan Required

**Note**: Watch the auto-calculator show the total!

Click **"Save Section"** when done.

#### Tab 5: Revenue Assumptions 📈
Enter your sales projections:
- **Product Price** (₹ per unit) - required
- Monthly Sales Year 1
- Monthly Sales Year 2
- Monthly Sales Year 3
- Growth Rate (%)

**Note**: Annual revenue is calculated automatically!

Click **"Save Section"** when done.

#### Tab 6: Cost Details 💸
Enter your monthly operational costs:

**Variable Costs:**
- Raw Material Cost
- Labor Cost
- Utilities

**Fixed Costs:**
- Rent
- Marketing
- Other Fixed Costs

**Note**: Monthly and annual totals are calculated automatically!

Click **"Save Section"** when done.

#### Tab 7: Staffing Details 👥
Enter your team structure:
- Management Staff count
- Technical Staff count
- Support Staff count
- **Total Employees** (auto-calculated or manual)
- Average Monthly Salary

**Note**: Total salary costs are calculated automatically!

Click **"Save Section"** when done.

#### Tab 8: Timeline Details 📅
Enter project timeline (in months):
- Land Acquisition (months)
- Construction (months)
- Machinery Installation (months)
- Trial Production (months)
- **Commercial Production Start Month** (required)

**Note**: Total preparation time is calculated automatically!

Click **"Save Section"** when done.

### Step 5: Auto-Save Feature

⏰ The form **auto-saves every 30 seconds** after you make changes!

You'll see:
- "Saving..." indicator when auto-save triggers
- Toast notification: "Section saved successfully"

### Step 6: Generate Financial Projections

After completing **at least** these sections:
- ✅ Financial Details (Tab 4)
- ✅ Revenue Assumptions (Tab 5)
- ✅ Cost Details (Tab 6)

You can now generate financial projections! (This will be integrated in the next update)

### Step 7: View Your Forms

1. Go back to Dashboard: `http://localhost:3000/dashboard`
2. You'll see your form listed with:
   - Form name
   - Status (draft/completed)
   - Completion percentage
   - Created date
   - **"Continue Editing"** button

## Testing Checklist ✅

Use this checklist to verify everything works:

- [ ] Can register a new account
- [ ] Can log in successfully
- [ ] Dashboard loads correctly
- [ ] Can click "Create New DPR" button
- [ ] Form page loads with 8 tabs
- [ ] Can navigate between tabs
- [ ] Can fill out Entrepreneur Details and save
- [ ] Can fill out Business Details and save
- [ ] Can fill out Product Details and save
- [ ] Can fill out Financial Details and save
- [ ] See auto-calculated total investment
- [ ] Can fill out Revenue Assumptions and save
- [ ] See auto-calculated annual revenue
- [ ] Can fill out Cost Details and save
- [ ] See auto-calculated monthly/annual costs
- [ ] Can fill out Staffing Details and save
- [ ] See auto-calculated salary totals
- [ ] Can fill out Timeline Details and save
- [ ] See auto-calculated timeline overview
- [ ] Auto-save triggers after 30 seconds
- [ ] Toast notifications appear on save
- [ ] Can go back to dashboard
- [ ] Created form appears in dashboard list
- [ ] Can click "Continue Editing" to return to form

## Sample Test Data 📝

Here's sample data you can use for quick testing:

### Entrepreneur Details
```
Full Name: John Doe
Date of Birth: 1990-01-15
Education: MBA in Entrepreneurship
Years of Experience: 5
Previous Business: E-commerce startup (2018-2020)
Technical Skills: Digital Marketing, Business Analytics
```

### Business Details
```
Business Name: EcoTech Solutions
Sector: Manufacturing
Sub-Sector: Renewable Energy
Legal Structure: Private Limited
Registration Number: CIN12345678
Location: Bangalore
Address: 123 Tech Park, Whitefield, Bangalore - 560066
```

### Product Details
```
Product Name: Solar Water Heater
Description: Energy-efficient solar water heating system for residential use
Key Features: High efficiency, 5-year warranty, eco-friendly
Target Customers: Middle-class homeowners in urban areas
Current Capacity: 100 units/month
Planned Capacity: 500 units/month
USP: 40% more efficient than competitors
Quality Certifications: ISO 9001, BIS certified
```

### Financial Details
```
Land Cost: ₹5,000,000
Building Cost: ₹3,000,000
Machinery Cost: ₹10,000,000
Working Capital: ₹2,000,000
Other Costs: ₹1,000,000
Total Investment: ₹21,000,000 (auto-calculated)

Own Contribution: ₹6,000,000
Loan Required: ₹15,000,000
```

### Revenue Assumptions
```
Product Price: ₹25,000 per unit
Monthly Sales Year 1: 100 units
Monthly Sales Year 2: 200 units
Monthly Sales Year 3: 300 units
Growth Rate: 15%
```

### Cost Details
```
Raw Material: ₹800,000
Labor: ₹300,000
Utilities: ₹50,000
Rent: ₹100,000
Marketing: ₹150,000
Other Fixed Costs: ₹100,000
```

### Staffing Details
```
Management: 3
Technical Staff: 10
Support Staff: 7
Total Employees: 20
Average Salary: ₹30,000
```

### Timeline Details
```
Land Acquisition: 2 months
Construction: 6 months
Machinery Installation: 3 months
Trial Production: 2 months
Commercial Production Start: 13 months
```

## Expected Results 🎯

### After Saving All Sections:

1. **Financial Details Tab**:
   - Total Investment: ₹21,000,000 (auto-calculated)

2. **Revenue Assumptions Tab**:
   - Year 1 Annual Revenue: ₹30,000,000
   - Year 2 Annual Revenue: ₹60,000,000
   - Year 3 Annual Revenue: ₹90,000,000

3. **Cost Details Tab**:
   - Monthly Total: ₹1,500,000
   - Annual Total: ₹18,000,000

4. **Staffing Details Tab**:
   - Monthly Salary: ₹600,000
   - Annual Salary: ₹7,200,000

5. **Timeline Details Tab**:
   - Total Preparation: 13 months

### Financial Projections (from backend test):
Based on your backend test output:
- ✅ Break-even month: 1
- ✅ ROI: 496.8%
- ✅ Payback period: 12 months
- ✅ NPV: ₹15,884,612.50
- ✅ Profit margin: 55.2%

## Troubleshooting 🔧

### Issue: Form doesn't load
**Solution**: Check browser console (F12) for errors. Ensure backend is running on port 8000.

### Issue: Can't save sections
**Solution**: 
1. Check if you're logged in
2. Verify backend is running
3. Check browser console for API errors
4. Ensure you've filled required fields (marked with *)

### Issue: Auto-save not working
**Solution**: Wait 30 seconds after making changes. You should see a toast notification.

### Issue: Can't see forms on dashboard
**Solution**: 
1. Refresh the dashboard page
2. Check if you're logged in with the correct account
3. Try creating a new form

### Issue: TypeScript errors in console
**Solution**: These are expected warnings from `z.coerce.number()`. They don't affect functionality.

## Direct URLs for Testing 🔗

- **Login**: http://localhost:3000/login
- **Register**: http://localhost:3000/register
- **Dashboard**: http://localhost:3000/dashboard
- **Form Editor**: http://localhost:3000/form/[id] (replace [id] with actual form ID)

## Backend API Endpoints Being Used 🔌

Your frontend is now calling these backend endpoints:

1. **POST** `/api/auth/register` - Create account
2. **POST** `/api/auth/login` - Login
3. **POST** `/api/form/create` - Create new form
4. **GET** `/api/form/{id}` - Fetch form data
5. **PUT** `/api/form/{id}/section/{section}` - Save section
6. **GET** `/api/form/user/forms` - Get all user forms
7. **POST** `/api/financial/{id}/calculate` - Calculate projections (coming soon in frontend)

## Next Steps After Testing ⏭️

Once basic form functionality is tested:

1. ✅ Integrate financial projection generation button
2. ✅ Display financial results in a dedicated page/modal
3. ✅ Add form completion status indicators
4. ✅ Add form validation error messages
5. ✅ Add ability to delete forms
6. ✅ Add PDF export functionality

---

**Happy Testing! 🚀**

If you encounter any issues, check:
1. Browser console (F12) for errors
2. Backend terminal for API errors
3. Network tab (F12) to see API calls
