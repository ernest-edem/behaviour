import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users, AlertTriangle, Brain } from "lucide-react";

import StatCard from "../../components/StatCard";
import Card from "../../components/Card";
import RiskBadge from "../../components/RiskBadge";
import LoadingSpinner from "../../components/LoadingSpinner";
import ErrorAlert from "../../components/ErrorAlert";

import { assessmentService } from "../../services/assessmentService";
import { getApiErrorMessage } from "../../utils/format";

import type { Assessment } from "../../types";

interface ClinicianPatientView {
  user_id: number;
  latest_assessment: Assessment;
  risk_level: string;
  condition: string;
  confidence: number;
}

const ClinicianDashboard: React.FC = () => {
  const [patients, setPatients] = useState<ClinicianPatientView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const allAssessments = await assessmentService.list();

        if (!mounted) return;

        // -----------------------------
        // STEP 1: GROUP BY USER (IMPORTANT FIX)
        // -----------------------------
        const grouped = new Map<number, Assessment>();

        for (const a of allAssessments) {
          const existing = grouped.get(a.user_id);

          if (
            !existing ||
            new Date(a.created_at) > new Date(existing.created_at)
          ) {
            grouped.set(a.user_id, a);
          }
        }

        // -----------------------------
        // STEP 2: BUILD CLINICIAN VIEW (NO N+1 CALLS)
        // -----------------------------
        const enriched: ClinicianPatientView[] = Array.from(
          grouped.values()
        ).map((latest) => {
          return {
            user_id: latest.user_id,
            latest_assessment: latest,
            risk_level: "unknown", // backend should provide this in Sprint 6+
            condition: "pending-analysis",
            confidence: 0,
          };
        });

        if (mounted) {
          setPatients(enriched);
        }
      } catch (err) {
        if (mounted) {
          setError(
            getApiErrorMessage(err, "Failed to load clinician dashboard")
          );
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, []);

  // -----------------------------
  // LOADING / ERROR
  // -----------------------------
  if (loading) {
    return <LoadingSpinner message="Loading clinician dashboard..." />;
  }

  if (error) {
    return <ErrorAlert message={error} />;
  }

  // -----------------------------
  // METRICS
  // -----------------------------
  const totalPatients = patients.length;

  const highRiskPatients = patients.filter(
    (p) => p.risk_level === "high" || p.risk_level === "critical"
  ).length;

  const avgRisk =
    patients.reduce((acc, p) => acc + p.confidence, 0) /
    (patients.length || 1);

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Clinician Dashboard
        </h1>
        <p className="text-sm text-gray-500">
          Patient risk monitoring & clinical triage
        </p>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        <StatCard
          title="Total Patients"
          value={totalPatients}
          subtitle="Unique users"
          icon={Users}
        />

        <StatCard
          title="High Risk Cases"
          value={highRiskPatients}
          subtitle="Require attention"
          icon={AlertTriangle}
          iconColor="text-red-600 bg-red-50"
        />

        <StatCard
          title="Avg Risk Confidence"
          value={`${Math.round(avgRisk * 100)}%`}
          subtitle="System baseline"
          icon={Brain}
          iconColor="text-purple-600 bg-purple-50"
        />

      </div>

      {/* TABLE */}
      <Card title="Patient Overview">
        <div className="space-y-3">

          {/* HEADER */}
          <div className="grid grid-cols-5 text-xs font-semibold text-gray-500 border-b pb-2">
            <span>Patient ID</span>
            <span>Condition</span>
            <span>Risk</span>
            <span>Confidence</span>
            <span>Action</span>
          </div>

          {/* ROWS */}
          {patients.map((p) => (
            <div
              key={p.user_id}
              className="grid grid-cols-5 items-center py-3 border-b last:border-0"
            >
              <span className="text-sm text-gray-700">
                #{p.user_id}
              </span>

              <span className="text-sm text-gray-700">
                {p.condition}
              </span>

              <RiskBadge level={p.risk_level as any} />

              <span className="text-sm text-gray-500">
                {Math.round(p.confidence * 100)}%
              </span>

              <Link
                to={`/explanations?user=${p.user_id}`}
                className="text-sm text-blue-600 hover:underline"
              >
                View insights
              </Link>
            </div>
          ))}

        </div>
      </Card>

    </div>
  );
};

export default ClinicianDashboard;