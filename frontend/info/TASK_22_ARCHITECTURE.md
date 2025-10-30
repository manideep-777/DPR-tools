# DPR Preview Page - Architecture & Data Flow

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Preview Page Component                        │
│                  (/preview/[id]/page.tsx)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────┐
                              │             │
                    ┌─────────▼─────┐   ┌──▼─────────┐
                    │  State Mgmt   │   │  API Calls │
                    │  - sections   │   │  Parallel  │
                    │  - formData   │   │  Fetching  │
                    │  - financial  │   └────────────┘
                    │  - schemes    │
                    │  - activeTab  │
                    └───────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │ Tabs UI │         │ Dialogs │         │ Actions │
    │ 4 Tabs  │         │ Edit AI │         │ Navigate│
    └─────────┘         └─────────┘         └─────────┘
```

## Data Flow Diagram

```
User Visits /preview/[formId]
         │
         ▼
┌─────────────────────┐
│  useEffect Hook     │
│  Triggered on Load  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│         fetchAllData() - Promise.all            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────────┐        │
│  │ GET /form/   │  │ GET /form/       │        │
│  │ {id}/complete│  │ {id}/generated-  │        │
│  │              │  │ content          │        │
│  └──────┬───────┘  └──────┬───────────┘        │
│         │                  │                    │
│         ▼                  ▼                    │
│  ┌──────────────┐  ┌──────────────────┐        │
│  │ setFormData  │  │ setSections      │        │
│  └──────────────┘  └──────────────────┘        │
│                                                 │
│  ┌──────────────────┐  ┌──────────────────┐    │
│  │ GET /financial/  │  │ POST /schemes/   │    │
│  │ {id}/summary     │  │ match/{id}       │    │
│  │                  │  │                  │    │
│  └──────┬───────────┘  └──────┬───────────┘    │
│         │                      │                │
│         ▼                      ▼                │
│  ┌──────────────────┐  ┌──────────────────┐    │
│  │ setFinancialData │  │ setSchemes       │    │
│  └──────────────────┘  └──────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  setLoading(false)  │
│  Render Tabs        │
└─────────────────────┘
```

## Tab Structure

```
┌──────────────────────────────────────────────────────────┐
│                    Tabs Component                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │   AI   │  │  Form  │  │Finance │  │Schemes │        │
│  │Content │  │  Data  │  │        │  │        │        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
│      ▲                                                  │
│      │ (activeTab state controls which is shown)       │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tab 1: AI Content (sections.map)                       │
│  ┌──────────────────────────────────────────┐           │
│  │ Card 1: Executive Summary                │           │
│  │   - Markdown rendered content            │           │
│  │   - Edit button → Opens Dialog           │           │
│  │   - Confidence score, version            │           │
│  ├──────────────────────────────────────────┤           │
│  │ Card 2: Market Analysis                  │           │
│  │   ... (8 sections total)                 │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  Tab 2: Form Data (formData conditional render)         │
│  ┌──────────────────────────────────────────┐           │
│  │ Card: Entrepreneur Details               │           │
│  │   - Grid layout with labels/values       │           │
│  ├──────────────────────────────────────────┤           │
│  │ Card: Business Details                   │           │
│  ├──────────────────────────────────────────┤           │
│  │ Card: Product Details                    │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  Tab 3: Financials (financialData conditional)          │
│  ┌──────────────────────────────────────────┐           │
│  │ Card: Investment Summary                 │           │
│  │   - Total Investment, ROI, Break-even    │           │
│  ├──────────────────────────────────────────┤           │
│  │ Card: 5-Year Projections Table           │           │
│  │   - Year | Revenue | Costs | Profit      │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  Tab 4: Schemes (schemes.map)                           │
│  ┌──────────────────────────────────────────┐           │
│  │ Scheme Card 1 (Match: 95%)               │           │
│  │   - Color-coded border by score          │           │
│  │   - Reasons list                         │           │
│  │   - Key benefit                          │           │
│  ├──────────────────────────────────────────┤           │
│  │ Scheme Card 2 (Match: 87%)               │           │
│  │   ... (up to 10 schemes)                 │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## User Interaction Flow

