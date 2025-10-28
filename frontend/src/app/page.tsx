import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, BarChart, CheckCircle, Clock } from "lucide-react";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-16">
      {/* Hero Section */}
      <section className="text-center mb-16">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-linear-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          MSME DPR Generator
        </h1>
        <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
          Generate comprehensive Detailed Project Reports for your MSME business in minutes
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register">
            <Button size="lg" className="w-full sm:w-auto">
              Get Started
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="w-full sm:w-auto">
              Login
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <Card>
          <CardHeader>
            <FileText className="h-10 w-10 mb-2 text-primary" />
            <CardTitle>Professional Reports</CardTitle>
            <CardDescription>
              Generate detailed, professional DPRs tailored to your business needs
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <Clock className="h-10 w-10 mb-2 text-primary" />
            <CardTitle>Save Time</CardTitle>
            <CardDescription>
              Create comprehensive reports in minutes instead of days
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <BarChart className="h-10 w-10 mb-2 text-primary" />
            <CardTitle>Financial Analysis</CardTitle>
            <CardDescription>
              Automatic financial projections and feasibility analysis
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <CheckCircle className="h-10 w-10 mb-2 text-primary" />
            <CardTitle>Bank Ready</CardTitle>
            <CardDescription>
              Reports formatted for bank loan applications and government schemes
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      {/* About Section */}
      <section className="text-center max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-6">
          Built for Andhra Pradesh MSMEs
        </h2>
        <p className="text-lg text-muted-foreground mb-8">
          Our platform helps Micro, Small, and Medium Enterprises in Andhra Pradesh create detailed project reports 
          required for bank loans, government subsidies, and business planning. Streamline your documentation process 
          and focus on growing your business.
        </p>
      </section>
    </div>
  );
}
