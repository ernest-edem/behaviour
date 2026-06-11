import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Lightbulb } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import RiskBadge from '../components/RiskBadge';
import { assessmentService } from '../services/assessmentService';
import { predictionService } from '../services/predictionService';
import { explanationService } from '../services/explanationService';
import { useWorkflow } from '../context/WorkflowContext';
import { getApiErrorMessage, formatDate } from '../utils/format';
import {
  confidenceToPercent,
  formatCondition,
  getRiskCardBorder,
  getSeverityColor,
} from '../utils/risk';
import type { Assessment, DiseasePredictionResult, PredictionExplanation } from '../types';

const HistoryDetailPage: React.FC = () => {
  const { assessmentId } = useParams<{ assessmentId: string }>();
  const { setWorkflow } = useWorkflow();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [predictions, setPredictions] = useState<DiseasePredictionResult | null>(null);
  const [explanations, setExplanations] = useState<Record<number, PredictionExplanation>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      if (!assessmentId) return;
      const id = parseInt(assessmentId, 10);
      try {
        const [assessmentData, predictionData] = await Promise.all([
          assessmentService.getById(id),
          predictionService.getByAssessment(id),
        ]);
        setAssessment(assessmentData);
        setPredictions(predictionData);
        setWorkflow(id, predictionData);

        const explanationResults: Record<number, PredictionExplanation> = {};
        await Promise.all(
          predictionData.predictions.map(async (p) => {
            try {
              const exp = await explanationService.getByPrediction(p.id);
              explanationResults[p.id] = exp;
            } catch {
              try {
                const exp = await explanationService.generate(p.id);
                explanationResults[p.id] = exp;
              } catch {
                // explanations not available
              }
            }
          })
        );
        setExplanations(explanationResults);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load assessment details.'));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [assessmentId, setWorkflow]);

  if (loading) return <LoadingSpinner message="Loading assessment details..." />;
  if (error) return <ErrorAlert message={error} />;
  if (!assessment) return null;

  return (
    <div className="space-y-6">
      <Link to="/history" className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-primary-600">
        <ArrowLeft size={16} />
        Back to History
      </Link>

      <Card title={`Assessment #${assessment.id}`} subtitle={formatDate(assessment.created_at)}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {[
            ['Age', assessment.age],
            ['Gender', assessment.gender],
            ['BMI', assessment.bmi],
            ['Blood Glucose', `${assessment.blood_glucose} mg/dL`],
            ['Blood Pressure', `${assessment.blood_pressure} mmHg`],
            ['Sleep', `${assessment.sleep_hours}h`],
            ['Stress', `${assessment.stress_level}/10`],
            ['Diet Quality', `${assessment.diet_quality}/5`],
          ].map(([label, value]) => (
            <div key={label as string}>
              <p className="text-gray-500">{label}</p>
              <p className="font-medium text-gray-900 capitalize">{value}</p>
            </div>
          ))}
        </div>
      </Card>

      {predictions && (
        <>
          <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4">
            <p className="text-sm text-purple-600 font-medium">Behavioral Phenotype</p>
            <p className="text-lg font-bold text-purple-900 mt-1">{predictions.behavioral_phenotype}</p>
          </div>

          {predictions.predictions.map((prediction) => (
            <div
              key={prediction.id}
              className={`bg-white rounded-xl border border-gray-200 shadow-sm border-l-4 ${getRiskCardBorder(prediction.risk_level)}`}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">
                    {formatCondition(prediction.predicted_condition)}
                  </h3>
                  <RiskBadge level={prediction.risk_level} />
                </div>
                <p className="text-sm text-gray-500 mb-4">
                  Confidence: {confidenceToPercent(prediction.confidence_score)}% · Source: {prediction.prediction_source}
                </p>

                {explanations[prediction.id] ? (
                  <div className="space-y-2 mt-4 border-t pt-4">
                    <p className="text-sm font-semibold text-gray-700 flex items-center gap-1">
                      <Lightbulb size={14} />
                      Explanations
                    </p>
                    {explanations[prediction.id].explanations
                      .sort((a, b) => a.importance_rank - b.importance_rank)
                      .map((item) => (
                        <div key={item.importance_rank} className="flex gap-3 p-3 bg-gray-50 rounded-lg text-sm">
                          <div className={`w-1.5 rounded-full self-stretch ${getSeverityColor(item.contribution)}`} />
                          <div>
                            <span className="font-medium text-gray-800 capitalize">
                              {item.feature_name.replace(/_/g, ' ')}
                            </span>
                            <p className="text-gray-600 mt-0.5">{item.explanation_text}</p>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <Link
                    to={`/explanations?predictionId=${prediction.id}`}
                    className="text-sm text-primary-600 hover:underline"
                  >
                    Generate explanations →
                  </Link>
                )}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default HistoryDetailPage;
