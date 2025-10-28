# Architecture Blueprint - MSME DPR Generator

**Document Purpose**: Detailed architectural overview of backend routes, frontend pages, and database schema (text format explanation, no code implementation)

**Date**: October 24, 2025  
**Status**: Design Reference Document

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Backend Architecture & Routes](#backend-architecture--routes)
3. [Frontend Architecture & Pages](#frontend-architecture--pages)
4. [PostgreSQL Database Schema](#postgresql-database-schema)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Integration Points](#integration-points)

---

## 🎯 Overview

### What This Document Explains

This document describes:
- **Backend Routes**: All API endpoints the frontend will call (organized by functionality)
- **Frontend Pages**: User interface screens and their purposes (organized by user journey)
- **Database Schema**: How data is organized in PostgreSQL (organized by entity)

### Architecture Approach

The system uses a **three-tier architecture**:
1. **Frontend Tier**: Next.js application running in browser (client-side)
2. **Backend Tier**: FastAPI application running on server (business logic)
3. **Database Tier**: PostgreSQL storing all persistent data

The frontend sends HTTP requests to backend routes, which process data and interact with PostgreSQL database.

---

## 🔌 Backend Architecture & Routes

### Overview of Backend Structure

The backend is organized by **functional domains**, with each domain handling specific responsibilities:

1. **Authentication Domain**: User login, signup, session management
2. **Form Management Domain**: Storing and retrieving DPR form data
3. **AI Processing Domain**: Calling Gemini API for DPR generation
4. **Financial Modeling Domain**: Calculating financial projections
5. **Scheme Matching Domain**: Recommending government schemes
6. **PDF Generation Domain**: Creating downloadable reports
7. **User Profile Domain**: Managing entrepreneur information
8. **Analytics Domain**: Tracking usage and success metrics

---

### Authentication Routes (Domain 1)

**Purpose**: Handle user registration, login, logout, and session management

#### Register New User
- **Route Path**: `POST /auth/register`
- **What It Does**: Creates a new MSME entrepreneur account
- **Request Data From Frontend**: 
  ```
  {
    name: string,
    email: string,
    phone: string,
    password: string,
    state: string,
    business_category: string
  }
  ```
- **Backend Processing**:
  - Validates email isn't already registered
  - Encrypts password for security
  - Creates new user record in Users table
  - Returns unique user ID and authentication token
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    user_id: string,
    token: string (JWT),
    user_details: object
  }
  ```

#### Login
- **Route Path**: `POST /auth/login`
- **What It Does**: Authenticates existing user and starts session
- **Request Data From Frontend**:
  ```
  {
    email: string,
    password: string
  }
  ```
- **Backend Processing**:
  - Looks up user by email from Users table
  - Verifies password matches stored (encrypted) password
  - Generates new authentication token (JWT)
  - Creates session record in Sessions table
  - Records login timestamp
- **Response To Frontend**:
  ```
  {
    success: boolean,
    message: string,
    token: string (JWT),
    user_id: string,
    user_name: string,
    email: string,
    business_type: string
  }
  ```

#### Logout
- **Route Path**: `POST /auth/logout`
- **What It Does**: Ends user session
- **Request Data From Frontend**: 
  ```
  {
    token: string (JWT in Authorization header)
  }
  ```
- **Backend Processing**:
  - Invalidates authentication token
  - Marks session as ended in Sessions table
  - Records logout timestamp
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string
  }
  ```

#### Verify Token / Check Session
- **Route Path**: `GET /auth/verify`
- **What It Does**: Checks if user's authentication token is still valid
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  ```
- **Backend Processing**:
  - Verifies token validity and expiration
  - Retrieves user info from Users table
  - Checks session is active in Sessions table
- **Response To Frontend**: 
  ```
  {
    valid: boolean,
    user_id: string,
    email: string,
    name: string,
    expires_at: timestamp
  }
  ```

---

### Form Management Routes (Domain 2)

**Purpose**: Save, retrieve, and manage DPR form data

#### Save Form Data (Create or Update)
- **Route Path**: `POST /form` (Create new) or `PUT /form/{form_id}` (Update existing)
- **What It Does**: Stores or updates entrepreneur-provided form data
- **Request Data From Frontend**:
  ```
  {
    form_id: string (null if creating new),
    section_type: string (entrepreneur_details, business_details, etc.),
    section_data: object (depends on section type),
    is_complete: boolean
  }
  ```
- **Backend Processing**:
  - Validates all data (numbers reasonable, dates valid, etc.)
  - Stores/updates data in corresponding database table
  - Marks which sections are complete vs incomplete
  - Records timestamp of save
  - Updates completion percentage
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    message: string,
    completion_percentage: number,
    incomplete_sections: array
  }
  ```

#### Get Complete Form Data
- **Route Path**: `GET /form/{form_id}`
- **What It Does**: Fetches all saved form data for a specific form
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Retrieves form record from DPR_Forms table
  - Validates user has permission (form belongs to logged-in user)
  - Joins and retrieves all associated data tables
  - Assembles complete form structure
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form: {
      form_id: string,
      user_id: string,
      business_name: string,
      entrepreneur_details: object,
      business_details: object,
      financial_details: object,
      ... (all sections)
    },
    completion_percentage: number,
    last_modified: timestamp
  }
  ```

#### Get All Forms for User
- **Route Path**: `GET /user/forms` or `GET /forms`
- **What It Does**: Lists all DPR forms user has created
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  Optional Query Params:
  - sort_by: created_date | modified_date | status
  - filter: all | draft | in_progress | completed
  - limit: number (default 10)
  - offset: number (for pagination)
  ```
- **Backend Processing**:
  - Queries DPR_Forms table WHERE user_id = logged_in_user
  - Applies filters and sorting
  - Paginates results
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    forms: [
      {
        form_id: string,
        business_name: string,
        status: string,
        completion_percentage: number,
        created_date: timestamp,
        last_modified: timestamp
      },
      ... (more forms)
    ],
    total_count: number,
    limit: number,
    offset: number
  }
  ```

#### Get Specific Section of Form
- **Route Path**: `GET /form/{form_id}/section/{section_name}`
- **What It Does**: Fetches only one section of a form (for partial loading)
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameters:
  - form_id: string
  - section_name: string (entrepreneur_details, business_details, financial_details, etc.)
  ```
- **Backend Processing**:
  - Retrieves specific section data from appropriate table
  - Validates access permissions
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    section_name: string,
    data: object,
    completion_status: boolean
  }
  ```

#### Save Specific Section
- **Route Path**: `POST /form/{form_id}/section/{section_name}`
- **What It Does**: Saves one section without requiring entire form
- **Request Data From Frontend**:
  ```
  {
    form_id: string,
    section_name: string,
    section_data: object,
    is_complete: boolean
  }
  ```
- **Backend Processing**:
  - Validates section data
  - Updates only that section in database
  - Recalculates form completion percentage
  - Records auto-save timestamp
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    form_id: string,
    section_name: string,
    completion_percentage: number
  }
  ```

#### Delete Form
- **Route Path**: `DELETE /form/{form_id}`
- **What It Does**: Permanently removes a form
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Verifies user owns this form
  - Marks form as deleted (soft-delete) in database
  - Records deletion in audit table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    form_id: string
  }
  ```

#### Duplicate/Copy Form
- **Route Path**: `POST /form/{form_id}/duplicate`
- **What It Does**: Creates a copy of existing form with all data
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    original_form_id: string,
    new_business_name: string (optional)
  }
  ```
- **Backend Processing**:
  - Creates new form record
  - Copies all data from original form
  - Resets status to draft
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    new_form_id: string,
    message: string
  }
  ```

---

### AI Processing Routes (Domain 3)

**Purpose**: Call Gemini AI to generate DPR content

#### Generate Complete DPR Content
- **Route Path**: `POST /ai/generate-dpr/{form_id}`
- **What It Does**: Sends form data to Gemini AI and receives generated DPR sections
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    form_id: string,
    sections_to_generate: array (e.g., ["executive_summary", "market_analysis", "risk_analysis"])
  }
  ```
- **Backend Processing**:
  - Retrieves form data from database
  - Constructs prompts for each requested section
  - Calls Gemini API multiple times (once per section)
  - Receives AI-generated text for each section
  - Validates AI output is reasonable
  - Stores generated content in Generated_DPR_Content table
  - Returns progress updates
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    generated_sections: {
      executive_summary: { text: string, confidence: number },
      market_analysis: { text: string, confidence: number },
      risk_analysis: { text: string, confidence: number },
      ... (other sections)
    },
    message: string,
    generation_status: "complete" | "partial" | "failed"
  }
  ```

#### Generate Single Section
- **Route Path**: `POST /ai/generate-section/{form_id}/{section_name}`
- **What It Does**: Generates AI content for a single DPR section
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameters:
  - form_id: string
  - section_name: string (executive_summary, market_analysis, etc.)
  Body:
  {
    context: string (optional, additional context for AI)
  }
  ```
