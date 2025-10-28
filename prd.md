# Product Requirements Document (PRD)
## MSME DPR Generator Platform

---

## 📋 Project Overview

**Project Name**: MSME DPR Generator  
**Purpose**: AI-powered platform to help MSMEs create professional Detailed Project Reports (DPRs) for bank loan applications  
**Target Users**: Micro, Small, and Medium Enterprises (MSMEs) in Andhra Pradesh  
**Problem Solved**: 75% of MSME loan applications fail due to poor-quality DPRs; consultants charge ₹50,000+ per report

---

## 🎯 Core Objective

Enable MSMEs to generate bank-ready DPRs in 2 hours instead of 2 weeks, at ₹50 instead of ₹50,000, using AI-powered automation.

---

## 🛠️ Technology Stack

### Frontend (Located in `/frontend` folder)
- **Framework**: Next.js 14 with TypeScript
- **UI Library**: shadcn/ui (accessible component library)
- **Styling**: Tailwind CSS
- **Form Handling**: React Hook Form + Zod validation
- **State Management**: Zustand
- **Deployment**: Vercel

### Backend (Located in `/backend` folder)
- **Framework**: FastAPI (Python 3.11)
- **ORM**: Prisma (database operations)
- **Deployment**: Railway

### Database
- **Database**: PostgreSQL 15
- **Container**: Docker (via docker-compose.yml)
- **Management**: pgAdmin (included in docker-compose)
- **Connection**: Prisma Client for type-safe queries

### AI Integration
- **AI Provider**: Google Gemini API (for content generation)
- **Use Cases**: Executive summary, market analysis, risk assessment, SWOT generation

### Authentication
- **Method**: JWT tokens (JSON Web Tokens)
- **Security**: bcrypt for password hashing

---

## 📊 System Architecture

```
User Browser
    ↓
Next.js Frontend (Port 3000) - /frontend folder
    ↓ (HTTP REST API)
FastAPI Backend (Port 8000) - /backend folder
    ↓
PostgreSQL Database (Port 5432, Docker)
    ↓
Prisma ORM
```

**Project Structure**:
```
msme-hackathon/
├── frontend/          # Next.js application with shadcn/ui
├── backend/           # FastAPI application with Prisma
├── docker-compose.yml # PostgreSQL + pgAdmin setup
└── DPR Preparation Tool/ # DPR templates and essential notes
```

**External Integrations**:
- Gemini API (AI content generation)
- Cloudinary (file storage for PDFs and images)

---

## 🔐 User Roles

1. **Entrepreneur/MSME Owner**: Creates and manages DPR forms
2. **Admin** (future): Views analytics and manages platform

---

## 📝 Core Features & Functionality

### 1. User Authentication & Profile Management
**What it does**: Allows users to create accounts, login, and manage profiles

**Features**:
- User registration (name, email, phone, password, business type, state)
- Login with email/password
- JWT token-based session management
- Profile update (address, Aadhar, PAN, business details)
- Password reset via email
- Profile photo upload

---

### 2. DPR Form Creation & Management
**What it does**: Multi-section form to collect business information based on actual DPR templates

**Form Sections** (Based on `/DPR Preparation Tool` templates):

**Standard DPR Sections** (Common across all cluster types):
1. **Proposal Under Consideration**: Brief overview and project identification
2. **Brief Particulars**: Executive summary of the proposal
3. **Information About SPV**: Special Purpose Vehicle registration details
4. **Details of Project Promoter/Sponsors**: Entrepreneur background and credentials
5. **Eligibility as per MSE-CDP Guidelines**: Compliance verification
6. **Implementing Arrangements**: Project execution framework
7. **Management and Shareholding Details**: Governance structure
8. **Technical Aspects**: Production process, technology, machinery
9. **Implementation Schedule**: Timeline and milestones
10. **Project Components**: Detailed breakdown of hard and soft interventions
11. **Fund Requirement/Availability Analysis**: Financial structuring
12. **Usage Charges**: Revenue model for common facilities
13. **Commercial Viability**: Market analysis and demand assessment
14. **Financial Economic Viability**: Projections and feasibility
15. **Projected Performance**: Production, sales, employment targets
16. **Status of Government Approvals**: Regulatory compliance
17. **Favourable and Risk Factors**: Opportunity and risk identification
18. **SWOT Analysis**: Structured analysis (Strengths, Weaknesses, Opportunities, Threats)
19. **Risk Mitigation Framework**: Contingency planning
20. **Economics of the Project**: Cost-benefit analysis
21. **Commercial Viability**: Break-even and profitability
22. **Conclusion**: Summary and recommendations

**Cluster-Specific Sections** (As per template in `/DPR Preparation Tool`):

