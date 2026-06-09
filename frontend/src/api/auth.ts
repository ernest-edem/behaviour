import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: "admin" | "user";
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

export const registerUser = async (
  data: RegisterRequest
): Promise<{ message: string; email: string }> => {
  const response = await apiClient.post("/auth/register", data);

  return response.data;
};

export const loginUser = async (
  data: LoginRequest
): Promise<LoginResponse> => {
  const response = await apiClient.post("/auth/login", data);

  return response.data;
};