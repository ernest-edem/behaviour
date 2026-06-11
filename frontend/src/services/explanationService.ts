import api from '../api/axios';
import type { PredictionExplanation } from '../types';

export const explanationService = {
  generate: async (predictionId: number): Promise<PredictionExplanation> => {
    const response = await api.post<PredictionExplanation>(
      `/explanations/${predictionId}`
    );
    return response.data;
  },

  getByPrediction: async (predictionId: number): Promise<PredictionExplanation> => {
    const response = await api.get<PredictionExplanation>(
      `/explanations/${predictionId}`
    );
    return response.data;
  },
};
