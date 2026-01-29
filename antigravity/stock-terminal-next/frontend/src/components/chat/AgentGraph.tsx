import React, { useEffect } from 'react';
import { ReactFlow, Background, useNodesState, useEdgesState, Position, Handle, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { Bot, Layers, Repeat, Globe, Zap, Database, Clock, BarChart2 } from 'lucide-react';

// --- Types ---
interface TopologyNode {
  id: string;
  label: string;
  type?: string;
  model?: string;
  tools?: string[];
  duration?: number;
}

interface TopologyEdge {
  source: string;
  target: string;
}

export interface ProcessorTopology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

interface AgentGraphProps {
  topology: ProcessorTopology | null;
  activeNodeId?: string | null;
  executionPath?: string[];
  nodeDurations?: Record<string, number>;
  nodeMetrics?: Record<string, any>;
  layoutDirection?: 'TB' | 'LR';
}

// --- Custom Nodes ---

const AgentNode = ({ data, sourcePosition = Position.Bottom, targetPosition = Position.Top }: { data: any, sourcePosition?: Position, targetPosition?: Position }) => {
  const isActive = data.isActive;
  const isVisited = data.isVisited;

  let Icon = Bot;
  let color = '#64748b'; 
  let bgColor = '#0f172a'; // Darker background for contrast
  let borderColor = '#334155';
  let opacity = 1;
  let textColor = '#e2e8f0'; 
  let iconBg = '#1e293b';

  // Icon Selection
  if (data.type === 'ParallelAgent') Icon = Layers;
  else if (data.type === 'SequentialAgent') Icon = Zap;
  else if (data.type === 'LoopAgent') Icon = Repeat;
  else if (data.label && data.label.includes("FactSet")) Icon = Database;

  const isCoreNode = data.label === 'User' || data.label === 'Smart Agent';
  
  // Highlight Active Path
  if (isActive || isVisited || isCoreNode) {
    color = '#10b981'; // Emerald Green for "Active/Alive"
    borderColor = '#10b981';
    textColor = '#f8fafc';
    iconBg = 'rgba(16, 185, 129, 0.1)';
    bgColor = '#0a0a0a';
  }

  // Thinking Latency (Generic Agent Latency)
  // Check metrics first, then duration fallback
  const thinkingTime = data.metrics?.ttft || data.duration;
  
  return (
    <div style={{
      padding: '12px 16px',
      borderRadius: '16px',
      background: bgColor,
      border: `2px solid ${borderColor}`,
      minWidth: '160px',
      boxShadow: isActive 
        ? '0 0 20px rgba(16, 185, 129, 0.4), inset 0 0 20px rgba(16, 185, 129, 0.1)' 
        : '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      position: 'relative',
      opacity: opacity,
      transform: isActive ? 'scale(1.05)' : 'scale(1)',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      <Handle type="target" position={targetPosition} style={{ opacity: 0 }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '8px',
          background: iconBg,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: color,
          boxShadow: isActive ? '0 0 10px rgba(16, 185, 129, 0.3)' : 'none'
        }}>
          {isActive ? (
             <Icon size={18} strokeWidth={2.5} className="animate-pulse" />
          ) : (
             <Icon size={18} strokeWidth={2} />
          )}
        </div>
        <div className="flex flex-col">
          <div style={{ fontSize: '14px', fontWeight: '700', color: textColor, letterSpacing: '0.02em' }}>
            {data.label}
          </div>
          {data.model && (
            <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '-2px' }}>
              {data.model}
            </div>
          )}
        </div>
      </div>

      {/* Latency Display */}
      {(thinkingTime > 0) && (
        <div style={{
          marginTop: '4px',
          padding: '4px 8px',
          background: 'rgba(16, 185, 129, 0.1)',
          borderRadius: '6px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          fontSize: '11px', fontWeight: '600', color: '#10b981'
        }}>
          <span style={{ opacity: 0.8 }}>Latency</span>
          <span>{Number(thinkingTime).toFixed(2)}s</span>
        </div>
      )}

      <Handle type="source" position={sourcePosition} style={{ opacity: 0 }} />
    </div>
  );
};

