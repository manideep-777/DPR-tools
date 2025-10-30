"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save, TrendingUp } from "lucide-react";

const schema = z.object({
  productPrice: z.coerce.number().min(1, "Product price is required"),
  monthlySalesYear1: z.coerce.number().min(0),
  monthlySalesYear2: z.coerce.number().min(0),
  monthlySalesYear3: z.coerce.number().min(0),
  growthRate: z.coerce.number().min(0).max(100, "Growth rate must be between 0 and 100"),
});

type RevenueData = z.infer<typeof schema>;

interface RevenueAssumptionsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function RevenueAssumptionsForm({ data, onSave, saving }: RevenueAssumptionsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RevenueData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const productPrice = watch("productPrice") || 0;
  const monthlySalesYear1 = watch("monthlySalesYear1") || 0;
  const monthlySalesYear2 = watch("monthlySalesYear2") || 0;
  const monthlySalesYear3 = watch("monthlySalesYear3") || 0;

  const annualRevenueYear1 = Number(productPrice) * Number(monthlySalesYear1) * 12;
  const annualRevenueYear2 = Number(productPrice) * Number(monthlySalesYear2) * 12;
  const annualRevenueYear3 = Number(productPrice) * Number(monthlySalesYear3) * 12;

  const handleFormSubmit = (formData: RevenueData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      product_price: formData.productPrice,
      monthly_sales_quantity_year1: formData.monthlySalesYear1,
      monthly_sales_quantity_year2: formData.monthlySalesYear2,
      monthly_sales_quantity_year3: formData.monthlySalesYear3,
      growth_rate_percentage: formData.growthRate,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Revenue Assumptions</CardTitle>
          <CardDescription>Project your sales and revenue expectations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Pricing */}
          <div className="space-y-2">
            <Label htmlFor="productPrice">Product/Service Price (₹ per unit) *</Label>
            <Input 
              type="number" 
              id="productPrice" 
              {...register("productPrice")} 
              step="0.01"
              placeholder="Enter selling price per unit"
            />
            {errors.productPrice && (
              <p className="text-sm text-destructive">{errors.productPrice.message}</p>
            )}
          </div>

          {/* Sales Projections */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold flex items-center">
              <TrendingUp className="mr-2 h-4 w-4" />
              Monthly Sales Projections (Units)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="monthlySalesYear1">Year 1 (Monthly)</Label>
                <Input 
                  type="number" 
                  id="monthlySalesYear1" 
                  {...register("monthlySalesYear1")} 
                  step="0.01"
                />
                <div className="text-sm text-muted-foreground">
                  Annual: ₹{annualRevenueYear1.toLocaleString('en-IN')}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="monthlySalesYear2">Year 2 (Monthly)</Label>
                <Input 
                  type="number" 
                  id="monthlySalesYear2" 
                  {...register("monthlySalesYear2")} 
                  step="0.01"
                />
                <div className="text-sm text-muted-foreground">
                  Annual: ₹{annualRevenueYear2.toLocaleString('en-IN')}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="monthlySalesYear3">Year 3 (Monthly)</Label>
                <Input 
                  type="number" 
                  id="monthlySalesYear3" 
                  {...register("monthlySalesYear3")} 
                  step="0.01"
                />
                <div className="text-sm text-muted-foreground">
                  Annual: ₹{annualRevenueYear3.toLocaleString('en-IN')}
                </div>
              </div>
            </div>
          </div>

          {/* Growth Rate */}
          <div className="space-y-2">
            <Label htmlFor="growthRate">Expected Growth Rate (% per year)</Label>
            <Input 
              type="number" 
              id="growthRate" 
              {...register("growthRate")} 
              step="0.1"
              placeholder="Enter expected annual growth rate"
            />
            {errors.growthRate && (
              <p className="text-sm text-destructive">{errors.growthRate.message}</p>
            )}
          </div>

          <div className="flex justify-end pt-4">
            <Button type="submit" disabled={saving}>
              <Save className="mr-2 h-4 w-4" />
              {saving ? "Saving..." : "Save Section"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </form>
  );
}
