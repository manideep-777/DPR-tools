# Form Data Display Fix - Preview Page

## Issue
The preview page was not showing all 8 form sections correctly. Sections like Cost Details, Revenue Assumptions were not visible because the frontend was using incorrect field names that didn't match the backend API response.

## Root Cause
**Field Name Mismatch**: The frontend code was using generic field names that didn't exist in the actual API response. The backend returns specific snake_case field names based on the Pydantic models.

### Backend API Field Names (Correct)

#### Financial Details
```typescript
{
  total_investment_amount: Decimal,
  land_cost: Decimal,
  building_cost: Decimal,
  machinery_cost: Decimal,
  working_capital: Decimal,
  other_costs: Decimal,
  own_contribution: Decimal,
  loan_required: Decimal
}
```

#### Revenue Assumptions
```typescript
{
  product_price: Decimal,
  monthly_sales_quantity_year1: int,
  monthly_sales_quantity_year2: int,
  monthly_sales_quantity_year3: int,
  growth_rate_percentage: Decimal
}
```

#### Cost Details
```typescript
{
  raw_material_cost_monthly: Decimal,
  labor_cost_monthly: Decimal,
  utilities_cost_monthly: Decimal,
  rent_monthly: Decimal,
  marketing_cost_monthly: Decimal,
  other_fixed_costs_monthly: Decimal
}
```

#### Staffing Details
```typescript
{
  total_employees: int,
  management_count: int,
  technical_staff_count: int,
  support_staff_count: int,
  average_salary: Decimal
}
```

#### Timeline Details
```typescript
{
  land_acquisition_months: int,
  construction_months: int,
  machinery_installation_months: int,
  trial_production_months: int,
  commercial_production_start_month: int
}
```

## Changes Made

### 1. Financial Details Section
**Before**: Used non-existent fields like `total_investment`, `loan_amount`, `equity_contribution`
**After**: Uses correct fields: `total_investment_amount`, `loan_required`, `own_contribution`

### 2. Revenue Assumptions Section
**Before**: Used fields like `unit_selling_price`, `units_per_month`, `monthly_revenue`
**After**: Uses correct fields: `product_price`, `monthly_sales_quantity_year1/2/3`, `growth_rate_percentage`

### 3. Cost Details Section
**Before**: Used fields without `_monthly` suffix: `raw_material_cost`, `labor_cost`
**After**: Uses correct fields with `_monthly` suffix: `raw_material_cost_monthly`, `labor_cost_monthly`
**Added**: Total monthly cost calculation by summing all cost components

### 4. Staffing Details Section
**Before**: Used non-existent fields like `skilled_workers`, `semi_skilled_workers`, `total_monthly_wages`
**After**: Uses correct fields: `management_count`, `technical_staff_count`, `support_staff_count`, `average_salary`

### 5. Timeline Details Section
**Before**: Used non-existent fields like `project_start_date`, `expected_completion_date`, `total_implementation_time`
**After**: Uses correct fields: `land_acquisition_months`, `construction_months`, `machinery_installation_months`, `trial_production_months`, `commercial_production_start_month`

## Additional Improvements

1. **Number Conversion**: Added `Number()` wrapper for Decimal fields to ensure proper formatting
2. **Total Cost Calculation**: Added automatic calculation of total monthly costs in Cost Details section
3. **Better Labels**: Changed "Cost Details" to "Cost Details (Monthly)" for clarity
4. **Removed Conditional Rendering**: Since the sections exist when returned by API, removed excessive conditional checks

## Testing

To verify the fix:
1. Navigate to `/preview/{formId}` 
2. Click on "Form Data" tab
3. All 8 sections should now display:
   - ✅ Entrepreneur Details
   - ✅ Business Details
   - ✅ Product/Service Details
   - ✅ Financial Details (8 fields)
   - ✅ Revenue Assumptions (5 fields)
   - ✅ Cost Details (6 fields + total)
   - ✅ Staffing Details (5 fields)
   - ✅ Timeline Details (5 fields)

## Files Modified
- `frontend/src/app/preview/[id]/page.tsx` - Updated all form section field names to match backend API

## API Reference
Backend model definitions: `backend/models/form_models.py`
- Lines 300-357: Response models for all sections
- All field names follow snake_case convention
- Monetary values are returned as Decimal type
