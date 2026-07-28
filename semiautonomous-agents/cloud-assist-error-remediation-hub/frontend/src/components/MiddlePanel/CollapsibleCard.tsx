import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Maximize2, Minimize2 } from 'lucide-react';

interface CollapsibleCardProps {
  title: React.ReactNode;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  children: React.ReactNode;
  defaultCollapsed?: boolean;
  className?: string;
  headerRightContent?: React.ReactNode;
  isLightMode?: boolean;
}

export const CollapsibleCard: React.FC<CollapsibleCardProps> = ({
  title,
  icon,
  badge,
  children,
  defaultCollapsed = false,
  className = "",
  headerRightContent,
  isLightMode = false
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  return (
    <div className={`rounded-2xl border shadow-lg transition-all duration-300 overflow-hidden ${
      isLightMode
        ? 'bg-white border-slate-300 text-slate-950 shadow-slate-200/60 font-sans'
        : 'bg-[#111622]/90 border-slate-800/80 text-white shadow-xl'
    } ${className}`}>
      {/* Clickable Section Header */}
      <div className={`p-4 border-b flex items-center justify-between gap-3 select-none ${
        isLightMode
          ? 'bg-slate-50 border-slate-200 text-slate-950'
          : 'bg-[#0f1420] border-slate-800/60 text-white'
      }`}>
        <div
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center space-x-2.5 cursor-pointer flex-1 group"
        >
          <button
            type="button"
            className={`p-1 rounded-md transition-colors ${
              isLightMode
                ? 'bg-slate-200 group-hover:bg-slate-300 text-slate-800'
                : 'bg-slate-800/80 group-hover:bg-slate-700 text-slate-300'
            }`}
          >
            {isCollapsed ? (
              <ChevronRight className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
            ) : (
              <ChevronDown className={`w-4 h-4 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
            )}
          </button>

          {icon && (
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 border ${
              isLightMode
                ? 'bg-slate-100 border-slate-300 text-slate-900'
                : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
            }`}>
              {icon}
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className={`text-sm font-bold tracking-tight transition-colors ${
                isLightMode
                  ? 'text-slate-950 group-hover:text-slate-700 font-mono'
                  : 'text-white group-hover:text-cyan-300'
              }`}>
                {title}
              </h2>
              {badge}
              {isCollapsed && (
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  isLightMode
                    ? 'bg-slate-200 text-slate-700 font-bold'
                    : 'bg-slate-800/50 text-slate-500'
                }`}>
                  [Collapsed]
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 flex-shrink-0">
          {headerRightContent}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`p-1.5 rounded-lg border transition-colors flex items-center gap-1 text-[11px] font-medium cursor-pointer ${
              isLightMode
                ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-800 font-mono font-bold'
                : 'bg-slate-800/60 hover:bg-slate-700 border-transparent text-slate-400 hover:text-white'
            }`}
            title={isCollapsed ? "Expand Section" : "Collapse Section"}
          >
            {isCollapsed ? (
              <>
                <Maximize2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Expand</span>
              </>
            ) : (
              <>
                <Minimize2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Shrink</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Expandable/Collapsible Body */}
      {!isCollapsed && <div className="p-5">{children}</div>}
    </div>
  );
};
