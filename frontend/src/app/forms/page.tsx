"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/authStore";
import { useToast } from "@/hooks/use-toast";
import { getUserForms, createForm, deleteForm } from "@/lib/api/form";
import { FileText, Loader2, Plus, Calendar, BarChart3, Eye, Edit, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function FormsPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [userForms, setUserForms] = useState<any[]>([]);
  const [loadingForms, setLoadingForms] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [formToDelete, setFormToDelete] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    // Check authentication on mount
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    // Fetch user forms when authenticated
    if (isAuthenticated) {
      fetchUserForms();
    }
  }, [isAuthenticated]);

  const fetchUserForms = async () => {
    try {
      setLoadingForms(true);
      const response = await getUserForms();
      setUserForms(response.forms || []);
    } catch (error) {
      console.error("Error fetching forms:", error);
      toast({
        title: "Error",
        description: "Failed to load forms. Please try again.",
        variant: "destructive",
      });
      setUserForms([]);
    } finally {
      setLoadingForms(false);
    }
  };

  const handleCreateForm = async () => {
    try {
      setCreating(true);
      const formName = `DPR Form - ${new Date().toLocaleDateString()}`;
      const response = await createForm(formName);
      
      toast({
        title: "Success",
        description: "DPR form created successfully!",
      });

      // Navigate to the form editing page
      router.push(`/form/${response.form_id}`);
    } catch (error) {
      console.error("Error creating form:", error);
      toast({
        title: "Error",
        description: "Failed to create DPR form. Please try again.",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteClick = (formId: number) => {
    setFormToDelete(formId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!formToDelete) return;

    try {
      setDeleting(true);
      await deleteForm(formToDelete);
      
      toast({
        title: "Success",
        description: "DPR form deleted successfully!",
      });

      // Refresh the forms list
      await fetchUserForms();
    } catch (error: any) {
      console.error("Error deleting form:", error);
      const errorMessage = error.response?.data?.detail || "Failed to delete form. Please try again.";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setFormToDelete(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline", label: string }> = {
      draft: { variant: "secondary", label: "Draft" },
      "in-progress": { variant: "default", label: "In Progress" },
      completed: { variant: "outline", label: "Completed" },
      submitted: { variant: "outline", label: "Submitted" },
    };

    const config = statusConfig[status] || { variant: "secondary", label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[calc(100vh-200px)]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <div className="container mx-auto px-4 py-16">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">My DPR Forms</h1>
          <p className="text-lg text-muted-foreground">
            Manage all your Detailed Project Reports
          </p>
        </div>
        <Button onClick={handleCreateForm} size="lg" disabled={creating}>
          {creating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <Plus className="mr-2 h-4 w-4" />
              Create New DPR
            </>
          )}
        </Button>
      </div>

      {/* Forms List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            All DPR Forms ({userForms.length})
          </CardTitle>
          <CardDescription>
            View and manage all your project reports
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingForms ? (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 mx-auto mb-4 text-muted-foreground animate-spin" />
              <p className="text-muted-foreground">Loading your forms...</p>
            </div>
          ) : userForms.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg text-muted-foreground mb-4">
                No DPR forms found
              </p>
              <Button onClick={handleCreateForm} disabled={creating}>
                {creating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First DPR
                  </>
                )}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {userForms.map((form: any) => (
                <Card key={form.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="font-semibold text-xl">
                            {form.business_name || `DPR Form #${form.id}`}
                          </h3>
                          {getStatusBadge(form.status)}
                        </div>
                        
                        <div className="grid md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>
                              Created: {new Date(form.created_at).toLocaleDateString("en-US", {
                                year: "numeric",
                                month: "short",
                                day: "numeric"
                              })}
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <BarChart3 className="h-4 w-4" />
                            <span>Progress: <span className="font-medium text-foreground">{form.completion_percentage || 0}%</span></span>
                          </div>

                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            <span>Form ID: <span className="font-medium text-foreground">#{form.id}</span></span>
                          </div>
                        </div>

                        {form.last_modified && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Last updated: {new Date(form.last_modified).toLocaleString("en-US", {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit"
                            })}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-col gap-2">
                        <Button 
                          onClick={() => router.push(`/form/${form.id}`)}
                          size="sm"
                          variant="default"
                        >
                          <Edit className="mr-2 h-4 w-4" />
                          {form.status === 'draft' || form.status === 'in-progress' ? 'Continue Editing' : 'Edit'}
                        </Button>
                        
                        {(form.completion_percentage >= 50 || form.status === 'completed') && (
                          <Button 
                            onClick={() => router.push(`/preview/${form.id}`)}
                            size="sm"
                            variant="outline"
                          >
                            <Eye className="mr-2 h-4 w-4" />
                            Preview
                          </Button>
                        )}

                        <Button 
                          onClick={() => handleDeleteClick(form.id)}
                          size="sm"
                          variant="destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete DPR Form</DialogTitle>
            <DialogDescription>
              Are you absolutely sure? This action cannot be undone. This will permanently delete your DPR form
              and all associated data including AI-generated content and financial projections.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Form
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
