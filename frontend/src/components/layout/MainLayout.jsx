import React, { useState, useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Vote, Map, Users, BarChart3, BrainCircuit, Menu, X, LogOut, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { logout } = useAuth();

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };
    // Set initial state based on window size
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Elections', path: '/elections', icon: Vote },
    { name: 'Constituencies', path: '/constituencies', icon: Map },
    { name: 'Parties', path: '/parties', icon: Users },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Predictions', path: '/predictions', icon: BrainCircuit },
  ];

  return (
    <div className="min-h-screen bg-transparent flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden glass-panel text-primary p-4 flex justify-between items-center">
        <h1 className="font-bold text-lg">TN Election Analytics</h1>
        <button onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} w-full md:w-64 glass-panel text-primary flex-shrink-0 flex flex-col shadow-xl transition-all duration-300`}>
        <div className="p-6 flex justify-between items-start">
          <h1 className="text-xl font-bold text-primary tracking-tight">TN Election<br/><span className="text-accent">Analytics</span></h1>
          <button onClick={() => setSidebarOpen(false)} className="hidden md:block text-slate-400 hover:text-primary transition-colors mt-1">
            <PanelLeftClose size={20} />
          </button>
        </div>
        
        <nav className="flex-1 px-4 pb-4 space-y-1 mt-4 md:mt-0">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={() => {
                if (window.innerWidth < 768) setSidebarOpen(false);
              }}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 mb-2 rounded-lg transition-all ${
                  isActive
                    ? 'bg-blue-50 text-accent shadow-sm border border-blue-100'
                    : 'hover:bg-slate-100 hover:text-primary text-secondary'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-slate-200">
          <button 
            onClick={logout}
            className="flex items-center w-full px-4 py-2 text-sm font-medium text-secondary hover:text-primary hover:bg-slate-100 rounded-lg transition-all"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-transparent">
        {/* Header containing toggle when sidebar is closed */}
        {!sidebarOpen && (
          <div className="hidden md:flex items-center p-4 pb-0 w-full">
             <button 
               onClick={() => setSidebarOpen(true)}
               className="p-2 bg-white rounded-lg border border-slate-200 shadow-sm text-slate-500 hover:text-primary transition-colors flex items-center gap-2"
             >
               <PanelLeftOpen size={20} />
               <span className="text-sm font-medium">Menu</span>
             </button>
          </div>
        )}
        <main className={`flex-1 overflow-y-auto p-4 md:p-8 animate-fade-in ${!sidebarOpen ? 'md:pt-4' : ''}`}>
          <div className="max-w-7xl mx-auto">
            <Outlet context={{ sidebarOpen }} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