- **Backend Processing**:
  - Retrieves form data
  - Constructs prompt for specific section
  - Calls Gemini API
  - Stores result
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    section_name: string,
    generated_text: string,
    confidence_score: number (0-100),
    generation_timestamp: timestamp
  }
  ```

#### Regenerate Section with Feedback
- **Route Path**: `POST /ai/regenerate-section/{form_id}/{section_name}`
- **What It Does**: Calls Gemini again to generate alternative version based on feedback
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameters:
  - form_id: string
  - section_name: string
  Body:
  {
    feedback: string (e.g., "make it more detailed", "focus on USP"),
    regeneration_attempt: number
  }
  ```
- **Backend Processing**:
  - Retrieves original form data
  - Modifies AI prompt based on feedback
  - Calls Gemini API with enhanced prompt
  - Returns new version
  - Stores as new version in database
  - Keeps history of all versions
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    section_name: string,
    new_generated_text: string,
    previous_version: string,
    confidence_score: number,
    version_number: number
  }
  ```

#### Get AI Generation Status (Long-running operations)
- **Route Path**: `GET /ai/generation-status/{form_id}`
- **What It Does**: Checks progress of DPR generation (for frontend polling)
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Retrieves generation status from cache/database
  - Returns progress information
- **Response To Frontend**: 
  ```
  {
    form_id: string,
    status: "processing" | "completed" | "failed",
    sections_completed: number,
    total_sections: number,
    current_section: string,
    error_message: string (if failed),
    estimated_time_remaining: number (seconds)
  }
  ```

#### Get Generation History
- **Route Path**: `GET /ai/history/{form_id}/{section_name}`
- **What It Does**: Lists all generated versions of a section (for comparison)
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameters:
  - form_id: string
  - section_name: string (optional, if null returns all sections)
  ```
- **Backend Processing**:
  - Queries Generated_DPR_Content table
  - Retrieves all versions for this section
  - Orders by generation date
- **Response To Frontend**: 
  ```
  {
    section_name: string,
    versions: [
      {
        version_id: string,
        version_number: number,
        text: string,
        confidence_score: number,
        generated_at: timestamp,
        feedback_provided: string
      },
      ... (more versions)
    ]
  }
  ```

---

### Financial Modeling Routes (Domain 4)

**Purpose**: Calculate financial projections and viability analysis

#### Calculate Financial Projections
- **Route Path**: `POST /financial/calculate/{form_id}`
- **What It Does**: Creates 3-year financial projections (revenue, expenses, profit)
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    form_id: string,
    initial_investment: number,
    monthly_revenue_estimate: number,
    monthly_fixed_costs: number,
    monthly_variable_costs: number,
    sector_type: string,
    business_category: string,
    growth_rate_percentage: number
  }
  ```
- **Backend Processing**:
  - Retrieves form financial details
  - Uses financial formulas to project month-by-month for 36 months
  - Applies industry benchmarks for sector
  - Calculates breakeven point
  - Calculates ROI (Return on Investment)
  - Calculates payback period
  - Applies conservative growth rates
  - Includes tax calculations
  - Stores monthly projections in Monthly_Projections table
  - Stores summary in Financial_Calculations table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    financial_summary: {
      breakeven_months: number,
      roi_percentage: number,
      payback_period_months: number,
      npv: number,
      profit_margin_percentage: number
    },
    monthly_data: [
      {
        month: number,
        revenue: number,
        fixed_costs: number,
        variable_costs: number,
        profit_loss: number,
        cumulative_profit_loss: number
      },
      ... (36 months)
    ],
    yearly_summary: [
      { year: 1, revenue: number, expenses: number, profit: number },
      { year: 2, revenue: number, expenses: number, profit: number },
      { year: 3, revenue: number, expenses: number, profit: number }
    ]
  }
  ```

#### Get Financial Summary
- **Route Path**: `GET /financial/summary/{form_id}`
- **What It Does**: Returns key financial metrics for dashboard/preview
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Retrieves calculated financial models from Financial_Calculations table
  - Summarizes key metrics
  - Formats for display
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    summary: {
      total_investment: number,
      breakeven_months: number,
      roi_3_year: number,
      payback_period: number,
      year_1_profit: number,
      year_2_profit: number,
      year_3_profit: number,
      average_monthly_cash_flow: number
    }
  }
  ```

#### Get Detailed Financial Report
- **Route Path**: `GET /financial/detailed-report/{form_id}`
- **What It Does**: Returns complete financial analysis for PDF/export
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  Query Params:
  - format: pdf | json | excel (optional, default json)
  ```
- **Backend Processing**:
  - Retrieves all calculations
  - Generates charts data (if format is pdf)
  - Formats for requested output
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    report: {
      executive_summary: object,
      monthly_breakdown: array,
      yearly_summary: array,
      metrics: object,
      assumptions_used: object
    }
  }
  ```

#### Get Sector Benchmarks
- **Route Path**: `GET /financial/benchmarks/{sector_name}`
- **What It Does**: Returns average financial metrics for business sector
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token> (optional for this endpoint)
  URL Parameter: sector_name
  ```
- **Backend Processing**:
  - Looks up sector from Sector_Benchmarks table
  - Returns average profit margins, growth rates, etc.
  - Returns industry comparison data
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    sector: string,
    benchmarks: {
      average_profit_margin: number,
      average_growth_rate: number,
      average_payback_period: number,
      average_roi: number,
      typical_investment_range: { min: number, max: number },
      typical_employees_per_crore: number
    }
  }
  ```

#### Compare with Sector Benchmarks
- **Route Path**: `POST /financial/compare-benchmarks/{form_id}`
- **What It Does**: Compares user's projections with sector averages
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Gets user's financial calculations
  - Gets sector benchmarks
  - Compares each metric
  - Generates insights
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    comparison: {
      profit_margin: { user: number, sector_average: number, variance: number },
      growth_rate: { user: number, sector_average: number, variance: number },
      roi: { user: number, sector_average: number, variance: number },
      payback_period: { user: number, sector_average: number, variance: number }
    },
    insights: array (e.g., ["Your profit margin is 15% higher than sector average"])
  }
  ```

---

### Scheme Matching Routes (Domain 5)

**Purpose**: Recommend applicable government schemes and subsidies

#### Get Matching Government Schemes
- **Route Path**: `POST /schemes/match` or `POST /schemes/find-applicable/{form_id}`
- **What It Does**: Recommends schemes the MSME is eligible for based on business details
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body (Option 1 - Full form):
  {
    form_id: string
  }
  
  Body (Option 2 - Manual):
  {
    business_category: string,
    state: string,
    investment_amount: number,
    number_of_employees: number,
    business_type: string (new | existing),
    sector: string
  }
  ```
- **Backend Processing**:
  - Queries Schemes table with filters
  - Filters schemes by eligibility criteria (sector, investment range, state, etc.)
  - Ranks schemes by relevance to business
  - Calculates potential subsidy amount for each scheme
  - Includes scheme details and application requirements
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    matching_schemes: [
      {
        scheme_id: string,
        scheme_name: string,
        ministry: string,
        scheme_type: string (subsidy | loan_guarantee | tax_benefit),
        subsidy_percentage: number,
        estimated_subsidy_amount: number,
        eligibility_criteria: string,
        required_documents: array,
        application_process: string,
        processing_time_days: number,
        scheme_url: string,
        contact_details: string,
        relevance_score: number (0-100),
        reason_for_match: string
      },
      ... (more schemes)
    ],
    total_estimated_subsidy: number,
    total_schemes_found: number
  }
  ```

#### Get Scheme Details
- **Route Path**: `GET /schemes/{scheme_id}`
- **What It Does**: Returns complete details about one specific scheme
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token> (optional)
  URL Parameter: scheme_id
  ```
- **Backend Processing**:
  - Retrieves scheme from Schemes table
  - Formats complete details
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    scheme: {
      scheme_id: string,
      scheme_name: string,
      ministry: string,
      scheme_type: string,
      description: string,
      subsidy_percentage: number,
      max_subsidy_amount: number,
      eligible_sectors: array,
      eligible_states: array,
      eligible_investment_range: { min: number, max: number },
      eligibility_criteria: string,
      required_documents: [
        { document_name: string, description: string },
        ...
      ],
      application_steps: array,
      processing_time_days: number,
      application_fee: number,
      contact_details: {
        phone: string,
        email: string,
        office_address: string,
        website: string
      },
      last_updated: timestamp,
      application_link: string
    }
  }
  ```

#### Search Schemes
- **Route Path**: `GET /schemes/search`
- **What It Does**: Search for schemes by keyword or filter
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token> (optional)
  Query Parameters:
  - keyword: string (e.g., "subsidy")
  - sector: string
  - state: string
  - scheme_type: string (subsidy | loan | grant)
  - sort_by: relevance | name | subsidy_amount (default: relevance)
  - limit: number (default: 10)
  ```
- **Backend Processing**:
  - Searches Schemes table with filters
  - Ranks by relevance
  - Paginates results
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    schemes: [
      { scheme_id, scheme_name, scheme_type, subsidy_percentage, ... },
      ...
    ],
    total_results: number,
    filters_applied: object
  }
  ```

