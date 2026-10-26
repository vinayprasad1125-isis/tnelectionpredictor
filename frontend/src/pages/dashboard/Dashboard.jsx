import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { StatCard, Loading, ErrorMessage } from '../../components/common/Common';
import { dataService } from '../../services/dataService';
import { analyticsService } from '../../services/analyticsService';
import { Map, Users, Vote, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { sidebarOpen } = useOutletContext();
  const [stats, setStats] = useState(null);
  const [performance, setPerformance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // We use Promise.all for parallel fetching
        const [constituencySummary, parties, elections] = await Promise.all([
          dataService.getConstituencySummary(),
          dataService.getParties(),
          dataService.getElections({ ordering: '-year' })
        ]);

        const latestYear = elections.results.length > 0 ? elections.results[0].year : 'N/A';
        const perf = await analyticsService.getPartyPerformance(latestYear);
        
        setStats({
          constituenciesCount: constituencySummary.count,
          partiesCount: parties.results ? parties.results.length : parties.length,
          latestElection: latestYear,
          totalElections: elections.count
        });
        
        const topParties = perf.slice(0, 10);
        const tvk = perf.find((party) => party.party__abbreviation === 'TVK');
        setPerformance(tvk && !topParties.includes(tvk) ? [...topParties, tvk] : topParties);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="space-y-6 relative">
      {/* Decorative Leader Image - visible when sidebar is closed */}
      <div
        className="hidden md:block fixed bottom-0 left-0 z-10 pointer-events-none"
        style={{
          transition: 'opacity 0.5s ease, transform 0.5s ease',
          opacity: sidebarOpen ? 0 : 1,
          transform: sidebarOpen ? 'scale(0.3) translateX(-50%)' : 'scale(1) translateX(0)',
          transformOrigin: 'bottom left',
          maxWidth: '260px',
          width: '18vw',
          minWidth: '160px',
          mixBlendMode: 'darken',
        }}
      >
        <img
          src="/vijay.png"
          alt="Vijay"
          className="w-full h-auto object-contain select-none"
          draggable={false}
          style={{ 
            filter: 'contrast(1.05) brightness(1.05)'
          }}
        />
      </div>

      {/* Decorative Center Image - visible when sidebar is closed */}
      <div
        className="hidden md:block fixed bottom-0 left-1/2 z-[9] pointer-events-none"
        style={{
          transition: 'opacity 0.5s ease, transform 0.5s ease',
          opacity: sidebarOpen ? 0 : 1,
          transform: sidebarOpen ? 'translateX(-50%) scale(0.3)' : 'translateX(-50%) scale(1)',
          transformOrigin: 'bottom center',
          maxWidth: '300px',
          width: '22vw',
          minWidth: '180px',
          mixBlendMode: 'darken',
        }}
      >
        <img
          src="/seeman.png"
          alt="Seeman"
          className="w-full h-auto object-contain select-none"
          draggable={false}
          style={{
            filter: 'contrast(1.05) brightness(1.05)'
          }}
        />
      </div>

      {/* Decorative Leader Image (Right) - visible when sidebar is closed */}
      <div
        className="hidden md:block fixed bottom-0 right-0 z-10 pointer-events-none"
        style={{
          transition: 'opacity 0.5s ease, transform 0.5s ease',
          opacity: sidebarOpen ? 0 : 1,
          transform: sidebarOpen ? 'scale(0.3) translateX(50%)' : 'scale(1) translateX(0)',
          transformOrigin: 'bottom right',
          maxWidth: '260px',
          width: '18vw',
          minWidth: '160px',
          mixBlendMode: 'darken',
        }}
      >
        <img
          src="/leader-point.png"
          alt="Leader"
          className="w-full h-auto object-contain select-none"
          draggable={false}
          style={{ 
            filter: 'contrast(1.05) brightness(1.05)'
          }}
        />
      </div>

      <div className="flex items-center justify-between mb-8">
        <div className="animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-primary drop-shadow-sm">Overview</h1>
          <p className="text-secondary text-sm mt-1 font-medium">Tamil Nadu Assembly Election Statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <StatCard title="Constituencies" value={stats?.constituenciesCount} icon={Map} />
        <StatCard title="Registered Parties" value={stats?.partiesCount} icon={Users} />
        <StatCard title="Total Elections" value={stats?.totalElections} icon={Vote} />
        <StatCard title="Latest Election Year" value={stats?.latestElection} icon={TrendingUp} />
      </div>

      {/* Main Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Latest Election Seats Won (Top 10)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performance} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="party__abbreviation" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <Tooltip 
                  cursor={{fill: '#f1f5f9'}}
                  contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                />
                <Bar dataKey="seats_won" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Seats Won" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Vote Share Breakdown (%)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performance} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="party__abbreviation" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <Tooltip 
                  cursor={{fill: '#f1f5f9'}}
                  contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                />
                <Bar dataKey="vote_share" fill="#0ea5e9" radius={[4, 4, 0, 0]} name="Vote Share %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