**For Manufacturing Clusters** (Coconut, Textile, Furniture, Gold Ornaments):
- Common Facility Center specifications
- Machinery and equipment list
- Raw material requirements
- Production capacity planning
- Quality testing facilities

**For Food Processing Cluster**:
- Medical diagnostic facilities (if health care)
- Processing technology details
- Storage and cold chain requirements
- Food safety certifications
- FSSAI compliance

**For Service Clusters** (Printing, Photo Frame):
- Design and CAD/CAM facilities
- Digital infrastructure
- Skill development programs
- Marketing and branding support

**Features**:
- Save form as draft (auto-save every 30 seconds)
- Edit saved forms
- View all user's forms (list view)
- Delete forms
- Track completion percentage (based on mandatory sections)
- Section-wise validation
- Cluster type selection (auto-loads relevant sections)
- Document upload for supporting evidence

---

### 3. AI-Powered Content Generation
**What it does**: Uses Gemini AI to write professional DPR sections based on templates in `/DPR Preparation Tool`

**Generated Sections** (According to DPR Essential Notes):

**Executive Summary**:
- Project at a glance (200-300 words)
- Key highlights and benefits
- Total investment and expected outcomes
- Alignment with MSE-CDP guidelines

**SWOT Analysis** (4 Quadrants):
- **Strengths**: Cluster advantages, existing capabilities
- **Weaknesses**: Current gaps and limitations
- **Opportunities**: Market potential, government schemes
- **Threats**: Competition, regulatory challenges

**Market Analysis**:
- Current market size and growth potential
- Target customer segments
- Competitive landscape
- Demand-supply gap analysis
- Market entry barriers
- Sector-specific trends

**Risk Analysis & Mitigation**:
- Identification of project risks (financial, operational, market)
- Risk severity assessment
- Mitigation strategies for each risk
- Contingency planning

**Implementation Strategy**:
- Phase-wise implementation plan
- Resource allocation timeline
- Key milestones and deliverables
- Success metrics and KPIs

**Business Description**:
- Detailed product/service description
- Production process explanation
- Technology and machinery requirements
- Quality standards and certifications

**Commercial Viability Assessment**:
- Break-even analysis
- Profitability projections
- Return on investment calculations
- Sustainability factors

**Features**:
- Generate all sections at once (complete DPR)
- Regenerate individual sections with user feedback
- View multiple versions of same section (version history)
- Edit AI-generated content manually (inline editing)
- Confidence score for each generated section (quality indicator)
- Sector-specific content generation (8+ cluster types supported)
- Template-based generation (follows MSE-CDP format)

---

### 4. Financial Modeling & Projections
**What it does**: Automatically calculates comprehensive financial projections based on DPR Essential Notes

**Calculations** (As per Financial Templates):

**Project Cost Analysis**:
- **Hard Interventions**: Infrastructure and equipment
  - Common Facility Center (building cost)
  - Machinery and equipment
  - Testing and quality control lab
  - Raw material bank/warehouse
  - Display center/showroom
  - IT infrastructure
  - Power backup systems
  - Effluent treatment plants
  
- **Soft Interventions**: Capacity building
  - Skill development training
  - Technology transfer programs
  - Marketing and branding
  - Product diversification
  - Design development
  - Quality certification support
  - Market linkage programs
  - E-commerce platform development
  - Export promotion
  - Cluster governance and management

**Financial Projections** (5-year detailed):
- Month-by-month revenue projections (60 months)
- Fixed costs and variable costs breakdown
- Profit/loss for each month
- Working capital requirements
- Depreciation calculations
- Tax computations

**Key Financial Ratios**:
- **Break-even Analysis**: When business becomes profitable
- **ROI (Return on Investment)**: Percentage return
- **Payback Period**: Months to recover investment
- **NPV (Net Present Value)**: Discounted cash flows
- **IRR (Internal Rate of Return)**: Project profitability rate
- **RoCE (Return on Capital Employed)**: Efficiency metric
- **Cost-Benefit Ratio**: Total benefits / Total costs

**Funding Structure**:
- Total project cost calculation
- Government grant percentage (varies by component)
- Beneficiary share calculation
- Per unit benefit distribution
- Employment generation (direct + indirect jobs)

**Sensitivity Analysis**:
- Revenue variation impact (+/- 10%, 20%)
- Cost escalation scenarios
- Interest rate changes
- Market demand fluctuations

**Features**:
- Uses sector-specific benchmarks (from DPR database)
- MSE-CDP guideline compliance (grant percentages)
- Automatic tax calculations
- Visual charts (revenue, profit, break-even, cash flow)
- Export financial tables to PDF and Excel
- Comparison with industry standards
- Validation against bank lending norms

---

### 5. Government Scheme Matching
**What it does**: Recommends eligible government schemes and subsidies

**Matching Criteria**:
- Business sector
- Investment amount
- Location (state)
- MSME category (micro/small/medium)

