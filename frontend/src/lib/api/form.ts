/**
 * DPR Form API functions
 */
import apiClient from './client';

export interface DprFormData {
  id?: number;
  user_id?: number;
  userId?: number;
  business_name?: string;
  formName?: string;
  status?: string;
  completion_percentage?: number;
  completionPercentage?: number;
  created_at?: string;
  createdAt?: string;
  last_modified?: string;
  updatedAt?: string;
  // Section data can come in either snake_case or camelCase
  entrepreneur_details?: any;
  entrepreneurDetails?: any;
  business_details?: any;
  businessDetails?: any;
  product_details?: any;
  productDetails?: any;
  financial_details?: any;
  financialDetails?: any;
  revenue_assumptions?: any;
  revenueAssumptions?: any;
  cost_details?: any;
  costDetails?: any;
  staffing_details?: any;
  staffingDetails?: any;
  timeline_details?: any;
  timelineDetails?: any;
}

export interface FormCreateResponse {
  success: boolean;
  message: string;
  form_id: number;
  business_name: string;
  status: string;
  created_at: string;
}

/**
 * Create a new DPR form
 */
export async function createForm(formName: string): Promise<FormCreateResponse> {
  const response = await apiClient.post('/form/create', { business_name: formName });
  return response.data;
}

/**
 * Get a specific form by ID with all section details
 */
export async function getFormById(formId: number): Promise<DprFormData> {
  // Use the /complete endpoint to get all sections
  const response = await apiClient.get(`/form/${formId}/complete`);
  return response.data;
}

/**
 * Update entire form
 */
export async function updateForm(formId: number, data: Partial<DprFormData>): Promise<DprFormData> {
  const response = await apiClient.put(`/form/${formId}`, data);
  return response.data;
}

/**
 * Update a specific form section
 */
export async function updateFormSection(
  formId: number,
  section: string,
  data: any
): Promise<DprFormData> {
  const response = await apiClient.put(`/form/${formId}/section/${section}`, data);
  return response.data;
}

/**
 * Delete a form
 */
export async function deleteForm(formId: number): Promise<void> {
  await apiClient.delete(`/form/${formId}`);
}

/**
 * Get all forms for the current user
 */
export async function getUserForms(): Promise<{ total_forms: number; forms: DprFormData[] }> {
  const response = await apiClient.get('/form/user/forms');
  return response.data;
}

/**
 * Generate AI content for a section
 */
export async function generateAIContent(
  formId: number,
  section: string
): Promise<any> {
  const response = await apiClient.post(`/form/${formId}/generate/${section}`);
  return response.data;
}