#### Add Selected Schemes to Form
- **Route Path**: `POST /form/{form_id}/schemes`
- **What It Does**: Associates chosen schemes with DPR form
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  Body:
  {
    selected_scheme_ids: array (e.g., ["sch_001", "sch_003", "sch_005"])
  }
  ```
- **Backend Processing**:
  - Validates all scheme IDs exist
  - Links schemes to form in Form_Scheme_Selections table
  - Calculates estimated subsidy amounts
  - Updates form record
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    message: string,
    selected_schemes: number,
    total_estimated_subsidy: number,
    schemes_added: [
      {
        scheme_id: string,
        scheme_name: string,
        estimated_subsidy: number
      },
      ...
    ]
  }
  ```

#### Get Form's Selected Schemes
- **Route Path**: `GET /form/{form_id}/schemes`
- **What It Does**: Retrieves all schemes user selected for this form
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  ```
- **Backend Processing**:
  - Queries Form_Scheme_Selections table
  - Joins with Schemes table to get details
  - Filters to show only selected schemes
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    schemes: [
      {
        scheme_id: string,
        scheme_name: string,
        scheme_type: string,
        estimated_subsidy_amount: number,
        selected_date: timestamp,
        is_included_in_pdf: boolean
      },
      ...
    ],
    total_schemes: number,
    total_subsidy: number
  }
  ```

#### Remove Scheme from Form
- **Route Path**: `DELETE /form/{form_id}/schemes/{scheme_id}`
- **What It Does**: Removes a selected scheme from form
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameters:
  - form_id: string
  - scheme_id: string
  ```
- **Backend Processing**:
  - Deletes record from Form_Scheme_Selections table
  - Recalculates total subsidy
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    form_id: string,
    remaining_schemes: number
  }
  ```

---

### PDF Generation Routes (Domain 6)

**Purpose**: Create downloadable, professional DPR PDF documents

#### Generate PDF Report
- **Route Path**: `POST /pdf/generate/{form_id}`
- **What It Does**: Creates complete DPR PDF combining form, AI content, and financial models
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  Body:
  {
    template_type: string (basic | professional | bank-ready),
    language: string (english | telugu),
    include_sections: array (optional, e.g., ["executive_summary", "financial", "schemes"]),
    custom_branding: object (optional)
  }
  ```
- **Backend Processing**:
  - Retrieves all form data from database
  - Retrieves generated AI content
  - Retrieves financial models
  - Retrieves scheme information
  - Assembles into proper DPR structure
  - Applies formatting and styling (template_type)
  - Renders in requested language (English or Telugu)
  - Uses WeasyPrint to convert HTML → PDF
  - Uploads PDF to Cloudinary
  - Stores PDF metadata in PDF_Documents table
  - Records generation in audit log
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    pdf_id: string,
    pdf_url: string,
    file_name: string,
    file_size: number,
    language: string,
    template_type: string,
    generation_timestamp: timestamp,
    expiry_date: timestamp (if temporary link)
  }
  ```

#### Download PDF
- **Route Path**: `GET /pdf/{pdf_id}/download` or `GET /pdf/download/{form_id}`
- **What It Does**: Returns PDF file for download
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token> (optional for user's own PDFs)
  URL Parameter: pdf_id or form_id
  ```
- **Backend Processing**:
  - Validates user has permission
  - Retrieves PDF URL from Cloudinary storage
  - Returns as downloadable file with proper headers
- **Response To Frontend**: 
  ```
  Binary PDF file with headers:
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="DPR_BusinessName.pdf"
  ```

#### Preview PDF
- **Route Path**: `GET /pdf/{pdf_id}/preview` or `GET /pdf/preview/{form_id}`
- **What It Does**: Shows PDF in browser without downloading
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token> (optional)
  URL Parameter: pdf_id or form_id
  Query Params:
  - page: number (optional, default 1)
  ```
- **Backend Processing**:
  - Retrieves PDF from Cloudinary
  - Returns in format suitable for in-browser viewing (base64 or direct URL)
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    pdf_url: string (URL for iframe or PDF viewer),
    total_pages: number,
    current_page: number,
    file_name: string
  }
  ```

#### Get PDF History/Versions
- **Route Path**: `GET /pdf/history/{form_id}` or `GET /form/{form_id}/pdfs`
- **What It Does**: Lists all PDFs generated for a specific form (version history)
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: form_id
  Query Params:
  - sort_by: created_date | modified_date (default: created_date)
  - limit: number (default: 10)
  ```
- **Backend Processing**:
  - Queries PDF_Documents table WHERE form_id = param
  - Retrieves metadata for each PDF
  - Sorts and paginates
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_id: string,
    pdfs: [
      {
        pdf_id: string,
        file_name: string,
        template_type: string,
        language: string,
        file_size: number,
        generated_date: timestamp,
        last_modified: timestamp,
        download_count: number
      },
      ... (more PDFs)
    ],
    total_count: number
  }
  ```

#### Delete PDF
- **Route Path**: `DELETE /pdf/{pdf_id}`
- **What It Does**: Removes a generated PDF
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: pdf_id
  ```
- **Backend Processing**:
  - Validates user permission
  - Marks as deleted in database (soft-delete)
  - Optionally removes from Cloudinary
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    pdf_id: string
  }
  ```

#### Share PDF Link
- **Route Path**: `POST /pdf/{pdf_id}/generate-share-link`
- **What It Does**: Generates shareable link for PDF (no authentication required)
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: pdf_id
  Body (optional):
  {
    expiry_days: number (e.g., 7, 30),
    download_limit: number (e.g., 5, 10)
  }
  ```
- **Backend Processing**:
  - Generates unique share token
  - Stores share details (expiry, limits)
  - Creates shareable URL
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    share_url: string (e.g., "https://app.com/share/token123"),
    expires_on: timestamp,
    download_limit: number,
    downloads_remaining: number
  }
  ```

#### Send PDF via Email
- **Route Path**: `POST /pdf/{pdf_id}/send-email`
- **What It Does**: Sends PDF to specified email address
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: pdf_id
  Body:
  {
    recipient_email: string,
    recipient_name: string (optional),
    message: string (optional),
    include_form_link: boolean (optional)
  }
  ```
- **Backend Processing**:
  - Validates email
  - Prepares email with PDF attachment/link
  - Sends via email service
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    email_sent_to: string,
    timestamp: timestamp
  }
  ```

#### Get PDF Metadata
- **Route Path**: `GET /pdf/{pdf_id}/metadata`
- **What It Does**: Returns PDF file information without downloading
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  URL Parameter: pdf_id
  ```
- **Backend Processing**:
  - Retrieves PDF record from database
  - Returns metadata
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    pdf_id: string,
    form_id: string,
    file_name: string,
    file_size: number,
    created_date: timestamp,
    language: string,
    template_type: string,
    page_count: number,
    last_downloaded: timestamp,
    download_count: number
  }
  ```

---

### User Profile Routes (Domain 7)

**Purpose**: Manage user account settings and preferences

#### Get User Profile
- **Route Path**: `GET /user/profile` or `GET /user`
- **What It Does**: Retrieves complete user account information
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  ```
- **Backend Processing**:
  - Retrieves user record from Users table
  - Retrieves extended profile from User_Profile_Extensions table
  - Combines user and profile data
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    user: {
      user_id: string,
      name: string,
      email: string,
      phone: string,
      business_type: string,
      state: string,
      address: string,
      aadhar_number: string,
      pan_number: string,
      years_in_business: number,
      profile_photo_url: string,
      bio: string,
      created_date: timestamp,
      last_login: timestamp,
      email_verified: boolean,
      phone_verified: boolean
    }
  }
  ```

#### Update User Profile
- **Route Path**: `PUT /user/profile` or `PATCH /user/profile`
- **What It Does**: Allows user to update their account information
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body (send only fields to update):
  {
    name: string (optional),
    phone: string (optional),
    business_type: string (optional),
    address: string (optional),
    years_in_business: number (optional),
    bio: string (optional),
    profile_photo_url: string (optional)
  }
  ```
- **Backend Processing**:
  - Validates new data
  - Updates Users table and/or User_Profile_Extensions table
  - Records modification timestamp
  - Logs change in audit table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    updated_user: object (complete user profile after update)
  }
  ```

#### Change Password
- **Route Path**: `POST /user/change-password`
- **What It Does**: Updates user password with verification of current password
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    current_password: string,
    new_password: string,
    confirm_password: string
  }
  ```
- **Backend Processing**:
  - Retrieves user from database
  - Verifies current password matches encrypted stored password
  - Validates new password meets security requirements (length, complexity)
  - Validates new_password == confirm_password
  - Encrypts new password
  - Updates Users table
  - Logs password change in audit table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    password_changed_at: timestamp
  }
  ```

#### Forgot Password - Request Reset
- **Route Path**: `POST /auth/forgot-password`
- **What It Does**: Initiates password reset by sending email
- **Request Data From Frontend**:
  ```
  Body:
  {
    email: string
  }
  ```
- **Backend Processing**:
  - Looks up user by email
  - Generates password reset token
  - Stores token with expiry (typically 1 hour) in database
  - Sends email with reset link containing token
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string (e.g., "Reset link sent to your email")
  }
  ```

