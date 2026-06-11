import api from '../api/axios';
import type { Assessment, AssessmentCreate } from '../types';

export const assessmentService = {
  create: async (data: AssessmentCreate): Promise<Assessment> => {
    const response = await api.post<Assessment>('/assessments', data);
    return response.data;
  },

  list: async (): Promise<Assessment[]> => {
    const response = await api.get<Assessment[]>('/assessments');
    return response.data;
  },

  getById: async (id: number): Promise<Assessment> => {
    const response = await api.get<Assessment>(`/assessments/${id}`);
    return response.data;
  },
};
