import { useEffect, useState } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { X, Search, Database, Code, Zap, MessageSquare, Brain, Bot } from 'lucide-react';
import clsx from 'clsx';

export const AdkOverlay = () => {
    const { isAdkOverlayOpen, setAdkOverlayOpen } = useDashboardStore();
    const [step, setStep] = useState(0);

    // Animation Loop for Data Flow
    useEffect(() => {
        if (!isAdkOverlayOpen) return;
        const interval = setInterval(() => {
            setStep((prev) => (prev + 1) % 5);
        }, 1500);
        return () => clearInterval(interval);
    }, [isAdkOverlayOpen]);

    if (!isAdkOverlayOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-8 backdrop-blur-xl bg-black/60">
            {/* Outer grid pattern for context */}
            <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:40px_40px] pointer-events-none opacity-20" />
            
            <button 
                onClick={() => setAdkOverlayOpen(false)}
                className="absolute top-8 right-8 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all z-50 group border border-white/20 hover:scale-110 active:scale-95 shadow-lg shadow-white/5"
            >
                <X size={32} className="group-hover:rotate-90 transition-transform" />
            </button>

            {/* Main Modal - Lighter Dark Theme */}
            <div className="relative w-full max-w-[90vw] h-[85vh] bg-gradient-to-br from-[#2a2a2a] via-[#1a1a1a] to-[#0a0a0a] border border-white/20 rounded-[3rem] overflow-hidden shadow-2xl shadow-black/50 p-8 flex flex-col">
                {/* Subtle Inner Spotlight - Brighter */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none" />
                {/* Header */}
                <div className="absolute top-10 left-0 right-0 text-center z-20">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-white to-purple-300 tracking-tight">
                        ADK System Architecture
                    </h1>
                    <p className="text-sm font-mono text-cyan-300/80 mt-2 tracking-[0.3em] uppercase">Agentic Neural Orchestration Layer</p>
                </div>

                {/* Flowchart Diagram */}
                <div className="flex-1 w-full relative mt-12 flex items-center justify-center">
                    
                    {/* Connection Lines (SVG Layer) */}
                    <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                        <defs>
                            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.4" />
                                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.4" />
                            </linearGradient>
                            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
                            </marker>
                        </defs>

                        {/* User -> Orchestrator */}
                        <path d="M 250,300 C 350,300 350,300 450,300" stroke="url(#flowGradient)" strokeWidth="2" fill="none" className={clsx("transition-all duration-500", step === 0 ? "stroke-cyan-400 stroke-[3px] opacity-100" : "opacity-40")} markerEnd="url(#arrowhead)" />

                        {/* Orchestrator -> Agent (Curved Up) */}
                        <path d="M 650,300 C 700,300 700,200 800,200" stroke="url(#flowGradient)" strokeWidth="2" fill="none" className={clsx("transition-all duration-500", step === 1 ? "stroke-purple-400 stroke-[3px] opacity-100" : "opacity-40")} markerEnd="url(#arrowhead)" />

                        {/* Agent -> Tools (Split downwards) */}
                        <path d="M 1000,200 C 1050,200 1050,350 1000,400" stroke="url(#flowGradient)" strokeWidth="2" fill="none" className={clsx("transition-all duration-500", step === 2 ? "stroke-yellow-400 stroke-[3px] opacity-100" : "opacity-40")} markerEnd="url(#arrowhead)" />

                        {/* Neural Agent Back to Orchestrator (The Big Loop) */}
                        <path d="M 900,100 C 700,50 400,100 300,250" stroke="url(#flowGradient)" strokeWidth="2" fill="none" strokeDasharray="5,5" className={clsx("transition-all duration-500", step === 3 ? "stroke-green-400 stroke-[3px] opacity-100" : "opacity-30")} markerEnd="url(#arrowhead)" />

                        {/* Tools -> Orchestrator (Return) - Optional, maybe implies data return */}
                        <path d="M 900,450 C 700,550 550,550 550,400" stroke="url(#flowGradient)" strokeWidth="2" fill="none" strokeDasharray="5,5" className={clsx("transition-all duration-500", step === 3 ? "stroke-white stroke-[3px] opacity-100" : "opacity-30")} />
                    </svg>

                    {/* Nodes Container */}
                    <div className="relative w-full h-full max-w-7xl mx-auto grid grid-cols-12 grid-rows-6 gap-4 z-10 pointer-events-none">

                        {/* 1. User Input Node */}
                        <div className="col-start-1 col-span-2 row-start-3 flex items-center justify-center">
                            <ArchitectureNode
                                icon={MessageSquare}
                                title="User Input"
                                subtitle="Natural Language"
                                color="cyan"
                                active={step === 0}
                            />
                        </div>

                        {/* 2. ADK Orchestrator Node (Center Hub) */}
                        <div className="col-start-4 col-span-3 row-start-3 flex items-center justify-center">
                            <ArchitectureNode
                                icon={Bot}
                                title="ADK Orchestrator"
                                subtitle="Runtime & Session Manager"
                                color="blue"
                                active={step === 0 || step === 3 || step === 4}
                                size="lg"
                            />
                        </div>

                        {/* 3. Neural Agent Node (Top Right) */}
                        <div className="col-start-8 col-span-3 row-start-2 flex items-center justify-center">
                            <ArchitectureNode
                                icon={Brain}
                                title="Neural Agent"
                                subtitle="Gemini 2.5 Pro"
                                color="purple"
                                active={step === 1}
                                size="lg"
                            />
                        </div>

                        {/* 4. Tools Cluster (Below Agent) */}
                        <div className="col-start-8 col-span-3 row-start-4 flex flex-row gap-4 justify-center items-start mt-4">
                            <ToolNode icon={Search} label="Search" active={step === 2} delay={0} />
                            <ToolNode icon={Database} label="FactSet" active={step === 2} delay={100} />
                            <ToolNode icon={Code} label="Code" active={step === 2} delay={200} />
                        </div>

                        {/* 5. Response Node (Bottom Left-Center) - Implied Output */}
                    </div>
                </div>

                <div className="absolute bottom-6 left-0 right-0 text-center">
                    <p className="font-mono text-[10px] text-gray-500 tracking-[0.2em] uppercase">Architecture Visualization • v2.5.1-adk-refreshed</p>
                </div>
            </div>
        </div>
    );
};

