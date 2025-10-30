# AI Scheme Matching - Form Switching Bug Fix

## Issue Description
When switching between different DPR forms in the AI-suggested schemes page, the completion status was incorrectly showing all sections as 100% complete, even for forms that were incomplete.

## Root Cause
The original implementation was checking form data from the `userForms` array, which only contains basic form metadata (id, business_name, completion_percentage, etc.) but **does not include the detailed section data** (entrepreneur_details, business_details, product_details, etc.).

### Original Flawed Code:
```typescript
useEffect(() => {
  if (selectedFormId) {
    const form = userForms.find((f) => f.id?.toString() === selectedFormId);
    if (form) {
      setSelectedForm(form);
      checkFormCompletion(form); // ❌ Checking incomplete data!
    }
  }
}, [selectedFormId, userForms]);
```

The `userForms` array from `getUserForms()` API returns:
```json
{
  "total_forms": 3,
  "forms": [
    {
      "id": 1,
      "business_name": "My Business",
      "completion_percentage": 25,
      "status": "draft"
      // ❌ NO section details included!
    }
  ]
}
```

## Solution
Fetch the **complete form data** (including all 8 section details) when a form is selected using the `getFormById()` API.

### Fixed Code:
```typescript
// Added new loading state
const [loadingFormDetails, setLoadingFormDetails] = useState(false);

// New effect to fetch complete form data
useEffect(() => {
  if (selectedFormId) {
    fetchFormDetails(selectedFormId);
  } else {
    setSelectedForm(null);
    setCompletedSections([]);
    setAllSectionsComplete(false);
    setMatchedSchemes([]); // Clear matched schemes when form changes
  }
}, [selectedFormId]);

// New function to fetch complete form data
const fetchFormDetails = async (formId: string) => {
  try {
    setLoadingFormDetails(true);
    setMatchedSchemes([]); // Clear previous matches when switching forms
    const formData = await getFormById(parseInt(formId)); // ✅ Fetches ALL sections
    setSelectedForm(formData);
    checkFormCompletion(formData);
  } catch (error) {
    console.error("Error fetching form details:", error);
    toast({
      title: "Error",
      description: "Failed to load form details",
      variant: "destructive",
    });
    setSelectedForm(null);
    setCompletedSections([]);
    setAllSectionsComplete(false);
  } finally {
    setLoadingFormDetails(false);
  }
};
```

## What `getFormById()` Returns
```json
{
  "id": 1,
  "business_name": "My Business",
  "completion_percentage": 25,
  "status": "draft",
  "entrepreneur_details": { /* data */ },  // ✅ Included
  "business_details": { /* data */ },      // ✅ Included
  "product_details": null,                 // ✅ Shows missing
  "financial_details": { /* data */ },     // ✅ Included
  "revenue_assumptions": null,             // ✅ Shows missing
  "cost_details": null,                    // ✅ Shows missing
  "staffing_details": null,                // ✅ Shows missing
  "timeline_details": null                 // ✅ Shows missing
}
```

## Changes Made

### 1. Added Import
```typescript
import { getUserForms, DprFormData, getFormById } from "@/lib/api/form";
```

### 2. Added Loading State
```typescript
const [loadingFormDetails, setLoadingFormDetails] = useState(false);
```

### 3. Replaced useEffect
- **Before**: Used form data from `userForms` array (incomplete)
- **After**: Fetches complete form data via `getFormById()` API

### 4. Added Loading UI
```typescript
{loadingFormDetails ? (
  <div className="text-center py-12">
    <Loader2 className="h-8 w-8 mx-auto mb-4 text-muted-foreground animate-spin" />
    <p className="text-sm text-muted-foreground">Loading form details...</p>
  </div>
) : selectedForm ? (
  // ... completion status UI
)}
```

### 5. Clear Matched Schemes on Form Switch
When switching forms, previously matched schemes are cleared to avoid confusion.

## Verification

### Test Scenario 1: Incomplete Form
1. Select a form with only 2/8 sections completed
2. **Expected**: Progress bar shows "2/8 sections"
3. **Expected**: Alert shows "Incomplete Form" message
4. **Expected**: "Get AI Recommendations" button is disabled

### Test Scenario 2: Complete Form
1. Select a form with all 8/8 sections completed
2. **Expected**: Progress bar shows "8/8 sections" (100%)
3. **Expected**: Green alert shows "All sections complete!"
4. **Expected**: "Get AI Recommendations" button is enabled

### Test Scenario 3: Switching Forms
1. Select Form A (2/8 complete)
2. Switch to Form B (8/8 complete)
3. **Expected**: Status updates correctly to show Form B's completion (100%)
4. **Expected**: Previous matched schemes are cleared
5. Switch back to Form A
6. **Expected**: Status correctly shows 2/8 sections again

## API Endpoints Used

### `/api/form/user/forms` (used for dropdown list)
- Returns: Basic form metadata only
- Use: Populating the form selection dropdown

### `/api/form/{form_id}/complete` (used for section checking)
- Returns: Complete form data with all 8 sections
- Use: Checking actual section completion status

## Benefits of This Fix

1. ✅ **Accurate completion tracking**: Shows real section status
2. ✅ **Prevents false positives**: Won't show incomplete forms as complete
3. ✅ **Better UX**: Clear loading state when switching forms
4. ✅ **Data consistency**: Always uses fresh data from backend
5. ✅ **Prevents errors**: Clears matched schemes when switching forms

## Files Modified
- `frontend/src/app/schemes/ai-match/page.tsx`

## Testing Checklist
- [x] Form completion status updates correctly when switching forms
- [x] Loading spinner shows while fetching form details
- [x] Matched schemes clear when switching forms
- [x] Incomplete forms cannot trigger AI matching
- [x] Complete forms enable AI matching button
- [x] Progress bar reflects actual section completion
- [x] All 8 sections checked individually
