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

const entrepreneurSchema = z.object({
  fullName: z.string().min(2, "Name must be at least 2 characters"),
  dateOfBirth: z.string().min(1, "Date of birth is required"),
  education: z.string().min(1, "Education is required"),
  yearsOfExperience: z.coerce.number().min(0, "Years of experience must be 0 or more"),
  previousBusinessExperience: z.string().optional(),
  technicalSkills: z.string().optional(),
});

type EntrepreneurData = z.infer<typeof entrepreneurSchema>;

interface EntrepreneurDetailsFormProps {
  data: any;
  onSave: (data: any) => void;
  saving: boolean;
}

export default function EntrepreneurDetailsForm({ data, onSave, saving }: EntrepreneurDetailsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EntrepreneurData>({
    resolver: zodResolver(entrepreneurSchema),
    defaultValues: data || {},
  });

  const onSubmit = (formData: EntrepreneurData) => {
    // Convert camelCase to snake_case for backend
    const backendData = {
      full_name: formData.fullName,
      date_of_birth: formData.dateOfBirth,
      education: formData.education,
      years_of_experience: formData.yearsOfExperience,
      previous_business_experience: formData.previousBusinessExperience,
      technical_skills: formData.technicalSkills,
    };
    onSave(backendData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Entrepreneur Details</CardTitle>
          <CardDescription>
            Provide information about the entrepreneur/business owner
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Full Name */}
          <div className="space-y-2">
            <Label htmlFor="fullName">Full Name *</Label>
            <Input
              id="fullName"
              {...register("fullName")}
              placeholder="Enter your full name"
            />
            {errors.fullName && (
              <p className="text-sm text-destructive">{errors.fullName.message}</p>
            )}
          </div>

          {/* Date of Birth */}
          <div className="space-y-2">
            <Label htmlFor="dateOfBirth">Date of Birth *</Label>
            <Input
              id="dateOfBirth"
              type="date"
              {...register("dateOfBirth")}
            />
            {errors.dateOfBirth && (
              <p className="text-sm text-destructive">{errors.dateOfBirth.message}</p>
            )}
          </div>

          {/* Education */}
          <div className="space-y-2">
            <Label htmlFor="education">Education *</Label>
            <Input
              id="education"
              {...register("education")}
              placeholder="e.g., Bachelor's in Engineering"
            />
            {errors.education && (
              <p className="text-sm text-destructive">{errors.education.message}</p>
            )}
          </div>

          {/* Years of Experience */}
          <div className="space-y-2">
            <Label htmlFor="yearsOfExperience">Years of Experience *</Label>
            <Input
              id="yearsOfExperience"
              type="number"
              {...register("yearsOfExperience")}
              placeholder="0"
              min="0"
            />
            {errors.yearsOfExperience && (
              <p className="text-sm text-destructive">{errors.yearsOfExperience.message}</p>
            )}
          </div>

          {/* Previous Business Experience */}
          <div className="space-y-2">
            <Label htmlFor="previousBusinessExperience">
              Previous Business Experience
            </Label>
            <Textarea
              id="previousBusinessExperience"
              {...register("previousBusinessExperience")}
              placeholder="Describe any previous business ventures or entrepreneurial experience..."
              rows={4}
            />
          </div>

          {/* Technical Skills */}
          <div className="space-y-2">
            <Label htmlFor="technicalSkills">Technical Skills</Label>
            <Textarea
              id="technicalSkills"
              {...register("technicalSkills")}
              placeholder="List relevant technical skills and expertise..."
              rows={4}
            />
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
