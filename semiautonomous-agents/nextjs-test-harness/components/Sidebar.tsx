"use client";

import { Plus, Clock, Search, Settings } from "lucide-react";

export function Sidebar({ onClose }: { onClose: () => void }) {
  return (
    <div className="flex flex-col h-full p-4 relative">
      {/* Top Header */}
      <div className="flex items-center justify-between mb-8 px-2">
        <h2 className="text-sm font-semibold tracking-tight text-shroud-subtle">Claude</h2>
        <button 
           onClick={onClose}
           className="p-1 hover:bg-shroud-border rounded transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <button className="flex items-center gap-2 w-full p-2 mb-6 bg-shroud-bg border border-shroud-border rounded-shroud hover:shadow-sm transition-all text-sm font-medium">
        <Plus size={16} />
        New Chat
      </button>

      {/* History List */}
      <div className="flex-1 overflow-y-auto space-y-2">
        <div className="text-[10px] font-bold text-shroud-subtle uppercase tracking-widest px-2 mb-2">Recent</div>
        <div className="p-2 text-sm hover:bg-shroud-bg rounded-md cursor-pointer truncate transition-colors">
          Strategic Harness Planning
        </div>
        <div className="p-2 text-sm hover:bg-shroud-bg rounded-md cursor-pointer truncate transition-colors">
          React UI Replication
        </div>
        <div className="p-2 text-sm hover:bg-shroud-bg rounded-md cursor-pointer truncate transition-colors">
          PWA Integration Strategy
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="pt-4 border-t border-shroud-border space-y-2">
        <button className="flex items-center gap-2 w-full p-2 hover:bg-shroud-bg rounded-md text-xs font-medium transition-colors">
          <Clock size={14} />
          Chat History
        </button>
        <button className="flex items-center gap-2 w-full p-2 hover:bg-shroud-bg rounded-md text-xs font-medium transition-colors">
          <Settings size={14} />
          Settings
        </button>
      </div>
    </div>
  );
}