const ArchitectureNode = ({ icon: Icon, title, subtitle, color, active, size = 'md' }: any) => {
    const gradients = {
        cyan: "from-cyan-500/20 to-cyan-900/40 border-cyan-400/50",
        blue: "from-blue-500/20 to-blue-900/40 border-blue-400/50",
        purple: "from-purple-500/20 to-purple-900/40 border-purple-400/50",
        white: "from-white/10 to-gray-800/40 border-white/50",
    };

    const iconColors = {
        cyan: "text-cyan-200 bg-cyan-500/20",
        blue: "text-blue-200 bg-blue-500/20",
        purple: "text-purple-200 bg-purple-500/20",
        white: "text-white bg-white/10",
    };

    const activeGlow = {
        cyan: "shadow-[0_0_50px_rgba(34,211,238,0.5)] border-cyan-300",
        blue: "shadow-[0_0_50px_rgba(59,130,246,0.5)] border-blue-300",
        purple: "shadow-[0_0_50px_rgba(168,85,247,0.5)] border-purple-300",
        white: "shadow-[0_0_50px_rgba(255,255,255,0.4)] border-white",
    };

    const isLg = size === 'lg';

    return (
        <div className={clsx(
            "relative rounded-2xl border backdrop-blur-xl transition-all duration-700 flex flex-col items-center justify-center gap-3 overflow-hidden group",
            isLg ? "w-64 h-48 p-6" : "w-48 h-36 p-4",
            "bg-gradient-to-br",
            gradients[color as keyof typeof gradients],
            active ? clsx("scale-105 opacity-100", activeGlow[color as keyof typeof activeGlow]) : "scale-100 opacity-80 grayscale-[0.3]"
        )}>
            {/* Chrome/Glass Shine Effect */}
            <div className={clsx(
                "absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent skew-x-12 translate-x-[-150%] transition-transform duration-1000",
                active ? "animate-shine" : ""
            )} />

            <div className={clsx(
                "rounded-full flex items-center justify-center transition-all duration-500 relative z-10",
                isLg ? "w-16 h-16" : "w-12 h-12",
                iconColors[color as keyof typeof iconColors],
                active ? "scale-110 shadow-lg text-white" : ""
            )}>
                <Icon size={isLg ? 32 : 24} className={clsx("transition-all duration-500", active ? "drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" : "")} />
            </div>

            <div className="text-center relative z-10">
                <h3 className={clsx("font-bold text-white tracking-wide transition-all duration-300", isLg ? "text-lg" : "text-sm", active ? "text-shadow-glow" : "")}>{title}</h3>
                <p className={clsx("font-mono uppercase tracking-wider transition-opacity duration-300", isLg ? "text-xs" : "text-[10px]", active ? "opacity-100 text-white/90" : "opacity-60 text-white/60")}>{subtitle}</p>
            </div>

            {/* Active Ping */}
            {active && (
                <span className="absolute top-3 right-3 flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                </span>
            )}
        </div>
    );
};

const ToolNode = ({ icon: Icon, label, active, delay }: any) => {
    return (
        <div className={clsx(
            "flex flex-col items-center gap-2 p-3 rounded-xl border backdrop-blur-md transition-all duration-500 min-w-[80px]",
            active ?
                "translate-y-2 border-yellow-400/80 bg-gradient-to-b from-yellow-500/10 to-yellow-900/10 shadow-[0_0_20px_rgba(250,204,21,0.2)] text-yellow-300 scale-105" :
                "border-white/10 bg-white/5 text-gray-400 hover:bg-white/10 hover:border-white/20"
        )} style={{ transitionDelay: `${delay}ms` }}>
            <Icon size={20} />
            <span className="text-[10px] font-mono font-bold uppercase">{label}</span>
            {active && <div className="w-1 absolute top-2 right-2 h-1 rounded-full bg-yellow-400 animate-pulse" />}
        </div>
    );
};
