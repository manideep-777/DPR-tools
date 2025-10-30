# Google Translate Control Guide

## Problem
When Google Translate is enabled, it translates the **entire page** by default, including navigation, buttons, and UI elements, which should remain in their original language (English).

## Solution
Use the `notranslate` class to prevent specific elements from being translated.

---

## How It Works

Google Translate respects the `notranslate` class. Any element with this class will **not** be translated when users switch languages.

```html
<!-- This will NOT be translated -->
<div className="notranslate">Dashboard</div>

<!-- This WILL be translated -->
<div>వినియోగదారు కంటెంట్</div>
```

---

## Implementation

### 1. **Navigation Bar** ✅
Already implemented in `frontend/src/components/layout/Navbar.tsx`:

```tsx
<nav className="border-b bg-white notranslate">
  {/* All navigation elements stay in English */}
</nav>
```

### 2. **Google Translate Dropdown** ✅
Already implemented in `frontend/src/app/layout.tsx`:

```tsx
<div
  id="google_translate_element"
  className="notranslate fixed bottom-4 right-4 z-9999"
>
  {/* Dropdown stays in English */}
</div>
```

### 3. **Form Labels and Buttons**
For forms, add `notranslate` to labels and buttons:

```tsx
// ❌ BAD - Labels will be translated
<label htmlFor="business_name">Business Name</label>

// ✅ GOOD - Labels stay in English
<label htmlFor="business_name" className="notranslate">
  Business Name
</label>

// ✅ GOOD - Button text stays in English
<button className="notranslate">Submit</button>
```

### 4. **UI Text vs User Content**
Separate UI elements from user-generated content:

```tsx
// UI elements - should NOT translate
<div className="notranslate">
  <h2>Business Details</h2>
  <button>Save</button>
</div>

// User content - SHOULD translate
<div>
  <p>{userBusinessDescription}</p>
  <p>{aiGeneratedContent}</p>
</div>
```

---

## What Should Be Translated?

### ✅ **SHOULD Translate:**
- AI-generated DPR content (Executive Summary, Market Analysis, etc.)
- User-entered business descriptions
- Scheme descriptions and details
- Financial analysis narratives
- PDF content (when viewing DPR)

### ❌ **Should NOT Translate:**
- Navigation menu items (Dashboard, Schemes, Login, etc.)
- Button labels (Submit, Save, Cancel, etc.)
- Form field labels (Business Name, Email, etc.)
- Table headers (Name, Status, Actions, etc.)
- Toast notifications
- Error messages
- Google Translate dropdown itself

---

## Implementation Checklist

### Pages to Update

1. **Dashboard Page** (`frontend/src/app/dashboard/page.tsx`)
   - [ ] Add `notranslate` to table headers
   - [ ] Add `notranslate` to button labels
   - [ ] Keep card content translatable

2. **Forms** (`frontend/src/app/form/[id]/page.tsx`)
   - [ ] Add `notranslate` to all form labels
   - [ ] Add `notranslate` to tab names
   - [ ] Add `notranslate` to button texts
   - [ ] Keep user input display translatable

3. **Schemes Page** (`frontend/src/app/schemes/`)
   - [ ] Add `notranslate` to filter labels
   - [ ] Keep scheme descriptions translatable
   - [ ] Add `notranslate` to action buttons

4. **Preview Page** (`frontend/src/app/preview/[id]/page.tsx`)
   - [ ] Add `notranslate` to navigation tabs
   - [ ] Keep DPR content translatable
   - [ ] Add `notranslate` to action buttons

5. **PDF Page** (`frontend/src/app/pdf/[id]/page.tsx`)
   - Keep all content translatable (user wants to read DPR in Telugu)

---

## Quick Fix Examples

### Example 1: Dashboard Table Headers
```tsx
// Before
<th>Business Name</th>
<th>Status</th>

// After
<th className="notranslate">Business Name</th>
<th className="notranslate">Status</th>
```

### Example 2: Tab Navigation
```tsx
// Before
<TabsTrigger value="basic">Basic Info</TabsTrigger>

// After
<TabsTrigger value="basic" className="notranslate">
  Basic Info
</TabsTrigger>
```

