import React, { createContext, useContext, useState, useCallback } from 'react';
import type { DiseasePredictionResult } from '../types';

interface WorkflowContextType {
  currentAssessmentId: number | null;
  currentPredictions: DiseasePredictionResult | null;
  setWorkflow: (assessmentId: number, predictions: DiseasePredictionResult) => void;
  clearWorkflow: () => void;
}

const ASSESSMENT_KEY = 'workflow_assessment_id';
const PREDICTIONS_KEY = 'workflow_predictions';

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentAssessmentId, setCurrentAssessmentId] = useState<number | null>(() => {
    const stored = sessionStorage.getItem(ASSESSMENT_KEY);
    return stored ? parseInt(stored, 10) : null;
  });

  const [currentPredictions, setCurrentPredictions] = useState<DiseasePredictionResult | null>(() => {
    const stored = sessionStorage.getItem(PREDICTIONS_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  const setWorkflow = useCallback((assessmentId: number, predictions: DiseasePredictionResult) => {
    setCurrentAssessmentId(assessmentId);
    setCurrentPredictions(predictions);
    sessionStorage.setItem(ASSESSMENT_KEY, String(assessmentId));
    sessionStorage.setItem(PREDICTIONS_KEY, JSON.stringify(predictions));
  }, []);

  const clearWorkflow = useCallback(() => {
    setCurrentAssessmentId(null);
    setCurrentPredictions(null);
    sessionStorage.removeItem(ASSESSMENT_KEY);
    sessionStorage.removeItem(PREDICTIONS_KEY);
  }, []);

  return (
    <WorkflowContext.Provider
      value={{ currentAssessmentId, currentPredictions, setWorkflow, clearWorkflow }}
    >
      {children}
    </WorkflowContext.Provider>
  );
};

export const useWorkflow = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within WorkflowProvider');
  }
  return context;
};
