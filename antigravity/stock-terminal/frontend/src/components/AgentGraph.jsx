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
      padding: '10px 16px',
      borderRadius: '8px',
      background: bgColor,
      border: `2px solid ${borderColor}`,
      minWidth: '180px',
      boxShadow: isActive ? `0 0 12px ${color}40` : '0 2px 4px rgba(0,0,0,0.05)',
      transition: 'all 0.3s ease'
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: data.tools?.length > 0 ? '8px' : '0' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '6px',
          background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: color
        }}>
          <Icon size={18} />
        </div>
        <div>
// AgentNode label
          <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#333', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={data.label}>{data.label}</div>
          <div style={{ fontSize: '10px', color: '#666' }}>{data.type}</div>
        </div>
      </div>

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

      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
};

const ToolNode = ({ data }) => {
  const isActive = data.isActive;

  return (
    <div style={{
      padding: '6px 12px',
      borderRadius: '20px',
      background: isActive ? '#e6fffa' : '#fff',
      border: isActive ? '2px solid #20c997' : '1px solid #777', // Green border when active
      minWidth: '120px',
      boxShadow: isActive ? '0 0 8px rgba(32, 201, 151, 0.4)' : '0 1px 2px rgba(0,0,0,0.1)',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      transition: 'all 0.3s ease',
      maxWidth: '200px' // Ensure it doesn't grow indefinitely
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{
        width: '20px', height: '20px', borderRadius: '50%',
        background: isActive ? '#20c997' : '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: isActive ? '#fff' : '#666',
        flexShrink: 0 // Prevent icon from shrinking
      }}>
        <Zap size={10} />
      </div>
      <span style={{ fontSize: '11px', fontWeight: 600, color: '#333', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={data.label}>{data.label}</span>
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
    const baseWidth = node.type === 'tool' ? 140 : 220;
    // Allow wider nodes if label is long, but cap it
    const width = Math.min(Math.max(baseWidth, labelLength * 8), 300);
    const height = node.type === 'tool' ? 50 : 100;
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
      style: { width: nodeWithPosition.width, maxWidth: 300 } // Pass width to style
    };
  });


  return { nodes: newNodes, edges };
};

const AgentGraph = ({ topology, activeNodeId }) => {
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

  // Update Active State
  useEffect(() => {
    // Logic: Highlight if ID matches OR if label matches (for robustness)
    // Also highlight incoming edge if active.

    const activeId = activeNodeId;

    setNodes((nds) =>
      nds.map((node) => {
        const isMatch = (node.id === activeId || node.id.endsWith(`_${activeId}`) || node.data.label === activeId);
        return {
          ...node,
          data: {
            ...node.data,
            isActive: isMatch
          }
        };
      })
    );

    setEdges((eds) =>
      eds.map((edge) => {
        // Highlight edge if TARGET is active
        const targetNode = nodes.find(n => n.id === edge.target);
        // This logic is tricky because 'nodes' inside setEdges might be stale if we don't depend on it.
        // Better to perform matching logic here based on activeId.
        const isTargetActive = (edge.target === activeId || edge.target.endsWith(`_${activeId}`));

        return {
          ...edge,
          animated: isTargetActive, // Animate flow
          style: {
            ...edge.style,
            stroke: isTargetActive ? '#20c997' : '#b1b1b7',
            strokeWidth: isTargetActive ? 2 : 1
          }
        };
      })
    );
  }, [activeNodeId, topology]); // Re-run when activeNodeId changes

  return (
    <div style={{ width: '100%', height: '100%', background: '#f8f9fa' }}>
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
