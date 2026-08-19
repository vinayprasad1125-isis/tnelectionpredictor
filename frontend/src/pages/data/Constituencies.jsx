import React, { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { analyticsService } from '../../services/analyticsService';
import { Loading, ErrorMessage } from '../../components/common/Common';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Search } from 'lucide-react';

const Constituencies = () => {
  const [data, setData] = useState({ results: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  
  const [selectedConstituency, setSelectedConstituency] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = { page, ordering: 'number' };
        if (search) params.search = search;
        
        const response = await dataService.getConstituencies(params);
        if (response.results) {
           setData(response);
        } else {
           setData({ results: response, count: response.length });
        }
      } catch (err) {
        setError('Failed to fetch constituencies.');
      } finally {
        setLoading(false);
      }
    };
    
    // Debounce search slightly
    const timeoutId = setTimeout(() => {
      fetchData();
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [page, search]);

  useEffect(() => {
    if (selectedConstituency) {
      const fetchHistory = async () => {
        try {
          setHistoryLoading(true);
          const histData = await analyticsService.getConstituencyHistory(selectedConstituency.id);
          // Sort ascending for charts
          setHistory([...histData].sort((a, b) => a.year - b.year));
        } catch (err) {
          console.error("Failed to load history");
        } finally {
          setHistoryLoading(false);
        }
      };
      fetchHistory();
    }
  }, [selectedConstituency]);

  // Derived Summary calculations
  const getSummary = () => {
    if (!history.length) return null;
    const latest = history[history.length - 1];
    
    // Calculate dominant party (mode)
    const partyCounts = {};
    let dominant = '';
    let maxWins = 0;
    history.forEach(h => {
      partyCounts[h.party] = (partyCounts[h.party] || 0) + 1;
      if (partyCounts[h.party] > maxWins) {
        maxWins = partyCounts[h.party];
        dominant = h.party;
      }
    });

    return {
      dominantParty: dominant,
      latestWinner: latest.candidate,
      latestParty: latest.party,
      latestMargin: latest.margin,
      latestShare: latest.vote_share
    };
  };

  const summary = getSummary();

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-6rem)]">
      {/* Sidebar List */}
      <div className="w-full lg:w-1/3 flex flex-col glass-card overflow-hidden animate-fade-in-up">
        <div className="p-4 border-b border-white/20">
          <h2 className="text-lg font-bold text-slate-800 mb-3">Constituency Explorer</h2>
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search by name or district..." 
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full pl-10 pr-4 py-2 border border-white/30 rounded-lg focus:ring-2 focus:ring-accent outline-none text-sm bg-white/40 text-slate-800 placeholder-slate-600"
            />
            <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {loading && page === 1 ? <Loading /> : (
            <ul className="divide-y divide-white/20">
              {data.results.map(c => (
                <li 
                  key={c.id} 
                  onClick={() => setSelectedConstituency(c)}
                  className={`p-4 cursor-pointer hover:bg-white/20 transition-colors ${selectedConstituency?.id === c.id ? 'bg-white/30 border-l-4 border-accent' : ''}`}
                >
                  <div className="font-bold text-slate-800">{c.name} <span className="text-xs text-slate-700 font-medium ml-1">({c.number})</span></div>
                  <div className="text-sm text-slate-700 mt-1 font-medium">{c.district} District</div>
                </li>
              ))}
              {data.results.length === 0 && <li className="p-4 text-center text-secondary text-sm">No results found</li>}
            </ul>
          )}
        </div>

        <div className="p-3 border-t border-white/20 flex justify-between items-center bg-white/10 text-sm">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1 bg-white/40 border border-white/20 rounded shadow-sm disabled:opacity-50 font-bold text-slate-800">Prev</button>
          <span className="text-slate-800 font-bold">Page {page}</span>
          <button disabled={!data.next} onClick={() => setPage(p => p + 1)} className="px-3 py-1 bg-white/40 border border-white/20 rounded shadow-sm disabled:opacity-50 font-bold text-slate-800">Next</button>
        </div>
      </div>

      {/* Main Detail Area */}
      <div className="w-full lg:w-2/3 flex flex-col gap-6 overflow-y-auto pb-8">
        {!selectedConstituency ? (
          <div className="bg-slate-50 border border-slate-200 border-dashed rounded-xl h-full flex items-center justify-center text-slate-400">
            Select a constituency from the list to view its history and analytics.
          </div>
        ) : (
          <>
            {/* Header / Summary */}
            <div className="glass-card p-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h1 className="text-3xl font-extrabold text-slate-900">{selectedConstituency.name}</h1>
                  <p className="text-slate-800 font-medium">{selectedConstituency.district} District • Type: {selectedConstituency.type}</p>
                </div>
                <div className="text-right bg-white/40 px-4 py-2 rounded-lg border border-white/30">
                  <span className="block text-xs text-slate-800 uppercase font-extrabold tracking-wider">Historical Dominance</span>
                  <span className="text-lg font-black text-accent">{summary?.dominantParty || 'N/A'}</span>
                </div>
              </div>

              {summary && (
                <div className="grid grid-cols-3 gap-4 border-t border-white/20 pt-4 mt-2">
                  <div>
                    <span className="block text-xs text-slate-800 uppercase font-bold">Latest Winner</span>
                    <span className="font-extrabold text-slate-900">{summary.latestWinner} ({summary.latestParty})</span>
                  </div>
                  <div>
                    <span className="block text-xs text-slate-800 uppercase font-bold">Winning Margin</span>
                    <span className="font-extrabold text-slate-900">{summary.latestMargin.toLocaleString()} votes</span>
                  </div>
                  <div>
                    <span className="block text-xs text-slate-800 uppercase font-bold">Vote Share</span>
                    <span className="font-extrabold text-slate-900">{summary.latestShare.toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>

            {historyLoading ? <Loading /> : (
              <>
                {/* Charts */}
                {history.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    <div className="glass-card p-5">
                      <h3 className="text-sm font-bold text-slate-800 mb-4">Winner Vote Share Trend (%)</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={history}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="year" tick={{fontSize: 12}} />
                            <YAxis tick={{fontSize: 12}} domain={['auto', 'auto']} />
                            <Tooltip contentStyle={{borderRadius: '8px'}} />
                            <Line type="monotone" dataKey="vote_share" stroke="#3b82f6" strokeWidth={2} dot={{r: 4}} name="Vote Share %" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                    
                    <div className="glass-card p-5">
                      <h3 className="text-sm font-bold text-slate-800 mb-4">Winning Margin by Year</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={history}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="year" tick={{fontSize: 12}} />
                            <YAxis tick={{fontSize: 12}} />
                            <Tooltip formatter={(val) => val.toLocaleString()} contentStyle={{borderRadius: '8px'}} />
                            <Bar dataKey="margin" fill="#10b981" radius={[4, 4, 0, 0]} name="Margin" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                )}

                {/* Table */}
                <div className="glass-card overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                  <div className="px-6 py-4 border-b border-white/20 bg-white/20">
                    <h3 className="font-bold text-slate-800">Detailed Election History</h3>
                  </div>
                  <table className="min-w-full divide-y divide-white/20">
                    <thead className="bg-white/10">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-800 uppercase">Year</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-800 uppercase">Winner</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-800 uppercase">Party</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-800 uppercase">Votes</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-800 uppercase">Margin</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/20">
                      {[...history].reverse().map((h) => (
                        <tr key={h.year} className="hover:bg-white/20 transition-colors">
                          <td className="px-6 py-3 whitespace-nowrap text-sm font-extrabold text-slate-900">{h.year}</td>
                          <td className="px-6 py-3 whitespace-nowrap text-sm font-medium text-slate-800">{h.candidate}</td>
                          <td className="px-6 py-3 whitespace-nowrap text-sm font-black text-accent">{h.party}</td>
                          <td className="px-6 py-3 whitespace-nowrap text-sm text-slate-800 font-medium">{h.votes.toLocaleString()} <span className="text-xs text-slate-700">({h.vote_share.toFixed(1)}%)</span></td>
                          <td className="px-6 py-3 whitespace-nowrap text-sm text-green-600 font-medium">+{h.margin.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {history.length === 0 && <div className="p-6 text-center text-secondary">No historical data available.</div>}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Constituencies;
