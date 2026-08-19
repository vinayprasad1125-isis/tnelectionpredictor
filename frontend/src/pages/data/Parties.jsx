import React, { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { analyticsService } from '../../services/analyticsService';
import { Loading, ErrorMessage } from '../../components/common/Common';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Parties = () => {
  const [partiesList, setPartiesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [selectedParty, setSelectedParty] = useState(null);
  const [seatTrends, setSeatTrends] = useState([]);
  const [voteTrends, setVoteTrends] = useState([]);
  const [wins, setWins] = useState([]);
  const [winsPage, setWinsPage] = useState(1);
  const [winsTotal, setWinsTotal] = useState(0);
  const [partyLoading, setPartyLoading] = useState(false);

  useEffect(() => {
    const fetchParties = async () => {
      try {
        setLoading(true);
        // Fetch all main parties for the dropdown (limit 200)
        const response = await dataService.getParties({ limit: 200, ordering: 'abbreviation' });
        setPartiesList(response.results || response);
      } catch (err) {
        setError('Failed to load parties list.');
      } finally {
        setLoading(false);
      }
    };
    fetchParties();
  }, []);

  useEffect(() => {
    if (selectedParty) {
      const fetchPartyData = async () => {
        try {
          setPartyLoading(true);
          const [seatsData, votesData, winsData] = await Promise.all([
            analyticsService.getSeatTrends(selectedParty.abbreviation),
            analyticsService.getVoteShareTrends(selectedParty.abbreviation),
            dataService.getElectionResults({ party: selectedParty.id, is_winner: 'True', page: winsPage, ordering: '-election__year' })
          ]);
          setSeatTrends(seatsData);
          setVoteTrends(votesData);
          setWins(winsData.results || winsData);
          setWinsTotal(winsData.count || winsData.length || 0);
        } catch (err) {
          console.error("Failed to load party analytics", err);
        } finally {
          setPartyLoading(false);
        }
      };
      fetchPartyData();
    }
  }, [selectedParty, winsPage]);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 animate-fade-in-up">
        <div>
          <h1 className="text-3xl font-extrabold text-primary drop-shadow-sm">Party Analysis</h1>
          <p className="text-secondary text-sm mt-1 font-medium">Select a party to view historical trends and victories.</p>
        </div>
        
        <div className="w-full md:w-72">
          <select 
            className="w-full px-4 py-2 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent bg-white/40 backdrop-blur-md text-slate-900 font-bold"
            onChange={(e) => {
              const party = partiesList.find(p => p.id === parseInt(e.target.value));
              setSelectedParty(party);
              setWinsPage(1); // reset pagination
            }}
            value={selectedParty?.id || ''}
          >
            <option value="" disabled>-- Select a Party --</option>
            {partiesList.map(p => (
              <option key={p.id} value={p.id}>{p.abbreviation} - {p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {!selectedParty ? (
        <div className="bg-white/20 border border-white/30 backdrop-blur-md border-dashed rounded-xl h-64 flex items-center justify-center text-slate-800 font-bold animate-pulse">
          Please select a political party from the dropdown above.
        </div>
      ) : partyLoading && winsPage === 1 ? (
        <Loading />
      ) : (
        <div className="space-y-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          {/* Party Header */}
          <div className="glass-card p-6 flex flex-col md:flex-row justify-between items-center">
            <div>
              <h2 className="text-3xl font-black text-slate-900">{selectedParty.abbreviation}</h2>
              <p className="text-slate-800 font-medium mt-1">{selectedParty.name}</p>
            </div>
            <div className="mt-4 md:mt-0 text-right">
              <span className="block text-sm text-secondary uppercase font-semibold">Total Historical Wins Recorded</span>
              <span className="text-3xl font-bold text-accent">{winsTotal}</span>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-4">Seats Won Over Time</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={seatTrends}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="year" axisLine={false} tickLine={false} />
                    <YAxis axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{borderRadius: '8px'}} cursor={{fill: '#f1f5f9'}} />
                    <Bar dataKey="seats_won" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Seats Won" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-4">Vote Share Trend (%)</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={voteTrends}>
                    <defs>
                      <linearGradient id="colorVoteShare" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="year" axisLine={false} tickLine={false} />
                    <YAxis axisLine={false} tickLine={false} domain={[0, 'auto']} />
                    <Tooltip contentStyle={{borderRadius: '8px'}} />
                    <Area type="monotone" dataKey="vote_share" stroke="#10b981" fillOpacity={1} fill="url(#colorVoteShare)" strokeWidth={3} name="Vote Share %" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Winning Constituencies Table */}
          <div className="glass-card overflow-hidden">
            <div className="px-6 py-4 border-b border-white/20 bg-white/20 flex justify-between items-center">
              <h3 className="font-bold text-slate-800">Constituency Victories</h3>
              <div className="flex gap-2 text-sm">
                <button disabled={winsPage === 1} onClick={() => setWinsPage(p => p - 1)} className="px-3 py-1 bg-white/40 border border-white/20 rounded disabled:opacity-50">Prev</button>
                <span className="py-1 px-2 font-bold text-slate-800">Page {winsPage}</span>
                <button disabled={wins.length < 10} onClick={() => setWinsPage(p => p + 1)} className="px-3 py-1 bg-white/40 border border-white/20 rounded disabled:opacity-50">Next</button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/20">
                <thead className="bg-white/10">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Year</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Constituency</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Candidate</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Votes</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Vote %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/20">
                  {wins.map((w) => (
                    <tr key={w.id} className="hover:bg-white/20 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-800">{w.election_year}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-800">{w.constituency_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 font-medium">{w.candidate_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">{w.votes_received.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">{w.vote_percentage}%</td>
                    </tr>
                  ))}
                  {wins.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-secondary">No victories recorded for the selected party.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Parties;
