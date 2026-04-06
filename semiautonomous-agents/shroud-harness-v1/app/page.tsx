"use client";

import { useState } from "react";
import { Search, Briefcase, Sparkles, MessageSquare, Files, Code, User, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatArea } from "@/components/ChatArea";
import { ArtifactPanel } from "@/components/ArtifactPanel";

export default function Home() {
  const [artifact, setArtifact] = useState<{ type: string; content: string } | null>(null);
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-[#212121] overflow-hidden text-[#ececec] font-sans selection:bg-[#d97757]/30">
      
      {/* 1. Navigation Rail (Icons) */}
      <aside className="w-[60px] flex flex-col items-center py-4 border-r border-[#343434] bg-[#171717] z-30">
        <div className="flex flex-col items-center gap-6 mt-2">
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <PlusIcon />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <Search size={20} />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <Briefcase size={20} />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <MessageSquare size={20} />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <Files size={20} />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <Sparkles size={20} />
           </button>
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors">
              <Code size={20} />
           </button>
        </div>
        
        <div className="mt-auto flex flex-col items-center gap-6 mb-4">
           <button className="p-2 text-[#9b9b9b] hover:text-white transition-colors relative">
              <Download size={20} />
              <div className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full border-2 border-[#171717]" />
           </button>
           <div className="w-8 h-8 bg-[#3d3d3d] rounded-full flex items-center justify-center text-xs font-bold text-white border border-[#343434] cursor-pointer hover:bg-[#4d4d4d]">
              J
           </div>
        </div>
      </aside>

      {/* 2. Chat Sidebar (Optional Expand) */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: 260 }}
            exit={{ width: 0 }}
            className="h-full border-r border-[#343434] bg-[#171717] overflow-hidden whitespace-nowrap"
          >
             <div className="p-4 pt-8">
                <h3 className="text-xs font-bold text-[#9b9b9b] uppercase tracking-widest mb-4">Recents</h3>
                <div className="text-sm text-[#ececec] py-2 px-3 hover:bg-[#2f2f2f] rounded-md cursor-pointer truncate">Casual greeting</div>
             </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. Main Content Area */}
      <main className="flex flex-1 overflow-hidden relative">
        <ChatArea 
          onNewArtifact={(type, content) => setArtifact({ type, content })} 
          isArtifactOpen={!!artifact}
        />

        {/* Artifact Panel - Dark Theme */}
        <AnimatePresence>
          {artifact && (
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="w-[48%] h-full border-l border-[#343434] bg-[#171717] shadow-2xl z-20"
            >
              <ArtifactPanel 
                artifact={artifact} 
                onClose={() => setArtifact(null)} 
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function PlusIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 4V16M4 10H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}
