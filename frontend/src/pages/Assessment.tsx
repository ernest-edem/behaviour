import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import Card from '../components/Card';
import { Activity, ClipboardCheck, Loader2, AlertCircle, ChevronRight } from 'lucide-react';

const Assessment: React.FC = () => {
  const [formData, setFormData] = useState({
    age: 30,
    bmi: 24.5,
    sleep_hours: 7,
    stress_level: 5,
    physical_activity: 5,
    smoking: 0,
    alcohol: 0,
    blood_pressure: 120,
    glucose_level: 100,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'smoking' || name === 'alcohol' ? parseInt(value) : parseFloat(value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/assessment/predict', formData);
      // Store result in local storage or state management to show on dashboard
      localStorage.setItem('latest_prediction', JSON.stringify(response.data));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to process assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formFields = [
    { name: 'age', label: 'Age', type: 'number', min: 1, max: 120 },
    { name: 'bmi', label: 'BMI', type: 'number', min: 10, max: 60, step: 0.1 },
    { name: 'sleep_hours', label: 'Sleep Hours', type: 'number', min: 0, max: 24, step: 0.5 },
    { name: 'blood_pressure', label: 'Blood Pressure (Systolic)', type: 'number', min: 50, max: 250 },
    { name: 'glucose_level', label: 'Glucose Level', type: 'number', min: 50, max: 500 },
  ];

  const sliderFields = [
    { name: 'stress_level', label: 'Stress Level (1-10)', min: 1, max: 10 },
    { name: 'physical_activity', label: 'Physical Activity (1-10)', min: 1, max: 10 },
  ];

  return (
    <div className="pt-20 pb-12 px-4 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <ClipboardCheck className="text-primary-600" />
            Health Risk Assessment
          </h1>
          <p className="text-gray-600 mt-2">Complete the form below to receive your AI-powered behavioral risk prediction.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {formFields.map(field => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{field.label}</label>
                  <input
                    type={field.type}
                    name={field.name}
                    min={field.min}
                    max={field.max}
                    step={field.step || 1}
                    value={formData[field.name as keyof typeof formData]}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                    required
                  />
                </div>
              ))}

              {sliderFields.map(field => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}: <span className="text-primary-600 font-bold">{formData[field.name as keyof typeof formData]}</span>
                  </label>
                  <input
                    type="range"
                    name={field.name}
                    min={field.min}
                    max={field.max}
                    value={formData[field.name as keyof typeof formData]}
                    onChange={handleChange}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                  />
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Smoking Status</label>
                <select
                  name="smoking"
                  value={formData.smoking}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value={0}>Non-smoker</option>
                  <option value={1}>Smoker</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Alcohol Consumption</label>
                <select
                  name="alcohol"
                  value={formData.alcohol}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value={0}>None / Occasional</option>
                  <option value={1}>Regular</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center gap-2">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <div className="mt-8 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="bg-primary-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-primary-700 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? <Loader2 className="animate-spin" /> : (
                  <>
                    Run AI Prediction
                    <ChevronRight size={20} />
                  </>
                )}
              </button>
            </div>
          </Card>
        </form>
      </div>
    </div>
  );
};

export default Assessment;
