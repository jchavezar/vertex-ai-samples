import React from 'react';
import { GcpErrorItem } from '../../types';
import { AlertTriangle, Server, Database, Box, HardDrive, ChevronRight } from 'lucide-react';

interface ErrorListProps {
  errors: GcpErrorItem[];
  selectedErrorId: string | null;
  onSelectError: (error: GcpErrorItem) => void;
  isLoading: boolean;
  isLightMode?: boolean;
}

const getServiceIcon = (serviceName: string, isLight: boolean) => {
  if (serviceName.includes('Cloud Run')) return <Server className={`w-4 h-4 ${isLight ? 'text-slate-900' : 'text-cyan-400'}`} />;
  if (serviceName.includes('SQL')) return <Database className={`w-4 h-4 ${isLight ? 'text-purple-700' : 'text-purple-400'}`} />;
  if (serviceName.includes('Kubernetes') || serviceName.includes('GKE')) return <Box className={`w-4 h-4 ${isLight ? 'text-blue-700' : 'text-blue-400'}`} />;
  return <HardDrive className={`w-4 h-4 ${isLight ? 'text-amber-700' : 'text-amber-400'}`} />;
};

export const ErrorList: React.FC<ErrorListProps> = ({
  errors,
  selectedErrorId,
  onSelectError,
  isLoading,
  isLightMode = false
}) => {
  if (isLoading) {
    return (
      <div className={`flex-1 flex flex-col items-center justify-center p-8 text-center ${isLightMode ? 'bg-white text-slate-600' : ''}`}>
        <div className={`w-8 h-8 rounded-full border-2 ${isLightMode ? 'border-slate-300 border-t-slate-900' : 'border-cyan-500/20 border-t-cyan-400'} animate-spin mb-3`}></div>
        <p className="text-xs font-mono">Querying Google Cloud Platform Telemetry...</p>
      </div>
    );
  }

  if (errors.length === 0) {
    return (
      <div className={`flex-1 flex flex-col items-center justify-center p-8 text-center ${isLightMode ? 'bg-white text-slate-600' : 'text-slate-400'}`}>
        <p className="text-sm font-medium">No errors detected in this time window.</p>
        <p className="text-xs opacity-75 mt-1">Try expanding the historical time range filter above.</p>
      </div>
    );
  }

  return (
    <div className={`flex-1 overflow-y-auto divide-y transition-colors duration-300 ${
      isLightMode
        ? 'bg-white divide-slate-200'
        : 'divide-slate-800/60'
    }`}>
      {errors.map((err) => {
        const isSelected = selectedErrorId === err.id;
        return (
          <div
            key={err.id}
            onClick={() => onSelectError(err)}
            className={`p-3.5 cursor-pointer transition-all duration-200 group relative ${
              isSelected
                ? isLightMode
                  ? 'bg-slate-100 border-l-4 border-slate-950 shadow-sm'
                  : 'bg-gradient-to-r from-blue-950/70 via-slate-900/90 to-cyan-950/40 border-l-4 border-cyan-400 shadow-md'
                : isLightMode
                  ? 'hover:bg-slate-50'
                  : 'hover:bg-slate-900/60'
            }`}
          >
            {/* Top Row: Severity + Service */}
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <span
                  className={`text-[10px] font-bold tracking-wider px-2 py-0.5 rounded uppercase ${
                    err.severity === 'CRITICAL'
                      ? isLightMode
                        ? 'bg-red-100 text-red-700 border border-red-300'
                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : isLightMode
                        ? 'bg-amber-100 text-amber-800 border border-amber-300'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {err.severity}
                </span>
                <span className={`flex items-center space-x-1.5 text-xs font-medium ${isLightMode ? 'text-slate-900 font-mono font-bold' : 'text-slate-300'}`}>
                  {getServiceIcon(err.serviceName, isLightMode)}
                  <span>{err.serviceName}</span>
                </span>
              </div>
              <span className={`text-[11px] font-mono ${isLightMode ? 'text-slate-500' : 'text-slate-400'}`}>
                {new Date(err.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>

            {/* Title / Summary */}
            <div className="flex items-start justify-between gap-2">
              <h3
                className={`text-xs font-semibold leading-relaxed line-clamp-2 ${
                  isSelected
                    ? isLightMode
                      ? 'text-slate-950 font-bold'
                      : 'text-cyan-200'
                    : isLightMode
                      ? 'text-slate-800 group-hover:text-slate-950'
                      : 'text-slate-200 group-hover:text-cyan-300'
                }`}
              >
                {err.summary}
              </h3>
              <ChevronRight
                className={`w-4 h-4 flex-shrink-0 transition-transform ${
                  isSelected
                    ? isLightMode
                      ? 'text-slate-950 translate-x-0.5'
                      : 'text-cyan-400 translate-x-0.5'
                    : isLightMode
                      ? 'text-slate-400 group-hover:text-slate-700'
                      : 'text-slate-600 group-hover:text-slate-400'
                }`}
              />
            </div>

            {/* Bottom Row: Resource Badge */}
            <div className="mt-2 flex items-center justify-between">
              <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                isLightMode
                  ? 'bg-slate-100 text-slate-700 border-slate-300'
                  : 'bg-slate-950/60 text-slate-400 border-slate-800/80'
              }`}>
                {err.resourceType}
              </span>
              <span className={`text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity ${
                isLightMode ? 'text-slate-950 font-mono font-bold' : 'text-cyan-400/80'
              }`}>
                Diagnose with Cloud Assist &rarr;
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
