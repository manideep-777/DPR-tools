/**
 * Analytics API functions
 */
import apiClient from './client';

export interface UserStats {
  total_forms: number;
  draft_forms: number;
  completed_forms: number;
  in_progress_forms: number;
  total_ai_generations: number;
  average_completion: number;
  last_activity: string | null;
}

/**
 * Get user statistics
 */
export async function getUserStats(): Promise<UserStats> {
  const response = await apiClient.get('/analytics/user-stats');
  return response.data;
}
