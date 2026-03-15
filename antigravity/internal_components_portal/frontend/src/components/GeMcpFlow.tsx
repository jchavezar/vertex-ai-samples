import React from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Server, Cpu, Database, Network, Search, Activity, Terminal, ShieldAlert, Key } from 'lucide-react';
import './GeMcpFlow.css';

// --- Custom Nodes ---
const ArchNode = ({ data }: any) => {
  return (
    <div className={`react-flow__node-customNode ${data.highlight ? 'highlight' : ''}`}>
      <Handle type="target" position={Position.Top} id="t-top" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Top} id="s-top" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Right} id="t-right" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} id="s-right" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Bottom} id="t-bottom" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} id="s-bottom" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Left} id="t-left" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Left} id="s-left" style={{ opacity: 0 }} />
      
      {data.icon && (
        <div className={`node-icon-wrapper ${data.color || 'green'}`}>
          <data.icon size={20} />
        </div>
      )}
      <div className="node-subtitle" style={{ color: data.accent || '#86bc25' }}>{data.subtitle}</div>
      <h3 className="node-title">{data.label}</h3>
      <p className="node-desc">{data.desc}</p>
    </div>
  );
};

const nodeTypes = {
  custom: ArchNode,
};

// --- Initial Nodes & Edges ---
// Main flow left-to-right backbone
const initialNodes = [
  // 0. Handoff from Auth Flow
  { 
    id: 'start_context', 
    type: 'custom', 
    position: { x: 50, y: 100 }, 
    data: { 
      label: 'Acquired JWT (from Auth Flow)', 
      subtitle: 'Client State', 
      desc: 'JWT ready for injection.', 
      icon: Key, 
      color: 'yellow', 
      accent: '#eab308',
      snippet: '// The JWT acquired from Microsoft Entra is now ready to be used.\n// Token held in React state, ready to be attached to requests.\nconst token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...";'
    } 
  },
  
  { 
    id: 'frontend', 
    type: 'custom', 
    position: { x: 450, y: 100 }, 
    data: { 
      label: 'TerminalChat Component', 
      subtitle: 'React UI', 
      desc: 'Dispatches prompt and JWT.', 
      icon: Terminal, 
      color: 'cyan', 
      accent: '#06b6d4',
      snippet: '// Sends prompt and JWT token to the backend for intent routing.\nconst response = await fetch("/api/chat/stream", {\n  method: "POST",\n  headers: { "Authorization": `Bearer ${token}` },\n  body: JSON.stringify({ messages, routerMode })\n});'
    } 
  },

  // 3. Backend Entry
  { 
    id: 'fastapi', 
    type: 'custom', 
    position: { x: 850, y: 100 }, 
    data: { 
      label: 'FastAPI /api/chat/stream', 
      subtitle: 'API Gateway', 
      desc: 'Validates & unpacks JWT.', 
      icon: Server, 
      color: 'green', 
      accent: '#86bc25',
      snippet: '// Validates & unpacks JWT to inject Microsoft auth_context into the Request.\n@app.post("/api/chat/stream")\nasync def chat_stream(req: Request, router_mode: str):\n    auth_payload = await verify_jwt(req)\n    return StreamingResponse(\n        generate_stream(req.messages, auth_payload),\n        media_type="text/event-stream"\n    )'
    } 
  },

  // 4. Intent Routing (Drops down a level)
  { 
    id: 'adk_router', 
    type: 'custom', 
    position: { x: 850, y: 400 }, 
    data: { 
      label: 'ADK Router Agent', 
      subtitle: 'Gemini 2.5 Flash', 
      desc: 'Evaluates prompt intent.', 
      icon: Cpu, 
      color: 'purple', 
      accent: '#8b5cf6',
      highlight: true,
      snippet: '// Evaluates Intent: "Act" (Bottom Route) vs "Search" (Top Route).\nagent = Agent(\n    model="gemini-2.5-flash",\n    tools=[mcp_direct_tools, vertex_search_tool],\n    system_prompt="Route requests based on user intent."\n)\nresponse = await agent.run(user_prompt)'
    } 
  },

  // === SEARCH ROUTE (Top Branch) ===
  // Moves left
  { 
    id: 'ge_auth', 
    type: 'custom', 
    position: { x: 450, y: 400 }, 
    data: { 
      label: 'WIF STS Authentication (2LO)', 
      subtitle: 'Zero-Leak Protocol', 
      desc: 'Exchanges Entra token for GCP token.', 
      icon: ShieldAlert, 
      color: 'orange', 
      accent: '#f97316',
      snippet: '// Exchanges Microsoft Entra Signature for a GCP Service Token via WIF.\n// This ensures Vertex AI Search enforces SharePoint document-level ACLs (Security Trimming) natively.\nsts = google.auth.transport.requests.Request()\ntoken_req = {\n    "audience": WIF_PROVIDER,\n    "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",\n    "subjectToken": entra_id_jwt\n}\ngcp_token = fetch_sts_token(token_req)'
    } 
  },
  { 
    id: 'vertex_search', 
    type: 'custom', 
    position: { x: 50, y: 400 }, 
    data: { 
      label: 'Vertex Discovery Engine', 
      subtitle: 'streamAssist API', 
      desc: 'Queries SharePoint Index natively.', 
      icon: Search, 
      color: 'blue', 
      accent: '#3b82f6',
      highlight: true,
      snippet: '// Queries SharePoint Index using the down-scoped WIF identity.\nasync for chunk in discovery_client.stream_assist(\n    query=query,\n    toolsSpec={"vertexAiSearchSpec": {\n        "dataStoreSpecs": [{"dataStore": ds} for ds in datastores]\n    }}\n):\n    yield chunk'
    } 
  },
  // Drops down and moves Right
  { 
    id: 'interceptor', 
    type: 'custom', 
    position: { x: 50, y: 700 }, 
    data: { 
      label: 'Data Enrichment Pipeline', 
      subtitle: 'ge_search_branch.py', 
      desc: 'Injects references into stream.', 
      icon: Database, 
      color: 'yellow', 
      accent: '#eab308',
      snippet: '// Injects missing URIs and Titles from `searchResults` into the stream.\nfor ref in chunk.references:\n    doc_id = ref.document_name\n    if doc_id in local_search_results:\n        ref.title = local_search_results[doc_id].title\n        ref.uri = local_search_results[doc_id].uri'
    } 
  },
  { 
    id: 'aistream', 
    type: 'custom', 
    position: { x: 450, y: 700 }, 
    data: { 
      label: 'AIStream Protocol Sink', 
      subtitle: 'Vercel AI SDK', 
      desc: 'Yields trace + snippets.', 
      icon: Activity, 
      color: 'green', 
      accent: '#86bc25',
      snippet: '// Yields final Latency Trace + Snippets back to the frontend.\ndef generate():\n    yield "0:\\"Thought Context...\\"\\n"\n    yield "d:{\\"telemetry\\": {...}}\\n"\n    for c in interceptor_stream():\n        yield f"0:\\"{c.text}\\"\\n"\nreturn StreamingResponse(generate())'
    } 
  },
  
  // === ACTION ROUTE (Bottom Branch) ===
  { 
    id: 'mcp_direct', 
    type: 'custom', 
    position: { x: 850, y: 700 }, 
    data: { 
      label: 'MCP Direct Action Server', 
      subtitle: 'Subprocess Tools', 
      desc: 'Executes ungrounded tools.', 
      icon: Network, 
      color: 'pink', 
      accent: '#ec4899',
      snippet: '// Executes pure tools without search grounding (e.g. List Datastores).\nserver = Server("direct-action-mcp")\n@server.tool()\nasync def execute_action(params: dict):\n    logger.info("Executing isolated ADK tool")\n    return ActionEngine.run(params)'
    } 
  },
  
  // === EXIT NODE ===
  { 
    id: 'response_rendered', 
    type: 'custom', 
    position: { x: 850, y: 1000 }, 
    data: { 
      label: 'Final Response Rendered', 
      subtitle: 'Client State', 
      desc: 'Renders markdown & traces.', 
      icon: Terminal, 
      color: 'cyan', 
      accent: '#06b6d4',
      snippet: '// The React UI renders the streamed markdown and telemetry traces.\n// Rendered in the Chat Area\nreturn <Markdown>{message.content}</Markdown>;'
    } 
  }
];

