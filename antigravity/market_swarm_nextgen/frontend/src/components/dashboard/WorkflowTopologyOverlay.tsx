import React from 'react';
import {
  ReactFlow,
  Background,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
  Node,
  Edge,
  BaseEdge,
  EdgeProps,
  getBezierPath
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import {
  X,
  Search,
  Cpu,
  Sparkles,
  Layout,
  Network,
  Brain
} from 'lucide-react';

interface WorkflowNodeData {
  label: string;
  description: string;
  icon: React.ElementType;
}

// --- Custom Node Component ---
const WorkflowNode = ({ data }: { data: WorkflowNodeData }) => {
  const Icon = data.icon;
  return (
    <div className="group relative">
      {/* Glow Effect */}
      <div className="absolute -inset-0.5 bg-emerald-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition duration-500" />

      <div className="relative flex flex-col items-center gap-3 p-4 rounded-xl bg-black/80 border border-emerald-500/30 backdrop-blur-md min-w-[180px] transition-all duration-300 group-hover:border-emerald-500/60 group-hover:scale-105">
        <Handle type="target" position={Position.Top} className="!opacity-0" />

        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
          <Icon size={24} strokeWidth={1.5} />
        </div>

        <div className="text-center">
          <h3 className="text-sm font-bold text-white tracking-wider uppercase mb-1">
            {data.label}
          </h3>
          <p className="text-[10px] text-emerald-400/70 font-mono leading-tight max-w-[140px]">
            {data.description}
          </p>
        </div>

        <Handle type="source" position={Position.Bottom} className="!opacity-0" />
      </div>
    </div>
  );
};

// --- Custom Edge Component ---
const CircuitEdge = ({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
}: EdgeProps) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{ ...style, stroke: 'rgba(16, 185, 129, 0.2)', strokeWidth: 2 }}
      />
      <path
        d={edgePath}
        fill="none"
        stroke="#10b981"
        strokeWidth={2}
        className="react-flow__edge-path-animated"
        style={{
          strokeDasharray: '8, 8',
          animation: 'dash 1s linear infinite',
          filter: 'drop-shadow(0 0 4px #10b981)'
        }}
      />
      <style>{`
        @keyframes dash {
          from { stroke-dashoffset: 16; }
          to { stroke-dashoffset: 0; }
        }
      `}</style>
    </>
  );
};

const nodeTypes = { workflow: WorkflowNode };
const edgeTypes = { circuit: CircuitEdge };

interface Props {
  onClose: () => void;
}

const WorkflowTopologyOverlay: React.FC<Props> = ({ onClose }) => {
  const initialNodes: Node[] = [
    {
      id: 'recon',
      type: 'workflow',
      data: {
        label: 'Neural Recon',
        description: 'Input Stream Analysis',
        icon: Search
      },
      position: { x: 0, y: 0 },
    },
    {
      id: 'context',
      type: 'workflow',
      data: {
        label: 'Strategic Context',
        description: 'Contextual Alpha Parameters',
        icon: Sparkles
      },
      position: { x: -200, y: 120 },
    },
    {
      id: 'discovery',
      type: 'workflow',
      data: {
        label: 'Peer Discovery',
        description: 'Strategic Search Bot',
        icon: Cpu
      },
      position: { x: 0, y: 120 },
    },
    {
      id: 'orchestrator',
      type: 'workflow',
      data: {
        label: 'Orchestrator',
        description: 'Parallel Task Spawner',
        icon: Network
      },
      position: { x: 0, y: 240 },
    },
    {
      id: 'primary',
      type: 'workflow',
      data: {
        label: 'Deep Research: P',
        description: 'Primary Anchor Recon',
        icon: Brain
      },
      position: { x: -150, y: 360 },
    },
    {
      id: 'peers',
      type: 'workflow',
      data: {
        label: 'Deep Research: S',
        description: 'Parallel Peer Recon',
        icon: Cpu
      },
      position: { x: 150, y: 360 },
    },
    {
      id: 'synthesis',
      type: 'workflow',
      data: {
        label: 'Synthesis',
        description: 'Cluster Aggregation',
        icon: Sparkles
      },
      position: { x: 0, y: 480 },
    },
    {
      id: 'arena',
      type: 'workflow',
      data: {
        label: 'Comps Arena',
        description: '3D Entity Projection',
        icon: Layout
      },
      position: { x: 0, y: 600 },
    },
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: 'recon', target: 'discovery', type: 'circuit' },
    { id: 'ec-2', source: 'context', target: 'discovery', type: 'circuit' },
    { id: 'e2-3', source: 'discovery', target: 'orchestrator', type: 'circuit' },
    { id: 'e3-4', source: 'orchestrator', target: 'primary', type: 'circuit' },
    { id: 'e3-5', source: 'orchestrator', target: 'peers', type: 'circuit' },
    { id: 'e4-6', source: 'primary', target: 'synthesis', type: 'circuit' },
    { id: 'e5-6', source: 'peers', target: 'synthesis', type: 'circuit' },
    { id: 'e6-7', source: 'synthesis', target: 'arena', type: 'circuit' },
  ];

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md p-8"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="relative w-full max-w-2xl h-[80vh] bg-zinc-900/90 border border-emerald-500/20 rounded-2xl overflow-hidden shadow-2xl shadow-emerald-500/10"
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 p-6 flex items-center justify-between z-10 bg-gradient-to-b from-zinc-900 to-transparent">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <Network size={20} className="text-emerald-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-widest uppercase">
                ADK Workflow Topology
              </h2>
              <p className="text-[10px] text-emerald-400/60 font-mono tracking-wider">
                NODE_GRAPH.COMPS_ENGINE_v2.0
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-emerald-500/10 rounded-full transition-colors text-zinc-400 hover:text-emerald-400"
          >
            <X size={24} />
          </button>
        </div>

        {/* Graph Container */}
        <div className="w-full h-full pt-16">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            proOptions={{ hideAttribution: true }}
            minZoom={0.5}
            maxZoom={1.5}
            nodesConnectable={false}
            nodesDraggable={true}
            elementsSelectable={false}
          >
            <Background color="#10b981" gap={30} size={1} />
          </ReactFlow>
        </div>

        {/* Footer Info */}
        <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between pointer-events-none">
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[8px] text-emerald-400 font-mono">SYSTEM_READY</span>
            </div>
            <div className="flex items-center gap-2 text-zinc-500 font-mono text-[8px]">
              <span>LATENCY: 42MS</span>
              <span className="opacity-30">|</span>
              <span>TOKEN_STREAM: ACTIVE</span>
            </div>
          </div>
          <div className="text-[8px] text-zinc-600 font-mono italic">
            &copy; 2024 ANTIGRAVITY_SYSTEMS
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default WorkflowTopologyOverlay;
