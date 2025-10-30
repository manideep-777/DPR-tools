"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Save, FileText, Sparkles } from "lucide-react";
import { getFormById, updateFormSection } from "@/lib/api/form";
import {
  transformEntrepreneurDetails,
  transformBusinessDetails,
  transformProductDetails,
  transformFinancialDetails,
  transformRevenueAssumptions,
  transformCostDetails,
  transformStaffingDetails,
  transformTimelineDetails,
} from "@/lib/utils/fieldTransform";

// Import form sections
import EntrepreneurDetailsForm from "@/components/form/EntrepreneurDetailsForm";
import BusinessDetailsForm from "@/components/form/BusinessDetailsForm";
import ProductDetailsForm from "@/components/form/ProductDetailsForm";
import FinancialDetailsForm from "@/components/form/FinancialDetailsForm";
import RevenueAssumptionsForm from "@/components/form/RevenueAssumptionsForm";
import CostDetailsForm from "@/components/form/CostDetailsForm";
import StaffingDetailsForm from "@/components/form/StaffingDetailsForm";
import TimelineDetailsForm from "@/components/form/TimelineDetailsForm";

export default function DPRFormPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const formId = params.id as string;

  const [activeTab, setActiveTab] = useState("entrepreneur");
  const [formData, setFormData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Fetch form data on mount
  useEffect(() => {
    fetchFormData();
  }, [formId]);

  const fetchFormData = async () => {
    try {
      const data = await getFormById(parseInt(formId));
      
      // The backend returns keys with underscores, so we need to map them correctly
      const transformedData = {
        id: data.id,
        userId: data.user_id,
        businessName: data.business_name,
        status: data.status,
        completionPercentage: data.completion_percentage,
        createdAt: data.created_at,
        lastModified: data.last_modified,
        // Transform section data (backend uses snake_case keys)
        entrepreneurDetails: transformEntrepreneurDetails(data.entrepreneur_details),
        businessDetails: transformBusinessDetails(data.business_details),
        productDetails: transformProductDetails(data.product_details),
        financialDetails: transformFinancialDetails(data.financial_details),
        revenueAssumptions: transformRevenueAssumptions(data.revenue_assumptions),
        costDetails: transformCostDetails(data.cost_details),
        staffingDetails: transformStaffingDetails(data.staffing_details),
        timelineDetails: transformTimelineDetails(data.timeline_details),
      };
      
      setFormData(transformedData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load form data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSectionUpdate = async (sectionName: string, sectionData: any) => {
    setSaving(true);
    try {
      await updateFormSection(parseInt(formId), sectionName, sectionData);

      toast({
        title: "Success",
        description: "Section saved successfully",
      });

      // Refresh form data
      await fetchFormData();
      
      // Move to next tab automatically
      moveToNextTab();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save section",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const moveToNextTab = () => {
    const tabs = [
      "entrepreneur",
      "business",
      "product",
      "financial",
      "revenue",
      "costs",
      "staffing",
      "timeline"
    ];
    
    const currentIndex = tabs.indexOf(activeTab);
    
    // Move to next tab if not on the last one
    if (currentIndex < tabs.length - 1) {
      setActiveTab(tabs[currentIndex + 1]);
      
      // Smooth scroll to top of form
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      // If on last tab, show completion message
      toast({
        title: "All Sections Complete! 🎉",
        description: "You've completed all form sections. Review or submit your DPR.",
      });
    }
  };

  const handleGenerateAI = async (section: string) => {
    // If generating all sections, navigate to the AI generation page
    if (section === "all") {
      router.push(`/generate/${formId}`);
      return;
    }

    // For individual section generation
    toast({
      title: "Generating Content...",
      description: `Generating ${section} section...`,
    });

    setSaving(true);
    
    try {
      const token = localStorage.getItem("token");
      
      if (!token) {
        throw new Error("Authentication required. Please log in again.");
      }
      
      const endpoint = `http://localhost:8000/api/form/${formId}/generate/${section}`;
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate AI content");
      }

      const result = await response.json();

      toast({
        title: "Success! ✨",
        description: "AI content generated successfully",
      });

      // Refresh form data to show the generated content
      await fetchFormData();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to generate AI content",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const calculateCompletionPercentage = () => {
    if (!formData) return 0;
    
    const sections = [
      formData.entrepreneurDetails,
      formData.businessDetails,
      formData.productDetails,
      formData.financialDetails,
      formData.revenueAssumptions,
      formData.costDetails,
      formData.staffingDetails,
      formData.timelineDetails,
    ];

    const completedSections = sections.filter(section => section !== null).length;
    return Math.round((completedSections / sections.length) * 100);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading form...</p>
        </div>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Form not found</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">{formData.businessName}</h1>
            <p className="text-muted-foreground">DPR Form - {formData.status}</p>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => router.push("/dashboard")}
              variant="outline"
            >
              <FileText className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
            <Button onClick={() => handleGenerateAI("all")}>
              <Sparkles className="mr-2 h-4 w-4" />
              Generate All Sections
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-secondary rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${calculateCompletionPercentage()}%` }}
          ></div>
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          {calculateCompletionPercentage()}% Complete
        </p>
      </div>

      {/* Tabbed Form */}
      <Card>
        <CardContent className="pt-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8 mb-6">
              <TabsTrigger value="entrepreneur">Entrepreneur</TabsTrigger>
              <TabsTrigger value="business">Business</TabsTrigger>
              <TabsTrigger value="product">Product</TabsTrigger>
              <TabsTrigger value="financial">Financial</TabsTrigger>
              <TabsTrigger value="revenue">Revenue</TabsTrigger>
              <TabsTrigger value="costs">Costs</TabsTrigger>
              <TabsTrigger value="staffing">Staffing</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
            </TabsList>

            <TabsContent value="entrepreneur">
              <EntrepreneurDetailsForm
                data={formData.entrepreneurDetails}
                onSave={(data) => handleSectionUpdate("entrepreneur_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="business">
              <BusinessDetailsForm
                data={formData.businessDetails}
                onSave={(data) => handleSectionUpdate("business_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="product">
              <ProductDetailsForm
                data={formData.productDetails}
                onSave={(data) => handleSectionUpdate("product_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="financial">
              <FinancialDetailsForm
                data={formData.financialDetails}
                onSave={(data) => handleSectionUpdate("financial_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="revenue">
              <RevenueAssumptionsForm
                data={formData.revenueAssumptions}
                onSave={(data) => handleSectionUpdate("revenue_assumptions", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="costs">
              <CostDetailsForm
                data={formData.costDetails}
                onSave={(data) => handleSectionUpdate("cost_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="staffing">
              <StaffingDetailsForm
                data={formData.staffingDetails}
                onSave={(data) => handleSectionUpdate("staffing_details", data)}
                saving={saving}
              />
            </TabsContent>

            <TabsContent value="timeline">
              <TimelineDetailsForm
                data={formData.timelineDetails}
                onSave={(data) => handleSectionUpdate("timeline_details", data)}
                saving={saving}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