**Features**:
- Show 5-10 relevant schemes
- Display subsidy percentage and max amount
- Show eligibility criteria
- Link to scheme application portal
- Save selected schemes to DPR

---

### 6. PDF Generation & Download
**What it does**: Creates professional, bank-ready DPR document following templates in `/DPR Preparation Tool`

**PDF Structure** (Based on Actual DPR Templates):

**Cover Page**:
- Project title and business name
- Logo (if uploaded)
- Location and date
- SPV details
- "Detailed Project Report" header
- MSE-CDP compliance badge

**Table of Contents**:
- Automated page numbers for all sections
- Hyperlinked navigation
- Section and subsection hierarchy

**Chapter 1: Executive Summary**
- Project at a glance (key metrics table)
- Progress so far (if applicable)
- Schedule of implementation (summary)
- Investment highlights

**Chapter 2: Introduction**
- Preamble
- Micro & Small Industry Cluster Development Programme overview
- The specific cluster profile (e.g., "The Gold Ornaments Cluster at Jaggayyapeta")
- Gap assessment and rationale
- Summary of stakeholder views
- Financial assistance structure
- Structure of proposal

**Chapter 3: The Proposal**
- Name and location of the cluster
- Nature of activity and products
- Scale of investment
- Information on value of output
- Production process (with diagrams)
- Proposed intervention details
- Projected economics
- Diagnostic study/benchmark survey
- Elaboration of gaps
- Implementation schedule – SPV structuring
- Revenue generation model
- Project implementation schedule (Gantt chart)
- Monitorable targets – year-wise
- Sustainability of SPV
- Previous track record of SPV
- Benchmarking impact of CFC
- Utilization of CFC

**Chapter 4: Management & Shareholding Pattern**
- Management structure
- Brief bio-data of promoters
- List of SPV members (table format)

**Chapter 5: Common Facility Center Details**
- Need and market for proposed facility
- Applications and use cases
- Land and buildings specifications
- Raw material requirements
- List of machinery (detailed specifications)
- Other equipment
- Power and utilities
- List of suppliers
- Justification for selection of machinery

**Chapter 6: Analysis of Project Economics**
- Project cost and means of finance
- Assumptions on profitability
- Working capital requirement
- Depreciation schedule
- Profitability projections (5 years)
- Balance sheet and fund flow
- Break-even analysis
- Internal rate of return & RoCE
- Sensitivity analysis
- Risk and uncertainty assessment

**Chapter 7: Stakeholder Consultation & Meetings**
- Focus group discussions summary
- Individual meetings with stakeholders
- Stakeholder concerns and mitigation measures

**Chapter 8: Institutional, Project Monitoring & Financial Mechanisms**
- Institutional arrangements
- Committees structure
- Financial mechanisms

**Chapter 9: Profile of Implementing Agency**
- Organization background
- Experience and expertise
- Previous projects

**Chapter 10: SWOT Analysis**
- Detailed four-quadrant analysis
- Strategic recommendations

**Chapter 11: Risk Mitigation Framework**
- Risk identification matrix
- Mitigation strategies
- Contingency planning

**Chapter 12: Government Schemes**
- Matched schemes (with eligibility criteria)
- Subsidy calculations
- Application procedures

**Chapter 13: Conclusion**
- Summary of viability
- Recommendations
- Next steps

**Annexures**:
- Cluster unit list (table)
- SPV registration documents
- Survey questionnaires
- Quotations and estimates
- Maps and layouts
- Photographs of cluster units
- Supporting documents

**Features**:
- Generate PDF in English or Telugu
- Professional templates matching bank standards
- Multiple format options:
  - **Basic**: Essential sections only
  - **Detailed**: All sections included
  - **Bank-Ready**: Full compliance format with all annexures
- Download PDF (optimized file size)
- Preview PDF in browser (embedded viewer)
- Share PDF via secure link
- Email PDF to user
- Watermark options (Draft/Final)
- Digital signature support
- Version control (track revisions)
- Automatic page numbering and cross-references

---

### 7. User Dashboard & Analytics
**What it does**: Shows user's activity and progress

**User Dashboard**:
- Total forms created
- Completed vs. in-progress forms
- Total PDFs generated
- Time spent on platform
- Estimated credit accessed (loan amounts)

---

## 🔌 Backend API Routes

### Authentication Routes (`/auth`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | User login (returns JWT token) |
| POST | `/auth/logout` | End user session |
| GET | `/auth/verify` | Check if token is valid |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |

---

