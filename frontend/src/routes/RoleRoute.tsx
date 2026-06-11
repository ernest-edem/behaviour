import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type Role = "user" | "admin" | "clinician";

interface RoleRouteProps {
  allowedRoles: Role[];
  children: React.ReactNode;
}

const RoleRoute: React.FC<RoleRouteProps> = ({
  allowedRoles,
  children,
}) => {
  const { role, token } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!role || !allowedRoles.includes(role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default RoleRoute;