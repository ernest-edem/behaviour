export type UserRole = "admin" | "clinician" | "user";

export const ROLES = {
  ADMIN: "admin",
  CLINICIAN: "clinician",
  USER: "user",
} as const;

/**
 * Strict role validation
 */
export function hasRole(
  userRole: UserRole | null,
  allowedRoles: UserRole[]
): boolean {
  if (!userRole) return false;
  return allowedRoles.includes(userRole);
}

/**
 * Determines default landing page after login
 */
export function getDefaultRoute(role: UserRole | null): string {
  switch (role) {
    case "admin":
      return "/admin/dashboard";
    case "clinician":
      return "/clinician/dashboard";
    case "user":
    default:
      return "/dashboard";
  }
}

/**
 * Guards route access (pure logic)
 */
export function canAccessRoute(
  role: UserRole | null,
  allowed: UserRole[]
): boolean {
  return hasRole(role, allowed);
}

/**
 * Centralized navigation map (single source of truth)
 */
export const ROUTES = {
  DASHBOARD: "/dashboard",
  ADMIN: "/admin/dashboard",
  CLINICIAN: "/clinician/dashboard",

  ASSESSMENTS: "/assessments",
  PREDICTIONS: "/predictions",
  EXPLANATIONS: "/explanations",
  HISTORY: "/history",
} as const;