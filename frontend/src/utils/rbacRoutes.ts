export type UserRole = "user" | "clinician" | "admin";

export const DEFAULT_ROUTES: Record<UserRole, string> = {
  user: "/dashboard",
  clinician: "/clinician/dashboard",
  admin: "/admin/dashboard",
};