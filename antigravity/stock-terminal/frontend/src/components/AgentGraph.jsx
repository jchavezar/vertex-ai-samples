import React, { useCallback, useEffect, useMemo } from 'react';
import { ReactFlow, Background, Controls, useNodesState, useEdgesState, Position, Handle } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { Terminal, Bot, Layers, Repeat, Globe, Zap, Database } from 'lucide-react';

// --- Custom Nodes ---

const AgentNode = ({ data }) => {
  const isActive = data.isActive; // Dynamic highlighting

  let Icon = Bot;
  let color = '#004b87';
  let bgColor = '#fff';
  let borderColor = '#e0e0e0';

  if (data.type === 'ParallelAgent') {
    Icon = Layers;
    color = '#6f42c1';
  } else if (data.type === 'SequentialAgent') {
    Icon = Zap;
    color = '#fd7e14';
  } else if (data.type === 'LoopAgent') {
    Icon = Repeat;
    color = '#20c997';
  } else if (data.label.includes("FactSet")) {
    Icon = Database;
    color = '#28a745';
  }

  if (isActive) {
    borderColor = color;
    bgColor = '#f0f9ff'; // Light glow
  }

  return (
    <div style={{
      padding: '12px 20px',
      borderRadius: '24px',
      background: 'var(--bg-card)',
      backdropFilter: 'var(--card-blur)',
      border: `2px solid ${isActive ? borderColor : 'var(--border)'}`,
      minWidth: '200px',
      boxShadow: isActive ? `0 0 20px ${color}60` : 'var(--glass-shadow)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: color, opacity: 0.6
      }} />
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: data.tools?.length > 0 ? '8px' : '0' }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '50%',
          background: `${color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: color,
          boxShadow: `0 0 10px ${color}40`
        }}>
          <Icon size={20} />
        </div>
        <div>
          <div style={{ fontSize: '13px', fontWeight: '800', color: 'var(--text-primary)', wordBreak: 'break-word' }} title={data.label}>{data.label}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontWeight: 600 }}>{data.type}</div>
            {data.model && (
              <div style={{
                fontSize: '8px',
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '1px 6px',
                borderRadius: '999px',
                color: 'var(--text-secondary)',
                fontWeight: 800,
                border: '1px solid var(--border)',
                textTransform: 'uppercase'
              }}>
                {data.model}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Latency / Duration Display */}
      {data.duration !== undefined && (
        <div style={{ position: 'absolute', top: '-10px', right: '-10px', background: '#7c3aed', color: 'white', fontSize: '9px', padding: '2px 6px', borderRadius: '10px', fontWeight: 'bold', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', zIndex: 10 }}>
          {data.duration < 0.01 ? '< 0.01s' : `${data.duration.toFixed(2)}s`}
        </div>
      )}

      {/* Tools Badge */}
      {data.tools && data.tools.length > 0 && (
        <div style={{ borderTop: '1px solid #eee', paddingTop: '6px', marginTop: '6px' }}>
          <div style={{ fontSize: '9px', color: '#999', marginBottom: '2px', textTransform: 'uppercase' }}>Tools</div>
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {data.tools.map((t, i) => (
              <span key={i} style={{ fontSize: '10px', background: '#f1f3f5', padding: '2px 6px', borderRadius: '4px', color: '#555', border: '1px solid #e9ecef' }}>
                {t}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Thinking state for agents */}
      {isActive && data.type !== 'tool' && (
        <div style={{ fontSize: '10px', color: color, fontStyle: 'italic', marginTop: '8px', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
          <div className="icon-pulse"><Bot size={12} /></div>
          <span>Reasoning...</span>
        </div>
      )}

      {/* Status Indicators */}
      {!isActive && data.isVisited && (
        <div style={{ position: 'absolute', bottom: '8px', right: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div style={{ fontSize: '8px', color: 'var(--green)', fontWeight: 800, textTransform: 'uppercase', opacity: 0.8 }}>Complete</div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--green)' }} />
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
};

const ToolNode = ({ data }) => {
  const isActive = data.isActive;
  const duration = data.duration;

  // Color code latency
  let latencyColor = 'var(--brand-light)';
  let latencyTextColor = 'var(--brand)';
  let latencyBorder = 'var(--brand)';

  if (duration > 5.0) {
    latencyColor = '#fef2f2'; // Red-ish
    latencyTextColor = '#dc3545';
    latencyBorder = '#dc3545';
  } else if (duration > 2.0) {
    latencyColor = '#fff3cd'; // Yellow-ish
    latencyTextColor = '#ffc107';
    latencyBorder = '#ffc107';
  } else if (duration < 0.5) {
    latencyColor = '#d1e7dd'; // Green-ish
    latencyTextColor = '#198754';
    latencyBorder = '#198754';
  }

  return (
    <div style={{
      padding: '10px 16px',
      borderRadius: '12px',
      background: 'var(--bg-card)',
      backdropFilter: 'var(--card-blur)',
      border: isActive ? '2px solid var(--green)' : '1px solid var(--border)',
      minWidth: '160px',
      boxShadow: isActive ? '0 0 15px var(--green-bg)' : 'var(--glass-shadow)',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      maxWidth: '350px',
      position: 'relative'
    }}
      title={isActive ? "Executing now..." : (data.isVisited ? `Execution complete (${duration?.toFixed(2)}s)` : "")}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{
        width: '32px', height: '32px', borderRadius: '50%',
        background: isActive ? 'var(--green)' : (data.isVisited ? 'var(--green-bg)' : 'var(--border-light)'),
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: isActive ? '#fff' : (data.isVisited ? 'var(--green)' : 'var(--text-muted)'),
        flexShrink: 0,
        boxShadow: isActive ? '0 0 10px var(--green-light)' : 'none'
      }}>
        {isActive ? <Zap size={16} className="icon-pulse" /> : (data.isVisited ? <Database size={16} /> : <Zap size={16} />)}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', flex: 1 }}>
        <span style={{
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis'
        }} title={data.label}>
          {data.label}
        </span>
        {/* Optional: Add description if available and space permits, or just keep it clean */}
      </div>

      {/* Latency Display for Tools (Prominent Badge) */}
      {duration !== undefined && (
        <div style={{ 
          position: 'absolute',
          bottom: '-10px',
          right: '-4px',
          fontSize: '10px',
          background: latencyColor,
          padding: '2px 8px',
          borderRadius: '12px',
          color: latencyTextColor,
          fontWeight: 800,
          border: `1px solid ${latencyBorder}`,
          boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
          zIndex: 10
        }}>
          {duration < 0.01 ? '< 0.01s' : `${duration.toFixed(2)}s`}
        </div>
      )}
    </div>
  );
};

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode
};

// --- Layout Logic ---
const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 150, // Wider spacing for natural loop
    ranksep: 100
  });

  nodes.forEach((node) => {
    // Dynamic dimensions for layout to prevent overlap
    const labelLength = node.data.label ? node.data.label.length : 10;

    // INCREASED WIDTHS for better readability
    const baseWidth = node.type === 'tool' ? 180 : 240; 
    // Allow wider nodes if label is long, but cap it
    const width = Math.min(Math.max(baseWidth, labelLength * 9), 350);
    const height = node.type === 'tool' ? 60 : 100;
    dagreGraph.setNode(node.id, { width, height });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? 'left' : 'top',
      sourcePosition: isHorizontal ? 'right' : 'bottom',
      position: {
        x: nodeWithPosition.x - nodeWithPosition.width / 2,
        y: nodeWithPosition.y - nodeWithPosition.height / 2,
      },
      style: { width: nodeWithPosition.width, maxWidth: 350 } // Pass width to style
    };
  });


  return { nodes: newNodes, edges };
};

const AgentGraph = ({ topology, activeNodeId, executionPath = [], nodeDurations = {} }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Apply Layout on topology change
  useEffect(() => {
    if (!topology || !topology.nodes) return;

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      topology.nodes,
      topology.edges
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [topology, setNodes, setEdges]);

  useEffect(() => {
    if (!nodes.length) return;

    // Build a map for edge lookup
    const sourceMap = {};
    edges.forEach(e => {
      if (!sourceMap[e.target]) sourceMap[e.target] = [];
      sourceMap[e.target].push(e.source);
    });

    const getAncestors = (nodeId, visited = new Set()) => {
      if (!nodeId || visited.has(nodeId)) return visited;
      visited.add(nodeId);
      const parents = sourceMap[nodeId] || [];
      parents.forEach(p => getAncestors(p, visited));
      return visited;
    };

    // Determine all nodes that should be highlighted
    const highlightedNodes = new Set();
    const activeAncestors = getAncestors(activeNodeId);
    activeAncestors.forEach(id => highlightedNodes.add(id));

    executionPath.forEach(pathId => {
      // Find actual node ID in the graph that matches pathId
      const targetNode = nodes.find(n => n.id === pathId || n.id.endsWith(`_${pathId}`) || n.data.label === pathId);
      if (targetNode) {
        const ancestors = getAncestors(targetNode.id);
        ancestors.forEach(id => highlightedNodes.add(id));
      }
    });

    setNodes((nds) =>
      nds.map((node) => {
        const isCurrent = (node.id === activeNodeId || node.id.endsWith(`_${activeNodeId}`) || node.data.label === activeNodeId);
        const isVisited = executionPath.some(pathId => node.id === pathId || node.id.endsWith(`_${pathId}`) || node.data.label === pathId);
        const isPartOfPath = highlightedNodes.has(node.id);

        return {
          ...node,
          data: {
            ...node.data,
            isActive: isCurrent,
            isVisited: isVisited || isPartOfPath,
            duration: nodeDurations[node.id] || nodeDurations[node.data.label] || node.data.duration
          }
        };
      })
    );

    setEdges((eds) =>
      eds.map((edge) => {
        // Highlight edge if TARGET is active or visited as an ancestor
        const isTargetHighlighted = highlightedNodes.has(edge.target);
        const isTargetCurrent = (edge.target === activeNodeId || edge.target.endsWith(`_${activeNodeId}`));

        return {
          ...edge,
          animated: isTargetHighlighted,
          style: {
            ...edge.style,
            stroke: isTargetCurrent ? '#20c997' : (isTargetHighlighted ? '#198754' : '#b1b1b7'),
            strokeWidth: isTargetHighlighted ? 2 : 1,
            opacity: isTargetHighlighted ? 1 : 0.5
          }
        };
      })
    );
  }, [activeNodeId, executionPath, nodeDurations, edges.length]); 

  return (
    <div id="printable-agent-graph" style={{ width: '100%', height: '100%', background: 'transparent' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
      >
        <Background gap={16} size={1} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default AgentGraph;
