"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save, DollarSign } from "lucide-react";

const schema = z.object({
  monthlyRawMaterial: z.coerce.number().min(0),
  monthlyLabor: z.coerce.number().min(0),
  monthlyUtilities: z.coerce.number().min(0),
  monthlyRent: z.coerce.number().min(0),
  monthlyMarketing: z.coerce.number().min(0),
  otherFixedCosts: z.coerce.number().min(0),
});

type CostData = z.infer<typeof schema>;

interface CostDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function CostDetailsForm({ data, onSave, saving }: CostDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<CostData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const rawMaterial = watch("monthlyRawMaterial") || 0;
  const labor = watch("monthlyLabor") || 0;
  const utilities = watch("monthlyUtilities") || 0;
  const rent = watch("monthlyRent") || 0;
  const marketing = watch("monthlyMarketing") || 0;
  const otherFixed = watch("otherFixedCosts") || 0;

  const totalMonthlyCost = Number(rawMaterial) + Number(labor) + Number(utilities) + Number(rent) + Number(marketing) + Number(otherFixed);
  const totalAnnualCost = totalMonthlyCost * 12;

  const handleFormSubmit = (formData: CostData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      raw_material_cost_monthly: formData.monthlyRawMaterial,
      labor_cost_monthly: formData.monthlyLabor,
      utilities_cost_monthly: formData.monthlyUtilities,
      rent_monthly: formData.monthlyRent,
      marketing_cost_monthly: formData.monthlyMarketing,
      other_fixed_costs_monthly: formData.otherFixedCosts,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Cost Details</CardTitle>
          <CardDescription>Estimate your monthly operational costs (in ₹)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Variable Costs */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold flex items-center">
              <DollarSign className="mr-2 h-4 w-4" />
              Variable Costs (Monthly)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="monthlyRawMaterial">Raw Material Cost (₹)</Label>
                <Input 
                  type="number" 
                  id="monthlyRawMaterial" 
                  {...register("monthlyRawMaterial")} 
                  step="0.01"
                  placeholder="Monthly raw material expenses"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="monthlyLabor">Labor Cost (₹)</Label>
                <Input 
                  type="number" 
                  id="monthlyLabor" 
                  {...register("monthlyLabor")} 
                  step="0.01"
                  placeholder="Monthly labor wages"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="monthlyUtilities">Utilities (₹)</Label>
                <Input 
                  type="number" 
                  id="monthlyUtilities" 
                  {...register("monthlyUtilities")} 
                  step="0.01"
                  placeholder="Electricity, water, etc."
                />
              </div>
            </div>
          </div>

          {/* Fixed Costs */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold">Fixed Costs (Monthly)</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="monthlyRent">Rent (₹)</Label>
                <Input 
                  type="number" 
                  id="monthlyRent" 
                  {...register("monthlyRent")} 
                  step="0.01"
                  placeholder="Monthly rent"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="monthlyMarketing">Marketing (₹)</Label>
                <Input 
                  type="number" 
                  id="monthlyMarketing" 
                  {...register("monthlyMarketing")} 
                  step="0.01"
                  placeholder="Monthly marketing expenses"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="otherFixedCosts">Other Fixed Costs (₹)</Label>
                <Input 
                  type="number" 
                  id="otherFixedCosts" 
                  {...register("otherFixedCosts")} 
                  step="0.01"
                  placeholder="Insurance, licenses, etc."
                />
              </div>
            </div>
          </div>

          {/* Cost Summary */}
          <div className="bg-primary/10 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Total Monthly Cost</div>
                <div className="text-2xl font-bold text-primary">
                  ₹{totalMonthlyCost.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Total Annual Cost</div>
                <div className="text-2xl font-bold text-primary">
                  ₹{totalAnnualCost.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </div>
              </div>
            </div>
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
