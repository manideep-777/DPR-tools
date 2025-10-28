/**
 * Authentication API endpoints
 */
import apiClient from './client';

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  business_type?: string;
  state?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  business_type?: string;
  state?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  access_token?: string;
  token_type?: string;
  user?: User;
  user_id?: number;
}

export const authApi = {
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<{ success: boolean; user: User }> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};
