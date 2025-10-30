"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import "./pdf-styles.css";

// Backend interfaces matching exact snake_case response structure
interface EntrepreneurDetails {
  full_name: string;
  date_of_birth: string;
  gender: string;
  category: string;
  pwd: boolean;
  education: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  email: string;
  aadhaar_number: string;
  pan_number: string;
  years_of_experience: number;
  technical_skills: string;
  previous_entrepreneurial_experience: string;
}

interface BusinessDetails {
  business_name: string;
  sector: string;
  sub_sector: string;
  business_type: string;
  legal_structure: string;
  registration_number: string | null;
  location: string;
  establishment_date: string | null;
  number_of_employees: number;
  ownership_percentage: number;
  business_model: string;
}

interface ProductDetails {
  product_name: string;
  product_description: string;
  product_category: string;
  unique_selling_points: string;
  stage_of_development: string;
  intellectual_property: string | null;
  certifications: string | null;
  target_market: string;
  market_size: string;
  competitors: string;
  competitive_advantage: string;
}

interface FinancialDetails {
  total_investment_amount: string;
  land_cost: string;
  building_cost: string;
  machinery_cost: string;
  other_fixed_capital: string;
  working_capital: string;
  own_contribution: string;
  loan_required: string;
  other_funding_sources: string | null;
  break_even_period: string;
  bank_name: string | null;
  bank_account_number: string | null;
  ifsc_code: string | null;
  existing_loans: string | null;
  credit_history: string | null;
}

interface RevenueAssumptions {
  year_1_revenue: string;
  year_2_revenue: string;
  year_3_revenue: string;
  year_1_units: number;
  year_2_units: number;
  year_3_units: number;
  price_per_unit: string;
  revenue_growth_assumptions: string;
  seasonal_factors: string | null;
}

interface CostDetails {
  raw_material_cost: string;
  labor_cost: string;
  overhead_cost: string;
  other_operational_costs: string;
  cost_growth_assumptions: string;
}

interface StaffingDetails {
  number_of_employees: number;
  key_positions: string;
  salary_structure: string;
  training_requirements: string | null;
}

interface TimelineDetails {
  project_start_date: string;
  expected_completion_date: string;
  key_milestones: string;
  critical_dependencies: string | null;
}

interface GeneratedContent {
  sections: {
    [key: string]: string;
  };
  generated_at: string;
}

interface FinancialSummary {
  form_id: number;
  business_name: string;
  breakeven_months: number;
  roi_percentage: number;
  payback_period_months: number;
  npv: number;
  profit_margin_percentage: number;
  calculated_at: string;
}

interface FormData {
  id: number;
  user_id: number;
  business_name: string;
  status: string;
  completion_percentage: number;
  created_at: string;
  last_modified: string;
  entrepreneur_details?: EntrepreneurDetails;
  business_details?: BusinessDetails;
  product_details?: ProductDetails;
  financial_details?: FinancialDetails;
  revenue_assumptions?: RevenueAssumptions;
  cost_details?: CostDetails;
  staffing_details?: StaffingDetails;
  timeline_details?: TimelineDetails;
  generated_content?: GeneratedContent;
}

