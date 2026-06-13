import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

type Role = "user" | "admin" | "clinician";

interface RoleRouteProps {
  allowedRoles: Role[];
  children: React.ReactNode;
}

// SAFE normalization (critical fix)
function normalizeRole(role: string | null | undefined): Role | null {
  if (!role) return null;

  const r = role.toLowerCase().trim();

  if (r === "admin") return "admin";
  if (r === "clinician") return "clinician";
  if (r === "user") return "user";

  return null;
}

const RoleRoute: React.FC<RoleRouteProps> = ({
  allowedRoles,
  children,
}) => {
  const { role, token } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const normalizedRole = normalizeRole(role);

  if (!normalizedRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  if (!allowedRoles.includes(normalizedRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default RoleRoute;