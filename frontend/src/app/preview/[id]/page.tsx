"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, FileText, Download, Edit, Loader2, DollarSign, Target, TrendingUp } from "lucide-react";
import { getValidToken } from "@/lib/utils/auth";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

interface GeneratedSection {
  section_name: string;
  generated_text: string;
  ai_model_used: string;
  confidence_score: number;
  version_number: number;
  generated_at: string;
}

interface FormData {
  id: number;
  business_name: string;
  status: string;
  completion_percentage: number;
  entrepreneur_details?: any;
  business_details?: any;
  product_details?: any;
  financial_details?: any;
  revenue_assumptions?: any;
  cost_details?: any;
  staffing_details?: any;
  timeline_details?: any;
}

interface FinancialProjection {
  year: number;
  revenue: number;
  total_costs: number;
  gross_profit: number;
  operating_profit: number;
  net_profit: number;
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

interface MatchedScheme {
  scheme_number: number;
  scheme_name: string;
  match_score: number;
  match_reasons: string[];
  key_benefit: string;
  ministry?: string;
  scheme_type?: string;
  subsidy_percentage?: string;
  max_subsidy_amount?: string;
}

export default function PreviewPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const formId = params.id as string;

  const [sections, setSections] = useState<GeneratedSection[]>([]);
  const [formData, setFormData] = useState<FormData | null>(null);
  const [financialData, setFinancialData] = useState<FinancialSummary | null>(null);
  const [schemes, setSchemes] = useState<MatchedScheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [formName, setFormName] = useState("DPR Form");
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [regenerating, setRegenerating] = useState(false);
  const [activeTab, setActiveTab] = useState("ai-content");

  useEffect(() => {
    fetchAllData();
  }, [formId]);

  const fetchAllData = async () => {
    setLoading(true);
    await Promise.all([
      fetchGeneratedContent(),
      fetchFormData(),
      fetchFinancialProjections(),
      fetchMatchedSchemes()
    ]);
    setLoading(false);
  };

  const fetchGeneratedContent = async () => {
    try {
      const token = getValidToken();
      
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(`http://localhost:8000/api/form/${formId}/generated-content`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load generated content");
      }

      const data = await response.json();
      console.log("Generated content:", data);
      
      // Define the correct section order
      const sectionOrder = [
        "executive_summary",
        "market_analysis",
        "competitive_analysis",
        "marketing_strategy",
        "operational_plan",
        "risk_analysis",
        "swot_analysis",
        "implementation_roadmap"
      ];
      
      // Sort sections according to the defined order
      const sortedSections = (data.sections || []).sort((a: GeneratedSection, b: GeneratedSection) => {
        const indexA = sectionOrder.indexOf(a.section_name);
        const indexB = sectionOrder.indexOf(b.section_name);
        
        // If section is not in the order array, put it at the end
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        
        return indexA - indexB;
      });
      
      setSections(sortedSections);
      setFormName(data.business_name || "DPR Form");
    } catch (error: any) {
      console.error("Error fetching generated content:", error);
      // Don't show error toast as this might not exist yet
    }
  };

  const fetchFormData = async () => {
    try {
      const token = getValidToken();
      
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(`http://localhost:8000/api/form/${formId}/complete`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load form data");
      }

      const data = await response.json();
      console.log("Form data:", data);
      setFormData(data);
      setFormName(data.business_name || "DPR Form");
    } catch (error: any) {
      console.error("Error fetching form data:", error);
      toast({
        title: "Warning",
        description: "Could not load form data",
        variant: "destructive",
      });
    }
  };

  const fetchFinancialProjections = async () => {
    try {
      const token = getValidToken();
      
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(`http://localhost:8000/api/financial/${formId}/summary`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // Silently skip if financial data not available
        console.log("Financial projections not available yet");
        return;
      }

      const data = await response.json();
      console.log("Financial data:", data);
      setFinancialData(data);
    } catch (error: any) {
      console.error("Error fetching financial projections:", error);
      // Don't show error as financials might not be calculated yet
    }
  };

