import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import Card from '../components/Card';
import RiskChart from '../charts/RiskChart';
import { 
  ShieldAlert, 
  Activity, 
  Target, 
  Info, 
  ArrowRight,
  TrendingUp,
  BrainCircuit
} from 'lucide-react';

interface Prediction {
  risk_score: number;
  risk_level: string;
  confidence: number;
  explanation: string;
}

const Dashboard: React.FC = () => {
  const { isAdmin } = useAuth();
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('latest_prediction');
    if (saved) {
      setPrediction(JSON.parse(saved));
    }
  }, []);

  // Mock SHAP data for visualization
  const featureImportance = [
    { feature: 'Stress Level', impact: 0.35 },
    { feature: 'Smoking', impact: 0.28 },
    { feature: 'BMI', impact: 0.15 },
    { feature: 'Activity', impact: -0.12 },
    { feature: 'Sleep', impact: -0.08 },
  ];

  if (!prediction) {
    return (
      <div className="pt-20 px-4 min-h-screen bg-gray-50 flex items-center justify-center text-center">
        <div className="max-w-md">
          <BrainCircuit className="h-16 w-16 text-primary-600 mx-auto mb-4 opacity-50" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Assessment Data Yet</h2>
          <p className="text-gray-600 mb-8">Take your first AI health risk assessment to see your dashboard results.</p>
          <Link
            to="/assessment"
            className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-primary-700 transition-all"
          >
            Start Assessment
            <ArrowRight size={20} />
          </Link>
        </div>
      </div>
    );
  }

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'mild': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="pt-20 pb-12 px-4 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isAdmin ? 'Personal Health Dashboard' : 'Health AI Dashboard'}
            </h1>
            <p className="text-gray-600 mt-1">
              {isAdmin
                ? 'Your personal assessment results. Use Admin Dashboard for system management.'
                : 'AI-driven behavioral and lifestyle risk analysis.'}
            </p>
            {isAdmin && (
              <Link
                to="/admin"
                className="inline-flex items-center gap-1 mt-2 text-sm font-medium text-primary-600 hover:text-primary-500"
              >
                Go to Admin Dashboard →
              </Link>
            )}
          </div>
          <Link
            to="/assessment"
            className="bg-white text-primary-600 border border-primary-600 px-6 py-2.5 rounded-xl font-bold hover:bg-primary-50 transition-all text-center"
          >
            New Assessment
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="flex flex-col items-center text-center">
            <div className="p-3 rounded-full bg-primary-50 text-primary-600 mb-4">
              <TrendingUp size={24} />
            </div>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Risk Score</p>
            <h2 className="text-4xl font-bold text-gray-900 mt-1">{(prediction.risk_score * 100).toFixed(0)}%</h2>
            <div className="w-full bg-gray-100 rounded-full h-2 mt-4">
              <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-1000" 
                style={{ width: `${prediction.risk_score * 100}%` }}
              ></div>
            </div>
          </Card>

          <Card className="flex flex-col items-center text-center">
            <div className="p-3 rounded-full bg-orange-50 text-orange-600 mb-4">
              <ShieldAlert size={24} />
            </div>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Risk Level</p>
            <div className={`mt-2 px-4 py-1 rounded-full border font-bold text-lg ${getRiskColor(prediction.risk_level)}`}>
              {prediction.risk_level}
            </div>
          </Card>

          <Card className="flex flex-col items-center text-center">
            <div className="p-3 rounded-full bg-green-50 text-green-600 mb-4">
              <Target size={24} />
            </div>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Confidence</p>
            <h2 className="text-4xl font-bold text-gray-900 mt-1">{(prediction.confidence * 100).toFixed(0)}%</h2>
            <p className="text-xs text-gray-400 mt-2 italic">Based on model reliability</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Explainable AI (XAI) Analysis" subtitle="Feature impact on your current risk score">
            <RiskChart data={featureImportance} />
            <div className="mt-4 flex gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>Increases Risk</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>Decreases Risk</span>
              </div>
            </div>
          </Card>

          <Card title="AI Clinical Insight" subtitle="Personalized feedback from BehaviorLens AI">
            <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
              <div className="flex gap-4">
                <div className="text-blue-600 shrink-0">
                  <Info size={24} />
                </div>
                <div>
                  <h4 className="font-bold text-blue-900 mb-2">Primary Drivers</h4>
                  <p className="text-blue-800 leading-relaxed">
                    {prediction.explanation}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 space-y-4">
              <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                <BrainCircuit size={18} className="text-primary-600" />
                Next Steps Recommended by AI
              </h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-gray-600">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-600 mt-1.5 shrink-0"></div>
                  Consider mindfulness techniques to lower stress levels.
                </li>
                <li className="flex items-start gap-2 text-sm text-gray-600">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-600 mt-1.5 shrink-0"></div>
                  Increase weekly physical activity to at least 150 minutes.
                </li>
                <li className="flex items-start gap-2 text-sm text-gray-600">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-600 mt-1.5 shrink-0"></div>
                  Consult a healthcare provider about your blood pressure readings.
                </li>
              </ul>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
