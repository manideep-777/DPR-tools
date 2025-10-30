"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/lib/store/authStore";
import { useToast } from "@/hooks/use-toast";
import { matchSchemes, Scheme } from "@/lib/api/schemes";
import { getUserForms, DprFormData, getFormById } from "@/lib/api/form";
import { Loader2, ArrowLeft, ExternalLink, IndianRupee, Tag, MapPin, Sparkles, AlertCircle, FileText, CheckCircle2, Star } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";

// All 8 sections that must be completed
const REQUIRED_SECTIONS = [
  "entrepreneur_details",
  "business_details",
  "product_details",
  "financial_details",
  "revenue_assumptions",
  "cost_details",
  "staffing_details",
  "timeline_details",
];

const SECTION_LABELS = {
  entrepreneur_details: "Entrepreneur Details",
  business_details: "Business Details",
  product_details: "Product Details",
  financial_details: "Financial Details",
  revenue_assumptions: "Revenue Assumptions",
  cost_details: "Cost Details",
  staffing_details: "Staffing Details",
  timeline_details: "Timeline Details",
};

export default function AIMatchSchemesPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [userForms, setUserForms] = useState<DprFormData[]>([]);
  const [selectedFormId, setSelectedFormId] = useState<string>("");
  const [matchedSchemes, setMatchedSchemes] = useState<Scheme[]>([]);
  const [loadingForms, setLoadingForms] = useState(true);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [loadingFormDetails, setLoadingFormDetails] = useState(false);
  const [selectedForm, setSelectedForm] = useState<DprFormData | null>(null);
  const [completedSections, setCompletedSections] = useState<string[]>([]);
  const [allSectionsComplete, setAllSectionsComplete] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserForms();
    }
  }, [isAuthenticated]);

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

  const fetchFormDetails = async (formId: string) => {
    try {
      setLoadingFormDetails(true);
      setMatchedSchemes([]); // Clear previous matches when switching forms
      const formData = await getFormById(parseInt(formId));
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

  const fetchUserForms = async () => {
    try {
      setLoadingForms(true);
      const response = await getUserForms();
      setUserForms(response.forms || []);
      
      // Auto-select first form if available
      if (response.forms && response.forms.length > 0) {
        setSelectedFormId(response.forms[0].id?.toString() || "");
      }
    } catch (error) {
      console.error("Error fetching forms:", error);
      toast({
        title: "Error",
        description: "Failed to load your forms",
        variant: "destructive",
      });
    } finally {
      setLoadingForms(false);
    }
  };

  const checkFormCompletion = (form: DprFormData) => {
    const completed: string[] = [];
    
    REQUIRED_SECTIONS.forEach((section) => {
      // Check both camelCase and snake_case versions
      const camelCaseKey = section.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      const sectionData = (form as any)[section] || (form as any)[camelCaseKey];
      
      if (sectionData && Object.keys(sectionData).length > 0) {
        completed.push(section);
      }
    });

    setCompletedSections(completed);
    setAllSectionsComplete(completed.length === REQUIRED_SECTIONS.length);
  };

  const handleMatchSchemes = async () => {
    if (!selectedFormId || !allSectionsComplete) return;

    try {
      setLoadingMatch(true);
      setMatchedSchemes([]);
      
      const response = await matchSchemes(parseInt(selectedFormId), 10);
      
      if (response.success) {
        setMatchedSchemes(response.matched_schemes);
        toast({
          title: "Success",
          description: response.message,
        });
      }
    } catch (error: any) {
      console.error("Error matching schemes:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to match schemes. Please ensure all form sections are completed.",
        variant: "destructive",
      });
    } finally {
      setLoadingMatch(false);
    }
  };

  const getSchemeTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "subsidy":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "loan":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "grant":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300";
      case "training":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };

  const formatCurrency = (value: string | null) => {
    if (!value) return "N/A";
    const num = parseFloat(value);
    if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)} Cr`;
    if (num >= 100000) return `₹${(num / 100000).toFixed(2)} L`;
    return `₹${num.toLocaleString()}`;
  };

  if (isLoading || loadingForms) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[calc(100vh-200px)]">
        <div className="text-center">
          <Loader2 className="h-12 w-12 mx-auto mb-4 text-primary animate-spin" />
          <p className="text-lg text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const completionPercentage = (completedSections.length / REQUIRED_SECTIONS.length) * 100;

  return (
    <div className="container mx-auto px-4 py-16">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          className="mb-4"
          onClick={() => router.push("/dashboard")}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <div className="flex items-center gap-3">
          <Sparkles className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-4xl font-bold mb-2">AI-Suggested Government Schemes</h1>
            <p className="text-lg text-muted-foreground">
              Get personalized scheme recommendations based on your complete DPR data
            </p>
          </div>
        </div>
      </div>

      {/* Form Selection and Completion Status */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Form Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Your DPR Form</CardTitle>
            <CardDescription>Choose a form to get AI-powered scheme recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            {userForms.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground mb-4">No DPR forms found</p>
                <Button onClick={() => router.push("/dashboard")}>
                  Create Your First DPR
                </Button>
              </div>
            ) : (
              <Select value={selectedFormId} onValueChange={setSelectedFormId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a form" />
                </SelectTrigger>
                <SelectContent>
                  {userForms.map((form) => (
                    <SelectItem key={form.id} value={form.id?.toString() || ""}>
                      {form.business_name || `Form #${form.id}`}
                      {form.completion_percentage && (
                        <span className="ml-2 text-xs text-muted-foreground">
                          ({form.completion_percentage}% complete)
                        </span>
                      )}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>

        {/* Completion Status */}
        <Card>
          <CardHeader>
            <CardTitle>Form Completion Status</CardTitle>
            <CardDescription>All 8 sections must be completed for AI matching</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingFormDetails ? (
              <div className="text-center py-12">
                <Loader2 className="h-8 w-8 mx-auto mb-4 text-muted-foreground animate-spin" />
                <p className="text-sm text-muted-foreground">Loading form details...</p>
              </div>
            ) : selectedForm ? (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Progress</span>
                    <span className="text-sm font-medium">
                      {completedSections.length}/{REQUIRED_SECTIONS.length} sections
                    </span>
                  </div>
                  <Progress value={completionPercentage} className="h-2" />
                </div>
                
                {allSectionsComplete ? (
                  <Alert className="bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <AlertTitle className="text-green-900 dark:text-green-100">All sections complete!</AlertTitle>
                    <AlertDescription className="text-green-700 dark:text-green-300">
                      Your form is ready for AI-powered scheme matching.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Incomplete Form</AlertTitle>
                    <AlertDescription>
                      Please complete all sections to enable AI matching.
                    </AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-2 gap-2 mt-4">
                  {REQUIRED_SECTIONS.map((section) => (
                    <div
                      key={section}
                      className={`flex items-center gap-2 p-2 rounded text-xs ${
                        completedSections.includes(section)
                          ? "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {completedSections.includes(section) ? (
                        <CheckCircle2 className="h-3 w-3" />
                      ) : (
                        <div className="h-3 w-3 rounded-full border-2" />
                      )}
                      <span>{SECTION_LABELS[section as keyof typeof SECTION_LABELS]}</span>
                    </div>
                  ))}
                </div>

                {!allSectionsComplete && (
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={() => router.push(`/form/${selectedFormId}`)}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    Complete Form Sections
                  </Button>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                Select a form to view completion status
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Get AI Suggestions Button */}
      {selectedForm && allSectionsComplete && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <Button
              size="lg"
              className="w-full gap-2"
              onClick={handleMatchSchemes}
              disabled={loadingMatch}
            >
              {loadingMatch ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  AI is analyzing your business data...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Get AI-Powered Scheme Recommendations
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Matched Schemes */}
      {matchedSchemes.length > 0 && (
        <div>
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">Recommended Schemes for You</h2>
            <p className="text-muted-foreground">
              Based on your complete business profile, AI has identified {matchedSchemes.length} suitable schemes
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {matchedSchemes.map((scheme, index) => (
              <Card key={scheme.id} className="hover:shadow-lg transition-shadow border-2">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {index < 3 && (
                          <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                            <Star className="h-3 w-3 mr-1" />
                            Top Pick
                          </Badge>
                        )}
                        <Badge className={getSchemeTypeColor(scheme.scheme_type)}>
                          {scheme.scheme_type}
                        </Badge>
                      </div>
                      <CardTitle className="text-xl mb-2">{scheme.scheme_name}</CardTitle>
                      <CardDescription className="text-sm">{scheme.ministry}</CardDescription>
                    </div>
                    {scheme.match_score && (
                      <div className="text-center">
                        <div className="text-3xl font-bold text-primary">{scheme.match_score}</div>
                        <div className="text-xs text-muted-foreground">Match Score</div>
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    {scheme.description}
                  </p>

                  {/* AI Key Benefit */}
                  {scheme.key_benefit && (
                    <Alert className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800">
                      <Sparkles className="h-4 w-4 text-blue-600" />
                      <AlertTitle className="text-blue-900 dark:text-blue-100">AI Insight</AlertTitle>
                      <AlertDescription className="text-blue-700 dark:text-blue-300">
                        {scheme.key_benefit}
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Match Reasons */}
                  {scheme.match_reasons && scheme.match_reasons.length > 0 && (
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-sm font-medium mb-2">Why this scheme matches:</p>
                      <ul className="space-y-1">
                        {scheme.match_reasons.map((reason, idx) => (
                          <li key={idx} className="text-xs text-muted-foreground flex items-start gap-2">
                            <CheckCircle2 className="h-3 w-3 mt-0.5 text-green-600 shrink-0" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Financial Details */}
                  {(scheme.subsidy_percentage || scheme.max_subsidy_amount) && (
                    <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <IndianRupee className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-green-900 dark:text-green-100">
                          Financial Benefit
                        </span>
                      </div>
                      <div className="text-sm text-green-700 dark:text-green-300">
                        {scheme.subsidy_percentage && (
                          <span>{scheme.subsidy_percentage}% subsidy</span>
                        )}
                        {scheme.subsidy_percentage && scheme.max_subsidy_amount && (
                          <span> • </span>
                        )}
                        {scheme.max_subsidy_amount && (
                          <span>Max: {formatCurrency(scheme.max_subsidy_amount)}</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Investment Range */}
                  <div className="flex items-center gap-2 text-sm">
                    <IndianRupee className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Investment Range:</span>
                    <span className="font-medium">
                      {formatCurrency(scheme.min_investment)} - {formatCurrency(scheme.max_investment)}
                    </span>
                  </div>

                  {/* Sectors */}
                  <div className="flex items-start gap-2">
                    <Tag className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground mb-1">Eligible Sectors:</p>
                      <div className="flex flex-wrap gap-1">
                        {scheme.eligible_sectors.slice(0, 3).map((sector, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {sector}
                          </Badge>
                        ))}
                        {scheme.eligible_sectors.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{scheme.eligible_sectors.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* States */}
                  <div className="flex items-start gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground mb-1">Eligible States:</p>
                      <div className="flex flex-wrap gap-1">
                        {scheme.eligible_states.slice(0, 3).map((state, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {state}
                          </Badge>
                        ))}
                        {scheme.eligible_states.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{scheme.eligible_states.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Eligibility */}
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs font-medium mb-1">Eligibility Criteria:</p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {scheme.eligibility_criteria}
                    </p>
                  </div>

                  {/* Apply Button */}
                  <Button
                    className="w-full"
                    onClick={() => window.open(scheme.application_link, "_blank")}
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Apply for This Scheme
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
