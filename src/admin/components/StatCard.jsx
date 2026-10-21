import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const StatCard = ({ title, value, change, isPositive = true, icon: Icon, color = 'indigo' }) => {
  const bgColors = {
    indigo: 'bg-indigo-50 text-indigo-600',
    amber: 'bg-amber-50 text-amber-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    rose: 'bg-rose-50 text-rose-600',
    blue: 'bg-sky-50 text-sky-600',
  };

  return (
    <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between">
      <div className="space-y-1">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">{title}</p>
        <h3 className="text-2xl font-extrabold text-gray-900 tracking-tight">{value}</h3>

        {change && (
          <div className="flex items-center gap-1 text-[11px] font-bold">
            {isPositive ? (
              <span className="text-emerald-600 flex items-center">
                <TrendingUp className="w-3 h-3 mr-0.5" /> +{change}
              </span>
            ) : (
              <span className="text-rose-600 flex items-center">
                <TrendingDown className="w-3 h-3 mr-0.5" /> -{change}
              </span>
            )}
            <span className="text-gray-400 font-normal">vs last month</span>
          </div>
        )}
      </div>

      {Icon && (
        <div className={`p-3.5 rounded-2xl ${bgColors[color] || bgColors.indigo}`}>
          <Icon className="w-6 h-6" />
        </div>
      )}
    </div>
  );
};

export default StatCard;