const ToolNode = ({ data, sourcePosition = Position.Bottom, targetPosition = Position.Top }: { data: any, sourcePosition?: Position, targetPosition?: Position }) => {
  const isActive = data.isActive;
  const isVisited = data.isVisited;
  const duration = data.duration;
  
  let Icon = Zap;
  let displayLabel = data.label;
  
  let borderColor = '#334155';
  let bgColor = '#0f172a';
  let iconColor = '#64748b';
  let textColor = '#cbd5e1';
  let iconBg = '#1e293b';

  if (isActive || isVisited) {
    borderColor = '#3b82f6'; // Blue-500 for Tools
    iconColor = '#3b82f6';
    textColor = '#f8fafc';
    iconBg = 'rgba(59, 130, 246, 0.1)';
    bgColor = '#0a0a0a';
  }

  // Heuristics for Icons (Label is strictly data.label per user request)
  if (data.label.includes('search') || data.label.includes('google')) {
    Icon = Globe;
  } else if (data.label.includes('FactSet') || data.label.includes('factset') || data.label.includes('prices')) {
    Icon = Database;
  } else if (data.label.includes('plot') || data.label.includes('chart')) {
    Icon = BarChart2;
  } else if (data.label.includes('datetime')) {
    Icon = Clock;
  }

  return (
    <div style={{
      padding: '10px 14px',
      borderRadius: '12px',
      background: bgColor,
      border: `2px solid ${borderColor}`,
      minWidth: '130px',
      boxShadow: isActive 
        ? '0 0 15px rgba(59, 130, 246, 0.4)' 
        : '0 4px 6px -1px rgba(0,0,0,0.3)',
      display: 'flex', flexDirection: 'column', gap: '8px',
      transition: 'all 0.2s ease-out',
      position: 'relative',
      transform: isActive ? 'scale(1.05)' : 'none'
    }}>
      <Handle type="target" position={targetPosition} style={{ opacity: 0 }} />
      
      <div className="flex items-center gap-3">
        <div style={{
            width: '28px', height: '28px', borderRadius: '6px',
            background: iconBg,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: iconColor,
        }}>
            <Icon size={16} strokeWidth={2.5} />
        </div>

        <div style={{ fontSize: '13px', fontWeight: 700, color: textColor, lineHeight: '1.2' }}>
            {displayLabel}
        </div>
      </div>

      {/* Latency List Display (Granular) */}
      {data.metrics?.latencies && Array.isArray(data.metrics.latencies) && data.metrics.latencies.length > 0 ? (
        <div style={{
          marginTop: '6px',
          display: 'flex', flexDirection: 'column', gap: '3px', width: '100%'
        }}>
          {data.metrics.latencies.map((dur: number, idx: number) => (
            <div key={idx} style={{
              padding: '2px 6px',
              background: 'rgba(59, 130, 246, 0.1)',
              borderRadius: '4px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              fontSize: '10px', fontWeight: '600', color: '#3b82f6'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={10} />
                <span style={{ opacity: 0.7 }}>#{idx + 1}</span>
              </div>
              <span>{dur.toFixed(2)}s</span>
            </div>
          ))}
        </div>
      ) : (
        /* Single Duration Fallback */
        duration !== undefined && duration > 0 && (
          <div style={{
            padding: '2px 6px',
            background: 'rgba(59, 130, 246, 0.1)',
            borderRadius: '4px',
            display: 'flex', alignItems: 'center', gap: '4px',
            fontSize: '10px', fontWeight: '600', color: '#3b82f6',
            alignSelf: 'flex-start'
          }}>
            <Clock size={10} />
            {duration.toFixed(2)}s
          </div>
          )
      )}

      <Handle type="source" position={sourcePosition} style={{ opacity: 0 }} />
    </div>
  );
};

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode
};

// --- Layout Logic ---
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 50,
    ranksep: 80
  });

  nodes.forEach((node) => {
    // Ideally use explicit dimensions or estimate
    const isTool = node.type === 'tool';
    dagreGraph.setNode(node.id, { width: isTool ? 160 : 200, height: isTool ? 70 : 90 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - nodeWithPosition.width / 2,
        y: nodeWithPosition.y - nodeWithPosition.height / 2,
      },
    };
  });

  return { nodes: newNodes, edges };
};

// --- Custom Edges ---
import { BaseEdge, EdgeProps, getBezierPath } from '@xyflow/react';

