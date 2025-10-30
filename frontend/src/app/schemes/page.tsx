"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/lib/store/authStore";
import { useToast } from "@/hooks/use-toast";
import { getAllSchemes, Scheme } from "@/lib/api/schemes";
import { Loader2, ArrowLeft, ExternalLink, Building2, MapPin, IndianRupee, Tag, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function SchemesPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [filteredSchemes, setFilteredSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterSector, setFilterSector] = useState("all");

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
      fetchSchemes();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    applyFilters();
  }, [schemes, searchQuery, filterType, filterSector]);

  const fetchSchemes = async () => {
    try {
      setLoading(true);
      const data = await getAllSchemes();
      setSchemes(data);
      setFilteredSchemes(data);
    } catch (error: any) {
      console.error("Error fetching schemes:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to load government schemes",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...schemes];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (scheme) =>
          scheme.scheme_name.toLowerCase().includes(query) ||
          scheme.description.toLowerCase().includes(query) ||
          scheme.ministry.toLowerCase().includes(query)
      );
    }

    // Type filter
    if (filterType !== "all") {
      filtered = filtered.filter((scheme) => scheme.scheme_type.toLowerCase() === filterType.toLowerCase());
    }

    // Sector filter
    if (filterSector !== "all") {
      filtered = filtered.filter((scheme) =>
        scheme.eligible_sectors.some((sector) => sector.toLowerCase().includes(filterSector.toLowerCase()))
      );
    }

    setFilteredSchemes(filtered);
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

  if (isLoading || loading) {
    return (
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[calc(100vh-200px)]">
        <div className="text-center">
          <Loader2 className="h-12 w-12 mx-auto mb-4 text-primary animate-spin" />
          <p className="text-lg text-muted-foreground">Loading government schemes...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Government Schemes</h1>
            <p className="text-lg text-muted-foreground">
              Browse all available government schemes for MSMEs
            </p>
          </div>
          <Button
            size="lg"
            onClick={() => router.push("/schemes/ai-match")}
            className="gap-2"
          >
            <Sparkles className="h-5 w-5" />
            AI Suggested Schemes
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Search</label>
              <Input
                placeholder="Search schemes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Scheme Type</label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="subsidy">Subsidy</SelectItem>
                  <SelectItem value="loan">Loan</SelectItem>
                  <SelectItem value="grant">Grant</SelectItem>
                  <SelectItem value="training">Training</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Sector</label>
              <Select value={filterSector} onValueChange={setFilterSector}>
                <SelectTrigger>
                  <SelectValue placeholder="All Sectors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sectors</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="services">Services</SelectItem>
                  <SelectItem value="textile">Textile</SelectItem>
                  <SelectItem value="food processing">Food Processing</SelectItem>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="trading">Trading</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="mb-4">
        <p className="text-sm text-muted-foreground">
          Showing {filteredSchemes.length} of {schemes.length} schemes
        </p>
      </div>

      {/* Schemes Grid */}
      {filteredSchemes.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Building2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg text-muted-foreground mb-2">No schemes found</p>
            <p className="text-sm text-muted-foreground">Try adjusting your filters</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {filteredSchemes.map((scheme) => (
            <Card key={scheme.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{scheme.scheme_name}</CardTitle>
                    <CardDescription className="text-sm">{scheme.ministry}</CardDescription>
                  </div>
                  <Badge className={getSchemeTypeColor(scheme.scheme_type)}>
                    {scheme.scheme_type}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {scheme.description}
                </p>

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
                  variant="outline"
                  onClick={() => window.open(scheme.application_link, "_blank")}
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Visit Application Portal
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
