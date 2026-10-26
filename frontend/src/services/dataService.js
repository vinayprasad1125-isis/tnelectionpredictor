import api from './api';

export const dataService = {
  getElections: async (params = {}) => {
    const response = await api.get('/elections/', { params });
    return response.data;
  },
  getConstituencies: async (params = {}) => {
    const response = await api.get('/constituencies/', { params });
    return response.data;
  },
  getConstituencySummary: async () => {
    const response = await api.get('/constituencies/summary/');
    return response.data;
  },
  getParties: async (params = {}) => {
    const response = await api.get('/parties/', { params });
    return response.data;
  },
  getElectionResults: async (params = {}) => {
    const response = await api.get('/results/', { params });
    return response.data;
  }
};
