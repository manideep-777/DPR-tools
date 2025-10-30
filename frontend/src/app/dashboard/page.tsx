"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/authStore";
import { useToast } from "@/hooks/use-toast";
import { createForm, getUserForms, deleteForm } from "@/lib/api/form";
import { getUserStats, UserStats } from "@/lib/api/analytics";
import { FileText, User, Mail, Phone, Building, MapPin, Plus, Loader2, BarChart3, Clock, CheckCircle2, FileEdit, Eye, Trash2, Sparkles, Building2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function DashboardPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { user, isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [creating, setCreating] = useState(false);
  const [userForms, setUserForms] = useState<any[]>([]);
  const [loadingForms, setLoadingForms] = useState(true);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
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
    // Fetch user forms and stats when authenticated
    if (isAuthenticated) {
      fetchUserForms();
      fetchUserStats();
    }
  }, [isAuthenticated]);

  const fetchUserForms = async () => {
    try {
      setLoadingForms(true);
      const response = await getUserForms();
      // Backend returns { total_forms, forms } - extract the forms array
      setUserForms(response.forms || []);
    } catch (error) {
      console.error("Error fetching forms:", error);
      setUserForms([]);
    } finally {
      setLoadingForms(false);
    }
  };

  const fetchUserStats = async () => {
    try {
      setLoadingStats(true);
      const stats = await getUserStats();
      setUserStats(stats);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setUserStats(null);
    } finally {
      setLoadingStats(false);
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

      // Navigate to the form editing page using form_id from response
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

      // Refresh the forms list and stats
      await fetchUserForms();
      await fetchUserStats();
      setDeleteDialogOpen(false);
      setFormToDelete(null);
    } catch (error: any) {
      console.error("Error deleting form:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to delete DPR form. Please try again.",
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
    }
  };

  const getStatusVariant = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'in-progress':
      case 'in_progress':
        return 'secondary';
      case 'draft':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[calc(100vh-200px)]">
        <p className="text-lg text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect to login
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Welcome, {user.full_name}!</h1>
        <p className="text-lg text-muted-foreground">
          Manage your DPR projects and profile information
        </p>
      </div>

      {/* Statistics Cards */}
      {loadingStats ? (
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : userStats ? (
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Forms</p>
                  <p className="text-3xl font-bold mt-2">{userStats.total_forms}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Draft Forms</p>
                  <p className="text-3xl font-bold mt-2">{userStats.draft_forms}</p>
                </div>
                <FileEdit className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Completed</p>
                  <p className="text-3xl font-bold mt-2">{userStats.completed_forms}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Avg Progress</p>
                  <p className="text-3xl font-bold mt-2">{userStats.average_completion}%</p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* User Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Profile Information
            </CardTitle>
            <CardDescription>Your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Name:</span>
              <span>{user.full_name}</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Email:</span>
              <span>{user.email}</span>
            </div>
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Phone:</span>
              <span>{user.phone}</span>
            </div>
            {user.business_type && (
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Business Type:</span>
                <span>{user.business_type}</span>
              </div>
            )}
            {user.state && (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">State:</span>
                <span>{user.state}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>Get started with your DPR</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full" 
              size="lg" 
              onClick={handleCreateForm}
              disabled={creating}
            >
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
            <Button 
              variant="outline" 
              className="w-full" 
              size="lg"
              onClick={() => router.push("/forms")}
            >
              <FileText className="mr-2 h-4 w-4" />
              View My DPRs ({userForms.length})
            </Button>
            <div className="pt-3 border-t">
              <p className="text-sm font-medium mb-2 text-muted-foreground">Government Schemes</p>
              <div className="space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full" 
                  size="lg"
                  onClick={() => router.push("/schemes")}
                >
                  <Building2 className="mr-2 h-4 w-4" />
                  Browse All Schemes
                </Button>
                <Button 
                  className="w-full" 
                  size="lg"
                  onClick={() => router.push("/schemes/ai-match")}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  AI Suggested Schemes
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent DPR Projects</CardTitle>
            <CardDescription>Your latest project reports</CardDescription>
          </div>
          {userForms.length > 4 && (
            <Button 
              variant="outline" 
              onClick={() => router.push("/forms")}
              size="sm"
            >
              View All ({userForms.length})
            </Button>
          )}
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
                No DPR projects yet
              </p>
              <Button onClick={handleCreateForm} disabled={creating}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First DPR
              </Button>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {userForms.slice(0, 4).map((form: any) => (
                  <Card key={form.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{form.business_name || `Form #${form.id}`}</h3>
                            <Badge variant={getStatusVariant(form.status)}>
                              {form.status === 'in_progress' ? 'In Progress' : form.status?.charAt(0).toUpperCase() + form.status?.slice(1)}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <BarChart3 className="h-3 w-3" />
                              Progress: <span className="font-medium text-foreground">{form.completion_percentage || 0}%</span>
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Created: {new Date(form.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            onClick={() => router.push(`/form/${form.id}`)}
                            size="sm"
                            variant="outline"
                          >
                            <FileText className="mr-2 h-4 w-4" />
                            Edit
                          </Button>
                          {(form.completion_percentage || 0) > 50 && (
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
              {userForms.length > 4 && (
                <div className="mt-6 text-center">
                  <Button 
                    variant="outline" 
                    onClick={() => router.push("/forms")}
                    className="w-full"
                  >
                    View All {userForms.length} Forms
                  </Button>
                </div>
              )}
            </>
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