#### Forgot Password - Reset via Token
- **Route Path**: `POST /auth/reset-password`
- **What It Does**: Resets password using token from email link
- **Request Data From Frontend**:
  ```
  Body:
  {
    reset_token: string,
    new_password: string,
    confirm_password: string
  }
  ```
- **Backend Processing**:
  - Validates reset token (exists, not expired)
  - Validates new_password == confirm_password
  - Encrypts new password
  - Updates user's password
  - Invalidates reset token
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string
  }
  ```

#### Update Preferences
- **Route Path**: `PUT /user/preferences`
- **What It Does**: Updates user notification and display preferences
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    language: string (english | telugu),
    email_notifications: boolean,
    sms_notifications: boolean,
    marketing_emails: boolean,
    pdf_template_preference: string (basic | professional | bank-ready)
  }
  ```
- **Backend Processing**:
  - Updates user preferences in database
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    preferences: object (updated preferences)
  }
  ```

#### Upload Profile Photo
- **Route Path**: `POST /user/upload-profile-photo`
- **What It Does**: Uploads user's profile picture
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Content-Type: multipart/form-data
  Body:
  {
    photo: file (image file, max 5MB)
  }
  ```
- **Backend Processing**:
  - Validates file is image (jpg, png, etc.)
  - Resizes/optimizes image
  - Uploads to Cloudinary
  - Stores URL in Users table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    photo_url: string
  }
  ```

#### Download User Data
- **Route Path**: `GET /user/download-data`
- **What It Does**: Exports all user's data (GDPR compliance)
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  Query Params:
  - format: json | csv (default: json)
  ```
- **Backend Processing**:
  - Compiles all user data from all tables
  - Prepares in requested format
  - Generates download file
- **Response To Frontend**: 
  ```
  JSON or CSV file containing:
  - User profile
  - All forms
  - Generated content
  - Financial data
  - Selected schemes
  - Activity logs
  ```

#### Delete Account
- **Route Path**: `DELETE /user/account`
- **What It Does**: Permanently deletes user account and all associated data
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    password: string (for verification),
    reason: string (optional feedback),
    confirmation: boolean (true to confirm)
  }
  ```
- **Backend Processing**:
  - Verifies password
  - Marks all user records as deleted (soft-delete)
  - Stores deleted data in archive (for potential recovery)
  - Invalidates all sessions
  - Logs deletion in audit table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    message: string,
    account_deleted_at: timestamp
  }
  ```

---

### Analytics Routes (Domain 8)

**Purpose**: Track platform usage and success metrics

#### Track User Activity
- **Route Path**: `POST /analytics/track-activity`
- **What It Does**: Logs user actions for analytics (called by frontend automatically)
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token> (optional)
  Body:
  {
    activity_type: string (e.g., form_created, form_saved, ai_generated, pdf_downloaded),
    form_id: string (optional),
    section_name: string (optional),
    duration_seconds: number (optional),
    device_type: string (web | mobile | tablet),
    page_url: string (optional)
  }
  ```
- **Backend Processing**:
  - Records activity in User_Activity_Log table
  - Aggregates metrics
  - Identifies patterns
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    activity_logged: true
  }
  ```

#### Track Form Completion
- **Route Path**: `POST /analytics/form-completion` or `POST /analytics/track-progress`
- **What It Does**: Records form section completion for funnel analysis
- **Request Data From Frontend**:
  ```
  Headers:
  Authorization: Bearer <token>
  Body:
  {
    form_id: string,
    section_name: string,
    completed: boolean,
    time_spent_seconds: number,
    field_errors: number
  }
  ```
- **Backend Processing**:
  - Records in User_Activity_Log or Form_Completion_Metrics
  - Updates completion tracking
  - Identifies bottlenecks
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    form_completion_percentage: number
  }
  ```

#### Get User Dashboard Statistics
- **Route Path**: `GET /user/dashboard-stats` or `GET /analytics/user-stats`
- **What It Does**: Returns metrics for user's personal dashboard
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <token>
  ```
- **Backend Processing**:
  - Queries User_Activity_Log
  - Queries DPR_Forms
  - Queries PDF_Documents
  - Aggregates statistics
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    stats: {
      total_forms_created: number,
      completed_forms: number,
      in_progress_forms: number,
      total_pdfs_generated: number,
      total_time_spent_hours: number,
      last_activity: timestamp,
      estimated_credit_accessed: number,
      estimated_subsidy_identified: number
    }
  }
  ```

#### Get Platform Analytics (Admin Only)
- **Route Path**: `GET /admin/analytics` or `GET /analytics/platform-stats`
- **What It Does**: Returns platform-wide metrics for administrators
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <admin_token>
  Query Params:
  - start_date: timestamp (optional)
  - end_date: timestamp (optional)
  - period: daily | weekly | monthly (optional)
  ```
- **Backend Processing**:
  - Aggregates statistics across all users
  - Calculates trends
  - Queries Platform_Statistics table
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    platform_stats: {
      total_users_registered: number,
      active_users_today: number,
      active_users_week: number,
      active_users_month: number,
      total_forms_created: number,
      total_forms_completed: number,
      completion_rate_percentage: number,
      total_pdfs_generated: number,
      total_schemes_recommended: number,
      total_estimated_credit_unlocked: number,
      average_form_completion_time_minutes: number,
      platform_uptime_percentage: number,
      new_users_today: number,
      new_users_week: number,
      new_users_month: number
    }
  }
  ```

#### Get Sector-wise Analytics
- **Route Path**: `GET /analytics/sector-stats`
- **What It Does**: Returns analytics broken down by business sector
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <admin_token> (optional)
  Query Params:
  - sector: string (optional, if null returns all sectors)
  ```
- **Backend Processing**:
  - Groups forms by sector
  - Aggregates metrics per sector
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    sectors: [
      {
        sector_name: string,
        users_in_sector: number,
        forms_created: number,
        forms_completed: number,
        average_investment: number,
        total_schemes_recommended: number,
        average_completion_time: number
      },
      ... (more sectors)
    ]
  }
  ```

#### Get Form Completion Funnel
- **Route Path**: `GET /analytics/completion-funnel`
- **What It Does**: Shows where users drop off in form completion
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <admin_token> (optional)
  ```
- **Backend Processing**:
  - Analyzes form section completion rates
  - Identifies highest dropout points
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    funnel: [
      {
        stage: string (e.g., "Started Form"),
        users: number,
        completion_percentage: number
      },
      {
        stage: string (e.g., "Entrepreneur Details"),
        users: number,
        completion_percentage: number
      },
      {
        stage: string (e.g., "Business Details"),
        users: number,
        completion_percentage: number
      },
      ... (all stages)
    ]
  }
  ```

#### Get Daily Statistics Report
- **Route Path**: `GET /analytics/daily-report`
- **What It Does**: Returns daily metrics for specific date range
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <admin_token>
  Query Params:
  - start_date: timestamp
  - end_date: timestamp (optional, default today)
  ```
