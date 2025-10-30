"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save, Users } from "lucide-react";

const schema = z.object({
  totalEmployees: z.coerce.number().min(1, "Total employees is required"),
  managementCount: z.coerce.number().min(0),
  technicalStaffCount: z.coerce.number().min(0),
  supportStaffCount: z.coerce.number().min(0),
  averageSalary: z.coerce.number().min(0),
});

type StaffingData = z.infer<typeof schema>;

interface StaffingDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function StaffingDetailsForm({ data, onSave, saving }: StaffingDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<StaffingData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const managementCount = watch("managementCount") || 0;
  const technicalStaffCount = watch("technicalStaffCount") || 0;
  const supportStaffCount = watch("supportStaffCount") || 0;
  const averageSalary = watch("averageSalary") || 0;

  const calculatedTotal = Number(managementCount) + Number(technicalStaffCount) + Number(supportStaffCount);
  const totalMonthlySalary = calculatedTotal * Number(averageSalary);
  const totalAnnualSalary = totalMonthlySalary * 12;

  const handleFormSubmit = (formData: StaffingData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      total_employees: formData.totalEmployees,
      management_count: formData.managementCount,
      technical_staff_count: formData.technicalStaffCount,
      support_staff_count: formData.supportStaffCount,
      average_salary: formData.averageSalary,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Staffing Details</CardTitle>
          <CardDescription>Define your team structure and salary expectations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Team Structure */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold flex items-center">
              <Users className="mr-2 h-4 w-4" />
              Team Structure
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="managementCount">Management Staff</Label>
                <Input 
                  type="number" 
                  id="managementCount" 
                  {...register("managementCount")} 
                  placeholder="Number of managers"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="technicalStaffCount">Technical Staff</Label>
                <Input 
                  type="number" 
                  id="technicalStaffCount" 
                  {...register("technicalStaffCount")} 
                  placeholder="Number of technical staff"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="supportStaffCount">Support Staff</Label>
                <Input 
                  type="number" 
                  id="supportStaffCount" 
                  {...register("supportStaffCount")} 
                  placeholder="Number of support staff"
                />
              </div>

              <div className="space-y-2">
                <Label>Calculated Total Staff</Label>
                <div className="text-2xl font-bold text-primary">
                  {calculatedTotal}
                </div>
              </div>
            </div>
          </div>

          {/* Total Employees */}
          <div className="space-y-2">
            <Label htmlFor="totalEmployees">Total Employees *</Label>
            <Input 
              type="number" 
              id="totalEmployees" 
              {...register("totalEmployees")} 
              placeholder="Enter total employees or use calculated total"
            />
            {errors.totalEmployees && (
              <p className="text-sm text-destructive">{errors.totalEmployees.message}</p>
            )}
          </div>

          {/* Salary Information */}
          <div className="space-y-2">
            <Label htmlFor="averageSalary">Average Monthly Salary (₹)</Label>
            <Input 
              type="number" 
              id="averageSalary" 
              {...register("averageSalary")} 
              step="0.01"
              placeholder="Average salary per employee"
            />
          </div>

          {/* Salary Summary */}
          <div className="bg-primary/10 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Total Monthly Salary</div>
                <div className="text-2xl font-bold text-primary">
                  ₹{totalMonthlySalary.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Total Annual Salary</div>
                <div className="text-2xl font-bold text-primary">
                  ₹{totalAnnualSalary.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
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
