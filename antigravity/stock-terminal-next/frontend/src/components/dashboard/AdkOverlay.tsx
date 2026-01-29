
import React from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { X, Search, Database, Cpu, Layers, Code, Zap, Server, Globe } from 'lucide-react';
import clsx from 'clsx';

export const AdkOverlay = () => {
    const { isAdkOverlayOpen, setAdkOverlayOpen } = useDashboardStore();

    if (!isAdkOverlayOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-8 backdrop-blur-2xl bg-black/80 animate-fade-in">
            <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:40px_40px] pointer-events-none" />
            
            <button 
                onClick={() => setAdkOverlayOpen(false)}
                className="absolute top-8 right-8 p-3 rounded-full bg-white/5 hover:bg-white/20 text-white transition-all z-20"
            >
                <X size={32} />
            </button>

            <div className="relative w-full max-w-6xl aspect-video bg-black/40 border border-white/10 rounded-3xl overflow-hidden shadow-2xl shadow-cyan-900/40 p-12 flex flex-col items-center justify-center">
                {/* Tech Background Rings */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-cyan-500/20 rounded-full animate-spin-slow opacity-30" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-purple-500/20 rounded-full animate-spin-reverse-slow opacity-30" />
                
                <h1 className="text-5xl font-bold text-center mb-16 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-white to-purple-400 tracking-tight z-10 relative">
                     Google Agent Development Kit (ADK)
                     <span className="block text-xl font-mono font-normal text-cyan-400/80 mt-4 tracking-widest uppercase">System Architecture Visualization</span>
                </h1>

                <div className="grid grid-cols-3 gap-12 w-full max-w-5xl z-10 relative">
                    
                    {/* Element 1: Agent Runtime */}
                    <div className="group relative">
                        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 to-transparent rounded-2xl blur-xl transition-all duration-500 group-hover:bg-cyan-500/20" />
                        <div className="relative p-8 rounded-2xl border border-white/10 bg-black/40 backdrop-blur-md flex flex-col items-center gap-6 hover:-translate-y-2 transition-transform duration-300 h-full border-t-cyan-500/50">
                            <div className="w-20 h-20 rounded-2xl bg-cyan-500/10 flex items-center justify-center border border-cyan-400/30 group-hover:scale-110 transition-transform">
                                <Cpu size={40} className="text-cyan-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white">Neural Agent</h3>
                            <div className="flex flex-col gap-2 w-full">
                                <CodeBadge label="google.adk.agents.Agent" color="cyan" />
                                <CodeBadge label="model='gemini-2.5-flash-lite'" color="blue" />
                                <CodeBadge label="Instruction Tuned" color="gray" />
                            </div>
                        </div>
                    </div>

                    {/* Element 2: Tools (Highlighted) */}
                    <div className="group relative scale-110 -translate-y-4">
                        <div className="absolute inset-0 bg-gradient-to-b from-yellow-500/10 to-transparent rounded-2xl blur-xl transition-all duration-500 group-hover:bg-yellow-500/20" />
                        <div className="relative p-8 rounded-2xl border border-white/10 bg-black/40 backdrop-blur-md flex flex-col items-center gap-6 hover:-translate-y-2 transition-transform duration-300 h-full border-t-yellow-500 shadow-2xl shadow-yellow-500/10">
                            <div className="w-24 h-24 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-400/50 relative group-hover:scale-110 transition-transform animate-pulse">
                                <div className="absolute inset-0 bg-yellow-400/20 rounded-full animate-ping" />
                                <Search size={48} className="text-yellow-400 relative z-10" />
                            </div>
                            <h3 className="text-2xl font-bold text-yellow-400">Search Tool</h3>
                            <p className="text-gray-400 text-sm text-center">Real-time Web Intelligence</p>
                            <div className="flex flex-col gap-2 w-full mt-2">
                                <CodeBadge label="google.adk.tools.google_search" color="yellow" filled={true} />
                                <CodeBadge label="Live Trends Extraction" color="gray" />
                            </div>
                        </div>
                    </div>

                     {/* Element 3: Runtime */}
                     <div className="group relative">
                        <div className="absolute inset-0 bg-gradient-to-b from-purple-500/10 to-transparent rounded-2xl blur-xl transition-all duration-500 group-hover:bg-purple-500/20" />
                        <div className="relative p-8 rounded-2xl border border-white/10 bg-black/40 backdrop-blur-md flex flex-col items-center gap-6 hover:-translate-y-2 transition-transform duration-300 h-full border-t-purple-500/50">
                            <div className="w-20 h-20 rounded-2xl bg-purple-500/10 flex items-center justify-center border border-purple-400/30 group-hover:scale-110 transition-transform">
                                <Server size={40} className="text-purple-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white">ADK Runtime</h3>
                            <div className="flex flex-col gap-2 w-full">
                                <CodeBadge label="google.adk.Runner" color="purple" />
                                <CodeBadge label="InMemorySessionService" color="purple" />
                                <CodeBadge label="Async Stream Prototype" color="gray" />
                            </div>
                        </div>
                    </div>

                </div>

                <div className="absolute bottom-8 text-center w-full">
                     <p className="font-mono text-xs text-gray-500 tracking-[0.2em] uppercase">Powered by Vertex AI • Built with Google ADK</p>
                </div>
            </div>
        </div>
    );
};

const CodeBadge = ({ label, color, filled = false }: { label: string, color: 'cyan' | 'blue' | 'purple' | 'yellow' | 'gray', filled?: boolean }) => {
    const colors = {
        cyan: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
        blue: "text-blue-400 border-blue-500/30 bg-blue-500/10",
        purple: "text-purple-400 border-purple-500/30 bg-purple-500/10",
        yellow: "text-yellow-400 border-yellow-500/50 bg-yellow-500/10",
        gray: "text-gray-400 border-gray-500/30 bg-gray-500/10",
    };

    const filledColors = {
        yellow: "text-black bg-yellow-400 border-yellow-400 font-bold",
        cyan: "", blue: "", purple: "", gray: "" // Add others if needed
    };

    return (
        <div className={clsx(
            "px-3 py-1.5 rounded-md text-xs font-mono border text-center transition-all",
            filled ? filledColors[color as keyof typeof filledColors] : colors[color],
            !filled && "hover:bg-opacity-20 hover:scale-105 cursor-default"
        )}>
            {label}
        </div>
    );
};
