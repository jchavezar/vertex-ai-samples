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
}

export const CollapsibleCard: React.FC<CollapsibleCardProps> = ({
  title,
  icon,
  badge,
  children,
  defaultCollapsed = false,
  className = "",
  headerRightContent
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  return (
    <div className={`rounded-xl bg-[#111622]/90 border border-slate-800/80 shadow-lg transition-all duration-300 ${className}`}>
      {/* Clickable Section Header */}
      <div className="p-4 border-b border-slate-800/60 flex items-center justify-between gap-3 select-none">
        <div
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center space-x-2.5 cursor-pointer flex-1 group"
        >
          <button
            type="button"
            className="p-1 rounded-md bg-slate-800/80 group-hover:bg-slate-700 text-slate-300 transition-colors"
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-cyan-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-cyan-400" />
            )}
          </button>

          {icon && (
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0">
              {icon}
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-sm font-bold text-white tracking-tight group-hover:text-cyan-300 transition-colors">
                {title}
              </h2>
              {badge}
              {isCollapsed && (
                <span className="text-[10px] font-mono text-slate-500 bg-slate-800/50 px-2 py-0.5 rounded">
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
            className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors flex items-center gap-1 text-[11px] font-medium"
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
