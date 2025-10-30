"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save, Calendar } from "lucide-react";

const schema = z.object({
  landAcquisitionMonths: z.coerce.number().min(0),
  constructionMonths: z.coerce.number().min(0),
  machineryInstallationMonths: z.coerce.number().min(0),
  trialProductionMonths: z.coerce.number().min(0),
  commercialProductionStartMonth: z.coerce.number().min(1, "Commercial production start is required"),
});

type TimelineData = z.infer<typeof schema>;

interface TimelineDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function TimelineDetailsForm({ data, onSave, saving }: TimelineDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<TimelineData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const landAcquisition = watch("landAcquisitionMonths") || 0;
  const construction = watch("constructionMonths") || 0;
  const machineryInstallation = watch("machineryInstallationMonths") || 0;
  const trialProduction = watch("trialProductionMonths") || 0;

  const totalPreparationTime = Number(landAcquisition) + Number(construction) + Number(machineryInstallation) + Number(trialProduction);

  const handleFormSubmit = (formData: TimelineData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      land_acquisition_months: formData.landAcquisitionMonths,
      construction_months: formData.constructionMonths,
      machinery_installation_months: formData.machineryInstallationMonths,
      trial_production_months: formData.trialProductionMonths,
      commercial_production_start_month: formData.commercialProductionStartMonth,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Timeline Details</CardTitle>
          <CardDescription>Project implementation timeline (in months)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Project Phases */}
          <div className="bg-secondary/30 p-4 rounded-lg space-y-4">
            <h3 className="font-semibold flex items-center">
              <Calendar className="mr-2 h-4 w-4" />
              Project Phases (Months)
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="landAcquisitionMonths">Land Acquisition</Label>
                <Input 
                  type="number" 
                  id="landAcquisitionMonths" 
                  {...register("landAcquisitionMonths")} 
                  placeholder="Months for land acquisition"
                />
                <p className="text-xs text-muted-foreground">
                  Time to acquire and finalize land
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="constructionMonths">Construction</Label>
                <Input 
                  type="number" 
                  id="constructionMonths" 
                  {...register("constructionMonths")} 
                  placeholder="Months for construction"
                />
                <p className="text-xs text-muted-foreground">
                  Building and infrastructure setup
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="machineryInstallationMonths">Machinery Installation</Label>
                <Input 
                  type="number" 
                  id="machineryInstallationMonths" 
                  {...register("machineryInstallationMonths")} 
                  placeholder="Months for machinery setup"
                />
                <p className="text-xs text-muted-foreground">
                  Equipment procurement and installation
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="trialProductionMonths">Trial Production</Label>
                <Input 
                  type="number" 
                  id="trialProductionMonths" 
                  {...register("trialProductionMonths")} 
                  placeholder="Months for trial production"
                />
                <p className="text-xs text-muted-foreground">
                  Testing and quality assurance
                </p>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="font-medium">Total Preparation Time:</span>
                <span className="text-2xl font-bold text-primary">
                  {totalPreparationTime} months
                </span>
              </div>
            </div>
          </div>

          {/* Commercial Production Start */}
          <div className="space-y-2">
            <Label htmlFor="commercialProductionStartMonth">
              Commercial Production Start (Month) *
            </Label>
            <Input 
              type="number" 
              id="commercialProductionStartMonth" 
              {...register("commercialProductionStartMonth")} 
              placeholder="Month when commercial production begins"
            />
            {errors.commercialProductionStartMonth && (
              <p className="text-sm text-destructive">{errors.commercialProductionStartMonth.message}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Expected month (from project start) when full commercial production begins
            </p>
          </div>

          {/* Timeline Visualization */}
          <div className="bg-primary/10 p-4 rounded-lg">
            <h4 className="font-semibold mb-3">Timeline Overview</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Months 1-{landAcquisition || 0}:</span>
                <span className="font-medium">Land Acquisition</span>
              </div>
              <div className="flex justify-between">
                <span>Months {(Number(landAcquisition) || 0) + 1}-{(Number(landAcquisition) || 0) + (Number(construction) || 0)}:</span>
                <span className="font-medium">Construction</span>
              </div>
              <div className="flex justify-between">
                <span>Months {(Number(landAcquisition) || 0) + (Number(construction) || 0) + 1}-{(Number(landAcquisition) || 0) + (Number(construction) || 0) + (Number(machineryInstallation) || 0)}:</span>
                <span className="font-medium">Machinery Installation</span>
              </div>
              <div className="flex justify-between">
                <span>Months {totalPreparationTime - (Number(trialProduction) || 0) + 1}-{totalPreparationTime}:</span>
                <span className="font-medium">Trial Production</span>
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
