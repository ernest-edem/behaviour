import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ClipboardCheck, Brain, Users, Activity } from "lucide-react";

import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";
import RiskBadge from "../components/RiskBadge";
import Card from "../components/Card";

import { assessmentService } from "../services/assessmentService";
import { predictionService } from "../services/predictionService";
import { getApiErrorMessage } from "../utils/format";
import { confidenceToPercent, formatCondition } from "../utils/risk";

import type { Assessment, DiseasePredictionResult } from "../types";

const DashboardHome: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [latestPredictions, setLatestPredictions] =
    useState<DiseasePredictionResult | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      try {
        const list = await assessmentService.list();

        if (!isMounted) return;

        setAssessments(list || []);

        // SAFE GUARD
        const firstAssessmentId = list?.[0]?.id;

        if (firstAssessmentId) {
          try {
            const predictions =
              await predictionService.getByAssessment(firstAssessmentId);

            if (isMounted) {
              setLatestPredictions(predictions ?? null);
            }
          } catch {
            if (isMounted) setLatestPredictions(null);
          }
        } else {
          setLatestPredictions(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(getApiErrorMessage(err, "Failed to load dashboard data."));
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    load();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading clinical dashboard..." />;
  }

  if (error) {
    return <ErrorAlert message={error} />;
  }

  const predictions = latestPredictions?.predictions ?? [];

  const highestRisk = predictions.length
    ? predictions.reduce((max, p) =>
        p.confidence_score > (max?.confidence_score ?? 0) ? p : max
      )
    : null;

  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Clinical Health Dashboard
        </h1>
        <p className="text-sm text-gray-500">
          AI-powered health insights based on your latest assessment
        </p>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        <StatCard
          title="Total Assessments"
          value={assessments.length}
          subtitle="Completed health assessments"
          icon={ClipboardCheck}
        />

        <StatCard
          title="Latest Risk Score"
          value={
            highestRisk
              ? `${confidenceToPercent(highestRisk.confidence_score)}%`
              : "—"
          }
          subtitle={
            highestRisk
              ? formatCondition(highestRisk.predicted_condition)
              : "No predictions yet"
          }
          icon={Brain}
        />

        <StatCard
          title="Behavioral Profile"
          value={latestPredictions ? "Generated" : "—"}
          subtitle={latestPredictions?.behavioral_phenotype ?? "Pending"}
          icon={Users}
        />

        <StatCard
          title="System Status"
          value={assessments.length > 0 ? "Active" : "Idle"}
          subtitle="Monitoring enabled"
          icon={Activity}
        />
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* QUICK ACTIONS */}
        <Card title="Quick Actions">
          <div className="space-y-3">

            <Link
              to="/assessments"
              className="flex justify-between p-4 border rounded-lg hover:bg-blue-50"
            >
              <div>
                <p className="font-medium">New Assessment</p>
                <p className="text-sm text-gray-500">
                  Submit health data
                </p>
              </div>
              <ClipboardCheck className="text-blue-600" />
            </Link>

            <Link
              to="/history"
              className="flex justify-between p-4 border rounded-lg hover:bg-blue-50"
            >
              <div>
                <p className="font-medium">View History</p>
                <p className="text-sm text-gray-500">
                  Past results
                </p>
              </div>
              <Brain className="text-blue-600" />
            </Link>

          </div>
        </Card>

        {/* PREDICTIONS */}
        <Card title="Latest Predictions">
          {predictions.length ? (
            <div className="space-y-3">

              {predictions.slice(0, 5).map((p) => (
                <div
                  key={p.id}
                  className="flex justify-between border-b py-2"
                >
                  <span>{formatCondition(p.predicted_condition)}</span>

                  <div className="flex gap-2 items-center">
                    <span className="text-sm text-gray-500">
                      {confidenceToPercent(p.confidence_score)}%
                    </span>
                    <RiskBadge level={p.risk_level} />
                  </div>
                </div>
              ))}

              <Link
                to="/predictions"
                className="text-blue-600 text-sm"
              >
                View full analysis →
              </Link>
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              No predictions yet. Run an assessment to generate insights.
            </p>
          )}
        </Card>

      </div>
    </div>
  );
};

export default DashboardHome;