```
User Action: Click "Edit" on AI Section
         │
         ▼
┌─────────────────────┐
│ setSelectedSection  │
│ setEditDialogOpen   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Dialog Opens       │
│  - Shows section    │
│  - Textarea for     │
│    custom prompt    │
└──────────┬──────────┘
           │
           ▼
User Enters Custom Prompt (Optional)
         │
         ▼
┌─────────────────────────────────┐
│ Click "Regenerate Section"      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ POST /api/form/{id}/generate/   │
│      {section_name}              │
│                                  │
│ Body: { custom_prompt: "..." }  │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Backend: AI Generation          │
│ - Reads form data                │
│ - Applies custom prompt          │
│ - Generates new content          │
│ - Saves to database              │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Response: New AI Content        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ fetchAllData()                  │
│ - Refresh all tabs              │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Dialog Closes                   │
│ Updated Content Displayed       │
│ Toast: Success Message          │
└─────────────────────────────────┘
```

## API Integration Summary

| Tab          | Endpoint                               | Method | Purpose                    |
|--------------|----------------------------------------|--------|----------------------------|
| AI Content   | `/api/form/{id}/generated-content`     | GET    | Fetch AI sections          |
| AI Content   | `/api/form/{id}/generate/{section}`    | POST   | Regenerate section         |
| Form Data    | `/api/form/{id}/complete`              | GET    | Fetch all form sections    |
| Financials   | `/api/financial/{id}/summary`          | GET    | Fetch projections & metrics|
| Schemes      | `/api/schemes/match/{id}`              | POST   | Fetch matched schemes      |

## Component Dependencies

```
preview/[id]/page.tsx
├── shadcn/ui components
│   ├── Card, CardHeader, CardTitle, CardDescription, CardContent
│   ├── Button
│   ├── Badge
│   ├── Tabs, TabsList, TabsTrigger, TabsContent
│   ├── Dialog, DialogContent, DialogHeader, DialogFooter
│   ├── Textarea
│   └── Label
├── Hooks
│   ├── useParams (Next.js)
│   ├── useRouter (Next.js)
│   ├── useToast (shadcn/ui)
│   ├── useState (React)
│   └── useEffect (React)
├── Libraries
│   ├── react-markdown
│   └── remark-gfm
└── Utils
    └── getValidToken (auth)
```

## State Machine

```
┌─────────────┐
│   LOADING   │ (initial state)
└──────┬──────┘
       │
       │ (fetchAllData completes)
       │
       ▼
┌─────────────┐
│   LOADED    │ (displaying data)
└──────┬──────┘
       │
       │ (user clicks Edit)
       │
       ▼
┌─────────────┐
│  EDITING    │ (dialog open)
└──────┬──────┘
       │
       │ (user clicks Regenerate)
       │
       ▼
┌─────────────┐
│REGENERATING │ (API call in progress)
└──────┬──────┘
       │
       │ (regeneration completes)
       │
       ▼
┌─────────────┐
│REFRESHING   │ (fetchAllData again)
└──────┬──────┘
       │
       │
       ▼
┌─────────────┐
│   LOADED    │ (back to normal)
└─────────────┘
```

## Error Handling Strategy

```
For each API call:
├── Try
│   ├── Check token validity
│   ├── Make API request
│   ├── Parse response
│   └── Update state
└── Catch
    ├── Log error to console
    ├── Show toast notification (for critical errors)
    └── Display empty state with CTA
        ├── "No AI Content" → "Generate Content" button
        ├── "No Form Data" → "Complete Form" button
        ├── "No Financials" → "Add Financial Details" button
        └── "No Schemes" → "Find Matching Schemes" button
```

## Performance Optimizations

1. **Parallel Data Fetching**
   - All 4 API calls run simultaneously using `Promise.all()`
   - Reduces total load time

2. **Conditional Rendering**
   - Only render tabs when data exists
   - Empty states prevent unnecessary rendering

3. **Memoization Opportunities** (Future Enhancement)
   - `useMemo` for expensive calculations
   - `useCallback` for event handlers

4. **Code Splitting** (Built-in Next.js)
   - Automatic code splitting per route
   - Lazy loading of heavy components

---

**Architecture Documentation**  
**Created**: January 2025  
**For**: Task 22 - DPR Preview Page Implementation
