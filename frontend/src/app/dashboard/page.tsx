"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/authStore";
import { useToast } from "@/hooks/use-toast";
import { createForm, getUserForms } from "@/lib/api/form";
import { FileText, User, Mail, Phone, Building, MapPin, Plus, Loader2 } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { user, isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [creating, setCreating] = useState(false);
  const [userForms, setUserForms] = useState<any[]>([]);
  const [loadingForms, setLoadingForms] = useState(true);

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
      // Backend returns { total_forms, forms } - extract the forms array
      setUserForms(response.forms || []);
    } catch (error) {
      console.error("Error fetching forms:", error);
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
          </CardContent>
        </Card>
      </div>

      {/* Projects Section */}
      <Card>
        <CardHeader>
          <CardTitle>My DPR Projects</CardTitle>
          <CardDescription>Your recent DPR projects</CardDescription>
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
            <div className="space-y-4">
              {userForms.map((form: any) => (
                <Card key={form.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{form.business_name || `Form #${form.id}`}</h3>
                        <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                          <span>Status: <span className="font-medium text-foreground">{form.status}</span></span>
                          <span>Progress: <span className="font-medium text-foreground">{form.completion_percentage || 0}%</span></span>
                          <span>Created: {new Date(form.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          onClick={() => router.push(`/form/${form.id}`)}
                          size="sm"
                        >
                          <FileText className="mr-2 h-4 w-4" />
                          {form.status === 'draft' ? 'Continue Editing' : 'View'}
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
    </div>
  );
}