- **Backend Processing**:
  - Queries Platform_Statistics table
  - Generates daily breakdown
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    daily_data: [
      {
        date: date,
        new_users: number,
        active_users: number,
        forms_created: number,
        forms_completed: number,
        pdfs_generated: number,
        uptime_percentage: number
      },
      ... (more days)
    ]
  }
  ```

#### Get User Engagement Report
- **Route Path**: `GET /analytics/engagement-report`
- **What It Does**: Analyzes user engagement patterns
- **Request Data From Frontend**: 
  ```
  Headers:
  Authorization: Bearer <admin_token> (optional)
  Query Params:
  - segment: string (optional, e.g., "new_users", "active_users", "inactive_users")
  ```
- **Backend Processing**:
  - Segments users by engagement level
  - Calculates engagement metrics
- **Response To Frontend**: 
  ```
  {
    success: boolean,
    engagement: {
      highly_engaged_users: number,
      moderately_engaged_users: number,
      low_engagement_users: number,
      inactive_users: number,
      average_forms_per_user: number,
      average_session_duration_minutes: number,
      return_rate_percentage: number
    }
  }
  ```

---

## 🖥️ Frontend Architecture & Pages

### Overview of Frontend Structure

The frontend is organized by **user journey stages**, with each stage representing a phase in the DPR creation process:

1. **Authentication Pages**: Login/Signup
2. **Onboarding Pages**: Initial user setup
3. **Form Pages**: Data collection
4. **Review Pages**: Preview before generation
5. **Generation Pages**: AI and financial processing
6. **Output Pages**: PDF download and results
7. **Dashboard Pages**: User account and history
8. **Help Pages**: Guidance and support

---

### Authentication Pages (Stage 1)

#### Login Page
- **What User Sees**:
  - Email input field
  - Password input field
  - "Login" button
  - "Sign up" link (for new users)
  - "Forgot password?" link
  - Optional: Social login (Google)
- **What Happens When User Interacts**:
  - User enters email and password
  - Clicks login button
  - Frontend validates email format and password not empty
  - Frontend sends request to backend login route
  - Backend verifies credentials
  - If success: User redirected to dashboard
  - If failure: Error message displayed
- **Data Submitted to Backend**: Email, password
- **Data Received from Backend**: Authentication token, user ID

#### Signup Page
- **What User Sees**:
  - Full name input
  - Email input
  - Phone number input
  - Password input
  - Confirm password input
  - Business type dropdown (Manufacturing, Services, Retail, etc.)
  - State selection (Andhra Pradesh)
  - Terms and conditions checkbox
  - "Create Account" button
  - "Already have account?" link to login
- **What Happens When User Interacts**:
  - User fills out form
  - Frontend validates all fields (email format, password strength, etc.)
  - User clicks create account
  - Frontend sends to backend signup route
  - Backend creates account and returns token
  - User redirected to dashboard
- **Data Submitted to Backend**: Name, email, phone, password, business type, state
- **Data Received from Backend**: Authentication token, user ID, confirmation message

#### Forgot Password Page
- **What User Sees**:
  - Email input
  - "Send Reset Link" button
  - Information about what happens next
- **What Happens When User Interacts**:
  - User enters email
  - Backend sends password reset email
  - User clicks link in email
  - User taken to reset password page
  - User enters new password
  - Password updated in backend
- **Data Flow**: Email → Backend → Email sent → User gets link → New password submitted

---

### Onboarding Pages (Stage 2)

#### Welcome Page
- **What User Sees**:
  - Welcome message
  - Overview of what tool does
  - Quick tutorial (3-5 steps)
  - Business category selector
  - "Get Started" button
- **What Happens**:
  - Page provides context about DPR process
  - User selects their business category
  - Frontend stores selection
  - User directed to form page
- **Data Stored**: Business category preference

#### Onboarding Tutorial
- **What User Sees**:
  - Interactive walkthrough showing:
    - How to fill form
    - How AI generates content
    - How to create PDF
    - How to download report
  - "Skip" option
  - "Next" buttons
- **What Happens**:
  - Shows new users how system works
  - Can be skipped by experienced users
  - Helps reduce confusion

---

### Form Pages (Stage 3)

The form is typically organized into multiple sections, with each section as its own page or tab.

#### Entrepreneur Details Page
- **What User Sees**:
  - Business name input
  - Entrepreneur name input
  - Date of birth picker
  - Aadhar/ID number input
  - Address fields (street, city, postal code)
  - Phone number
  - Email
  - Years in business input
  - Save progress button
- **What Happens**:
  - User fills basic information
  - Information auto-saves periodically
  - User can click "Next" to go to next section
  - Previous data is remembered
- **Data Submitted**: All entrepreneur details
- **Data Received**: Confirmation of save, completion status

#### Business Details Page
- **What User Sees**:
  - Business type selection (service, manufacturing, retail, etc.)
  - Business description text area
  - Current annual revenue input
  - Number of employees
  - Current facilities description
  - Business registration details
  - GST number (if applicable)
  - Save button
- **What Happens**:
  - User provides business context
  - Backend calculates sector benchmarks based on business type
  - Frontend provides suggestions
- **Data Submitted**: Business information
- **Data Received**: Sector benchmarks, suggestions for next section

#### Product/Service Details Page
- **What User Sees**:
  - Product/service name
  - Detailed description text area
  - Key features/benefits list
  - Target customers description
  - Current capacity
  - Planned capacity increase (if applicable)
  - Unique selling points list
  - Save button
- **What Happens**:
  - User describes what they sell
  - This information used by AI to generate better DPR content
- **Data Submitted**: Product/service details

#### Market Analysis Page
- **What User Sees**:
  - Total market size input
  - Estimated market share
  - Key competitors list
  - Competitive advantage description
  - Customer acquisition strategy
  - Pricing strategy
  - Market growth projections
  - Save button
- **What Happens**:
  - User provides market context
  - AI will use this for market section of DPR

#### Financial Details Page
- **What User Sees**:
  - Total investment amount
  - Land cost (if applicable)
  - Building/facility cost
  - Machinery/equipment costs (with item list)
  - Working capital needed
  - Furniture and fixtures
  - Software licenses
  - Initial inventory
  - Breakdown of each cost category
  - Total calculation (auto-sum)
  - Save button
  - Next button to review
- **What Happens**:
  - User enters investment details
  - Frontend calculates totals
  - Backend uses these for financial models
  - System checks if investment is reasonable for sector
- **Data Submitted**: All investment amounts

#### Revenue Projection Page
- **What User Sees**:
  - Monthly revenue estimate
  - Seasonality adjustments (if business is seasonal)
  - Growth rate projection (% per year)
  - Break-even analysis section (calculated by backend)
  - Number of potential customers
  - Average transaction value
  - Save button
- **What Happens**:
  - User enters revenue assumptions
  - Backend calculates financial models based on this
  - Displays payback period and ROI calculations

#### Cost Details Page
- **What User Sees**:
  - Monthly fixed costs:
    - Rent/facility cost
    - Salaries and wages
    - Utilities
    - Insurance
    - Other fixed costs (user can add)
  - Monthly variable costs:
    - Raw materials
    - Packaging
    - Transportation
    - Commission/distribution
    - Other variable costs (user can add)
  - Cost total (auto-calculated)
  - Staffing details section:
    - Number of staff
    - Average salary
    - Total monthly salary cost
  - Save button
- **What Happens**:
  - User enters cost structure
  - Backend uses this for financial projections
  - System validates costs are realistic

#### Staffing Plan Page
- **What User Sees**:
  - Current staff count and roles
  - Planned staff hiring over 3 years
  - Skills required
  - Training plans
  - Salary structure table
  - Total monthly labor cost
  - Save button
- **What Happens**:
  - User provides staffing information
  - Helps with financial modeling
  - Shows in final DPR

#### Timeline/Implementation Page
- **What User Sees**:
  - Project start date picker
  - Construction/setup phase timeline
  - Equipment procurement timeline
  - Staff recruitment timeline
  - Operational launch date
  - Major milestones
  - Save button
- **What Happens**:
  - User enters implementation schedule
  - Shows when cash will be needed
  - Helps with cash flow projections

#### Loan Requirements Page
- **What User Sees**:
  - Required loan amount
  - Requested tenure (months)
  - Interest rate assumption
  - Purpose of loan dropdown
  - Collateral details (if applicable)
  - Bank preference (optional)
  - Save button
- **What Happens**:
  - User specifies financing needs
  - Backend calculates EMI (monthly payment)
  - Helps generate relevant schemes

---

### Review Pages (Stage 4)

#### Form Review Page
- **What User Sees**:
  - Summary of all entered data
  - Organized by sections
  - "Edit" button next to each section
  - Completion percentage
  - List of missing required fields (if any)
  - "Continue to AI Generation" button
  - "Save as Draft" button
- **What Happens**:
  - User reviews what they've entered
  - Can go back and edit any section
  - Confirms all data is correct before proceeding
  - Can save incomplete form for later

#### Completeness Check Page
- **What User Sees**:
  - Checklist of all required fields
  - Green check marks for completed fields
  - Red X marks for missing fields
  - Summary of completion
  - Suggestions for what to fill next
  - "Proceed to AI Generation" button (only if complete)
  - "Save and Complete Later" button
- **What Happens**:
  - Ensures user has filled everything needed
  - Won't proceed to AI generation until requirements met
  - Helps user focus on missing information

---

### Generation Pages (Stage 5)

#### AI Content Generation Page
- **What User Sees**:
  - Progress indicator showing which sections are being generated
  - Status messages:
    - "Analyzing your business..."
    - "Generating Executive Summary..."
    - "Creating Market Analysis..."
    - "Calculating Financial Models..."
    - "Recommending Government Schemes..."
    - "Finalizing Document..."
  - Estimated time remaining
  - "Cancel" button
  - Animated loading indicator
- **What Happens**:
  - Frontend sends form data to backend
  - Backend processes each section (calls Gemini AI, calculates financials, etc.)
  - Frontend receives status updates and displays progress
  - Takes 30-60 seconds typically
  - Once complete, redirects to preview page
- **Backend Activity**:
  - Calls Gemini API multiple times for different sections
  - Calculates financial models
  - Queries schemes database
  - Stores all generated content

#### Financial Model Generation Page
- **What User Sees**:
  - "Calculating Financial Projections..."
  - Progress bar showing calculation status
  - Key metrics as they're calculated (breakeven, ROI, payback period)
  - Option to view detailed assumptions used
  - "Continue" button when ready
- **What Happens**:
  - Backend calculates 36-month financial projections
  - Shows results as they're calculated
  - User can review assumptions

#### Scheme Recommendations Page
- **What User Sees**:
  - "Finding Applicable Government Schemes..."
  - Loading indicator
  - As schemes found, displays:
    - Scheme name
    - Subsidy percentage
    - Eligibility criteria met
  - List builds as schemes are matched
  - "Add Selected Schemes to DPR" button
  - "Skip" option
- **What Happens**:
  - Backend queries scheme database
  - Displays matching schemes
  - User can select which schemes to include

---

### Output Pages (Stage 6)

#### Preview Page
- **What User Sees**:
  - Preview of what DPR will look like
  - Sections included:
    - Executive Summary
    - Entrepreneur details
    - Business description
    - Market analysis
    - Financial projections (with tables and charts)
    - Scheme recommendations
    - Risk analysis
    - Implementation plan
  - Can scroll through entire preview
  - "Edit Specific Section" buttons for each part
  - "Regenerate Section" option for AI content
  - "Generate PDF" button
  - Language selector (English/Telugu)
- **What Happens**:
  - Shows user what final DPR will contain
  - User can edit any AI-generated section if not satisfied
  - Can regenerate sections with feedback
  - Once satisfied, proceeds to PDF generation

#### Section Editing Page
- **What User Sees**:
  - Text area with generated content
  - "Edit" mode where user can modify text
  - "Regenerate" button to get new AI version
  - "Regenerate with Feedback" where user can provide guidance (e.g., "make more detailed")
  - Preview of how edited text will look
  - "Save Changes" button
- **What Happens**:
  - User can manually edit any AI-generated content
  - Can ask AI to try again with specific feedback
  - Changes saved to form

#### PDF Download Page
- **What User Sees**:
  - Message confirming PDF generated
  - PDF preview (first page visible)
  - "Download PDF" button
  - Document details:
    - File name
    - File size
    - Creation date
    - Language
  - "Open in New Window" option
  - "Print" option
  - "Share" option (generates link)
  - "Create Another DPR" button
  - "Go to Dashboard" button
- **What Happens**:
  - User downloads professional DPR
  - Can share via link (backend generates shareable URL)
  - Can print directly
  - Returned to dashboard when done
- **Data Received from Backend**: PDF link, file metadata

---

### Dashboard Pages (Stage 7)

#### Main Dashboard Page
- **What User Sees**:
  - Welcome message with user's name
  - Quick stats cards:
    - Number of DPRs created
    - Total investment planning amount
    - Schemes identified
  - Recent DPRs list (last 5):
    - Business name
    - Creation date
    - Completion status (% complete)
    - Last modified date
    - Action buttons: Continue, View, Download, Delete
  - Quick action buttons:
    - "Create New DPR"
    - "View All Forms"
    - "View Generated Reports"
  - Help and support section
- **What Happens**:
  - User can see overview of all their work
  - Can resume incomplete DPRs
  - Can view previously generated PDFs

#### My Forms Page
- **What User Sees**:
  - List of all DPR forms created
  - Filter options:
    - All forms
    - Completed
    - In progress
    - By date range
  - Search box to find forms by business name
  - Sort options:
    - By creation date
    - By modification date
    - By status
  - For each form:
    - Business name
    - Category
    - Status (% complete)
    - Creation date
    - Last modified
    - Action buttons: Edit, View, Copy, Delete, Share
- **What Happens**:
  - User can find specific forms
  - Can create new DPR from existing one
  - Can manage their DPRs

#### My Reports Page
- **What User Sees**:
  - List of all generated PDFs
  - For each PDF:
    - Associated business/form
    - Generation date
    - PDF preview thumbnail
    - File size
    - Language (English/Telugu)
    - Template used (basic/professional)
    - Action buttons: Download, Preview, Delete, Share, Email
  - Download all as ZIP option
- **What Happens**:
  - User can access all generated reports
  - Can download again anytime
  - Can share reports with banks via email

#### Account Settings Page
- **What User Sees**:
  - Profile section:
    - Name (editable)
    - Email (editable but requires verification)
    - Phone (editable)
    - Business type (editable)
  - Password section:
    - "Change Password" button
  - Preferences section:
    - Language preference
    - Email notifications checkbox
    - SMS notifications checkbox
  - Data & Privacy section:
    - Download my data button
    - Delete account button (with warning)
  - Save button for changes
- **What Happens**:
  - User can update account information
  - Can change password
  - Can manage notification preferences
  - Can request data export

#### Account Settings - Change Password Dialog
- **What User Sees**:
  - Current password field
  - New password field
  - Confirm new password field
  - Password strength indicator
  - "Update Password" button
- **What Happens**:
  - User enters current password (verified by backend)
  - Enters new password
  - Backend validates password strength
  - Password changed

---

### Help Pages (Stage 8)

#### Help/FAQ Page
- **What User Sees**:
  - Frequently asked questions organized by category:
    - Getting Started
    - Form Fields
    - AI Generation
    - Financial Models
    - PDF Download
    - Schemes & Subsidies
    - Technical Issues
  - Search box to find answers
  - Each FAQ expandable to show answer
  - Links to contact support
  - Video tutorials (if available)
- **What Happens**:
  - Users can self-serve common questions
  - Reduces support tickets

#### Contact Support Page
- **What User Sees**:
  - Support contact options:
    - Email form
    - Phone number
    - Chat form
    - FAQ link
  - Subject line
  - Message text area
  - File upload (for screenshots/documents)
  - Submit button
- **What Happens**:
  - User submits support request
  - Backend sends to support team
  - Support team responds

#### Tutorial/Guide Pages
- **What User Sees**:
  - Step-by-step guides for:
    - Creating first DPR
    - Understanding financial models
    - Accessing government schemes
    - Downloading and using PDF
  - Videos (if embedded)
  - Downloadable guides as PDFs
- **What Happens**:
  - Users learn how to use system

---

## 🗄️ PostgreSQL Database Schema

### Overview of Database Structure

The database is organized into **logical entity groups**:

1. **User Management Tables**: Store user accounts and authentication
2. **Form Management Tables**: Store DPR form data
3. **Generated Content Tables**: Store AI-generated text and PDFs
4. **Financial Data Tables**: Store calculations and projections
5. **Scheme Tables**: Store government scheme information
6. **Analytics Tables**: Track usage and metrics
7. **Audit Tables**: Track changes and deletions

---

### User Management Tables

#### Users Table
**Purpose**: Store basic user account information

**Data This Table Holds**:
- Unique user ID (primary identifier)
- Email address (unique, used for login)
- Full name
- Phone number
- Password (encrypted/hashed, never stored plain text)
- Business category/type
- State (Andhra Pradesh)
- Account creation date and time
- Last login date and time
- Account status (active, suspended, deleted)
- Preferred language (English, Telugu)

**Why This Structure**:
- Email is unique so no two accounts with same email
- Password encrypted for security
- Status field allows soft-delete (mark as deleted without removing)
- Timestamps help track account activity

**Example Data**: Email: "entrepreneur@example.com", Name: "Rajesh Kumar", Phone: "9999888877", State: "Andhra Pradesh", Created: "2025-01-15"

---

#### User Sessions Table
**Purpose**: Track active login sessions

**Data This Table Holds**:
- Session ID (unique identifier)
- User ID (links to Users table)
- Authentication token (JWT token)
- Login date and time
- Logout date and time (null if still logged in)
- Device type (web, mobile, tablet)
- IP address (for security)
- User agent/browser info

**Why This Structure**:
- Allows tracking multiple devices per user
- Can invalidate specific sessions on logout
- Helps detect suspicious access

---

#### User Profile Extensions Table
**Purpose**: Store additional user details

**Data This Table Holds**:
- User ID (links to Users table)
- Aadhar/ID number
- Pan card number (if applicable)
- Address (street, city, postal code)
- Years in business
- Business registration number
- GST registration number
- Date of birth
- Gender (optional)
- Profile photo URL (stored on Cloudinary)
- Bio/description

**Why This Structure**:
- Separates core user info from detailed profile
- Allows users to optionally provide more information
- Some fields may not be required for signup

---

### Form Management Tables

#### DPR Forms Table
**Purpose**: Store each DPR form as a record

**Data This Table Holds**:
- Form ID (unique identifier)
- User ID (links to user who created it)
- Form title/business name
- Business category
- Form status (draft, in-progress, completed, submitted)
- Completion percentage (0-100)
- Creation date and time
- Last modified date and time
- Submitted date (if submitted to bank)
- Is submitted flag (true/false)
- Notes from user

**Why This Structure**:
- Each user can have multiple forms
- Status helps track where form is in process
- Completion % helps in UI progress tracking
- Soft-delete by setting status instead of removing

**Example Data**: Form ID: "frm_12345", User ID: "usr_789", Status: "in-progress", Completion: "65%"

---

#### Form Entrepreneur Details Table
**Purpose**: Store entrepreneur personal information for a form

**Data This Table Holds**:
- Detail ID (unique identifier)
- Form ID (links to DPR form)
- Entrepreneur name
- Date of birth
- Aadhar number
- Address fields (street, city, postal code, state, country)
- Phone number
- Email address
- Years of business experience
- Previous business experience (description)

**Why This Structure**:
- Separate from user profile (user profile is account settings, this is DPR-specific)
- User might fill in different details for different DPRs
- Allows historical records of what was in submitted DPR

---

#### Form Business Details Table
**Purpose**: Store business information for a form

**Data This Table Holds**:
- Detail ID (unique identifier)
- Form ID
- Business name
- Business type (manufacturing, services, retail, etc.)
- Business description (text)
- Current annual revenue
- Number of current employees
- Current facility details
- Business registration details
- GST registration number
- Sector/industry classification

**Why This Structure**:
- Contains business-specific information
- Separate table allows form to focus on form-level data
- Business type helps in scheme matching and financial benchmarking

---

#### Form Product Details Table
**Purpose**: Store product/service information

**Data This Table Holds**:
- Detail ID
- Form ID
- Product/service name
- Description
- Key features/benefits (list)
- Target customer description
- Current production/service capacity
- Planned capacity increase
- Unique selling points
- Quality certifications (if any)

**Why This Structure**:
- Captures business offering details
- Used by AI for generating market section

---

#### Form Financial Details Table
**Purpose**: Store investment and financial information

**Data This Table Holds**:
- Detail ID
- Form ID
- Total investment amount
- Land/property cost
- Building/facility construction cost
- Machinery and equipment costs (with itemized breakdown)
- Furniture and fixtures cost
- IT and software licenses cost
- Initial working capital
- Initial inventory cost
- Other investment costs (allow user to add)
- Currency (INR)

**Why This Structure**:
- Centralizes all financial inputs
- Itemized breakdown helps AI understand business structure
- Used for financial modeling calculations

---

#### Form Revenue Assumptions Table
**Purpose**: Store user's revenue projections and assumptions

**Data This Table Holds**:
- Assumption ID
- Form ID
- Monthly revenue estimate (at full capacity)
- Seasonality factor (if business is seasonal, provide adjustment %)
- Expected growth rate per year (%)
- Ramp-up period (months to reach full capacity)
- Number of potential customers
- Average transaction/order value
- Market share target
- Pricing strategy notes

**Why This Structure**:
- Captures user's revenue assumptions
- Backend uses to calculate financial models
- Allows documenting business reasoning

---

#### Form Cost Details Table
**Purpose**: Store monthly operating cost information

**Data This Table Holds**:
- Cost ID
- Form ID
- Monthly fixed costs:
  - Rent/facility lease cost
  - Salaries and wages total
  - Utilities (electricity, water, etc.)
  - Insurance
  - Maintenance
  - License/permit fees
  - Other fixed costs (user can add)
- Monthly variable costs:
  - Raw materials/cost of goods
  - Packaging materials
  - Transportation/logistics
  - Sales commission
  - Distribution
  - Other variable costs (user can add)
- Total monthly cost (calculated)

**Why This Structure**:
- Separates fixed vs variable costs (important for financial analysis)
- Used for profitability calculations
- Helps identify cost structure

---

#### Form Staffing Details Table
**Purpose**: Store employment and staffing information

**Data This Table Holds**:
- Staffing ID
- Form ID
- Current number of employees
- Current staffing breakdown (roles, counts, salaries)
- Planned hiring over 3 years (Year 1, Year 2, Year 3 employee count)
- Skills required
- Training needs/plans
- Total monthly salary cost
- Benefits/perks cost

**Why This Structure**:
- Documents employment plans
- Used for financial modeling (salary is major cost)
- Helps with labour cost projections

---

#### Form Timeline Details Table
**Purpose**: Store implementation schedule

**Data This Table Holds**:
- Timeline ID
- Form ID
- Project start date
- Permitting/approval phase end date
- Construction/setup phase end date
- Equipment procurement end date
- Staff recruitment end date
- Training phase end date
- Operational launch date
- Milestones (with dates and descriptions)
- Critical path analysis

**Why This Structure**:
- Maps out when money will be spent
- Helps with cash flow projections
- Shows expected timeline to profitability

---

#### Form Loan Details Table
**Purpose**: Store loan request information

**Data This Table Holds**:
- Loan ID
- Form ID
- Requested loan amount
- Requested loan tenure (months)
- Interest rate assumption (%)
- Purpose of loan
- Proposed collateral description
- Collateral value
- Bank preferences (if any)
- Loan disbursement timeline

**Why This Structure**:
- Captures financing needs
- Backend calculates EMI (monthly payment)
- Helps identify applicable schemes

---

### Generated Content Tables

#### Generated DPR Content Table
**Purpose**: Store AI-generated content for each form

**Data This Table Holds**:
- Content ID (unique identifier)
- Form ID (links to form)
- Section name (executive_summary, market_analysis, risk_analysis, etc.)
- Generated text (the AI-generated content)
- AI model used (Gemini, version number)
- Generation date and time
- Confidence score (how good is the AI output, 0-100)
- User edited flag (true if user manually edited)
- User edit history (track what user changed)
- Version number (track iterations if regenerated)

**Why This Structure**:
- Stores all AI-generated sections
- Tracks versions if user asks to regenerate
- Records whether user edited

---

#### PDF Documents Table
**Purpose**: Store information about generated PDFs

**Data This Table Holds**:
- PDF ID (unique identifier)
- Form ID
- Generation date and time
- Language (English, Telugu)
- Template type used (basic, professional, bank-ready)
- PDF file name
- PDF file URL (stored on Cloudinary)
- File size (bytes)
- Sections included (which sections were in this PDF)
- Bank target (if submitting to specific bank)
- Submitted date (if submitted to bank)

**Why This Structure**:
- Records all generated PDFs
- Can regenerate same PDF format later if needed
- Can track which PDFs were submitted to banks

---

### Financial Data Tables

#### Financial Calculations Table
**Purpose**: Store calculated financial models

**Data This Table Holds**:
- Calculation ID
- Form ID
- Calculation date
- Breakeven point (months to profitability)
- ROI (Return on Investment %)
- Payback period (months to recover investment)
- NPV (Net Present Value)
- Profit margin %
- Cash flow status (positive/negative)
- Revenue year 1, 2, 3
- Expenses year 1, 2, 3
- Profit year 1, 2, 3

**Why This Structure**:
- Stores high-level financial metrics
- Used for financial summary in DPR
- Calculated from form financial details

---

#### Monthly Projections Table
**Purpose**: Store month-by-month financial projections

**Data This Table Holds**:
- Projection ID
- Form ID
- Month number (1-36 for 3 years)
- Month date
- Revenue projected
- Fixed costs projected
- Variable costs projected
- Profit/loss
- Cumulative profit/loss
- Cash balance
- Loan repayment amount (if applicable)
- Growth assumptions applied

**Why This Structure**:
- Detailed month-by-month breakdown
- Used to create financial tables in PDF
- Shows business trajectory over time

---

#### Sector Benchmarks Table
**Purpose**: Store industry average financial data

**Data This Table Holds**:
- Benchmark ID
- Sector/industry name
- Average profit margin (%)
- Average growth rate (%)
- Average payback period (months)
- Average ROI (%)
- Typical investment range
- Typical staff per ₹10L investment
- Typical revenue per ₹10L investment
- Data source
- Last updated date

**Why This Structure**:
- Reference data for comparisons
- Backend uses to validate user's assumptions
- Helps user understand if projections are realistic

---

### Scheme Tables

#### Government Schemes Table
**Purpose**: Store government scheme information

**Data This Table Holds**:
- Scheme ID (unique identifier)
- Scheme name
- Ministry/Department (which government body offers it)
- Scheme type (subsidy, loan guarantee, tax benefit, etc.)
- Subsidy/benefit amount or percentage
- Eligibility criteria description
- Eligible sectors/categories
- Eligible states (Andhra Pradesh, etc.)
- Eligible loan amount range
- Application process description
- Required documents list
- Processing time (days)
- Scheme official URL
- Contact details
- Application deadline (if applicable)
- Scheme active flag (true/false)
- Last updated date

**Why This Structure**:
- Central repository of scheme information
- Used for scheme matching
- Can be updated as schemes change

---

#### Form Scheme Selections Table
**Purpose**: Track which schemes user selected for their DPR

**Data This Table Holds**:
- Selection ID
- Form ID
- Scheme ID (links to scheme)
- Selection date
- Is included in final DPR flag
- Estimated subsidy amount for this business
- Notes from user about this scheme

**Why This Structure**:
- Records which schemes user chose
- Can have multiple schemes per form
- Tracks estimated benefit amounts

---

### Analytics Tables

#### User Activity Log Table
**Purpose**: Track user actions for analytics

**Data This Table Holds**:
- Activity ID
- User ID
- Activity type (form_created, form_saved, ai_generated, pdf_downloaded, etc.)
- Form ID (if applicable)
- Activity date and time
- Duration (how long user spent on section)
- Page/section name
- Device type
- IP address

**Why This Structure**:
- Records all user actions
- Can identify where users drop off (incomplete forms)
- Can measure performance

---

#### Form Completion Metrics Table
**Purpose**: Track completion rates for analytics

**Data This Table Holds**:
- Metric ID
- Form ID
- Total sections
- Completed sections
- Completion percentage
- Time spent (minutes)
- Sections abandoned (user started but didn't complete)
- Last active date
- Conversion status (completed to PDF or abandoned)

**Why This Structure**:
- Identifies bottlenecks in form
- Can see which sections users struggle with
- Helps optimize user experience

---

#### Platform Statistics Table
**Purpose**: Store aggregated platform-wide metrics

**Data This Table Holds**:
- Stat ID
- Date
- Total users registered
- Active users today/week/month
- Total forms created
- Total forms completed
- Total PDFs generated
- Total schemes recommended
- Total estimated credit unlocked
- Average form completion time
- Platform uptime %

**Why This Structure**:
- Summary metrics for dashboard
- Track platform growth
- Monitor performance

---

### Audit Tables

#### Change Audit Table
**Purpose**: Track what changed and when (for debugging)

**Data This Table Holds**:
- Audit ID
- Table affected (which table was changed)
- Record ID (which record was changed)
- Change type (create, update, delete)
- User who made change
- Change date and time
- Old value (what it was)
- New value (what it became)
- Reason for change (if recorded)

**Why This Structure**:
- Allows rolling back mistakes
- Compliance and audit trail
- Debugging (see what happened to data)

---

#### Soft Delete Records Table
**Purpose**: Store deleted records (not permanently removed)

**Data This Table Holds**:
- Deleted ID
- Original table name
- Original record ID
- Entire record data (as JSON)
- Deletion date and time
- User who deleted it
- Reason for deletion
- Can be restored flag

**Why This Structure**:
- Allows recovery of accidentally deleted data
- Maintains complete history
- Helps with compliance

---

## 📊 Data Flow Diagrams

### User Registration Flow

```
User Signup Page
    ↓ User fills form (name, email, password, business type)
    ↓ Frontend validates fields
    ↓ Frontend sends to POST /register endpoint
    ↓ Backend validates email not already registered
    ↓ Backend creates new user in Users table
    ↓ Backend creates user session in Sessions table
    ↓ Backend returns authentication token
    ↓ Frontend stores token
    ↓ User redirected to dashboard
    ↓ Dashboard fetches user profile from GET /user/profile
    ↓ Backend retrieves from Users + User Profile Extensions
    ↓ Dashboard displays user info
