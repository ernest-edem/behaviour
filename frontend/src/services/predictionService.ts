import api from '../api/axios';
import type { DiseasePredictionResult } from '../types';

export const predictionService = {
  generate: async (assessmentId: number): Promise<DiseasePredictionResult> => {
    const response = await api.post<DiseasePredictionResult>(
      `/predictions/${assessmentId}`
    );
    return response.data;
  },

  getByAssessment: async (assessmentId: number): Promise<DiseasePredictionResult> => {
    const response = await api.get<DiseasePredictionResult>(
      `/predictions/${assessmentId}`
    );
    return response.data;
  },
};
