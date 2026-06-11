import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Brain, RefreshCw } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import RiskBadge from '../components/RiskBadge';
import { predictionService } from '../services/predictionService';
import { useWorkflow } from '../context/WorkflowContext';
import { getApiErrorMessage } from '../utils/format';
import {
  confidenceToPercent,
  formatCondition,
  getRiskCardBorder,
} from '../utils/risk';
import type { DiseasePredictionResult } from '../types';

const PredictionsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { currentAssessmentId, currentPredictions, setWorkflow } = useWorkflow();
  const [predictions, setPredictions] = useState<DiseasePredictionResult | null>(currentPredictions);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const assessmentId =
    Number(searchParams.get('assessmentId')) || currentAssessmentId;

  useEffect(() => {
    if (!assessmentId) {
      setLoading(false);
      return;
    }

    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await predictionService.getByAssessment(assessmentId);
        setPredictions(data);
        setWorkflow(assessmentId, data);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load predictions.'));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [assessmentId, setWorkflow]);

  const handleRegenerate = async () => {
    if (!assessmentId) return;
    setLoading(true);
    setError('');
    try {
      const data = await predictionService.generate(assessmentId);
      setPredictions(data);
      setWorkflow(assessmentId, data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to regenerate predictions.'));
    } finally {
      setLoading(false);
    }
  };

  if (!assessmentId && !loading) {
    return (
      <div className="text-center py-16">
        <Brain className="mx-auto h-12 w-12 text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No predictions available</h3>
        <p className="text-gray-500 mt-2 mb-6">Complete a health assessment to generate predictions.</p>
        <Link to="/assessments" className="text-primary-600 hover:underline font-medium">
          Go to Assessments →
        </Link>
      </div>
    );
  }

  if (loading) return <LoadingSpinner message="Loading predictions..." />;
  if (error) return <ErrorAlert message={error} />;
  if (!predictions) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4">
          <p className="text-sm text-purple-600 font-medium">Behavioral Phenotype</p>
          <p className="text-lg font-bold text-purple-900 mt-1">{predictions.behavioral_phenotype}</p>
        </div>
        <button onClick={handleRegenerate}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 border border-gray-300 px-4 py-2 rounded-lg hover:border-primary-300 transition-colors">
          <RefreshCw size={16} />
          Regenerate
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {predictions.predictions.map((prediction) => (
          <div
            key={prediction.id}
            className={`bg-white rounded-xl border border-gray-200 shadow-sm border-l-4 ${getRiskCardBorder(prediction.risk_level)} overflow-hidden`}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {formatCondition(prediction.predicted_condition)}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Source: {prediction.prediction_source}
                  </p>
                </div>
                <RiskBadge level={prediction.risk_level} />
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Confidence Score</span>
                  <span className="font-bold text-gray-900">
                    {confidenceToPercent(prediction.confidence_score)}%
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full transition-all ${
                      prediction.risk_level === 'high' || prediction.risk_level === 'critical'
                        ? 'bg-red-500'
                        : prediction.risk_level === 'moderate'
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${confidenceToPercent(prediction.confidence_score)}%` }}
                  />
                </div>
              </div>

              <Link
                to={`/explanations?predictionId=${prediction.id}`}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View explanations →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PredictionsPage;
