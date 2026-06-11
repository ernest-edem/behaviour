import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Loader2 } from 'lucide-react';
import Card from '../components/Card';
import ErrorAlert from '../components/ErrorAlert';
import { assessmentService } from '../services/assessmentService';
import { predictionService } from '../services/predictionService';
import { useWorkflow } from '../context/WorkflowContext';
import { calculateBmi } from '../utils/bmi';
import { getApiErrorMessage } from '../utils/format';
import type { AssessmentCreate } from '../types';

const DIET_LABELS: Record<number, string> = {
  1: 'Very Poor',
  2: 'Poor',
  3: 'Average',
  4: 'Good',
  5: 'Excellent',
};

const initialForm: Omit<AssessmentCreate, 'bmi'> = {
  age: 30,
  gender: 'male',
  weight: 70,
  height: 170,
  physical_activity: 5,
  diet_quality: 3,
  sleep_hours: 7,
  stress_level: 5,
  smoking: 0,
  alcohol_use: 0,
  blood_pressure: 120,
  blood_glucose: 100,
  medication_adherence: 7,
  emotional_wellbeing: 7,
};

const AssessmentsPage: React.FC = () => {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setWorkflow } = useWorkflow();

  const bmi = useMemo(() => calculateBmi(form.weight, form.height), [form.weight, form.height]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const intFields = ['age', 'physical_activity', 'diet_quality', 'stress_level', 'smoking', 'alcohol_use', 'medication_adherence', 'emotional_wellbeing'];
    setForm((prev) => ({
      ...prev,
      [name]: intFields.includes(name) ? parseInt(value, 10) : parseFloat(value),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload: AssessmentCreate = { ...form, bmi };
      const assessment = await assessmentService.create(payload);
      const predictions = await predictionService.generate(assessment.id);
      setWorkflow(assessment.id, predictions);
      navigate('/predictions');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to submit assessment. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        <Card title="Demographics">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
              <input type="number" name="age" min={1} max={120} value={form.age} onChange={handleChange} required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
              <select name="gender" value={form.gender} onChange={handleChange} required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">BMI (calculated)</label>
              <input type="text" readOnly value={bmi} className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600" />
            </div>
          </div>
        </Card>

        <Card title="Physical Measurements">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
              <input type="number" name="weight" min={1} step={0.1} value={form.weight} onChange={handleChange} required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
              <input type="number" name="height" min={1} step={0.1} value={form.height} onChange={handleChange} required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
          </div>
        </Card>

        <Card title="Lifestyle & Clinical">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              { name: 'physical_activity', label: 'Physical Activity (1-10)', min: 1, max: 10 },
              { name: 'sleep_hours', label: 'Sleep Hours', min: 0, max: 24, step: 0.5 },
              { name: 'stress_level', label: 'Stress Level (1-10)', min: 1, max: 10 },
              { name: 'blood_pressure', label: 'Blood Pressure (Systolic)', min: 50, max: 250 },
              { name: 'blood_glucose', label: 'Blood Glucose (mg/dL)', min: 50, max: 500 },
              { name: 'medication_adherence', label: 'Medication Adherence (1-10)', min: 1, max: 10 },
              { name: 'emotional_wellbeing', label: 'Emotional Wellbeing (1-10)', min: 1, max: 10 },
            ].map((field) => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.name !== 'sleep_hours' && field.name !== 'blood_pressure' && field.name !== 'blood_glucose' && (
                    <span className="text-primary-600 font-bold ml-1">
                      {form[field.name as keyof typeof form]}
                    </span>
                  )}
                </label>
                <input
                  type={field.name === 'sleep_hours' || field.name === 'blood_pressure' || field.name === 'blood_glucose' ? 'number' : 'range'}
                  name={field.name}
                  min={field.min}
                  max={field.max}
                  step={field.step || 1}
                  value={form[field.name as keyof typeof form]}
                  onChange={handleChange}
                  className={field.name.includes('sleep') || field.name.includes('blood')
                    ? 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none'
                    : 'w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600'}
                  required
                />
              </div>
            ))}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diet Quality: <span className="text-primary-600 font-bold">{DIET_LABELS[form.diet_quality]}</span>
              </label>
              <input type="range" name="diet_quality" min={1} max={5} value={form.diet_quality} onChange={handleChange}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600" />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Very Poor</span>
                <span>Excellent</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Smoking</label>
              <select name="smoking" value={form.smoking} onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
                <option value={0}>Non-smoker</option>
                <option value={1}>Smoker</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Alcohol Use</label>
              <select name="alcohol_use" value={form.alcohol_use} onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
                <option value={0}>None / Occasional</option>
                <option value={1}>Regular</option>
              </select>
            </div>
          </div>
        </Card>

        {error && <ErrorAlert message={error} />}

        <div className="flex justify-end">
          <button type="submit" disabled={loading}
            className="bg-primary-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-primary-700 transition-all flex items-center gap-2 disabled:opacity-50">
            {loading ? <Loader2 className="animate-spin" size={20} /> : (
              <>Submit & Generate Predictions<ChevronRight size={20} /></>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AssessmentsPage;
