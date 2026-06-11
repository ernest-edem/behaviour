import { Routes, Route } from "react-router-dom";
import AppLayout from "../layouts/AppLayout";
import ProtectedRoute from "../components/ProtectedRoute";

import AdminDashboard from "../pages/admin/AdminDashboard";
import UserDashboard from "../pages/user/UserDashboard";
import ClinicianDashboard from "../pages/clinician/ClinicianDashboard";

export default function AppRouter() {
  return (
    <Routes>

      <Route
        element={
          <ProtectedRoute allowedRoles={["user", "admin", "clinician"]}>
            <AppLayout />
          </ProtectedRoute>
        }
      >

        {/* USER */}
        <Route path="/user" element={<UserDashboard />} />

        {/* ADMIN */}
        <Route path="/admin" element={<AdminDashboard />} />

        {/* CLINICIAN */}
        <Route path="/clinician" element={<ClinicianDashboard />} />

      </Route>

    </Routes>
  );
}