import React from 'react';
import { Clock, Filter } from 'lucide-react';

interface TimeFilterBarProps {
  selectedRange: string;
  onSelectRange: (range: string) => void;
  isLoading: boolean;
  isLightMode?: boolean;
}

const TIME_OPTIONS = [
  { id: '15m', label: 'Last 15m' },
  { id: '1h', label: 'Last 1h' },
  { id: '6h', label: 'Last 6h' },
  { id: '24h', label: 'Last 24h' },
  { id: '7d', label: 'Last 7d' }
];

export const TimeFilterBar: React.FC<TimeFilterBarProps> = ({
  selectedRange,
  onSelectRange,
  isLoading,
  isLightMode = false
}) => {
  return (
    <div className={`p-2.5 border-b flex flex-col gap-2 w-full overflow-hidden transition-colors duration-300 ${
      isLightMode
        ? 'bg-white border-slate-200 text-slate-900'
        : 'bg-[#0e131d]/90 border-slate-800/80 text-slate-400'
    }`}>
      <div className={`flex items-center space-x-1.5 text-xs font-medium ${isLightMode ? 'text-slate-700 font-mono font-bold' : 'text-slate-400'}`}>
        <Clock className={`w-3.5 h-3.5 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
        <span>Cloud Logging Window:</span>
      </div>
      <div className={`grid grid-cols-5 gap-0.5 p-0.5 rounded-lg border w-full ${
        isLightMode
          ? 'bg-slate-100 border-slate-300'
          : 'bg-slate-950/70 border-slate-800/80'
      }`}>
        {TIME_OPTIONS.map((opt) => {
          const isActive = selectedRange === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => onSelectRange(opt.id)}
              disabled={isLoading}
              className={`w-full py-1 text-[11px] font-medium rounded-md transition-all duration-150 cursor-pointer text-center truncate ${
                isActive
                  ? isLightMode
                    ? 'bg-slate-950 text-white font-mono font-bold shadow-sm'
                    : 'bg-gradient-to-r from-blue-600/80 to-cyan-600/80 text-white shadow-sm ring-1 ring-cyan-400/30'
                  : isLightMode
                    ? 'text-slate-600 hover:text-slate-950 hover:bg-slate-200'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
              title={opt.label}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};