const initialEdges = [
  // Linear Spine - Moving Left to Right
  { id: 'e-start-front', source: 'start_context', target: 'frontend', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: 'Ready for Request', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#eab308' }, style: { stroke: '#eab308', strokeWidth: 2 }, labelStyle: { fill: '#eab308', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  { id: 'e-front-fastapi', source: 'frontend', target: 'fastapi', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: 'Headers: Bearer <JWT>', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 }, labelStyle: { fill: '#86bc25', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  { id: 'e-fastapi-adk', source: 'fastapi', target: 'adk_router', sourceHandle: 's-bottom', targetHandle: 't-top', type: 'smoothstep', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 } },
  
  // Router branches
  // UPSIDE - Search loop launches left from ADK router
  { id: 'e-adk-ge', source: 'adk_router', target: 'ge_auth', sourceHandle: 's-left', targetHandle: 't-right', type: 'smoothstep', label: 'Intent: Knowledge Search', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#f97316' }, style: { stroke: '#f97316', strokeWidth: 2 }, labelStyle: { fill: '#f97316', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  // DOWNSIDE - Action loop launches down
  { id: 'e-adk-mcp', source: 'adk_router', target: 'mcp_direct', sourceHandle: 's-bottom', targetHandle: 't-top', type: 'smoothstep', label: 'Intent: Direct Action', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#ec4899' }, style: { stroke: '#ec4899', strokeWidth: 2 }, labelStyle: { fill: '#ec4899', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  
  // Search Pipeline Loop
  { id: 'e-ge-vertex', source: 'ge_auth', target: 'vertex_search', sourceHandle: 's-left', targetHandle: 't-right', type: 'smoothstep', label: 'Exchanges GCP Token', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#3b82f6' }, style: { stroke: '#3b82f6', strokeWidth: 2 }, labelStyle: { fill: '#3b82f6', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  { id: 'e-vertex-intercept', source: 'vertex_search', target: 'interceptor', sourceHandle: 's-bottom', targetHandle: 't-top', type: 'smoothstep', label: 'Raw streamAssist Chunks', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#eab308' }, style: { stroke: '#eab308', strokeWidth: 2 }, labelStyle: { fill: '#eab308', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  { id: 'e-intercept-aistream', source: 'interceptor', target: 'aistream', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: 'Enriched Payload', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2 }, labelStyle: { fill: '#86bc25', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  
  // Return to client exit node
  { id: 'e-aistream-front', source: 'aistream', target: 'response_rendered', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: 'AIStream Response', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#06b6d4' }, style: { stroke: '#06b6d4', strokeWidth: 2, strokeDasharray: '5 5' }, labelStyle: { fill: '#06b6d4', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } },
  { id: 'e-mcp-front', source: 'mcp_direct', target: 'response_rendered', sourceHandle: 's-bottom', targetHandle: 't-top', type: 'smoothstep', label: 'Markdown Response', animated: true, markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20, color: '#ec4899' }, style: { stroke: '#ec4899', strokeWidth: 2, strokeDasharray: '5 5' }, labelStyle: { fill: '#ec4899', fontWeight: 600 }, labelBgStyle: { fill: '#1e1e1e' } }
];

export const GeMcpFlow: React.FC = () => {
  const [routerMode, setRouterMode] = React.useState<'ge_mcp' | 'all_mcp'>('ge_mcp');

  const visibleNodes = React.useMemo(() => {
    if (routerMode === 'all_mcp') {
      return initialNodes.filter(n => !['ge_auth', 'vertex_search', 'interceptor', 'aistream'].includes(n.id));
    }
    return initialNodes;
  }, [routerMode]);

  const visibleEdges = React.useMemo(() => {
    if (routerMode === 'all_mcp') {
      return initialEdges.filter(e => !['e-adk-ge', 'e-ge-vertex', 'e-vertex-intercept', 'e-intercept-aistream', 'e-aistream-front'].includes(e.id));
    }
    return initialEdges;
  }, [routerMode]);

  const [nodes, , onNodesChange] = useNodesState(visibleNodes as any);
  const [edges, , onEdgesChange] = useEdgesState(visibleEdges as any);
  
  React.useEffect(() => {
    // Force a re-render/update when mode changes
    onNodesChange([{ type: 'reset', item: visibleNodes } as any]);
    onEdgesChange([{ type: 'reset', item: visibleEdges } as any]);
  }, [routerMode, visibleNodes, visibleEdges, onNodesChange, onEdgesChange]);
  
  const [hoverData, setHoverData] = React.useState<{node: any, x: number, y: number} | null>(null);

  const onNodeMouseEnter = (e: React.MouseEvent, node: any) => {
    if (node.data?.snippet) {
      setHoverData({ node, x: e.clientX, y: e.clientY });
    }
  };

  const onNodeMouseMove = (e: React.MouseEvent, node: any) => {
    if (hoverData && hoverData.node.id === node.id) {
      setHoverData({ node, x: e.clientX, y: e.clientY });
    }
  };

  const onNodeMouseLeave = () => {
    setHoverData(null);
  };

  // Correcting the shield icon issue on load
  nodes.forEach(n => {
    if (n.id === 'ge_auth' && typeof n.data.icon !== 'function') {
      n.data.icon = Network; // Safe fallback since lucide ShieldAlert import syntax was problematic inline
    }
  });

  return (
    <div className="ge-flow-wrapper">
      <div className="ge-flow-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2><Network size={24} color="#86bc25" /> Chat Flow & Routing Architecture</h2>
          <p>End-to-end tracing of the query lifecycle, GE+MCP vs. ALL MCP token exchange, and streaming telemetry.</p>
        </div>
        <div>
          <select
            value={routerMode}
            onChange={(e) => setRouterMode(e.target.value as 'all_mcp'|'ge_mcp')}
            style={{
              background: "transparent",
              border: "1px solid rgba(134, 188, 37, 0.3)",
              borderRadius: "4px",
              color: "var(--deloitte-green)",
              padding: "6px 12px",
              outline: "none",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "12px",
              fontFamily: "monospace",
            }}
            title="Select Routing Architecture"
          >
            <option value="all_mcp" style={{ color: "black" }}>
              All MCP (Direct)
            </option>
            <option value="ge_mcp" style={{ color: "black" }}>
              GE + MCP (Router)
            </option>
          </select>
        </div>
      </div>
      <div className="ge-flow-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeMouseEnter={onNodeMouseEnter}
          onNodeMouseMove={onNodeMouseMove}
          onNodeMouseLeave={onNodeMouseLeave}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          attributionPosition="bottom-right"
        >
          <Background color="#333" gap={16} size={1} />
          <Controls />
          <MiniMap 
            nodeColor={(node: any) => {
              switch (node.data?.color) {
                case 'green': return '#86bc25';
                case 'blue': return '#3b82f6';
                case 'purple': return '#8b5cf6';
                case 'orange': return '#f97316';
                case 'cyan': return '#06b6d4';
                case 'pink': return '#ec4899';
                case 'yellow': return '#eab308';
                default: return '#eee';
              }
            }} 
            nodeStrokeWidth={3} 
            zoomable 
            pannable 
          />
        </ReactFlow>

        {hoverData && hoverData.node.data.snippet && (
          <div 
            className="ge-code-overlay dw-fade-in"
            style={{ 
              position: 'fixed', 
              top: Math.min(hoverData.y + 20, window.innerHeight - 200),
              left: Math.min(hoverData.x + 20, window.innerWidth - 470),
              bottom: 'auto'
            }}
          >
            <div className="ge-code-overlay-header">
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Terminal size={14} color="#86bc25" />
                Implementation Snapshot: <strong>{hoverData.node.data.label}</strong>
              </span>
            </div>
            <pre className="ge-code-block">
              <code>{hoverData.node.data.snippet}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