### User Profile Routes (`/user`)

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/user/profile` | Get user profile |
| PUT | `/user/profile` | Update user profile |
| POST | `/user/profile/photo` | Upload profile photo |
| PUT | `/user/change-password` | Change password |
| DELETE | `/user/account` | Delete account |

---

### Form Management Routes (`/form`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/form/create` | Create new DPR form |
| GET | `/form/{form_id}` | Get complete form data |
| PUT | `/form/{form_id}` | Update entire form |
| PUT | `/form/{form_id}/section/{section_name}` | Update specific section |
| GET | `/user/forms` | List all user's forms |
| DELETE | `/form/{form_id}` | Delete form |
| GET | `/form/{form_id}/progress` | Get completion percentage |

---

### AI Processing Routes (`/ai`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/ai/generate-dpr/{form_id}` | Generate all DPR sections |
| POST | `/ai/generate-section/{form_id}/{section}` | Generate single section |
| POST | `/ai/regenerate-section/{form_id}/{section}` | Regenerate with feedback |
| GET | `/ai/history/{form_id}/{section}` | Get all versions of section |
| GET | `/ai/status/{form_id}` | Check generation progress |

---

### Financial Routes (`/financial`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/financial/calculate/{form_id}` | Calculate financial projections |
| GET | `/financial/projections/{form_id}` | Get monthly projections |
| GET | `/financial/summary/{form_id}` | Get financial summary (ROI, NPV, etc.) |
| GET | `/financial/report/{form_id}` | Get detailed financial report |

---

### Scheme Routes (`/schemes`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/schemes/match/{form_id}` | Find matching government schemes |
| GET | `/schemes/{scheme_id}` | Get scheme details |
| POST | `/schemes/select/{form_id}` | Save selected schemes to form |
| GET | `/schemes/all` | Get all available schemes |

---

### PDF Routes (`/pdf`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/pdf/generate/{form_id}` | Generate PDF from form |
| GET | `/pdf/{pdf_id}/download` | Download PDF file |
| GET | `/pdf/{pdf_id}/preview` | Preview PDF in browser |
| GET | `/pdf/history/{form_id}` | Get all PDFs for form |
| DELETE | `/pdf/{pdf_id}` | Delete PDF |
| POST | `/pdf/email/{pdf_id}` | Email PDF to user |

---

