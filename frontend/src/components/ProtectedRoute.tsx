import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export type Role = "user" | "clinician" | "admin";

interface Props {
  allowedRoles: Role[];
  children?: React.ReactNode;
}

function normalizeRole(role: string | null | undefined): Role | null {
  if (!role) return null;

  const r = role.toLowerCase().trim();

  if (r === "admin" || r === "role_admin") return "admin";
  if (r === "clinician" || r === "role_clinician") return "clinician";
  if (r === "user" || r === "role_user") return "user";

  return null;
}

export default function ProtectedRoute({
  allowedRoles,
  children,
}: Props) {
  const { token, role, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;

  // not logged in
  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const normalizedRole = normalizeRole(role);

  // invalid role → treat as auth failure
  if (!normalizedRole) {
    return <Navigate to="/login" replace />;
  }

  // role not allowed
  if (!allowedRoles.includes(normalizedRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
}