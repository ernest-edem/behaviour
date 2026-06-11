import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import TopNavbar from "../components/TopNavbar";
import { useAuth } from "../auth/AuthContext";

const pageTitles: Record<string, { title: string; subtitle?: string }> = {
  "/dashboard": {
    title: "Dashboard",
    subtitle: "Health overview and AI insights",
  },
  "/assessments": {
    title: "Health Assessment",
    subtitle: "Submit a new health assessment",
  },
  "/predictions": {
    title: "Disease Predictions",
    subtitle: "AI-powered risk analysis",
  },
  "/explanations": {
    title: "Explainable AI",
    subtitle: "Understand your risk factors",
  },
  "/history": {
    title: "Assessment History",
    subtitle: "Past assessments and results",
  },
  "/admin": {
    title: "Admin Panel",
    subtitle: "System management and user control",
  },
  "/clinician": {
    title: "Clinician Dashboard",
    subtitle: "Patient monitoring and triage",
  },
};

export default function DashboardLayout() {
  const location = useLocation();
  const { role, loading } = useAuth();

  // -----------------------------
  // LOADING GUARD (IMPORTANT)
  // -----------------------------
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        Loading dashboard...
      </div>
    );
  }

  // -----------------------------
  // SAFE ROUTE MATCHING
  // -----------------------------
  const match = Object.keys(pageTitles)
    .sort((a, b) => b.length - a.length)
    .find((path) => location.pathname === path || location.pathname.startsWith(path + "/"));

  const pageInfo = match
    ? pageTitles[match]
    : {
        title: "BehaviorLens AI",
        subtitle: role ? `Logged in as ${role}` : undefined,
      };

  // -----------------------------
  // ROLE SANITY CHECK (UI SAFETY ONLY)
  // -----------------------------
  const safeRole = role ?? "user";

  return (
    <div className="min-h-screen bg-gray-50 flex">

      {/* Sidebar (UI only, RBAC enforced at route level) */}
      <Sidebar role={safeRole} />

      {/* Main layout */}
      <div className="flex-1 flex flex-col">

        <TopNavbar
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
        />

        <main className="p-8">
          <Outlet />
        </main>

      </div>
    </div>
  );
}