### Example 3: Buttons
```tsx
// Before
<Button>Generate DPR</Button>

// After
<Button className="notranslate">Generate DPR</Button>
```

### Example 4: Section Titles
```tsx
// Before (if it's a UI label)
<h2>Financial Projections</h2>

// After
<h2 className="notranslate">Financial Projections</h2>

// But if it's AI-generated content, keep it translatable:
<h2>{aiGeneratedTitle}</h2> // No notranslate class
```

---

## Testing

### Visual Test
1. Refresh the page (Ctrl + Shift + R)
2. Click Google Translate dropdown (bottom-right)
3. Select "తెలుగు" (Telugu)
4. **Verify:**
   - ✅ Navigation stays in English (Dashboard, Login, etc.)
   - ✅ Buttons stay in English (Submit, Save, etc.)
   - ✅ Form labels stay in English
   - ✅ DPR content translates to Telugu
   - ✅ Scheme descriptions translate to Telugu

### DevTools Test
1. Open DevTools (F12)
2. Inspect elements
3. Elements with `notranslate` class should NOT have `<font>` wrapper
4. Translatable elements WILL have `<font>` wrapper

---

## CSS Reference

The `notranslate` class is built into Google Translate. No custom CSS needed!

However, our custom CSS (in `globals.css`) handles layout preservation:

```css
/* Ensure translated content doesn't break layout */
font {
  font-family: inherit !important;
  font-size: inherit !important;
  /* ... more inheritance rules */
}
```

---

## Best Practices

1. **Default Behavior**: By default, everything translates
2. **Be Selective**: Only add `notranslate` to UI elements, not user content
3. **Test Both Languages**: Always test in English and Telugu
4. **Consistent Labeling**: Keep UI labels in English for consistency
5. **User Content First**: Prioritize translating what users need to read

---

## Common Mistakes

### ❌ Mistake 1: Translating Everything
```tsx
// Don't wrap entire page in notranslate
<main className="notranslate">
  {children} {/* Nothing will translate! */}
</main>
```

### ❌ Mistake 2: Not Translating User Content
```tsx
// Don't add notranslate to AI content
<div className="notranslate">
  {aiGeneratedDPR} {/* User can't read this in Telugu! */}
</div>
```

### ✅ Correct Approach
```tsx
// UI stays English, content translates
<div>
  <h2 className="notranslate">Business Details</h2>
  <p>{userBusinessDescription}</p> {/* Translates */}
</div>
```

---

## Summary

| Element Type | Should Translate? | Add `notranslate`? |
|-------------|-------------------|-------------------|
| Navigation items | ❌ No | ✅ Yes |
| Button labels | ❌ No | ✅ Yes |
| Form labels | ❌ No | ✅ Yes |
| Table headers | ❌ No | ✅ Yes |
| AI-generated content | ✅ Yes | ❌ No |
| User descriptions | ✅ Yes | ❌ No |
| Scheme details | ✅ Yes | ❌ No |
| DPR sections | ✅ Yes | ❌ No |

---

## Next Steps

To fully implement selective translation:

1. **Audit all pages** - Go through each page and identify UI elements
2. **Add `notranslate`** - Add class to navigation, buttons, labels
3. **Test thoroughly** - Switch to Telugu and verify behavior
4. **Document updates** - Note which pages have been updated

---

## Current Status

✅ **Already Implemented:**
- Navbar has `notranslate` class
- Google Translate dropdown has `notranslate` class
- Layout preservation CSS in place

⏸️ **Pending Implementation:**
- Dashboard table headers
- Form labels and buttons
- Tab navigation labels
- Scheme page filters
- Preview page UI elements

---

## Support

If translation is still affecting UI elements:
1. Check that `notranslate` class is applied
2. Inspect element in DevTools (should NOT have `<font>` wrapper)
3. Clear browser cache and hard refresh (Ctrl + Shift + R)
4. Check browser console for errors

For questions or issues, refer to:
- `GOOGLE_TRANSLATE_INTEGRATION.md` - Initial setup
- `TRANSLATION_LAYOUT_FIX.md` - Layout preservation
- This document - Selective translation control
