import api from "../api/axios";
import type { LoginResponse } from "../types";

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
    try {
      const response = await api.post<LoginResponse>(
        "/auth/login",
        data
      );

      console.log("LOGIN SUCCESS:", response.data);

      return response.data;
    } catch (error: any) {
      console.error("LOGIN ERROR");

      console.error("Status:", error.response?.status);
      console.error("Data:", error.response?.data);
      console.error(error);

      throw error;
    }
  },

  register: async (
    data: RegisterRequest
  ): Promise<{ message: string; email: string }> => {
    const response = await api.post(
      "/auth/register",
      data
    );

    return response.data;
  },
};