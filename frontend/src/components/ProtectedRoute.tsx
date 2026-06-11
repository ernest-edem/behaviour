import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export type Role = "user" | "clinician" | "admin";

interface Props {
  allowedRoles: Role[];
}

export default function ProtectedRoute({ allowedRoles }: Props) {
  const { token, role, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!token || !role) {
    return <Navigate to="/login" replace />;
  }

  // ❌ STRICT BLOCK (no fallback to another dashboard)
  if (!allowedRoles.includes(role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}