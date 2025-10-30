"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save } from "lucide-react";

const businessSchema = z.object({
  businessName: z.string().min(2, "Business name is required"),
  sector: z.string().min(1, "Sector is required"),
  subSector: z.string().optional(),
  legalStructure: z.string().min(1, "Legal structure is required"),
  registrationNumber: z.string().optional(),
  location: z.string().min(1, "Location is required"),
  address: z.string().min(1, "Address is required"),
});

type BusinessData = z.infer<typeof businessSchema>;

interface BusinessDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function BusinessDetailsForm({ data, onSave, saving }: BusinessDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<BusinessData>({
    resolver: zodResolver(businessSchema),
    defaultValues: data || {},
  });

  // Watch for legal structure to set default in Select component
  const legalStructure = watch("legalStructure");

  const onSubmit = (formData: BusinessData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      business_name: formData.businessName,
      sector: formData.sector,
      sub_sector: formData.subSector,
      legal_structure: formData.legalStructure,
      registration_number: formData.registrationNumber,
      location: formData.location,
      address: formData.address,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Business Details</CardTitle>
          <CardDescription>
            Provide information about your business
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Business Name */}
            <div className="space-y-2">
              <Label htmlFor="businessName">Business Name *</Label>
              <Input
                id="businessName"
                {...register("businessName")}
                placeholder="Enter business name"
              />
              {errors.businessName && (
                <p className="text-sm text-destructive">{errors.businessName.message}</p>
              )}
            </div>

            {/* Sector */}
            <div className="space-y-2">
              <Label htmlFor="sector">Sector *</Label>
              <Input
                id="sector"
                {...register("sector")}
                placeholder="e.g., Manufacturing, Services"
              />
              {errors.sector && (
                <p className="text-sm text-destructive">{errors.sector.message}</p>
              )}
            </div>

            {/* Sub Sector */}
            <div className="space-y-2">
              <Label htmlFor="subSector">Sub Sector</Label>
              <Input
                id="subSector"
                {...register("subSector")}
                placeholder="e.g., Textiles, Food Processing"
              />
            </div>

            {/* Legal Structure */}
            <div className="space-y-2">
              <Label htmlFor="legalStructure">Legal Structure *</Label>
              <Select 
                value={legalStructure}
                onValueChange={(value) => setValue("legalStructure", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select legal structure" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="proprietorship">Proprietorship</SelectItem>
                  <SelectItem value="partnership">Partnership</SelectItem>
                  <SelectItem value="LLP">LLP</SelectItem>
                  <SelectItem value="Pvt Ltd">Pvt Ltd</SelectItem>
                </SelectContent>
              </Select>
              {errors.legalStructure && (
                <p className="text-sm text-destructive">{errors.legalStructure.message}</p>
              )}
            </div>

            {/* Registration Number */}
            <div className="space-y-2">
              <Label htmlFor="registrationNumber">Registration Number</Label>
              <Input
                id="registrationNumber"
                {...register("registrationNumber")}
                placeholder="Enter registration number if available"
              />
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                {...register("location")}
                placeholder="City, State"
              />
              {errors.location && (
                <p className="text-sm text-destructive">{errors.location.message}</p>
              )}
            </div>
          </div>

          {/* Address */}
          <div className="space-y-2">
            <Label htmlFor="address">Complete Address *</Label>
            <Textarea
              id="address"
              {...register("address")}
              placeholder="Enter complete business address"
              rows={3}
            />
            {errors.address && (
              <p className="text-sm text-destructive">{errors.address.message}</p>
            )}
          </div>

          {/* Submit Button */}
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
