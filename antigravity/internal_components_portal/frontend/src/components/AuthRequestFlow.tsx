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
import { User, Server, Cpu, Key, Lock, FileSearch, Send, MessageSquareText, ArrowRightCircle } from 'lucide-react';
import './GeMcpFlow.css';

interface AuthRequestFlowProps {
  onNavigateToChat?: () => void;
}

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
const initialNodes = [
  // Authentication Phase
  { 
    id: 'user', 
    type: 'custom', 
    position: { x: 50, y: 150 }, 
    data: { 
      label: 'End User', 
      subtitle: 'Client Layer', 
      desc: 'Clicks "Sign In" on the portal.', 
      icon: User, 
      color: 'blue', 
      accent: '#3b82f6',
      snippet: 'instance.loginRedirect(loginRequest);'
    } 
  },
  { 
    id: 'entra_login', 
    type: 'custom', 
    position: { x: 550, y: 150 }, 
    data: { 
      label: 'Microsoft Entra ID', 
      subtitle: 'SSO Identity Provider', 
      desc: 'Authenticates user and issues OAuth OIDC JWT Token.', 
      icon: Key, 
      color: 'yellow', 
      accent: '#eab308',
      snippet: 'const response = await instance.acquireTokenSilent({ account });\nconst token = response.accessToken;'
    } 
  },
  
  // Request Phase
  // Post-Login Storage
  { 
    id: 'frontend_store', 
    type: 'custom', 
    position: { x: 50, y: 500 }, 
    data: { 
      label: 'React Frontend State', 
      subtitle: 'MSAL Instance', 
      desc: 'Stores Azure AD payload ready for Bearer auth.', 
      icon: MessageSquareText, 
      color: 'cyan', 
      accent: '#06b6d4',
      snippet: 'const [tokens, setTokens] = useState({accessToken, idToken});\n// Used automatically in fetch headers'
    } 
  },
  { 
    id: 'fastapi_auth', 
    type: 'custom', 
    position: { x: 550, y: 500 }, 
    data: { 
      label: 'FastAPI Extracted Setup', 
      subtitle: 'API Startup/Ping', 
      desc: 'Validates issuer, RS256 signature, maps email claims.', 
      icon: Lock, 
      color: 'purple', 
      accent: '#8b5cf6',
      snippet: 'async def verify_jwt(token: str):\n    decoded = jwt.decode(token, algorithms=["RS256"])\n    return Identity(email=decoded["preferred_username"])'
    } 
  },
  { 
    id: 'chat_handoff', 
    type: 'custom', 
    position: { x: 1050, y: 500 }, 
    data: { 
      label: 'JWT Acquired: Proceed to Chat Flow', 
      subtitle: 'Triggering WIF STS & RAG', 
      desc: 'Context is now ready. Click here to trace how the backend exchanges this JWT for a GCP Vertex Token.', 
      icon: ArrowRightCircle, 
      color: 'orange', 
      accent: '#f97316',
      highlight: true,
      snippet: '// Next Phase: The backend uses this validated identity to acquire a GCP credentials token via Workload Identity Federation.'
    } 
  }
];

const initialEdges = [
  // Auth Flow
  { id: 'e-user-entra', source: 'user', target: 'entra_login', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: '1. Sign In Request', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#eab308' }, style: { stroke: '#eab308', strokeWidth: 2 }, labelBgStyle: { fill: '#1e1e1e' }, labelStyle: { fill: '#eab308' } },
  { id: 'e-entra-user', source: 'entra_login', target: 'user', sourceHandle: 's-left', targetHandle: 't-right', type: 'smoothstep', label: '2. Return OIDC JWT', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#86bc25' }, style: { stroke: '#86bc25', strokeWidth: 2, strokeDasharray: '5 5' }, labelBgStyle: { fill: '#1e1e1e' }, labelStyle: { fill: '#86bc25' } },
  { id: 'e-user-frontend', source: 'user', target: 'frontend_store', sourceHandle: 's-bottom', targetHandle: 't-top', type: 'smoothstep', label: '3. Store Token Locally', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' }, style: { stroke: '#3b82f6', strokeWidth: 2 }, labelBgStyle: { fill: '#1e1e1e' }, labelStyle: { fill: '#3b82f6' } },
  { id: 'e-frontend-backend', source: 'frontend_store', target: 'fastapi_auth', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: '4. Ping / Validate', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' }, style: { stroke: '#8b5cf6', strokeWidth: 2 }, labelBgStyle: { fill: '#1e1e1e' }, labelStyle: { fill: '#8b5cf6' } },
  { id: 'e-backend-chat', source: 'fastapi_auth', target: 'chat_handoff', sourceHandle: 's-right', targetHandle: 't-left', type: 'smoothstep', label: 'Begin Chat Protocol', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#f97316' }, style: { stroke: '#f97316', strokeWidth: 2 }, labelBgStyle: { fill: '#1e1e1e' }, labelStyle: { fill: '#f97316', fontWeight: 'bold' } },
];

export const AuthRequestFlow: React.FC<AuthRequestFlowProps> = ({ onNavigateToChat }) => {
  const [nodes, , onNodesChange] = useNodesState(initialNodes as any);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges as any);
  
  const [hoverData, setHoverData] = React.useState<{node: any, x: number, y: number} | null>(null);

  const onNodeClick = (_e: React.MouseEvent, node: any) => {
    if (node.id === 'chat_handoff' && onNavigateToChat) {
      onNavigateToChat();
    }
  };

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

  // Ensure icons load correctly
  nodes.forEach(n => {
    if (n.id === 'user' && typeof n.data.icon !== 'function') n.data.icon = User;
    if (n.id === 'entra_login' && typeof n.data.icon !== 'function') n.data.icon = Key;
    if (n.id === 'frontend' && typeof n.data.icon !== 'function') n.data.icon = MessageSquareText;
    if (n.id === 'fastapi_auth' && typeof n.data.icon !== 'function') n.data.icon = Lock;
    if (n.id === 'adk_agent' && typeof n.data.icon !== 'function') n.data.icon = Cpu;
    if (n.id === 'data_source' && typeof n.data.icon !== 'function') n.data.icon = FileSearch;
    if (n.id === 'response' && typeof n.data.icon !== 'function') n.data.icon = Send;
  });

  return (
    <div className="ge-flow-wrapper">
      <div className="ge-flow-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2><Key size={24} color="#eab308" /> Authentication Flow (Zero-Leak)</h2>
          <p>End-to-end tracing of the Microsoft Entra ID authentication to acquire a secure token ready for Chat.</p>
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
          onNodeClick={onNodeClick}
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
                <Server size={14} color="#86bc25" />
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