### Analytics Routes (`/analytics`)

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/analytics/user-stats` | Get user's dashboard stats |
| GET | `/analytics/platform-stats` | Get platform-wide stats (admin) |
| POST | `/analytics/track-activity` | Log user activity |

---

## 🗄️ Database Schema (PostgreSQL + Prisma)

### Table 1: `users`
**Purpose**: Store user accounts

**Columns**:
- `id` (Primary Key, Auto-increment)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `phone`
- `business_type` (e.g., "Manufacturing", "Services")
- `state`
- `created_at` (Timestamp)
- `last_login` (Timestamp)

---

### Table 2: `user_profiles`
**Purpose**: Extended user information

**Columns**:
- `id` (Primary Key)
- `user_id` (Foreign Key → users)
- `address`
- `aadhar_number`
- `pan_number`
- `years_in_business`
- `profile_photo_url`
- `bio`

---

### Table 3: `dpr_forms`
**Purpose**: Main DPR form data

**Columns**:
- `id` (Primary Key)
- `user_id` (Foreign Key → users)
- `business_name`
- `status` (draft, generating, completed)
- `completion_percentage` (0-100)
- `created_at`
- `last_modified`

---

### Table 4: `entrepreneur_details`
**Purpose**: Entrepreneur section of form

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `full_name`
- `date_of_birth`
- `education`
- `years_of_experience`
- `previous_business_experience`
- `technical_skills`

---

### Table 5: `business_details`
**Purpose**: Business information section

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `business_name`
- `sector` (food, textiles, IT, etc.)
- `sub_sector`
- `legal_structure` (proprietorship, partnership, LLP, Pvt Ltd)
- `registration_number`
- `location` (city/district)
- `address`

---

### Table 6: `product_details`
**Purpose**: Product/service information

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `product_name`
- `description`
- `key_features` (JSON array)
- `target_customers`
- `current_capacity`
- `planned_capacity`
- `unique_selling_points`
- `quality_certifications`

---

### Table 7: `financial_details`
**Purpose**: Investment and cost breakdown

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `total_investment_amount`
- `land_cost`
- `building_cost`
- `machinery_cost`
- `working_capital`
- `other_costs`
- `own_contribution`
- `loan_required`

---

### Table 8: `revenue_assumptions`
**Purpose**: Revenue projections input

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `product_price`
- `monthly_sales_quantity_year1`
- `monthly_sales_quantity_year2`
- `monthly_sales_quantity_year3`
- `growth_rate_percentage`

---

### Table 9: `cost_details`
**Purpose**: Operating costs

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `raw_material_cost_monthly`
- `labor_cost_monthly`
- `utilities_cost_monthly`
- `rent_monthly`
- `marketing_cost_monthly`
- `other_fixed_costs_monthly`

---

### Table 10: `staffing_details`
**Purpose**: Employee information

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `total_employees`
- `management_count`
- `technical_staff_count`
- `support_staff_count`
- `average_salary`

---

### Table 11: `timeline_details`
**Purpose**: Implementation plan

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `land_acquisition_months`
- `construction_months`
- `machinery_installation_months`
- `trial_production_months`
- `commercial_production_start_month`

---

### Table 12: `generated_content`
**Purpose**: AI-generated DPR sections

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `section_name` (executive_summary, market_analysis, etc.)
- `generated_text`
- `ai_model_used` (e.g., "gemini-pro")
- `confidence_score` (0-100)
- `version_number`
- `user_edited` (boolean)
- `generated_at` (Timestamp)

---

### Table 13: `financial_projections`
**Purpose**: Calculated monthly projections

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `month_number` (1-36)
- `revenue`
- `fixed_costs`
- `variable_costs`
- `profit_loss`
- `cumulative_profit_loss`

---

### Table 14: `financial_summary`
**Purpose**: Key financial metrics

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `breakeven_months`
- `roi_percentage`
- `payback_period_months`
- `npv`
- `profit_margin_percentage`
- `calculated_at` (Timestamp)

---

### Table 15: `schemes`
**Purpose**: Government schemes database

**Columns**:
- `id` (Primary Key)
- `scheme_name`
- `ministry`
- `scheme_type` (subsidy, loan, training, etc.)
- `description`
- `subsidy_percentage`
- `max_subsidy_amount`
- `eligible_sectors` (JSON array)
- `eligible_states` (JSON array)
- `min_investment`
- `max_investment`
- `eligibility_criteria`
- `application_link`

---

### Table 16: `selected_schemes`
**Purpose**: Schemes chosen for each DPR

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `scheme_id` (Foreign Key → schemes)
- `selected_at` (Timestamp)

---

### Table 17: `pdf_documents`
**Purpose**: Generated PDF metadata

**Columns**:
- `id` (Primary Key)
- `form_id` (Foreign Key → dpr_forms)
- `file_url` (Cloudinary URL)
- `file_name`
- `file_size`
- `language` (english, telugu)
- `template_type` (basic, professional, bank-ready)
- `generated_at` (Timestamp)
- `download_count`

---

### Table 18: `user_activity_log`
**Purpose**: Track user actions for analytics

**Columns**:
- `id` (Primary Key)
- `user_id` (Foreign Key → users)
- `activity_type` (form_created, pdf_generated, etc.)
- `form_id` (Foreign Key, nullable)
- `timestamp`
- `device_type` (web, mobile)

---

## 🔄 User Journey Flow

### Journey 1: First-Time User Creating DPR

1. **Register** → User creates account (email, password, business type)
2. **Login** → User logs in, receives JWT token
3. **Create Form** → User clicks "Create New DPR"
4. **Fill Sections** → User fills entrepreneur, business, financial sections (can save draft anytime)
5. **Generate Content** → User clicks "Generate DPR" → Gemini AI creates executive summary, market analysis, risk analysis
6. **Review & Edit** → User reviews AI content, can regenerate or edit manually
7. **Calculate Financials** → System auto-calculates 3-year projections, ROI, break-even
8. **Match Schemes** → System recommends 5-10 government schemes based on business details
9. **Generate PDF** → User clicks "Download PDF" → System creates professional DPR document
10. **Download** → User downloads PDF for bank submission

**Time**: 30 minutes to 2 hours  
**Cost**: ₹50 (vs. ₹50,000 consultant fee)

---

### Journey 2: Returning User Editing Existing DPR

1. **Login** → User logs in
2. **View Forms** → User sees list of all saved DPRs
3. **Select Form** → User opens existing form
4. **Edit Section** → User updates financial details or business description
5. **Regenerate** → User regenerates AI content with new data
6. **Download Updated PDF** → User gets updated PDF

---

## 🔐 Security & Authentication

**Authentication Method**: JWT (JSON Web Tokens)

**Flow**:
1. User logs in with email/password
2. Backend verifies credentials
3. Backend generates JWT token (contains user_id, email, expiry)
4. Frontend stores token (localStorage or cookies)
5. Every API request includes token in `Authorization: Bearer <token>` header
6. Backend validates token before processing request

**Security Measures**:
- Passwords hashed using bcrypt
- Tokens expire after 24 hours
- HTTPS for all API calls
- CORS enabled only for frontend domain
- Input validation on all forms
- SQL injection prevention (Prisma ORM)

---

## 🎨 Frontend Pages & Components

### Page 1: Landing Page (`/`)
**Purpose**: Introduce platform to visitors

**Components**:
- Hero section with value proposition
- "How It Works" (3-step process)
- Features showcase
- Pricing (free tier, ₹50 per DPR)
- Testimonials
- "Get Started" button → Signup

---

### Page 2: Signup Page (`/signup`)
**Purpose**: User registration

**Form Fields**:
- Full name
- Email
- Phone
- Password (with strength indicator)
- Business type (dropdown)
- State (dropdown)
- Terms & conditions checkbox

**Action**: Submit → Create account → Redirect to login

---

### Page 3: Login Page (`/login`)
**Purpose**: User authentication

**Form Fields**:
- Email
- Password
- "Forgot Password?" link

**Action**: Submit → Receive JWT token → Redirect to dashboard

---

### Page 4: Dashboard (`/dashboard`)
**Purpose**: User's main control panel

**Sections**:
- Welcome message ("Hello, [Name]")
- Statistics cards:
  - Total Forms Created
  - Completed Forms
  - PDFs Downloaded
  - Time Spent
- "Create New DPR" button (prominent)
- List of recent forms (with status: draft, completed)
- Quick actions (view profile, logout)

---

### Page 5: DPR Form Page (`/form/[id]`)
**Purpose**: Multi-step form to collect business data

**Layout**: Tabbed interface with sections:

**Tab 1: Entrepreneur Details**
- Name, DOB, education, experience, skills

**Tab 2: Business Details**
- Business name, sector, legal structure, location

**Tab 3: Product/Service**
- Product name, description, features, USP, certifications

**Tab 4: Market Analysis**
- Target customers, market size, competitors, demand

**Tab 5: Financial Details**
- Investment breakdown (land, building, machinery, working capital)
- Revenue assumptions (price, quantity, growth rate)
- Cost details (raw materials, labor, utilities, rent)

**Tab 6: Staffing**
- Number of employees by role
- Salary structure

**Tab 7: Timeline**
- Implementation milestones (land acquisition, construction, production start)

**Tab 8: Loan Requirements**
- Loan amount, own contribution, repayment terms

**Features**:
- Progress bar (% completion)
- Auto-save every 30 seconds
- "Save Draft" button
- "Generate DPR" button (enabled when 80%+ complete)
- Form validation (real-time error messages)

---

### Page 6: DPR Generation Page (`/generate/[id]`)
**Purpose**: Shows AI generation progress

**UI**:
- Loading spinner
- Progress messages:
  - "Analyzing your business data..."
  - "Generating Executive Summary..."
  - "Creating Market Analysis..."
  - "Calculating Financial Projections..."
  - "Matching Government Schemes..."
  - "Finalizing Document..."
- Estimated time remaining
- Cancel button

**Action**: After completion → Redirect to preview page

---

### Page 7: DPR Preview Page (`/preview/[id]`)
**Purpose**: Review generated DPR before download

**Layout**:
- Left sidebar: Table of contents (clickable sections)
- Main area: DPR content with sections:
  - Executive Summary (AI-generated)
  - Business Details (from form)
  - Market Analysis (AI-generated)
  - Financial Projections (tables + charts)
  - Risk Analysis (AI-generated)
  - Government Schemes (matched schemes)

**Actions**:
- Edit section (opens modal to regenerate or manually edit)
- "Regenerate Section" (with feedback option)
- "Download PDF" button
- "Save & Exit" button

---

### Page 8: PDF Download Page (`/download/[pdf_id]`)
**Purpose**: Download completed DPR

**UI**:
- PDF preview (embedded viewer)
- Download button
- Language toggle (English/Telugu)
- Template selector (Basic, Professional, Bank-Ready)
- Email PDF option
- Share link option

---

### Page 9: User Profile Page (`/profile`)
**Purpose**: Manage account settings

**Sections**:
- Profile photo upload
- Edit profile (name, phone, address, Aadhar, PAN)
- Change password
- Delete account (with confirmation)

---

### Page 10: Forms List Page (`/forms`)
**Purpose**: View all user's DPRs

**UI**:
- Grid/list view of forms
- Each card shows:
  - Business name
  - Status (draft, completed)
  - Last modified date
  - Progress percentage
- Actions: Edit, Delete, Download PDF
- Filter: All, Draft, Completed
- Sort: Date, Name

---

## 🤖 AI Integration (Gemini API)

### How It Works:

1. **User completes form** → Frontend sends form data to backend
2. **Backend receives data** → Extracts business details, sector, investment, location
3. **Backend constructs prompts** for each section:
   - "Write a professional executive summary for a [sector] business in [location] with ₹[investment] investment..."
   - "Analyze market potential for [product] in [location] sector..."
   - "Identify risks for a [sector] business and suggest mitigation strategies..."
4. **Backend calls Gemini API** → Sends prompt, receives AI-generated text
5. **Backend stores content** → Saves to `generated_content` table
6. **Frontend displays content** → User can review, edit, regenerate

---

### Example Prompts:

**Executive Summary Prompt**:
```
Write a 200-word professional executive summary for a business plan with these details:
- Business Name: [name]
- Sector: [sector]
- Investment: ₹[amount]
- Location: [city]
- Product: [description]
- Target Market: [customers]
```

**Market Analysis Prompt**:
```
Write a 300-word market analysis for a [sector] business in [location]:
- Current market size
- Growth potential
- Competition overview
- Customer demand trends
- Market entry barriers
```

---

## 🧮 Financial Modeling Logic

### Input Data (from form):
- Total investment: ₹10,00,000
- Monthly revenue (Year 1): ₹2,00,000
- Monthly revenue (Year 2): ₹2,50,000
- Monthly revenue (Year 3): ₹3,00,000
- Fixed costs (monthly): ₹50,000
- Variable costs (% of revenue): 40%

### Calculation Steps:

**For each month (1-36)**:
1. Calculate revenue (based on year)
2. Calculate variable costs = Revenue × 40%
3. Calculate total costs = Fixed costs + Variable costs
4. Calculate profit/loss = Revenue - Total costs
5. Calculate cumulative profit/loss = Previous cumulative + Current profit/loss

**Summary Metrics**:
- **Break-even month**: First month where cumulative profit > 0
- **ROI**: (Total profit after 3 years / Total investment) × 100
- **Payback period**: Months until cumulative profit = investment
- **NPV**: Discounted future cash flows

---

## 🎯 Government Scheme Matching Logic

### Matching Algorithm:

**Step 1**: Filter schemes by sector
- If business sector = "Food Processing" → Show schemes tagged with "Food Processing"

**Step 2**: Filter by investment range
- If investment = ₹10,00,000 → Show schemes with min_investment ≤ ₹10,00,000 AND max_investment ≥ ₹10,00,000

**Step 3**: Filter by state
- If state = "Andhra Pradesh" → Show schemes eligible in AP

**Step 4**: Rank by subsidy amount
- Sort by `subsidy_percentage` (highest first)

**Step 5**: Return top 10 matches

**Example Output**:
```
1. PMEGP (Prime Minister Employment Generation Programme)
   - Subsidy: 25% (max ₹2,50,000)
   - Eligible: Manufacturing, All states
   
