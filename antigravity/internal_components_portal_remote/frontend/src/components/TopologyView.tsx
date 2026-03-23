import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import { useEffect } from 'react';
import '@xyflow/react/dist/style.css';

interface TopologyViewProps {
  routerMode: 'all_mcp' | 'ge_mcp';
}

const ALL_MCP_NODES: Node[] = [
  {
    id: 'user',
    position: { x: 350, y: 50 },
    data: { label: 'User Request (React UI)' },
    style: { background: '#1e1e1e', color: '#fff', border: '1px solid #86bc25', borderRadius: '8px', padding: '10px', width: 220 }
  },
  {
    id: 'mcp_proxy',
    position: { x: 350, y: 150 },
    data: { label: 'Zero-Leak Security Proxy\nModel: gemini-3-flash-preview\nParallelism: Direct\nProtocol: Vercel AI SDK + MCP' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #5eaefd', borderRadius: '8px', padding: '16px', width: 280 }
  },
  {
    id: 'sharepoint',
    position: { x: 100, y: 350 },
    data: { label: 'SharePoint Sentinel MCP\nEndpoint: http://localhost:8003\nConnector: MS Graph API\nAuth: Entra ID / FactSet' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #f36c5b', borderRadius: '8px', padding: '16px', width: 240 }
  },
  {
    id: 'web_search',
    position: { x: 370, y: 350 },
    data: { label: 'Public Web Consensus MCP\nEndpoint: stdio (npx)\nConnector: Brave Search API\nConfig: Max Results 10' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #f36c5b', borderRadius: '8px', padding: '16px', width: 240 }
  },
  {
    id: 'other_mcp',
    position: { x: 640, y: 350 },
    data: { label: 'Other Active MCPs\n(GitHub, Jira, etc)' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #f36c5b', borderRadius: '8px', padding: '16px', width: 200 }
  }
];

const ALL_MCP_EDGES: Edge[] = [
  { id: 'e_usr_proxy', source: 'user', target: 'mcp_proxy', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  { id: 'e_proxy_sp', source: 'mcp_proxy', target: 'sharepoint', animated: true, label: 'MCP Call: query_sharepoint', labelStyle: { fill: '#fff', fontSize: 10 }, labelBgStyle: { fill: '#1e1e1e' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f36c5b' }, style: { stroke: '#f36c5b', strokeWidth: 2, strokeDasharray: '5 5' } },
  { id: 'e_proxy_web', source: 'mcp_proxy', target: 'web_search', animated: true, label: 'MCP Call: brave_web_search', labelStyle: { fill: '#fff', fontSize: 10 }, labelBgStyle: { fill: '#1e1e1e' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f36c5b' }, style: { stroke: '#f36c5b', strokeWidth: 2, strokeDasharray: '5 5' } },
  { id: 'e_proxy_other', source: 'mcp_proxy', target: 'other_mcp', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#f36c5b' }, style: { stroke: '#f36c5b', strokeWidth: 2, strokeDasharray: '5 5' } },
];

const GE_MCP_NODES: Node[] = [
  {
    id: 'user',
    position: { x: 350, y: 50 },
    data: { label: 'User Request (React UI)' },
    style: { background: '#1e1e1e', color: '#fff', border: '1px solid #86bc25', borderRadius: '8px', padding: '10px', width: 220 }
  },
  {
    id: 'router',
    position: { x: 350, y: 150 },
    data: { label: 'Router Agent (ADK Orchestrator)\nModel: gemini-3-flash-preview\nFramework: Google ADK\nTask: Intent Classification' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #b47dff', borderRadius: '8px', padding: '16px', width: 280 }
  },
  {
    id: 'ge_agent',
    position: { x: 150, y: 320 },
    data: { label: 'Discovery Engine Agent\nType: Vertex AI Search\nProtocol: google.cloud.discoveryengine_v1\nTools: Search Data Store' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #5eaefd', borderRadius: '8px', padding: '16px', width: 260 }
  },
  {
    id: 'mcp_agent',
    position: { x: 500, y: 320 },
    data: { label: 'MCP Swarm Agent\nType: Zero-Leak Proxy\nProtocol: Vercel AI SDK + ADK Tools\nRole: Tool Executor' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #5eaefd', borderRadius: '8px', padding: '16px', width: 260 }
  },
  {
    id: 'sharepoint_source',
    position: { x: 150, y: 480 },
    data: { label: 'Vertex AI Data Store\n(Indexed SharePoint Data)' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #f36c5b', borderRadius: '8px', padding: '16px', width: 260 }
  },
  {
    id: 'mcp_tools',
    position: { x: 500, y: 480 },
    data: { label: 'MCP Tool Repertoire\n- Public Web Consensus\n- Project Analytics\n- Math / Execution' },
    style: { background: '#1a1a1a', color: '#fff', border: '1px solid #f36c5b', borderRadius: '8px', padding: '16px', width: 260 }
  }
];

const GE_MCP_EDGES: Edge[] = [
  { id: 'e_usr_router', source: 'user', target: 'router', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  { id: 'e_router_ge', source: 'router', target: 'ge_agent', animated: true, label: 'Internal Search', labelStyle: { fill: '#fff' }, labelBgStyle: { fill: '#1e1e1e' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  { id: 'e_router_mcp', source: 'router', target: 'mcp_agent', animated: true, label: 'External/Tools', labelStyle: { fill: '#fff' }, labelBgStyle: { fill: '#1e1e1e' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  { id: 'e_ge_data', source: 'ge_agent', target: 'sharepoint_source', animated: false, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  { id: 'e_mcp_tools', source: 'mcp_agent', target: 'mcp_tools', animated: false, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } }
];

export function TopologyView({ routerMode }: TopologyViewProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    if (routerMode === 'all_mcp') {
      setNodes(ALL_MCP_NODES);
      setEdges(ALL_MCP_EDGES);
    } else {
      setNodes(GE_MCP_NODES);
      setEdges(GE_MCP_EDGES);
    }
  }, [routerMode, setNodes, setEdges]);

  return (
    <div style={{ width: '100%', height: '100%', background: '#121212', borderRadius: '12px', border: '1px solid rgba(134, 188, 37, 0.2)', overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls style={{ background: '#1e1e1e', fill: '#fff' }} />
        {/* @ts-expect-error The variant type is mismatched but 'dots' is a valid string literal for this component */}
        <Background variant="dots" gap={16} size={1} color="#333" />
      </ReactFlow>
    </div>
  );
}
