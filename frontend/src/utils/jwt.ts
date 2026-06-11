import { jwtDecode } from "jwt-decode";

export interface DecodedToken {
  sub: string;
  role?: "user" | "clinician" | "admin";
  email?: string;
  exp?: number;
}

export const decodeJWT = (token: string): DecodedToken | null => {
  try {
    return jwtDecode<DecodedToken>(token);
  } catch {
    return null;
  }
};