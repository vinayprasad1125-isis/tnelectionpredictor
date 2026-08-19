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
  getParties: async (params = {}) => {
    const response = await api.get('/parties/', { params });
    return response.data;
  },
  getElectionResults: async (params = {}) => {
    const response = await api.get('/election-results/', { params });
    return response.data;
  }
};
