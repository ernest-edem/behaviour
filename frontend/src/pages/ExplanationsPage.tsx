import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Lightbulb, Loader2, RefreshCw } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import RiskBadge from '../components/RiskBadge';
import { explanationService } from '../services/explanationService';
import { predictionService } from '../services/predictionService';
import { useWorkflow } from '../context/WorkflowContext';
import { getApiErrorMessage } from '../utils/format';
import { formatCondition, getSeverityColor } from '../utils/risk';
import type { Prediction, PredictionExplanation } from '../types';

const ExplanationsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { currentAssessmentId, currentPredictions } = useWorkflow();
  const [predictions, setPredictions] = useState<Prediction[]>(currentPredictions?.predictions ?? []);
  const [explanations, setExplanations] = useState<Record<number, PredictionExplanation>>({});
  const [loadingIds, setLoadingIds] = useState<Set<number>>(new Set());
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState('');

  const selectedPredictionId = Number(searchParams.get('predictionId')) || null;
  const assessmentId = currentAssessmentId;

  useEffect(() => {
    const load = async () => {
      if (!assessmentId) {
        setPageLoading(false);
        return;
      }
      try {
        const data = await predictionService.getByAssessment(assessmentId);
        setPredictions(data.predictions);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load predictions.'));
      } finally {
        setPageLoading(false);
      }
    };
    load();
  }, [assessmentId]);

  const loadExplanation = useCallback(async (predictionId: number, regenerate = false) => {
    setLoadingIds((prev) => new Set(prev).add(predictionId));
    try {
      const data = regenerate
        ? await explanationService.generate(predictionId)
        : await (async () => {
            try {
              return await explanationService.getByPrediction(predictionId);
            } catch {
              return await explanationService.generate(predictionId);
            }
          })();
      setExplanations((prev) => ({ ...prev, [predictionId]: data }));
    } catch (err) {
      setError(getApiErrorMessage(err, `Failed to load explanations for prediction #${predictionId}.`));
    } finally {
      setLoadingIds((prev) => {
        const next = new Set(prev);
        next.delete(predictionId);
        return next;
      });
    }
  }, []);

  useEffect(() => {
    if (selectedPredictionId && predictions.length > 0) {
      loadExplanation(selectedPredictionId);
    }
  }, [selectedPredictionId, predictions.length, loadExplanation]);

  if (!assessmentId && !pageLoading) {
    return (
      <div className="text-center py-16">
        <Lightbulb className="mx-auto h-12 w-12 text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No explanations available</h3>
        <p className="text-gray-500 mt-2 mb-6">Generate predictions first to view explanations.</p>
        <Link to="/assessments" className="text-primary-600 hover:underline font-medium">
          Go to Assessments →
        </Link>
      </div>
    );
  }

  if (pageLoading) return <LoadingSpinner message="Loading explanations..." />;

  return (
    <div className="space-y-6">
      {error && <ErrorAlert message={error} />}

      {predictions.map((prediction) => {
        const explanation = explanations[prediction.id];
        const isLoading = loadingIds.has(prediction.id);
        const isExpanded = selectedPredictionId === prediction.id || explanation;

        return (
          <Card
            key={prediction.id}
            title={formatCondition(prediction.predicted_condition)}
            subtitle={`Prediction #${prediction.id} · ${prediction.behavioral_phenotype}`}
          >
            <div className="flex items-center gap-3 mb-4">
              <RiskBadge level={prediction.risk_level} />
              {!explanation && !isLoading && (
                <button
                  onClick={() => loadExplanation(prediction.id, true)}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
                >
                  <Lightbulb size={14} />
                  Generate Explanations
                </button>
              )}
              {explanation && (
                <button
                  onClick={() => loadExplanation(prediction.id, true)}
                  className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1"
                >
                  <RefreshCw size={14} />
                  Regenerate
                </button>
              )}
            </div>

            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-gray-500 py-4">
                <Loader2 className="animate-spin" size={16} />
                Generating explanations...
              </div>
            )}

            {explanation && isExpanded && (
              <div className="space-y-3">
                {explanation.explanations
                  .sort((a, b) => a.importance_rank - b.importance_rank)
                  .map((item) => (
                    <div
                      key={`${item.feature_name}-${item.importance_rank}`}
                      className="flex gap-4 p-4 rounded-lg bg-gray-50 border border-gray-100"
                    >
                      <div className="flex flex-col items-center gap-1 shrink-0">
                        <span className="text-xs font-bold text-gray-400">#{item.importance_rank}</span>
                        <div className={`w-2 h-8 rounded-full ${getSeverityColor(item.contribution)}`} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-800 capitalize">
                          {item.feature_name.replace(/_/g, ' ')}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">{item.explanation_text}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Contribution: {(item.contribution * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
};

export default ExplanationsPage;
