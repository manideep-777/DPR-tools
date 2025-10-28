/**
 * Auth store using Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, User } from '../api/auth';
import { toast } from 'sonner';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      setToken: (token) => {
        if (token) {
          localStorage.setItem('access_token', token);
        } else {
          localStorage.removeItem('access_token');
        }
        set({ token });
      },

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await authApi.login({ email, password });
          
          if (response.success && response.access_token && response.user) {
            get().setToken(response.access_token);
            get().setUser(response.user);
            // Centralized success toast
            toast.success('Login successful');
          } else {
            const msg = response.message || 'Login failed';
            toast.error(msg);
            throw new Error(msg);
          }
        } catch (error: any) {
          // Parse FastAPI validation errors if present
          const detail = error?.response?.data?.detail;
          if (Array.isArray(detail) && detail.length > 0) {
            const messages = detail.map((d: any) => d.msg || d.message || JSON.stringify(d));
            toast.error(messages.join('; '));
          } else if (typeof detail === 'string') {
            toast.error(detail);
          } else {
            toast.error(error?.message || 'Login failed');
          }
          console.error('Login error:', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          const response = await authApi.register(data);
          
          if (response.success) {
            // Centralized success toast for registration
            toast.success('Registration successful');
            // After registration, log in automatically
            await get().login(data.email, data.password);
          } else {
            const msg = response.message || 'Registration failed';
            toast.error(msg);
            throw new Error(msg);
          }
        } catch (error: any) {
          const detail = error?.response?.data?.detail;
          if (Array.isArray(detail) && detail.length > 0) {
            const messages = detail.map((d: any) => d.msg || d.message || JSON.stringify(d));
            toast.error(messages.join('; '));
          } else if (typeof detail === 'string') {
            toast.error(detail);
          } else {
            toast.error(error?.message || 'Registration failed');
          }
          console.error('Registration error:', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        authApi.logout();
        set({ user: null, token: null, isAuthenticated: false });
        toast.message('Logged out');
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, user: null, token: null });
          return;
        }

        try {
          const response = await authApi.getCurrentUser();
          if (response.success && response.user) {
            get().setUser(response.user);
            get().setToken(token);
          } else {
            get().logout();
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          get().logout();
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
