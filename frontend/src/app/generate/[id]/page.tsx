"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { Sparkles, CheckCircle, Loader2, ArrowLeft, FileText } from "lucide-react";
import { getValidToken } from "@/lib/utils/auth";

interface GenerationStatus {
  status: "idle" | "generating" | "completed" | "error";
  sectionsGenerated: string[];
  currentSection: string | null;
  totalSections: number;
  error: string | null;
}

export default function AIGenerationPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const formId = params.id as string;

  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    status: "idle",
    sectionsGenerated: [],
    currentSection: null,
    totalSections: 8,
    error: null,
  });
  
  const [isCheckingExisting, setIsCheckingExisting] = useState(true);

  // Check for existing generated content on mount
  useEffect(() => {
    const checkExistingContent = async () => {
      const token = getValidToken();
      if (!token) {
        toast({
          title: "Authentication Required",
          description: "Your session has expired. Please log in again.",
          variant: "destructive",
        });
        router.push("/login");
        return;
      }

      try {
        // Fetch the form to check if it has generated content
        const response = await fetch(`http://localhost:8000/api/form/${formId}/complete`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log("🔍 Checking for existing content:", data);
          
          // Check if generated_content exists and has sections
          if (data.generated_content && data.generated_content.sections) {
            const sections = data.generated_content.sections;
            const sectionKeys = Object.keys(sections);
            console.log("✅ Found existing sections:", sectionKeys);
            
            if (sectionKeys.length > 0) {
              // Content already exists!
              const generatedSectionNames = sectionKeys.map(key => {
                // Convert snake_case to Title Case with proper handling of acronyms
                const words = key.split('_').map((word: string) => 
                  word.charAt(0).toUpperCase() + word.slice(1)
                );
                
                // Handle special case for SWOT
                const sectionName = words.join(' ');
                if (sectionName === 'Swot Analysis') {
                  return 'SWOT Analysis';
                }
                
                return sectionName;
              });

              console.log("📝 Setting status to completed with sections:", generatedSectionNames);

              setGenerationStatus({
                status: "completed",
                sectionsGenerated: generatedSectionNames,
                currentSection: null,
                totalSections: sectionKeys.length,
                error: null,
              });
            }
          } else {
            console.log("❌ No generated content found");
          }
        }
      } catch (error) {
        console.error("Error checking existing content:", error);
        // Don't show error, just keep status as idle
      } finally {
        setIsCheckingExisting(false);
      }
    };

    checkExistingContent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formId]); // Only run when formId changes, not on every render

  const sectionNames = [
    "Executive Summary",
    "Market Analysis",
    "Competitive Analysis",
    "Marketing Strategy",
    "Operational Plan",
    "Risk Analysis",
    "SWOT Analysis",
    "Implementation Roadmap",
  ];

  const handleGenerateAll = async () => {
    setGenerationStatus({
      status: "generating",
      sectionsGenerated: [],
      currentSection: "Starting AI generation...",
      totalSections: 8,
      error: null,
    });

    try {
      const token = getValidToken();
      
      if (!token) {
        // Redirect to login if token is expired
        toast({
          title: "Session Expired",
          description: "Please log in again to continue",
          variant: "destructive",
        });
        router.push("/login");
        return;
      }

      console.log("Sending AI generation request for form:", formId);

      const response = await fetch(`http://localhost:8000/api/form/${formId}/generate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sections: null, // Generate all sections
          regenerate: false, // Only generate missing sections
        }),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error response:", errorData);
        
        // If unauthorized, token is expired - redirect to login
        if (response.status === 401) {
          localStorage.removeItem("access_token");
          toast({
            title: "Session Expired",
            description: "Please log in again to continue",
            variant: "destructive",
          });
          router.push("/login");
          return;
        }
        
        throw new Error(errorData.detail || "Failed to generate AI content");
      }

      const result = await response.json();
      console.log("Generation result:", result);

      // Extract section names from the response
      const generatedSectionNames = result.sections_generated?.map((s: any) => {
        // Convert snake_case to Title Case for display with proper handling of acronyms
        const words = s.section_name?.split('_').map((word: string) => 
          word.charAt(0).toUpperCase() + word.slice(1)
        );
        const sectionName = words?.join(' ');
        
        // Handle special case for SWOT
        if (sectionName === 'Swot Analysis') {
          return 'SWOT Analysis';
        }
        
        return sectionName;
      }) || sectionNames;

      setGenerationStatus({
        status: "completed",
        sectionsGenerated: generatedSectionNames,
        currentSection: null,
        totalSections: result.total_sections || 8,
        error: null,
      });

      toast({
        title: "Success! ✨",
        description: `Successfully generated ${result.total_sections || 8} sections! View them in the form.`,
      });
    } catch (error: any) {
      console.error("Generation error:", error);
      
      setGenerationStatus({
        status: "error",
        sectionsGenerated: [],
        currentSection: null,
        totalSections: 8,
        error: error.message || "Failed to generate AI content",
      });

      toast({
        title: "Error",
        description: error.message || "Failed to generate AI content",
        variant: "destructive",
      });
    }
  };

  const getProgressPercentage = () => {
    if (generationStatus.status === "completed") return 100;
    if (generationStatus.status === "generating") return 50;
    return 0;
  };

  return (
    <div className="container mx-auto max-w-4xl py-8">
      {/* Loading state while checking for existing content */}
      {isCheckingExisting ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-3 text-muted-foreground">Checking for existing content...</span>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <Button
              variant="ghost"
              onClick={() => router.push(`/form/${formId}`)}
              className="mb-4"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Form
            </Button>

            <div className="flex items-center gap-4">
              <div className="bg-primary/10 p-3 rounded-lg">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">AI Content Generation</h1>
                <p className="text-muted-foreground">
                  Generate comprehensive content for all DPR sections using AI
                </p>
              </div>
            </div>
          </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Generation Progress</CardTitle>
          <CardDescription>
            AI will analyze your business and generate detailed content for all sections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{getProgressPercentage()}%</span>
            </div>
            <Progress value={getProgressPercentage()} className="h-2" />
          </div>

          {/* Current Status */}
          {generationStatus.status === "generating" && (
            <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-900">
              <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
              <div>
                <p className="font-medium text-blue-900 dark:text-blue-100">
                  {generationStatus.currentSection || "Generating content..."}
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  This may take 1-2 minutes. Please don't close this page.
                </p>
              </div>
            </div>
          )}

          {generationStatus.status === "completed" && (
            <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-950/30 rounded-lg border border-green-200 dark:border-green-900">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-900 dark:text-green-100">
                  All sections generated successfully!
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  AI has created comprehensive business analysis sections. Click "View Generated Content" to see the results.
                </p>
              </div>
            </div>
          )}

          {generationStatus.status === "error" && (
            <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200 dark:border-red-900">
              <div className="flex-1">
                <p className="font-medium text-red-900 dark:text-red-100">
                  Generation failed
                </p>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {generationStatus.error || "An error occurred during generation"}
                </p>
              </div>
            </div>
          )}

          {/* Section Checklist */}
          <div className="space-y-2">
            <h3 className="font-medium">Sections to Generate</h3>
            <div className="grid gap-2">
              {sectionNames.map((section, index) => {
                const isGenerated = generationStatus.sectionsGenerated.includes(section);
                const isGenerating = 
                  generationStatus.status === "generating" && 
                  index === generationStatus.sectionsGenerated.length;

                return (
                  <div
                    key={section}
                    className={`flex items-center gap-3 p-3 rounded-lg border ${
                      isGenerated
                        ? "bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900"
                        : isGenerating
                        ? "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900"
                        : "bg-muted/50"
                    }`}
                  >
                    {isGenerated ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : isGenerating ? (
                      <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30" />
                    )}
                    <span className={isGenerated ? "text-green-900 dark:text-green-100" : ""}>
                      {section}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            {generationStatus.status === "idle" || generationStatus.status === "error" ? (
              <Button
                onClick={handleGenerateAll}
                className="flex-1"
                size="lg"
              >
                <Sparkles className="mr-2 h-5 w-5" />
                Generate All Sections with AI
              </Button>
            ) : generationStatus.status === "completed" ? (
              <>
                <Button
                  onClick={() => router.push(`/preview/${formId}`)}
                  className="flex-1"
                  size="lg"
                >
                  <FileText className="mr-2 h-5 w-5" />
                  View Generated Content
                </Button>
                <Button
                  onClick={() => router.push(`/form/${formId}`)}
                  variant="outline"
                  size="lg"
                >
                  Back to Form
                </Button>
              </>
            ) : (
              <Button disabled className="flex-1" size="lg">
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Generating...
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Information Card */}
      <Card>
        <CardHeader>
          <CardTitle>How AI Generation Works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-3">
            <div className="bg-primary/10 p-2 rounded-lg h-fit">
              <span className="font-bold text-primary">1</span>
            </div>
            <div>
              <p className="font-medium">Analysis</p>
              <p className="text-sm text-muted-foreground">
                AI analyzes any existing information in your form
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="bg-primary/10 p-2 rounded-lg h-fit">
              <span className="font-bold text-primary">2</span>
            </div>
            <div>
              <p className="font-medium">Generation</p>
              <p className="text-sm text-muted-foreground">
                Creates comprehensive, professional content for each section
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="bg-primary/10 p-2 rounded-lg h-fit">
              <span className="font-bold text-primary">3</span>
            </div>
            <div>
              <p className="font-medium">Review & Edit</p>
              <p className="text-sm text-muted-foreground">
                You can review and customize the generated content as needed
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
        </>
      )}
    </div>
  );
}
