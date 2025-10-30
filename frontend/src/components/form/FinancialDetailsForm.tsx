"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save, Calculator } from "lucide-react";

const schema = z.object({
  totalInvestmentAmount: z.coerce.number().min(1, "Total investment is required"),
  landCost: z.coerce.number().min(0),
  buildingCost: z.coerce.number().min(0),
  machineryCost: z.coerce.number().min(0),
  workingCapital: z.coerce.number().min(0),
  otherCosts: z.coerce.number().min(0),
  ownContribution: z.coerce.number().min(0),
  loanRequired: z.coerce.number().min(0),
});

type FinancialData = z.infer<typeof schema>;

interface FinancialDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function FinancialDetailsForm({ data, onSave, saving }: FinancialDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FinancialData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const landCost = watch("landCost") || 0;
  const buildingCost = watch("buildingCost") || 0;
  const machineryCost = watch("machineryCost") || 0;
  const workingCapital = watch("workingCapital") || 0;
  const otherCosts = watch("otherCosts") || 0;
  
  const calculatedTotal = Number(landCost) + Number(buildingCost) + Number(machineryCost) + Number(workingCapital) + Number(otherCosts);

  const handleFormSubmit = (formData: FinancialData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      total_investment_amount: formData.totalInvestmentAmount,
      land_cost: formData.landCost,
      building_cost: formData.buildingCost,
      machinery_cost: formData.machineryCost,
      working_capital: formData.workingCapital,
      other_costs: formData.otherCosts,
      own_contribution: formData.ownContribution,
      loan_required: formData.loanRequired,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Financial Details</CardTitle>
          <CardDescription>Provide investment and funding details (in ₹)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Investment Breakdown */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold flex items-center">
              <Calculator className="mr-2 h-4 w-4" />
              Investment Breakdown
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="landCost">Land Cost (₹)</Label>
                <Input type="number" id="landCost" {...register("landCost")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="buildingCost">Building Cost (₹)</Label>
                <Input type="number" id="buildingCost" {...register("buildingCost")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="machineryCost">Machinery Cost (₹)</Label>
                <Input type="number" id="machineryCost" {...register("machineryCost")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="workingCapital">Working Capital (₹)</Label>
                <Input type="number" id="workingCapital" {...register("workingCapital")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="otherCosts">Other Costs (₹)</Label>
                <Input type="number" id="otherCosts" {...register("otherCosts")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label>Calculated Total</Label>
                <div className="text-2xl font-bold text-primary">
                  ₹{calculatedTotal.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </div>
              </div>
            </div>
          </div>

          {/* Total Investment */}
          <div className="space-y-2">
            <Label htmlFor="totalInvestmentAmount">Total Investment Amount (₹) *</Label>
            <Input 
              type="number" 
              id="totalInvestmentAmount" 
              {...register("totalInvestmentAmount")} 
              step="0.01"
              placeholder="Enter total investment or use calculated total"
            />
            {errors.totalInvestmentAmount && (
              <p className="text-sm text-destructive">{errors.totalInvestmentAmount.message}</p>
            )}
          </div>

          {/* Funding Structure */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold">Funding Structure</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ownContribution">Own Contribution (₹)</Label>
                <Input type="number" id="ownContribution" {...register("ownContribution")} step="0.01" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="loanRequired">Loan Required (₹)</Label>
                <Input type="number" id="loanRequired" {...register("loanRequired")} step="0.01" />
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