2. MSME Technology Upgradation Scheme
   - Subsidy: 15% (max ₹1,50,000)
   - Eligible: Manufacturing, All states
```

---

## 📄 PDF Generation Process

### PDF Structure:

1. **Cover Page**
   - Business name
   - Logo (if uploaded)
   - Date
   - "Detailed Project Report"

2. **Table of Contents**
   - Page numbers for each section

3. **Section 1: Executive Summary**
   - AI-generated 200-word overview

4. **Section 2: Entrepreneur Profile**
   - Name, education, experience (from form)

5. **Section 3: Business Description**
   - Product/service details (from form)

6. **Section 4: Market Analysis**
   - AI-generated market assessment

7. **Section 5: Financial Projections**
   - 3-year revenue table
   - Profit/loss table
   - Break-even chart
   - ROI calculation

8. **Section 6: Implementation Timeline**
   - Gantt chart of milestones

9. **Section 7: Risk Analysis**
   - AI-generated risk identification + mitigation

10. **Section 8: Government Schemes**
    - List of matched schemes with details

11. **Appendices**
    - Uploaded documents (if any)

---

### PDF Generation Flow:

1. User clicks "Download PDF"
2. Backend retrieves:
   - Form data (from database)
   - AI-generated content (from `generated_content` table)
   - Financial projections (from `financial_projections` table)
   - Matched schemes (from `selected_schemes` table)
3. Backend assembles HTML template
4. Backend converts HTML → PDF (using Python library like WeasyPrint or ReportLab)
5. Backend uploads PDF to Cloudinary
6. Backend saves PDF metadata to `pdf_documents` table
7. Backend returns PDF URL to frontend
8. Frontend triggers download

---

## 🚀 Deployment Architecture

### Frontend (Next.js):
- **Host**: Vercel
- **Process**: 
  - Push code to GitHub
  - Vercel auto-deploys on git push
  - Environment variables set in Vercel dashboard
- **URL**: `https://your-app.vercel.app`