```

---

### DPR Creation Flow

```
User creates new DPR
    ↓ Frontend creates form via POST /form
    ↓ Backend creates record in DPR Forms table
    ↓ Backend returns Form ID
    ↓ Frontend redirects to form page

User fills Entrepreneur Details
    ↓ Frontend displays Entrepreneur Details Page
    ↓ User fills fields
    ↓ Frontend periodically saves via POST /form/{id}/entrepreneur
    ↓ Backend creates/updates record in Entrepreneur Details table
    ↓ Backend confirms save

User fills Business Details
    ↓ Similar save flow to Entrepreneur Details

User completes all sections
    ↓ User views form review page
    ↓ Frontend fetches complete form via GET /form/{id}
    ↓ Backend retrieves from all relevant tables
    ↓ Backend assembles into single response
    ↓ User clicks "Generate DPR"
```

---

### DPR Generation Flow

```
User clicks "Generate DPR"
    ↓ Frontend sends POST /generate-dpr/{form_id}
    ↓ Backend retrieves form data from database
    ↓
    ├─ AI Generation Process:
    │  ├─ Sends form data to Gemini API (Executive Summary)
    │  ├─ Backend stores response in Generated Content table
    │  ├─ Repeats for Market Analysis
    │  ├─ Repeats for Financial section intro
    │  └─ Repeats for Risk Analysis
    │
    ├─ Financial Calculation Process:
    │  ├─ Retrieves Financial Details from form
    │  ├─ Calculates month-by-month projections
    │  ├─ Stores in Monthly Projections table
    │  └─ Stores summary metrics in Calculations table
    │
    └─ Scheme Matching Process:
       ├─ Queries Schemes table by sector/investment/state
       ├─ Filters by eligibility
       ├─ Stores selections in Form Scheme Selections table
       └─ Calculates estimated subsidy amounts
    
    ↓ Backend responds with completion status
    ↓ Frontend redirects to preview page
    ↓ Frontend fetches preview data via GET /form/{id}/preview
    ↓ Backend assembles from all generated content
    ↓ Frontend displays to user
