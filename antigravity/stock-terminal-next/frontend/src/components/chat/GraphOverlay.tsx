import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Maximize2, Minimize2, Share2 } from 'lucide-react';
import { useDashboardStore } from '../../store/dashboardStore';
import AgentGraph from './AgentGraph';

export const GraphOverlay: React.FC = () => {
    const { isGraphOverlayOpen, setGraphOverlayOpen, chatSidebarWidth, isChatOpen, chatDockPosition, topology, executionPath, nodeDurations, nodeMetrics } = useDashboardStore();
    // Use execution path from store

    const [isMaximized, setIsMaximized] = React.useState(false);

    if (!isGraphOverlayOpen) return null;

    // Calculate dynamic right offset
    // If chat is docked and open, offset by sidebar width + padding.
    // Otherwise, just standard padding.
    const rightOffset = (isChatOpen && chatDockPosition === 'right') ? chatSidebarWidth + 24 : 24;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="fixed z-40 overflow-hidden bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col"
                style={{
                    boxShadow: "0 0 40px rgba(0,0,0,0.3)",
                    top: isMaximized ? 16 : 80,
                    bottom: isMaximized ? 16 : 80,
                    left: isMaximized ? 16 : 80,
                    right: isMaximized ? 16 : rightOffset
                }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--bg-app)]/50">
                    <div className="flex items-center gap-2 text-[var(--brand)] font-bold">
                        <Share2 size={18} />
                        <h3>Live Execution Topology</h3>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setIsMaximized(!isMaximized)}
                            className="p-1.5 hover:bg-[var(--bg-app)] rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                        >
                            {isMaximized ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                        </button>
                        <button
                            onClick={() => setGraphOverlayOpen(false)}
                            className="p-1.5 hover:bg-red-500/10 rounded-md text-[var(--text-muted)] hover:text-red-500 transition-colors"
                        >
                            <X size={18} />
                        </button>
                    </div>
                </div>

                {/* Graph Content */}
                <div className="flex-1 relative bg-[var(--bg-app)]">
                    {!topology ? (
                        <div className="w-full h-full flex flex-col items-center justify-center text-[var(--text-muted)]">
                            <Share2 size={48} className="mb-4 opacity-20" />
                            <p>No Execution Graph Available</p>
                            <p className="text-xs opacity-60">Start a chat to generate the agent topology.</p>
                        </div>
                    ) : (
                        <AgentGraph
                            topology={topology}
                            executionPath={executionPath}
                            activeNodeId={executionPath.length > 0 ? executionPath[executionPath.length - 1] : null}
                            nodeDurations={nodeDurations}
                            nodeMetrics={nodeMetrics}
                            layoutDirection="LR"
                        />
                    )}
                </div>
            </motion.div>
        </AnimatePresence>
    );
};
