import React, { useState, useEffect } from 'react';
import { analyticsService } from '../../services/analyticsService';
import { dataService } from '../../services/dataService';
import { Loading, ErrorMessage } from '../../components/common/Common';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Filter } from 'lucide-react';

const Analytics = () => {
  const [turnout, setTurnout] = useState([]);
  const [elections, setElections] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  
  const [partyPerformance, setPartyPerformance] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBaseData = async () => {
      try {
        const [turnoutData, electionsData] = await Promise.all([
          analyticsService.getTurnout(),
          dataService.getElections({ ordering: '-year' })
        ]);
        setTurnout(turnoutData);
        
        const elList = electionsData.results || electionsData;
        setElections(elList);
        if (elList.length > 0) {
          setSelectedYear(elList[0].year.toString());
        }
      } catch (err) {
        console.error(err);
        setError('Failed to load base analytics data.');
      }
    };
    fetchBaseData();
  }, []);

  useEffect(() => {
    if (selectedYear) {
      const fetchPerformance = async () => {
        try {
          setLoading(true);
          const data = await analyticsService.getPartyPerformance(selectedYear);
          setPartyPerformance(data.slice(0, 8)); // Top 8 parties
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchPerformance();
    }
  }, [selectedYear]);

  if (loading && !partyPerformance.length && !turnout.length) return <Loading />;
  if (error && !turnout.length) return <ErrorMessage message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div className="animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-primary drop-shadow-sm">State-level Analytics</h1>
          <p className="text-secondary text-sm mt-1 font-medium">Cross-sectional election data and state-wide trends.</p>
        </div>
      </div>

      {/* Turnout Trend */}
      <div className="glass-card p-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Historical Voter Turnout (Total Votes Cast)</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={turnout} margin={{ top: 10, right: 30, left: 30, bottom: 0 }}>
              <defs>
                <linearGradient id="colorTurnout" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} />
              <Tooltip 
                formatter={(value) => new Intl.NumberFormat('en-IN').format(value)}
                contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} 
              />
              <Area type="monotone" dataKey="total_votes" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorTurnout)" strokeWidth={3} name="Total Votes" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-12 pt-8 border-t border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <h2 className="text-xl font-bold text-primary drop-shadow-sm">Cross-sectional Election Comparison</h2>
          <div className="flex items-center glass-card overflow-hidden">
            <div className="pl-3 py-2 bg-slate-100 border-r border-slate-200">
              <Filter size={16} className="text-primary" />
            </div>
            <select 
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="px-4 py-2 outline-none text-sm font-bold w-32 bg-transparent text-slate-800 cursor-pointer"
            >
              {elections.map(e => (
                <option key={e.year} value={e.year}>{e.year}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          {/* Seat Distribution */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider">Seat Distribution ({selectedYear})</h3>
            {loading ? <div className="h-80 flex justify-center items-center"><Loading/></div> : (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={partyPerformance} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="party__abbreviation" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569'}} width={60} />
                    <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px'}}/>
                    <Bar dataKey="seats_won" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Seats Won">
                      {/* Optional custom labels could go here */}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Vote Share Distribution */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider">Vote Share Breakdown (%)</h3>
            {loading ? <div className="h-80 flex justify-center items-center"><Loading/></div> : (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={partyPerformance} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="party__abbreviation" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} domain={[0, 'auto']} />
                    <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px'}} />
                    <Bar dataKey="vote_share" fill="#10b981" radius={[4, 4, 0, 0]} name="Vote Share %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