const CircuitEdge = ({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data
}: EdgeProps) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  // Dynamic Color
  const isFlowing = data?.isFlowing;
  const flowColor = data?.flowColor || '#2563eb';

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={{ ...style, strokeOpacity: 0.15, stroke: '#64748b', strokeWidth: 1.5 }} />

      {isFlowing && (
          <path
            d={edgePath}
            fill="none"
          stroke={(flowColor as string) || "#333"}
            strokeWidth={2}
            className="react-flow__edge-path-animated"
            style={{
              strokeDasharray: '6, 4',
              animation: 'dashdraw 0.8s linear infinite',
              strokeOpacity: 1,
              pointerEvents: 'none',
              filter: `drop-shadow(0 0 3px ${flowColor})`
            }}
          />
      )}
      <style>{`
        @keyframes dashdraw {
          from { stroke-dashoffset: 20; }
          to { stroke-dashoffset: 0; }
        }
      `}</style>
    </>
  );
};

const edgeTypes = {
  circuit: CircuitEdge,
};

const AgentGraph: React.FC<AgentGraphProps> = ({ topology, activeNodeId, executionPath = [], nodeDurations = {}, nodeMetrics = {}, layoutDirection = 'LR' }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [rfInstance, setRfInstance] = React.useState<any>(null);

  useEffect(() => {
    if (!topology || !topology.nodes) return;

    // --- STRICT FILTERING ---
    // User Requirement: "Present ONLY the components that were used"
    // We filter down to:
    // 1. 'User' (Start)
    // 2. 'Smart Agent' (Hub)
    // 3. ANY node in 'executionPath'
    // 4. ANY node that has a duration > 0
    // 5. ANY node that is currently 'activeNodeId'
    
    // Always include User and Smart Agent for structure
    const alwaysShow = new Set(['user', 'smart agent', 'factset_analyst']);
    
    const usedNodeIds = new Set<string>();
    
    // Add path nodes
    executionPath.forEach(id => usedNodeIds.add(id.toLowerCase()));
    
    // Add duration nodes
    Object.keys(nodeDurations).forEach(id => {
        if (nodeDurations[id] > 0) usedNodeIds.add(id.toLowerCase());
    });
    
    // Add active node
    if (activeNodeId) usedNodeIds.add(activeNodeId.toLowerCase());

    const filteredNodes = topology.nodes.filter(n => {
        const nid = n.id.toLowerCase();
        const nlabel = (n.label || '').toLowerCase();
        return alwaysShow.has(nid) || alwaysShow.has(nlabel) || usedNodeIds.has(nid);
    });

    const nodeIdSet = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = topology.edges.filter(e => 
        nodeIdSet.has(e.source) && nodeIdSet.has(e.target)
    );

    // --- MAPPING TO REACT FLOW ---
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      filteredNodes.map((node) => {
        const isActive = node.id === activeNodeId;
        const isVisited = executionPath.some(pid => pid.toLowerCase() === node.id.toLowerCase()) || (nodeDurations[node.id] || 0) > 0;
        
        return {
            id: node.id,
            type: node.type === 'tool' ? 'tool' : 'agent',
            position: { x: 0, y: 0 },
            data: {
              label: node.label,
              type: node.type,
              model: node.model,
              isActive: isActive,
              isVisited: isVisited,
              duration: nodeDurations[node.id],
              metrics: nodeMetrics[node.id]
            },
        };
      }),
      filteredEdges.map((edge) => {
         const isFlowing = executionPath.includes(edge.source) && (executionPath.includes(edge.target) || edge.target === activeNodeId);
          
         return {
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            type: 'circuit',
            animated: true,
            data: {
              isFlowing: true, // Always animate edges in the filtered graph for "aliveness"
              flowColor: isFlowing ? '#10b981' : '#3b82f6'
            }
          };
      }),
      layoutDirection
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [topology, activeNodeId, executionPath, nodeDurations, nodeMetrics, layoutDirection]);

  // Robust FitView on Updates
  useEffect(() => {
    if (rfInstance && nodes.length > 0) {
      const timer = setTimeout(() => {
        window.requestAnimationFrame(() => {
           rfInstance.fitView({ padding: 0.2, duration: 600 });
        });
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [rfInstance, nodes.length, edges.length, layoutDirection]);

  return (
    <div style={{ width: '100%', height: '100%', background: 'transparent' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onInit={setRfInstance}
        fitView
        attributionPosition="bottom-right"
        minZoom={0.1}
        maxZoom={2.0}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(255,255,255,0.02)" gap={24} size={1} />
      </ReactFlow>
    </div>
  );
};

export default AgentGraph;
