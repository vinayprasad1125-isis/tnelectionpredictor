import React, { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { Loading, ErrorMessage } from '../../components/common/Common';

const Elections = () => {
  const [elections, setElections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchElections = async () => {
      try {
        const data = await dataService.getElections({ ordering: '-year' });
        setElections(data.results || data);
      } catch (err) {
        setError('Failed to fetch elections.');
      } finally {
        setLoading(false);
      }
    };
    fetchElections();
  }, []);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 animate-fade-in-up">
        <div>
          <h1 className="text-3xl font-extrabold text-primary drop-shadow-sm">Elections</h1>
          <p className="text-secondary text-sm mt-1 font-medium">Historical records of Tamil Nadu Assembly Elections.</p>
        </div>
      </div>

      <div className="glass-card overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/20">
            <thead className="bg-white/20">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-800 uppercase tracking-wider">Year</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-800 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-800 uppercase tracking-wider">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/20">
              {elections.map((election) => (
                <tr key={election.id} className="hover:bg-white/10 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-800">{election.year}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">
                    <span className="px-2 inline-flex text-xs leading-5 font-bold rounded-full bg-blue-100/50 text-blue-900 border border-blue-200/50">
                      {election.election_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-700">{election.state}</td>
                </tr>
              ))}
              {elections.length === 0 && (
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-center text-slate-700">No elections found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Elections;
