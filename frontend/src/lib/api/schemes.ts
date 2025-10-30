/**
 * Government Schemes API functions
 */
import apiClient from './client';

export interface Scheme {
  id: number;
  scheme_name: string;
  ministry: string;
  scheme_type: string;
  description: string;
  subsidy_percentage: string | null;
  max_subsidy_amount: string | null;
  eligible_sectors: string[];
  eligible_states: string[];
  min_investment: string;
  max_investment: string;
  eligibility_criteria: string;
  application_link: string;
  match_score?: number;
  match_reasons?: string[];
  key_benefit?: string;
}

export interface SchemeMatchResponse {
  success: boolean;
  form_id: number;
  business_name: string;
  total_matches: number;
  matched_schemes: Scheme[];
  message: string;
}

/**
 * Get all available government schemes
 */
export async function getAllSchemes(): Promise<Scheme[]> {
  const response = await apiClient.get('/schemes/all');
  return response.data;
}

/**
 * Match government schemes based on form data
 * @param formId - The DPR form ID to match schemes against
 * @param maxResults - Maximum number of results to return (default: 10)
 */
export async function matchSchemes(formId: number, maxResults: number = 10): Promise<SchemeMatchResponse> {
  const response = await apiClient.post(`/schemes/match/${formId}`, { max_results: maxResults });
  return response.data;
}
