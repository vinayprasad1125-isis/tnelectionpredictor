import api from './api';

export const analyticsService = {
  getPartyPerformance: async (year = null) => {
    const params = year ? { year } : {};
    const response = await api.get('/analytics/party-performance/', { params });
    return response.data;
  },
  getVoteShareTrends: async (partyAbbr) => {
    const response = await api.get('/analytics/vote-share-trends/', { params: { party: partyAbbr } });
    return response.data;
  },
  getSeatTrends: async (partyAbbr) => {
    const response = await api.get('/analytics/seat-trends/', { params: { party: partyAbbr } });
    return response.data;
  },
  getTurnout: async () => {
    const response = await api.get('/analytics/turnout/');
    return response.data;
  },
  getConstituencyHistory: async (pk) => {
    const response = await api.get(`/analytics/constituency/${pk}/`);
    return response.data;
  }
};
