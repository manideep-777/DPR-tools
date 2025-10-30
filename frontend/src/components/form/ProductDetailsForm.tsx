"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Save } from "lucide-react";

const schema = z.object({
  productName: z.string().min(1, "Product name is required"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  keyFeatures: z.string().optional(),
  targetCustomers: z.string().min(1, "Target customers is required"),
  currentCapacity: z.coerce.number().optional(),
  plannedCapacity: z.coerce.number().min(1, "Planned capacity is required"),
  uniqueSellingPoints: z.string().min(1, "USP is required"),
  qualityCertifications: z.string().optional(),
});

type ProductData = z.infer<typeof schema>;

interface ProductDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function ProductDetailsForm({ data, onSave, saving }: ProductDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProductData>({
    resolver: zodResolver(schema),
    defaultValues: data || {},
  });

  const handleFormSubmit = (formData: ProductData) => {
    // Convert keyFeatures string to array (split by newlines or commas)
    let keyFeaturesArray = null;
    if (formData.keyFeatures && formData.keyFeatures.trim()) {
      // Split by newlines and filter out empty lines
      keyFeaturesArray = formData.keyFeatures
        .split('\n')
        .map(f => f.trim())
        .filter(f => f.length > 0);
    }

    // Convert camelCase to snake_case for backend
    const backendData = {
      product_name: formData.productName,
      description: formData.description,
      key_features: keyFeaturesArray,
      target_customers: formData.targetCustomers,
      current_capacity: formData.currentCapacity,
      planned_capacity: formData.plannedCapacity,
      unique_selling_points: formData.uniqueSellingPoints,
      quality_certifications: formData.qualityCertifications,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Product/Service Details</CardTitle>
          <CardDescription>Describe your product or service</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="productName">Product/Service Name *</Label>
              <Input id="productName" {...register("productName")} />
              {errors.productName && (
                <p className="text-sm text-destructive">{errors.productName.message}</p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea 
                id="description" 
                {...register("description")}
                rows={3}
                placeholder="Detailed description of your product or service"
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="keyFeatures">Key Features (one per line)</Label>
              <Textarea 
                id="keyFeatures" 
                {...register("keyFeatures")}
                rows={4}
                placeholder="Durable&#10;Eco-friendly&#10;Cost-effective"
              />
              <p className="text-xs text-muted-foreground">Enter each feature on a new line</p>
              {errors.keyFeatures && (
                <p className="text-sm text-destructive">{errors.keyFeatures.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="targetCustomers">Target Customers *</Label>
              <Input id="targetCustomers" {...register("targetCustomers")} />
              {errors.targetCustomers && (
                <p className="text-sm text-destructive">{errors.targetCustomers.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="plannedCapacity">Planned Capacity *</Label>
              <Input type="number" id="plannedCapacity" {...register("plannedCapacity")} />
              {errors.plannedCapacity && (
                <p className="text-sm text-destructive">{errors.plannedCapacity.message}</p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="uniqueSellingPoints">Unique Selling Points *</Label>
              <Input id="uniqueSellingPoints" {...register("uniqueSellingPoints")} />
              {errors.uniqueSellingPoints && (
                <p className="text-sm text-destructive">{errors.uniqueSellingPoints.message}</p>
              )}
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
