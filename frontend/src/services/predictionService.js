import api from './api';

export const predictionService = {
  getModelsInfo: async () => {
    const response = await api.get('/predictions/models/');
    return response.data;
  },
  predictConstituency: async (constituencyName, year = 2031) => {
    const response = await api.get(`/predictions/constituency/${constituencyName}/`, { params: { year } });
    return response.data;
  },
  getHistory: async (params = {}) => {
    const response = await api.get('/prediction-history/', { params });
    return response.data;
  },
  getModelMetrics: async (modelId) => {
    const response = await api.get(`/predictions/models/${modelId}/metrics/`);
    return response.data;
  }
};