  const fetchMatchedSchemes = async () => {
    try {
      const token = getValidToken();
      
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(`http://localhost:8000/api/schemes/match/${formId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          max_results: 10
        })
      });

      if (!response.ok) {
        throw new Error("Failed to load matched schemes");
      }

      const data = await response.json();
      console.log("Matched schemes:", data);
      setSchemes(data.matched_schemes || []);
    } catch (error: any) {
      console.error("Error fetching matched schemes:", error);
      // Don't show error as schemes matching might not be done yet
    }
  };

  const formatSectionName = (sectionName: string) => {
    const formatted = sectionName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    // Handle special case for SWOT
    if (formatted === 'Swot Analysis') {
      return 'SWOT Analysis';
    }
    
    return formatted;
  };

  const handleEditSection = (sectionName: string) => {
    setSelectedSection(sectionName);
    setEditPrompt("");
    setEditDialogOpen(true);
  };

  const handleRegenerateSection = async () => {
    if (!selectedSection) return;

    setRegenerating(true);
    try {
      const token = getValidToken();
      
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `http://localhost:8000/api/form/${formId}/generate/${selectedSection}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            custom_prompt: editPrompt || undefined,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to regenerate section");
      }

      const data = await response.json();
      
      toast({
        title: "Success",
        description: `${formatSectionName(selectedSection)} regenerated successfully!`,
      });

      // Refresh all content
      await fetchAllData();
      
      // Close dialog
      setEditDialogOpen(false);
      setSelectedSection(null);
      setEditPrompt("");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to regenerate section",
        variant: "destructive",
      });
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto max-w-6xl py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading DPR data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-6xl py-8">
      <div className="mb-6 flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.push(`/form/${formId}`)}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Form
        </Button>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.print()}>
            <Download className="mr-2 h-4 w-4" />
            Print/Save as PDF
          </Button>
        </div>
      </div>

      <div className="mb-6">
        <h1 className="text-4xl font-bold mb-2">{formName}</h1>
        <p className="text-muted-foreground">Complete DPR Preview</p>
        {formData && (
          <div className="mt-2 flex gap-2">
            <Badge variant="outline">Status: {formData.status}</Badge>
            <Badge variant="outline">Completion: {formData.completion_percentage}%</Badge>
          </div>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="ai-content">
            <FileText className="mr-2 h-4 w-4" />
            AI Content
          </TabsTrigger>
          <TabsTrigger value="form-data">
            <Edit className="mr-2 h-4 w-4" />
            Form Data
          </TabsTrigger>
          <TabsTrigger value="financials">
            <DollarSign className="mr-2 h-4 w-4" />
            Financials
          </TabsTrigger>
          <TabsTrigger value="schemes">
            <Target className="mr-2 h-4 w-4" />
            Schemes
          </TabsTrigger>
        </TabsList>

        {/* AI-Generated Content Tab */}
        <TabsContent value="ai-content" className="space-y-4">
          {sections.length === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>No AI Content Generated</CardTitle>
                <CardDescription>
                  Generate AI content for your DPR to see it here.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => router.push(`/generate/${formId}`)}>
                  Generate Content
                </Button>
              </CardContent>
            </Card>
          ) : (
            sections.map((section, index) => (
              <Card key={index} className="print:break-inside-avoid">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-2xl">{formatSectionName(section.section_name)}</CardTitle>
                      <CardDescription className="mt-2">
                        Generated by {section.ai_model_used} • 
                        Confidence: {section.confidence_score}% • 
                        Version {section.version_number}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2 print:hidden">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditSection(section.section_name)}
                      >
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </Button>
                      <div className="bg-primary/10 px-3 py-1 rounded-full text-sm font-medium text-primary">
                        #{index + 1}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-base dark:prose-invert max-w-none 
                    prose-headings:font-bold prose-headings:text-foreground
                    prose-h1:text-3xl prose-h1:mb-4 prose-h1:mt-6
                    prose-h2:text-2xl prose-h2:mb-3 prose-h2:mt-5
                    prose-h3:text-xl prose-h3:mb-2 prose-h3:mt-4
                    prose-p:text-foreground prose-p:leading-relaxed prose-p:mb-4
                    prose-strong:text-foreground prose-strong:font-semibold
                    prose-ul:my-4 prose-ul:list-disc prose-ul:pl-6
                    prose-ol:my-4 prose-ol:list-decimal prose-ol:pl-6
                    prose-li:text-foreground prose-li:mb-2">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {section.generated_text}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* Form Data Tab */}
        <TabsContent value="form-data" className="space-y-4">
          {!formData ? (
            <Card>
              <CardHeader>
                <CardTitle>No Form Data</CardTitle>
                <CardDescription>
                  Complete your form to see the data here.
                </CardDescription>
              </CardHeader>
            </Card>
          ) : (
            <>
              {formData.entrepreneur_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Entrepreneur Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Full Name</Label>
                      <p className="font-medium">{formData.entrepreneur_details.full_name}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Date of Birth</Label>
                      <p className="font-medium">{formData.entrepreneur_details.date_of_birth}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Education</Label>
                      <p className="font-medium">{formData.entrepreneur_details.education}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Years of Experience</Label>
                      <p className="font-medium">{formData.entrepreneur_details.years_of_experience}</p>
                    </div>
                    {formData.entrepreneur_details.previous_business_experience && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Previous Business Experience</Label>
                        <p className="font-medium">{formData.entrepreneur_details.previous_business_experience}</p>
                      </div>
                    )}
                    {formData.entrepreneur_details.technical_skills && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Technical Skills</Label>
                        <p className="font-medium">{formData.entrepreneur_details.technical_skills}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {formData.business_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Business Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Sector</Label>
                      <p className="font-medium">{formData.business_details.sector}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Sub-Sector</Label>
                      <p className="font-medium">{formData.business_details.sub_sector}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Legal Structure</Label>
                      <p className="font-medium">{formData.business_details.legal_structure}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Location</Label>
                      <p className="font-medium">{formData.business_details.location}</p>
                    </div>
                    {formData.business_details.address && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Address</Label>
                        <p className="font-medium">{formData.business_details.address}</p>
                      </div>
                    )}
                    {formData.business_details.business_objective && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Business Objective</Label>
                        <p className="font-medium">{formData.business_details.business_objective}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {formData.product_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Product/Service Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <Label className="text-muted-foreground">Product Name</Label>
                      <p className="font-medium">{formData.product_details.product_name}</p>
                    </div>
                    {formData.product_details.description && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Description</Label>
                        <p className="font-medium">{formData.product_details.description}</p>
                      </div>
                    )}
                    {formData.product_details.unique_selling_points && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Unique Selling Points</Label>
                        <p className="font-medium">{formData.product_details.unique_selling_points}</p>
                      </div>
                    )}
                    {formData.product_details.target_market && (
                      <div className="col-span-2">
                        <Label className="text-muted-foreground">Target Market</Label>
                        <p className="font-medium">{formData.product_details.target_market}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {formData.financial_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Financial Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Total Investment</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.total_investment_amount)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Loan Required</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.loan_required)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Own Contribution</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.own_contribution)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Working Capital</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.working_capital)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Land Cost</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.land_cost)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Building Cost</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.building_cost)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Machinery Cost</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.machinery_cost)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Other Costs</Label>
                      <p className="font-medium">₹{Number(formData.financial_details.other_costs)?.toLocaleString('en-IN')}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {formData.revenue_assumptions && (
                <Card>
                  <CardHeader>
                    <CardTitle>Revenue Assumptions</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Product Price</Label>
                      <p className="font-medium">₹{Number(formData.revenue_assumptions.product_price)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Monthly Sales (Year 1)</Label>
                      <p className="font-medium">{Number(formData.revenue_assumptions.monthly_sales_quantity_year1)?.toLocaleString('en-IN')} units</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Monthly Sales (Year 2)</Label>
                      <p className="font-medium">{Number(formData.revenue_assumptions.monthly_sales_quantity_year2)?.toLocaleString('en-IN')} units</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Monthly Sales (Year 3)</Label>
                      <p className="font-medium">{Number(formData.revenue_assumptions.monthly_sales_quantity_year3)?.toLocaleString('en-IN')} units</p>
                    </div>
                    <div className="col-span-2">
                      <Label className="text-muted-foreground">Growth Rate</Label>
                      <p className="font-medium">{Number(formData.revenue_assumptions.growth_rate_percentage)}% per year</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {formData.cost_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Cost Details (Monthly)</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Raw Material Cost</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.raw_material_cost_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Labor Cost</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.labor_cost_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Utilities Cost</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.utilities_cost_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Rent</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.rent_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Marketing Cost</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.marketing_cost_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Other Fixed Costs</Label>
                      <p className="font-medium">₹{Number(formData.cost_details.other_fixed_costs_monthly)?.toLocaleString('en-IN')}</p>
                    </div>
                    <div className="col-span-2">
                      <Label className="text-muted-foreground">Total Monthly Cost</Label>
                      <p className="text-lg font-bold">₹{(
                        Number(formData.cost_details.raw_material_cost_monthly || 0) +
                        Number(formData.cost_details.labor_cost_monthly || 0) +
                        Number(formData.cost_details.utilities_cost_monthly || 0) +
                        Number(formData.cost_details.rent_monthly || 0) +
                        Number(formData.cost_details.marketing_cost_monthly || 0) +
                        Number(formData.cost_details.other_fixed_costs_monthly || 0)
                      )?.toLocaleString('en-IN')}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {formData.staffing_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Staffing Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Total Employees</Label>
                      <p className="font-medium">{formData.staffing_details.total_employees}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Management</Label>
                      <p className="font-medium">{formData.staffing_details.management_count}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Technical Staff</Label>
                      <p className="font-medium">{formData.staffing_details.technical_staff_count}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Support Staff</Label>
                      <p className="font-medium">{formData.staffing_details.support_staff_count}</p>
                    </div>
                    <div className="col-span-2">
                      <Label className="text-muted-foreground">Average Salary</Label>
                      <p className="text-lg font-bold">₹{Number(formData.staffing_details.average_salary)?.toLocaleString('en-IN')}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {formData.timeline_details && (
                <Card>
                  <CardHeader>
                    <CardTitle>Timeline Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Land Acquisition</Label>
                      <p className="font-medium">{formData.timeline_details.land_acquisition_months} months</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Construction</Label>
                      <p className="font-medium">{formData.timeline_details.construction_months} months</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Machinery Installation</Label>
                      <p className="font-medium">{formData.timeline_details.machinery_installation_months} months</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Trial Production</Label>
                      <p className="font-medium">{formData.timeline_details.trial_production_months} months</p>
                    </div>
                    <div className="col-span-2">
                      <Label className="text-muted-foreground">Commercial Production Start</Label>
                      <p className="text-lg font-bold">Month {formData.timeline_details.commercial_production_start_month}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="flex gap-2">
                <Button onClick={() => router.push(`/form/${formId}`)}>
                  Edit Form Data
                </Button>
              </div>
            </>
          )}
        </TabsContent>

        {/* Financial Projections Tab */}
        <TabsContent value="financials" className="space-y-4">
          {!financialData ? (
            <Card>
              <CardHeader>
                <CardTitle>No Financial Projections</CardTitle>
                <CardDescription>
                  {formData?.financial_details 
                    ? "Financial details are ready. Click below to generate 36-month projections with ROI, break-even analysis, and NPV calculations."
                    : "Complete your financial details first, then generate projections to see them here."}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {formData?.financial_details ? (
                  <Button 
                    onClick={async () => {
                      try {
                        const token = getValidToken();
                        
                        if (!token) {
                          router.push("/login");
                          return;
                        }

                        const response = await fetch(`http://localhost:8000/api/financial/${formId}/calculate`, {
                          method: "POST",
                          headers: {
                            Authorization: `Bearer ${token}`,
                          },
                        });
                        
                        if (response.ok) {
                          toast({
                            title: "Success",
                            description: "Financial projections generated successfully!",
                          });
                          // Refresh financial data
                          await fetchFinancialProjections();
                        } else {
                          throw new Error("Failed to generate projections");
                        }
                      } catch (error) {
                        toast({
                          title: "Error",
                          description: "Failed to generate financial projections",
                          variant: "destructive",
                        });
                      }
                    }}
                  >
                    Generate Financial Projections
                  </Button>
                ) : (
                  <Button onClick={() => router.push(`/form/${formId}`)}>
                    Add Financial Details First
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Financial Analysis Summary
                  </CardTitle>
                  <CardDescription>
                    Calculated on {new Date(financialData.calculated_at).toLocaleDateString('en-IN', { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Break-Even Period</Label>
                    <p className="text-2xl font-bold text-blue-600">{financialData.breakeven_months} months</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">ROI</Label>
                    <p className="text-2xl font-bold text-green-600">{financialData.roi_percentage}%</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Payback Period</Label>
                    <p className="text-2xl font-bold text-purple-600">{financialData.payback_period_months} months</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">NPV (Net Present Value)</Label>
                    <p className="text-2xl font-bold text-orange-600">₹{Number(financialData.npv).toLocaleString('en-IN')}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Profit Margin</Label>
                    <p className="text-2xl font-bold text-teal-600">{financialData.profit_margin_percentage}%</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Business Name</Label>
                    <p className="text-lg font-semibold">{financialData.business_name}</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>About Financial Projections</CardTitle>
                  <CardDescription>
                    The financial analysis is based on 36-month projections calculated from your form data
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="bg-blue-100 text-blue-600 p-2 rounded">
                      <TrendingUp className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold">Break-Even Analysis</h4>
                      <p className="text-sm text-muted-foreground">
                        Month when cumulative cash flow turns positive
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="bg-green-100 text-green-600 p-2 rounded">
                      <DollarSign className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold">Return on Investment (ROI)</h4>
                      <p className="text-sm text-muted-foreground">
                        Total return percentage over the 36-month period
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="bg-purple-100 text-purple-600 p-2 rounded">
                      <Target className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold">Net Present Value (NPV)</h4>
                      <p className="text-sm text-muted-foreground">
                        Present value of future cash flows (10% discount rate)
                      </p>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={async () => {
                      try {
                        const token = getValidToken();
                        
                        if (!token) {
                          router.push("/login");
                          return;
                        }

                        const response = await fetch(`http://localhost:8000/api/financial/${formId}/calculate`, {
                          method: "POST",
                          headers: {
                            Authorization: `Bearer ${token}`,
                          },
                        });
                        
                        if (response.ok) {
                          toast({
                            title: "Success",
                            description: "Financial projections recalculated successfully!",
                          });
                          await fetchFinancialProjections();
                        }
                      } catch (error) {
                        toast({
                          title: "Error",
                          description: "Failed to recalculate projections",
                          variant: "destructive",
                        });
                      }
                    }}
                  >
                    Recalculate Projections
                  </Button>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Government Schemes Tab */}
        <TabsContent value="schemes" className="space-y-4">
          {schemes.length === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>No Matched Schemes</CardTitle>
                <CardDescription>
                  Complete your form and generate scheme matches to see relevant government schemes here.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => router.push(`/schemes/ai-match`)}>
                  Find Matching Schemes
                </Button>
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="mb-4">
                <h3 className="text-lg font-semibold">Top {schemes.length} Matched Government Schemes</h3>
                <p className="text-sm text-muted-foreground">AI-powered scheme recommendations based on your business profile</p>
              </div>
              
              {schemes.map((scheme, index) => (
                <Card key={index} className="border-l-4" style={{ borderLeftColor: scheme.match_score >= 80 ? '#22c55e' : scheme.match_score >= 60 ? '#eab308' : '#94a3b8' }}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={scheme.match_score >= 80 ? "default" : "secondary"} className="text-lg px-3 py-1">
                            {scheme.match_score}% Match
                          </Badge>
                          <span className="text-sm text-muted-foreground">Rank #{index + 1}</span>
                        </div>
                        <CardTitle className="text-xl">{scheme.scheme_name}</CardTitle>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-sm font-semibold">Key Benefit</Label>
                      <p className="text-sm mt-1">{scheme.key_benefit}</p>
                    </div>
                    
                    <div>
                      <Label className="text-sm font-semibold">Why This Scheme Matches</Label>
                      <ul className="mt-2 space-y-1">
                        {scheme.match_reasons?.map((reason: string, idx: number) => (
                          <li key={idx} className="text-sm flex items-start gap-2">
                            <span className="text-primary mt-1">•</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <Button variant="outline" size="sm" onClick={() => router.push('/schemes')}>
                      View Full Scheme Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </TabsContent>
      </Tabs>

      {/* Edit Section Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Edit {selectedSection && formatSectionName(selectedSection)}
            </DialogTitle>
            <DialogDescription>
              Provide instructions for how you want this section to be regenerated. 
              The AI will use your current form data along with your custom instructions.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">Custom Instructions (Optional)</Label>
              <Textarea
                id="prompt"
                placeholder="Example: Make it more detailed with specific market statistics, focus on sustainability aspects, include competitive advantages..."
                value={editPrompt}
                onChange={(e) => setEditPrompt(e.target.value)}
                rows={6}
                className="resize-none"
              />
              <p className="text-sm text-muted-foreground">
                Leave empty to regenerate with default AI instructions, or provide specific guidance for customization.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setEditDialogOpen(false);
                setSelectedSection(null);
                setEditPrompt("");
              }}
              disabled={regenerating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRegenerateSection}
              disabled={regenerating}
            >
              {regenerating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {regenerating ? "Regenerating..." : "Regenerate Section"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