### Backend (FastAPI):
- **Host**: Railway
- **Process**:
  - Push code to GitHub
  - Railway auto-deploys on git push
  - Environment variables set in Railway dashboard
- **URL**: `https://your-app.up.railway.app`

### Database (PostgreSQL):
- **Host**: Docker (local development)
- **Production**: Railway PostgreSQL service
- **Access**: 
  - Local: `localhost:5432`
  - Production: Railway-provided URL

### Docker Compose (for local development):
- Runs PostgreSQL container
- Runs pgAdmin container (database management UI)
- Accessed via `docker-compose up`

---

## 🔧 Environment Variables

### Backend `.env`:
```
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/msme_dpr
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_for_jwt
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### Frontend `.env`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000 (or production backend URL)
```

---

## ✅ Success Metrics

**User Success**:
- Form completion rate > 80%
- DPR generation success rate > 95%
- Average time to complete form < 2 hours
- PDF quality rated 4.5+ stars

**Business Success**:
- 1,000 MSMEs create DPRs in first 3 months
- 50% of users download PDF
- 30% of DPRs result in successful loan applications

**Technical Success**:
- API response time < 500ms
- AI generation time < 60 seconds
- PDF generation time < 30 seconds
- Platform uptime > 99.5%

---

## 🎯 MVP Scope (Hackathon Deliverable)

