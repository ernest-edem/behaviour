import api from '../api/axios';
import type { LoginResponse } from '../types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export const authService = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<{ message: string; email: string }> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
};