const PDFPage = () => {
  const params = useParams();
  const formId = params.id;
  const [formData, setFormData] = useState<FormData | null>(null);
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        
        // Build headers - token is optional for PDF generation
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };
        
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        // Fetch complete form data
        const formResponse = await fetch(
          `http://localhost:8000/api/form/${formId}/complete`,
          { headers }
        );

        if (!formResponse.ok) {
          throw new Error(`Failed to fetch form data: ${formResponse.status}`);
        }

        const formDataResponse = await formResponse.json();
        console.log("📋 Complete Form Data:", formDataResponse);
        console.log("👤 Entrepreneur Details:", formDataResponse.entrepreneur_details);
        console.log("🏢 Business Details:", formDataResponse.business_details);
        console.log("📦 Product Details:", formDataResponse.product_details);
        console.log("💰 Financial Details:", formDataResponse.financial_details);
        console.log("📊 Revenue Assumptions:", formDataResponse.revenue_assumptions);
        console.log("💵 Cost Details:", formDataResponse.cost_details);
        setFormData(formDataResponse);

        // Fetch financial summary - this is optional
        try {
          const financialResponse = await fetch(
            `http://localhost:8000/api/financial/${formId}/summary`,
            { headers }
          );

          if (financialResponse.ok) {
            const financialData = await financialResponse.json();
            console.log("📈 Financial Summary:", financialData);
            setFinancialSummary(financialData);
          }
          // Don't throw error if financial summary doesn't exist
        } catch (finErr) {
          console.log("Financial summary not available:", finErr);
          // This is non-critical, continue without financial data
        }
      } catch (err: any) {
        console.error("Error fetching data:", err);
        setError(err.message || "Failed to load data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [formId]);

  if (loading) {
    return (
      <div className="pdf-loading">
        <div className="pdf-spinner"></div>
        <p>Loading DPR Data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pdf-error">
        <h2>Error Loading DPR</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="pdf-error">
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div className="pdf-container">
      {/* Cover Page */}
      <div className="pdf-page pdf-cover-page">
        <div className="pdf-cover-content">
          <h1 className="pdf-cover-title">
            Detailed Project Report (DPR)
          </h1>
          <h2 className="pdf-cover-subtitle">
            {formData.business_details?.business_name || formData.business_name}
          </h2>
          <div className="pdf-cover-info">
            <p><strong>Prepared for:</strong> {formData.entrepreneur_details?.full_name || "N/A"}</p>
            <p><strong>Date:</strong> {new Date(formData.created_at).toLocaleDateString("en-IN")}</p>
            <p><strong>DPR Reference:</strong> DPR-{formId}</p>
          </div>
        </div>
      </div>

      {/* Table of Contents */}
      {/* <div className="pdf-page">
        <h1 className="pdf-section-title">Table of Contents</h1>
        <div className="pdf-toc">
          <div className="pdf-toc-item">
            <span>1. Executive Summary</span>
            <span className="pdf-toc-dots"></span>
            <span>3</span>
          </div>
          <div className="pdf-toc-item">
            <span>2. Entrepreneur Information</span>
            <span className="pdf-toc-dots"></span>
            <span>4</span>
          </div>
          <div className="pdf-toc-item">
            <span>3. Business Overview</span>
            <span className="pdf-toc-dots"></span>
            <span>5</span>
          </div>
          <div className="pdf-toc-item">
            <span>4. Product/Service Details</span>
            <span className="pdf-toc-dots"></span>
            <span>7</span>
          </div>
          <div className="pdf-toc-item">
            <span>5. Financial Requirements</span>
            <span className="pdf-toc-dots"></span>
            <span>9</span>
          </div>
          <div className="pdf-toc-item">
            <span>6. Project Description</span>
            <span className="pdf-toc-dots"></span>
            <span>11</span>
          </div>
        </div>
      </div> */}

      {/* Section 1: Executive Summary */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">1. Executive Summary</h1>
        <div className="pdf-section-content">
          <div className="pdf-field-group">
            <div className="pdf-field-label">Business Name</div>
            <div className="pdf-field-value">
              {formData.business_details?.business_name || formData.business_name}
            </div>
          </div>
          <div className="pdf-field-group">
            <div className="pdf-field-label">Sector</div>
            <div className="pdf-field-value">
              {formData.business_details?.sector || "Not specified"}
            </div>
          </div>
          <div className="pdf-field-group">
            <div className="pdf-field-label">Sub-Sector</div>
            <div className="pdf-field-value">
              {formData.business_details?.sub_sector || "Not specified"}
            </div>
          </div>
          <div className="pdf-field-group">
            <div className="pdf-field-label">Total Investment</div>
            <div className="pdf-field-value">
              {formData.financial_details?.total_investment_amount
                ? `₹ ${parseFloat(formData.financial_details.total_investment_amount).toLocaleString("en-IN")}`
                : "Not specified"}
            </div>
          </div>
          <div className="pdf-field-group">
            <div className="pdf-field-label">Project Status</div>
            <div className="pdf-field-value">
              {formData.status} ({formData.completion_percentage}% complete)
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Entrepreneur Information */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">2. Entrepreneur Information</h1>
        {formData.entrepreneur_details ? (
          <div className="pdf-section-content">
            <h2 className="pdf-subsection-title">Personal Details</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Full Name</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.full_name}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Date of Birth</div>
              <div className="pdf-field-value">
                {new Date(formData.entrepreneur_details.date_of_birth).toLocaleDateString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Gender</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.gender || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Category</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.category || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Person with Disability</div>
              <div className="pdf-field-value">
                {formData.entrepreneur_details.pwd ? "Yes" : "No"}
              </div>
            </div>

            <h2 className="pdf-subsection-title">Contact Information</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Address</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.address || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">City</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.city || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">State</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.state || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Pincode</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.pincode || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Phone</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.phone || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Email</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.email || "Not specified"}</div>
            </div>

            <h2 className="pdf-subsection-title">Educational & Professional Background</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Education</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.education}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Years of Experience</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.years_of_experience} years</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Technical Skills</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.technical_skills}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Previous Entrepreneurial Experience</div>
              <div className="pdf-field-value">
                {formData.entrepreneur_details.previous_entrepreneurial_experience}
              </div>
            </div>

            <h2 className="pdf-subsection-title">Identity Verification</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Aadhaar Number</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.aadhaar_number || "Not provided"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">PAN Number</div>
              <div className="pdf-field-value">{formData.entrepreneur_details.pan_number || "Not provided"}</div>
            </div>
          </div>
        ) : (
          <p className="pdf-no-data">Entrepreneur details not available</p>
        )}
      </div>

      {/* Section 3: Business Overview */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">3. Business Overview</h1>
        {formData.business_details ? (
          <div className="pdf-section-content">
            <h2 className="pdf-subsection-title">Basic Information</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Business Name</div>
              <div className="pdf-field-value">{formData.business_details.business_name}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Sector</div>
              <div className="pdf-field-value">{formData.business_details.sector}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Sub-Sector</div>
              <div className="pdf-field-value">{formData.business_details.sub_sector}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Business Type</div>
              <div className="pdf-field-value">{formData.business_details.business_type || "Not specified"}</div>
            </div>

            <h2 className="pdf-subsection-title">Legal Structure</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Legal Structure</div>
              <div className="pdf-field-value">{formData.business_details.legal_structure}</div>
            </div>
            {formData.business_details.registration_number && (
              <div className="pdf-field-group">
                <div className="pdf-field-label">Registration Number</div>
                <div className="pdf-field-value">{formData.business_details.registration_number}</div>
              </div>
            )}

            <h2 className="pdf-subsection-title">Operational Details</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Location</div>
              <div className="pdf-field-value">{formData.business_details.location}</div>
            </div>
            {formData.business_details.establishment_date && (
              <div className="pdf-field-group">
                <div className="pdf-field-label">Establishment Date</div>
                <div className="pdf-field-value">
                  {new Date(formData.business_details.establishment_date).toLocaleDateString("en-IN")}
                </div>
              </div>
            )}
            <div className="pdf-field-group">
              <div className="pdf-field-label">Number of Employees</div>
              <div className="pdf-field-value">{formData.business_details.number_of_employees || 0}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Ownership Percentage</div>
              <div className="pdf-field-value">{formData.business_details.ownership_percentage || 0}%</div>
            </div>

            <h2 className="pdf-subsection-title">Business Model</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Business Model Description</div>
              <div className="pdf-field-value">{formData.business_details.business_model}</div>
            </div>
          </div>
        ) : (
          <p className="pdf-no-data">Business details not available</p>
        )}
      </div>

      {/* Section 4: Product/Service Details */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">4. Product/Service Details</h1>
        {formData.product_details ? (
          <div className="pdf-section-content">
            <h2 className="pdf-subsection-title">Product Overview</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Product Name</div>
              <div className="pdf-field-value">{formData.product_details.product_name}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Product Category</div>
              <div className="pdf-field-value">{formData.product_details.product_category}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Description</div>
              <div className="pdf-field-value">{formData.product_details.product_description || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Unique Selling Points</div>
              <div className="pdf-field-value">{formData.product_details.unique_selling_points}</div>
            </div>

            <h2 className="pdf-subsection-title">Development & Protection</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Stage of Development</div>
              <div className="pdf-field-value">{formData.product_details.stage_of_development || "Not specified"}</div>
            </div>
            {formData.product_details.intellectual_property && (
              <div className="pdf-field-group">
                <div className="pdf-field-label">Intellectual Property</div>
                <div className="pdf-field-value">{formData.product_details.intellectual_property}</div>
              </div>
            )}
            {formData.product_details.certifications && (
              <div className="pdf-field-group">
                <div className="pdf-field-label">Certifications</div>
                <div className="pdf-field-value">{formData.product_details.certifications}</div>
              </div>
            )}

            <h2 className="pdf-subsection-title">Market Analysis</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Target Market</div>
              <div className="pdf-field-value">{formData.product_details.target_market || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Market Size</div>
              <div className="pdf-field-value">{formData.product_details.market_size || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Competitors</div>
              <div className="pdf-field-value">{formData.product_details.competitors || "Not specified"}</div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Competitive Advantage</div>
              <div className="pdf-field-value">{formData.product_details.competitive_advantage || "Not specified"}</div>
            </div>
          </div>
        ) : (
          <p className="pdf-no-data">Product details not available</p>
        )}
      </div>

      {/* Section 5: Financial Requirements */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">5. Financial Requirements</h1>
        {formData.financial_details ? (
          <div className="pdf-section-content">
            <h2 className="pdf-subsection-title">Investment Breakdown</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Total Investment Amount</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.total_investment_amount).toLocaleString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Land Cost</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.land_cost).toLocaleString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Building Cost</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.building_cost).toLocaleString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Machinery Cost</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.machinery_cost).toLocaleString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Other Fixed Capital</div>
              <div className="pdf-field-value">
                {formData.financial_details.other_fixed_capital && !isNaN(parseFloat(formData.financial_details.other_fixed_capital))
                  ? `₹ ${parseFloat(formData.financial_details.other_fixed_capital).toLocaleString("en-IN")}`
                  : "₹ 0"}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Working Capital</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.working_capital).toLocaleString("en-IN")}
              </div>
            </div>

            <h2 className="pdf-subsection-title">Funding Structure</h2>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Own Contribution</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.own_contribution).toLocaleString("en-IN")}
              </div>
            </div>
            <div className="pdf-field-group">
              <div className="pdf-field-label">Loan Required</div>
              <div className="pdf-field-value">
                ₹ {parseFloat(formData.financial_details.loan_required).toLocaleString("en-IN")}
              </div>
            </div>
            {formData.financial_details.other_funding_sources && (
              <div className="pdf-field-group">
                <div className="pdf-field-label">Other Funding Sources</div>
                <div className="pdf-field-value">{formData.financial_details.other_funding_sources}</div>
              </div>
            )}
            <div className="pdf-field-group">
              <div className="pdf-field-label">Break-even Period</div>
              <div className="pdf-field-value">{formData.financial_details.break_even_period || "Not calculated"}</div>
            </div>

            {(formData.financial_details.bank_name ||
              formData.financial_details.existing_loans ||
              formData.financial_details.credit_history) && (
              <>
                <h2 className="pdf-subsection-title">Banking & Credit Information</h2>
                {formData.financial_details.bank_name && (
                  <div className="pdf-field-group">
                    <div className="pdf-field-label">Bank Name</div>
                    <div className="pdf-field-value">{formData.financial_details.bank_name}</div>
                  </div>
                )}
                {formData.financial_details.bank_account_number && (
                  <div className="pdf-field-group">
                    <div className="pdf-field-label">Bank Account Number</div>
                    <div className="pdf-field-value">{formData.financial_details.bank_account_number}</div>
                  </div>
                )}
                {formData.financial_details.ifsc_code && (
                  <div className="pdf-field-group">
                    <div className="pdf-field-label">IFSC Code</div>
                    <div className="pdf-field-value">{formData.financial_details.ifsc_code}</div>
                  </div>
                )}
                {formData.financial_details.existing_loans && (
                  <div className="pdf-field-group">
                    <div className="pdf-field-label">Existing Loans</div>
                    <div className="pdf-field-value">{formData.financial_details.existing_loans}</div>
                  </div>
                )}
                {formData.financial_details.credit_history && (
                  <div className="pdf-field-group">
                    <div className="pdf-field-label">Credit History</div>
                    <div className="pdf-field-value">{formData.financial_details.credit_history}</div>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          <p className="pdf-no-data">Financial details not available</p>
        )}

        {formData.revenue_assumptions && (
          <>
            <h2 className="pdf-subsection-title">Revenue Projections</h2>
            <div className="pdf-section-content">
              <div className="pdf-field-group">
                <div className="pdf-field-label">Year 1 Revenue</div>
                <div className="pdf-field-value">
                  {formData.revenue_assumptions.year_1_revenue && !isNaN(parseFloat(formData.revenue_assumptions.year_1_revenue))
                    ? `₹ ${parseFloat(formData.revenue_assumptions.year_1_revenue).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Year 2 Revenue</div>
                <div className="pdf-field-value">
                  {formData.revenue_assumptions.year_2_revenue && !isNaN(parseFloat(formData.revenue_assumptions.year_2_revenue))
                    ? `₹ ${parseFloat(formData.revenue_assumptions.year_2_revenue).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Year 3 Revenue</div>
                <div className="pdf-field-value">
                  {formData.revenue_assumptions.year_3_revenue && !isNaN(parseFloat(formData.revenue_assumptions.year_3_revenue))
                    ? `₹ ${parseFloat(formData.revenue_assumptions.year_3_revenue).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Price per Unit</div>
                <div className="pdf-field-value">
                  {formData.revenue_assumptions.price_per_unit && !isNaN(parseFloat(formData.revenue_assumptions.price_per_unit))
                    ? `₹ ${parseFloat(formData.revenue_assumptions.price_per_unit).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Revenue Growth Assumptions</div>
                <div className="pdf-field-value">{formData.revenue_assumptions.revenue_growth_assumptions}</div>
              </div>
            </div>
          </>
        )}

        {formData.cost_details && (
          <>
            <h2 className="pdf-subsection-title">Cost Structure</h2>
            <div className="pdf-section-content">
              <div className="pdf-field-group">
                <div className="pdf-field-label">Raw Material Cost</div>
                <div className="pdf-field-value">
                  {formData.cost_details.raw_material_cost && !isNaN(parseFloat(formData.cost_details.raw_material_cost))
                    ? `₹ ${parseFloat(formData.cost_details.raw_material_cost).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Labor Cost</div>
                <div className="pdf-field-value">
                  {formData.cost_details.labor_cost && !isNaN(parseFloat(formData.cost_details.labor_cost))
                    ? `₹ ${parseFloat(formData.cost_details.labor_cost).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Overhead Cost</div>
                <div className="pdf-field-value">
                  {formData.cost_details.overhead_cost && !isNaN(parseFloat(formData.cost_details.overhead_cost))
                    ? `₹ ${parseFloat(formData.cost_details.overhead_cost).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
              <div className="pdf-field-group">
                <div className="pdf-field-label">Other Operational Costs</div>
                <div className="pdf-field-value">
                  {formData.cost_details.other_operational_costs && !isNaN(parseFloat(formData.cost_details.other_operational_costs))
                    ? `₹ ${parseFloat(formData.cost_details.other_operational_costs).toLocaleString("en-IN")}`
                    : "Not specified"}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Section 5.5: Financial Analysis Summary */}
      {financialSummary && (
        <div className="pdf-page">
          <h1 className="pdf-section-title">5.5. Financial Analysis Summary</h1>
          <div className="pdf-section-content">
            <p className="pdf-field-note" style={{ marginBottom: '20px', fontStyle: 'italic', color: '#666' }}>
              This section provides calculated financial metrics based on the investment and revenue projections.
              Calculated on: {new Date(financialSummary.calculated_at).toLocaleString("en-IN")}
            </p>

            <h2 className="pdf-subsection-title">Key Financial Metrics</h2>
            
            <div className="pdf-field-group">
              <div className="pdf-field-label">Break-even Period</div>
              <div className="pdf-field-value">
                <strong>{financialSummary.breakeven_months} months</strong>
              </div>
            </div>

            <div className="pdf-field-group">
              <div className="pdf-field-label">Return on Investment (ROI)</div>
              <div className="pdf-field-value">
                <strong>{financialSummary.roi_percentage.toFixed(2)}%</strong>
              </div>
            </div>

            <div className="pdf-field-group">
              <div className="pdf-field-label">Payback Period</div>
              <div className="pdf-field-value">
                <strong>{financialSummary.payback_period_months} months</strong>
              </div>
            </div>

            <div className="pdf-field-group">
              <div className="pdf-field-label">Net Present Value (NPV)</div>
              <div className="pdf-field-value">
                <strong>₹ {financialSummary.npv.toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}</strong>
              </div>
            </div>

            <div className="pdf-field-group">
              <div className="pdf-field-label">Profit Margin</div>
              <div className="pdf-field-value">
                <strong>{financialSummary.profit_margin_percentage.toFixed(2)}%</strong>
              </div>
            </div>

            <div className="pdf-field-group" style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
              <div className="pdf-field-label" style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '10px' }}>
                Financial Viability Assessment
              </div>
              <div className="pdf-field-value" style={{ lineHeight: '1.6' }}>
                {financialSummary.roi_percentage > 100 && financialSummary.npv > 0 ? (
                  <span style={{ color: '#28a745' }}>
                    ✓ Project shows strong financial viability with positive ROI and NPV.
                  </span>
                ) : financialSummary.roi_percentage > 50 && financialSummary.npv > 0 ? (
                  <span style={{ color: '#ffc107' }}>
                    ⚠ Project shows moderate financial viability. Review assumptions carefully.
                  </span>
                ) : (
                  <span style={{ color: '#dc3545' }}>
                    ⚠ Project requires careful review of financial assumptions and risk factors.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Section 6: Project Description (AI-Generated Content) */}
      <div className="pdf-page">
        <h1 className="pdf-section-title">6. Project Description</h1>
        {formData.generated_content && formData.generated_content.sections ? (
          <div className="pdf-section-content">
            {Object.entries(formData.generated_content.sections).map(([key, value]) => (
              <div key={key} className="pdf-content-section">
                <div className="pdf-content-body">
                  <ReactMarkdown>{value}</ReactMarkdown>
                </div>
              </div>
            ))}
            <div className="pdf-generation-info">
              <em>
                Generated on:{" "}
                {new Date(formData.generated_content.generated_at).toLocaleString("en-IN")}
              </em>
            </div>
          </div>
        ) : (
          <p className="pdf-no-data">AI-generated content not available</p>
        )}
      </div>
    </div>
  );
};

export default PDFPage;