**Must-Have Features**:
1. ✅ User registration + login (JWT)
2. ✅ DPR form (all 8 sections)
3. ✅ AI content generation (executive summary, market analysis)
4. ✅ Basic financial projections (3-year)
5. ✅ Scheme matching (5+ schemes)
6. ✅ PDF generation (English)
7. ✅ Download PDF

**Can Skip in MVP**:
- Telugu language support
- Advanced charts/visualizations
- Email notifications
- Profile photo upload
- Multiple PDF templates

---

## 📋 Summary for Taskmaster MCP

**Project**: MSME DPR Generator  
**Goal**: Enable MSMEs to create professional DPRs using AI based on actual MSE-CDP templates

**Tech Stack**:
- Frontend: Next.js + TypeScript + shadcn/ui (in `/frontend` folder)
- Backend: FastAPI + Python (in `/backend` folder)
- Database: PostgreSQL + Docker + Prisma
- AI: Gemini API

**Project Structure**:
```
msme-hackathon/
├── frontend/              # Next.js with shadcn/ui components
│   ├── src/
│   │   ├── app/          # Next.js 14 app directory
│   │   ├── components/   # shadcn/ui components
│   │   └── lib/          # Utilities and helpers
│   └── package.json
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── routes/       # API endpoints
│   │   ├── models/       # Prisma models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Helper functions
│   ├── prisma/
│   │   └── schema.prisma # Database schema
│   └── requirements.txt
├── docker-compose.yml     # PostgreSQL + pgAdmin
├── DPR Preparation Tool/  # Template references
│   ├── DPR_ESSENTIAL_NOTES.txt
│   ├── note.txt          # Cluster type specifications
│   └── DPR Template.pdf  # Reference templates
└── Information_about_Project/  # Additional documentation

```

**Supported Cluster Types** (from `/DPR Preparation Tool/note.txt`):
1. **Coconut Cluster**: Processing and value addition
2. **Textile Cluster**: Designing & weaving of sarees
3. **Printing Cluster**: Commercial printing services
4. **Food Processing Cluster**: Health care and food products
5. **Furniture Manufacturing**: Wooden furniture production
6. **Gold Ornaments/Goldsmiths**: Jewelry manufacturing
7. **Photo Frame Cluster**: Frame manufacturing
8. **Pulses & Pulses Products**: Processing and packaging

**Core Flow**:
1. User selects cluster type (auto-loads relevant DPR sections)
2. User fills 22 standard DPR sections (based on MSE-CDP template)
3. AI generates executive summary, SWOT, market analysis, risk assessment
4. System calculates comprehensive financial projections (hard + soft interventions)
5. System matches applicable government schemes (MSE-CDP guidelines)
6. System generates professional PDF (13 chapters + annexures)
7. User downloads bank-ready DPR document

**Database**: 18 tables (users, forms, financials, schemes, PDFs, analytics)  
**API Routes**: 40+ endpoints (auth, forms, AI, financials, schemes, PDFs)  
**Deployment**: Vercel (frontend) + Railway (backend) + Docker (local DB)

**Key Differentiators**:
- Based on actual MSE-CDP DPR templates (in `/DPR Preparation Tool`)
- Supports 8+ cluster types with specific requirements
- Follows government guidelines (MSE-CDP w.e.f 24 May 2022)
- Generates 13-chapter comprehensive DPR
- Includes hard and soft intervention calculations
- SPV (Special Purpose Vehicle) management support
- Stakeholder consultation documentation
- Compliance with bank lending norms

**Reference Documents** (Available in project):
- `/DPR Preparation Tool/DPR_ESSENTIAL_NOTES.txt`: Critical fields and requirements
- `/DPR Preparation Tool/note.txt`: Cluster type specifications
- `/Information_about_Project/`: Additional project documentation and guidelines

**Outcome**: 
- 75% reduction in DPR cost
- 90% reduction in time (6 weeks → 2 hours)
- 50% increase in loan approval rates
- MSE-CDP compliance guaranteed
- Bank-ready professional output

---

This PRD provides a complete, simple, and understandable overview of the project for implementation planning.