```

---

### PDF Generation Flow

```
User clicks "Generate PDF"
    ↓ Frontend sends POST /generate-pdf/{form_id}?language=English
    ↓ Backend retrieves:
    │  ├─ Form data (all sections)
    │  ├─ Generated AI content
    │  ├─ Financial models
    │  ├─ Scheme selections
    │  └─ User profile
    │
    ↓ Backend assembles into DPR structure:
    │  ├─ Executive Summary
    │  ├─ Entrepreneur Details
    │  ├─ Business Description
    │  ├─ Market Analysis
    │  ├─ Financial Projections (with tables)
    │  ├─ Implementation Plan
    │  ├─ Risk Analysis
    │  └─ Scheme Recommendations
    │
    ↓ Backend renders HTML with proper formatting
    ↓ Backend applies language (English or Telugu)
    ↓ Backend converts HTML → PDF using WeasyPrint
    ↓ Backend uploads PDF to Cloudinary
    ↓ Backend stores PDF info in PDF Documents table
    ↓ Backend returns download link
    ↓ Frontend provides download button
    ↓ User downloads PDF file
```

---

### Scheme Matching Flow

```
Backend receives request for schemes
    ↓ Extracts from form data:
    │  ├─ Business sector
    │  ├─ Investment amount
    │  ├─ Number of employees
    │  ├─ State (Andhra Pradesh)
    │  └─ Business type (new/existing)
    │
    ↓ Queries Schemes table with filters:
    │  ├─ WHERE eligible_sectors CONTAINS sector
    │  ├─ AND investment_range INCLUDES user_investment
    │  ├─ AND eligible_states CONTAINS state
    │  └─ AND scheme_active = true
    │
    ↓ For each matching scheme:
    │  ├─ Calculates estimated subsidy for user's investment
    │  ├─ Checks if user meets specific eligibility criteria
    │  └─ Calculates ranking score
    │
    ↓ Sorts by relevance/benefit
    ↓ Returns top 10-15 schemes with details
    ↓ User can select which to include in DPR
    ↓ Selections stored in Form Scheme Selections table
