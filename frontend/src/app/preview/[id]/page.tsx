"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, FileText, Download, Edit, Loader2 } from "lucide-react";
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

interface GeneratedSection {
  section_name: string;
  generated_text: string;
  ai_model_used: string;
  confidence_score: number;
  version_number: number;
  generated_at: string;
}

export default function PreviewPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const formId = params.id as string;

  const [sections, setSections] = useState<GeneratedSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [formName, setFormName] = useState("DPR Form");
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    fetchGeneratedContent();
  }, [formId]);

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
      toast({
        title: "Error",
        description: error.message || "Failed to load generated content",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
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

      // Refresh the content
      await fetchGeneratedContent();
      
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
            <p className="mt-4 text-muted-foreground">Loading generated content...</p>
          </div>
        </div>
      </div>
    );
  }

  if (sections.length === 0) {
    return (
      <div className="container mx-auto max-w-6xl py-8">
        <Button
          variant="ghost"
          onClick={() => router.push(`/form/${formId}`)}
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Form
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>No Generated Content</CardTitle>
            <CardDescription>
              No AI-generated content found for this form. Click the button below to generate content.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push(`/generate/${formId}`)}>
              Generate Content
            </Button>
          </CardContent>
        </Card>
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
        <p className="text-muted-foreground">AI-Generated Business Analysis</p>
      </div>

      <div className="space-y-6">
        {sections.map((section, index) => (
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
        ))}
      </div>

      <div className="mt-8 p-6 bg-muted/50 rounded-lg print:hidden">
        <h3 className="font-semibold mb-2">Next Steps</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
          <li>Review all sections for accuracy and completeness</li>
          <li>Edit or regenerate any section as needed</li>
          <li>Download the complete DPR as PDF for submission</li>
        </ul>
        <div className="mt-4 flex gap-2">
          <Button onClick={() => router.push(`/generate/${formId}`)}>
            Regenerate Content
          </Button>
          <Button variant="outline" onClick={() => router.push(`/form/${formId}`)}>
            Edit Form Data
          </Button>
        </div>
      </div>

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
