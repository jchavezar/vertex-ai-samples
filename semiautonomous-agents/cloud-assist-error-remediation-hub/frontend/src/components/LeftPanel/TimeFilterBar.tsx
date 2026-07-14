import React from 'react';
import { Clock, Filter } from 'lucide-react';

interface TimeFilterBarProps {
  selectedRange: string;
  onSelectRange: (range: string) => void;
  isLoading: boolean;
}

const TIME_OPTIONS = [
  { id: '15m', label: 'Last 15m' },
  { id: '1h', label: 'Last 1h' },
  { id: '6h', label: 'Last 6h' },
  { id: '24h', label: 'Last 24h' },
  { id: '7d', label: 'Last 7d' }
];

export const TimeFilterBar: React.FC<TimeFilterBarProps> = ({ selectedRange, onSelectRange, isLoading }) => {
  return (
    <div className="p-3 border-b border-slate-800/80 bg-[#0e131d]/90 flex items-center justify-between gap-2">
      <div className="flex items-center space-x-1.5 text-xs font-medium text-slate-400">
        <Clock className="w-3.5 h-3.5 text-cyan-400" />
        <span>Cloud Logging Window:</span>
      </div>
      <div className="flex items-center bg-slate-950/70 p-0.5 rounded-lg border border-slate-800/80">
        {TIME_OPTIONS.map((opt) => {
          const isActive = selectedRange === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => onSelectRange(opt.id)}
              disabled={isLoading}
              className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all duration-150 ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600/80 to-cyan-600/80 text-white shadow-sm ring-1 ring-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
