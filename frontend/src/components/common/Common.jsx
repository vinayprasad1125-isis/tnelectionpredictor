import React from 'react';

export const StatCard = ({ title, value, icon: Icon, trend }) => {
  return (
    <div className="glass-card p-6 hover:-translate-y-1 hover:shadow-[0_8px_32px_0_rgba(31,38,135,0.15)] transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-700/80">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">{value}</p>
        </div>
        <div className="w-12 h-12 bg-white/40 backdrop-blur-sm rounded-lg flex items-center justify-center text-accent shadow-sm">
          {Icon && <Icon size={24} />}
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center text-sm">
          <span className={`font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {trend.value}
          </span>
          <span className="text-secondary ml-2">{trend.label}</span>
        </div>
      )}
    </div>
  );
};

export const Loading = () => (
  <div className="flex justify-center items-center h-64">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
  </div>
);

export const ErrorMessage = ({ message }) => (
  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg relative" role="alert">
    <strong className="font-bold mr-2">Error:</strong>
    <span className="block sm:inline">{message}</span>
  </div>
);