```

---

## 🔗 Integration Points

### Frontend → Backend Connections

**Every time frontend needs data**, it calls a backend route and waits for response:

1. **Authentication Flow**:
   - Login form → POST /auth/login
   - Signup form → POST /auth/register
   - Check session → GET /auth/verify

2. **Form Data Flow**:
   - Save section → POST/PUT /form/{id}/{section}
   - Get form → GET /form/{id}
   - List forms → GET /user/forms

3. **AI Generation Flow**:
   - Start generation → POST /generate-dpr/{id}
   - Poll status → GET /generate-dpr/{id}/status

4. **PDF Flow**:
   - Generate PDF → POST /pdf/generate/{id}
   - Download PDF → GET /pdf/{id}/download

5. **Schemes Flow**:
   - Get schemes → POST /schemes/match (sends form data)
   - Select schemes → POST /form/{id}/schemes (stores selection)

---

### Backend → Database Connections

**For every backend route**, it typically:

1. **Reads data**:
   - SELECT * FROM Users WHERE email = ?
   - SELECT * FROM DPR_Forms WHERE form_id = ?

2. **Writes data**:
   - INSERT INTO Users (name, email, ...) VALUES (...)
   - UPDATE DPR_Forms SET completion = ? WHERE form_id = ?

3. **Complex queries**:
   - JOIN form data with scheme eligibility criteria
   - Calculate financial projections using mathematical formulas

---

### Backend → External API Connections

**Backend also connects to external services**:

1. **Gemini AI API**:
   - Backend → Gemini: "Generate DPR executive summary for [business data]"
   - Gemini → Backend: Generated text

2. **Cloudinary Storage**:
   - Backend → Cloudinary: Upload PDF file
   - Cloudinary → Backend: File URL and metadata

3. **Email Service** (future):
   - Backend → Email Service: Send form link to user
   - Email Service → Backend: Confirmation

---

## 📝 Summary

### Database Contains:
- **User accounts and sessions** (who is using system)
- **Form data** (what user entered)
- **Generated AI content** (what Gemini created)
- **Financial calculations** (what we calculated)
- **Scheme information** (government schemes data)
- **PDF metadata** (what PDFs were generated)
- **Analytics** (how system is performing)
- **Audit trails** (what changed and when)

### Backend Provides:
- **Authentication** (login/logout)
- **Form management** (save/retrieve/delete forms)
- **AI integration** (call Gemini, manage content)
- **Financial processing** (calculate projections)
- **Scheme matching** (find eligible schemes)
- **PDF generation** (combine data into professional PDF)
- **Analytics** (track usage)

### Frontend Shows:
- **Pages for each step** (signup, form, review, generation, download)
- **Real-time feedback** (progress indicators, validation messages)
- **User management** (dashboard, settings, history)
- **Content display** (preview, edit, download)

---

**This architecture enables:**
✅ Multiple users creating multiple DPRs
✅ Complex financial calculations
✅ AI-powered content generation
✅ Professional PDF output
✅ Government scheme recommendations
✅ Complete audit trail
✅ Scalable to handle 5L+ users

*Architecture Design Complete — Ready for Development*
