import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, ChevronRight } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import RiskBadge from '../components/RiskBadge';
import { assessmentService } from '../services/assessmentService';
import { predictionService } from '../services/predictionService';
import { getApiErrorMessage, formatDate } from '../utils/format';
import { formatCondition } from '../utils/risk';
import type { Assessment, Prediction } from '../types';

interface AssessmentSummary extends Assessment {
  topPrediction?: Prediction;
}

const HistoryPage: React.FC = () => {
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        const list = await assessmentService.list();
        const withPredictions = await Promise.all(
          list.map(async (assessment) => {
            try {
              const preds = await predictionService.getByAssessment(assessment.id);
              const top = preds.predictions.reduce((max, p) =>
                p.confidence_score > (max?.confidence_score ?? 0) ? p : max
              , preds.predictions[0]);
              return { ...assessment, topPrediction: top };
            } catch {
              return { ...assessment, topPrediction: undefined };
            }
          })
        );
        setAssessments(withPredictions);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load assessment history.'));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading history..." />;
  if (error) return <ErrorAlert message={error} />;

  if (assessments.length === 0) {
    return (
      <div className="text-center py-16">
        <History className="mx-auto h-12 w-12 text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No assessments yet</h3>
        <p className="text-gray-500 mt-2">Your assessment history will appear here.</p>
      </div>
    );
  }

  return (
    <Card title="Assessment History" subtitle={`${assessments.length} total assessments`}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 uppercase border-b">
              <th className="py-3 px-4">Date</th>
              <th className="py-3 px-4">Age</th>
              <th className="py-3 px-4">Gender</th>
              <th className="py-3 px-4">BMI</th>
              <th className="py-3 px-4">Top Risk</th>
              <th className="py-3 px-4"></th>
            </tr>
          </thead>
          <tbody>
            {assessments.map((a) => (
              <tr
                key={a.id}
                onClick={() => navigate(`/history/${a.id}`)}
                className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="py-3 px-4 text-gray-700">{formatDate(a.created_at)}</td>
                <td className="py-3 px-4 font-medium text-gray-900">{a.age}</td>
                <td className="py-3 px-4 text-gray-600 capitalize">{a.gender}</td>
                <td className="py-3 px-4 text-gray-600">{a.bmi}</td>
                <td className="py-3 px-4">
                  {a.topPrediction ? (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-700">
                        {formatCondition(a.topPrediction.predicted_condition)}
                      </span>
                      <RiskBadge level={a.topPrediction.risk_level} />
                    </div>
                  ) : (
                    <span className="text-gray-400">No predictions</span>
                  )}
                </td>
                <td className="py-3 px-4 text-right">
                  <ChevronRight size={16} className="inline text-gray-400" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default HistoryPage;
