"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface DashboardStats {
  total_dprs: number;
  dprs_this_month: number;
  total_investment: number;
  recent_dprs: Array<{
    id: number;
    project_name: string;
    sector: string;
    investment_amount: number;
    status: string;
    created_at: string;
  }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/users/dashboard-stats", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }
        throw new Error("Failed to fetch dashboard data");
      }

      const data = await response.json();
      setStats(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/");
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`;
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} L`;
    } else {
      return `₹${amount.toLocaleString("en-IN")}`;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-medium">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-medium text-red-600">{error}</div>
          <Button onClick={fetchDashboardData} className="mt-4">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg"></div>
              <span className="font-bold text-xl">MSME DPR Generator</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage your DPRs and track project statistics</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardDescription>Total DPRs</CardDescription>
              <CardTitle className="text-3xl">{stats?.total_dprs || 0}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                All-time project reports created
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>This Month</CardDescription>
              <CardTitle className="text-3xl">{stats?.dprs_this_month || 0}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                DPRs generated in last 30 days
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Total Investment</CardDescription>
              <CardTitle className="text-3xl">
                {stats?.total_investment ? formatCurrency(stats.total_investment) : "₹0"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Combined project value
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Action Button */}
        <div className="mb-6">
          <Link href="/dashboard/create">
            <Button size="lg">
              + Create New DPR
            </Button>
          </Link>
        </div>

        {/* Recent DPRs Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent DPRs</CardTitle>
            <CardDescription>Your latest project reports</CardDescription>
          </CardHeader>
          <CardContent>
            {stats?.recent_dprs && stats.recent_dprs.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Project Name</TableHead>
                    <TableHead>Sector</TableHead>
                    <TableHead>Investment</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats.recent_dprs.map((dpr) => (
                    <TableRow key={dpr.id}>
                      <TableCell className="font-medium">{dpr.project_name}</TableCell>
                      <TableCell>{dpr.sector}</TableCell>
                      <TableCell>{formatCurrency(dpr.investment_amount)}</TableCell>
                      <TableCell>
                        <Badge variant={dpr.status === "GENERATED" ? "default" : "secondary"}>
                          {dpr.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(dpr.created_at)}</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg
                    className="mx-auto h-12 w-12"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No DPRs yet</h3>
                <p className="text-gray-600 mb-4">
                  Get started by creating your first Detailed Project Report
                </p>
                <Link href="/dashboard/create">
                  <Button>Create Your First DPR</Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
