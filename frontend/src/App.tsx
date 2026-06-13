import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import { WorkflowProvider } from "./context/WorkflowContext";
import { useAuth } from "./auth/AuthContext";

import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

// pages
import Login from "./pages/Login";
import Register from "./pages/Register";

import DashboardHome from "./pages/DashboardHome";
import ClinicianDashboard from "./pages/clinician/ClinicianDashboard";
import AdminDashboard from "./pages/admin/AdminDashboard";

import AssessmentsPage from "./pages/AssessmentsPage";
import PredictionsPage from "./pages/PredictionsPage";
import ExplanationsPage from "./pages/ExplanationsPage";
import HistoryPage from "./pages/HistoryPage";
import HistoryDetailPage from "./pages/HistoryDetailPage";

import Unauthorized from "./pages/Unauthorized";
import { DEFAULT_ROUTES } from "./utils/rbacRoutes";
import type { UserRole } from "./utils/rbacRoutes";

/**
 * ROLE REDIRECT
 */
const RoleRedirect = () => {
  const { role, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated || !role) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={DEFAULT_ROUTES[role as UserRole]} replace />;
};

/**
 * ROUTES
 */
function AppRoutes() {
  return (
    <Routes>

      {/* PUBLIC */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      {/* ROOT */}
      <Route path="/" element={<RoleRedirect />} />

      {/* =========================
          USER (LAYOUT ROUTE)
      ========================= */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["user"]}>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardHome />} />
        <Route path="/assessments" element={<AssessmentsPage />} />
        <Route path="/predictions" element={<PredictionsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/history/:assessmentId" element={<HistoryDetailPage />} />
      </Route>

      {/* =========================
          CLINICIAN
      ========================= */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["clinician"]}>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/clinician/dashboard" element={<ClinicianDashboard />} />
        <Route path="/explanations" element={<ExplanationsPage />} />
      </Route>

      {/* =========================
          ADMIN
      ========================= */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["admin"]}>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Route>

      {/* FALLBACK */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}

/**
 * ROOT APP
 */
export default function App() {
  return (
    <Router>
      <AuthProvider>
        <WorkflowProvider>
          <AppRoutes />
        </WorkflowProvider>
      </AuthProvider>
    </Router>
  );
}