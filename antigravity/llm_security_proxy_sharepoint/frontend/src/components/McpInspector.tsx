import { useState, useCallback } from 'react';
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { Copy, Check, ChevronDown, ChevronRight, Play, Server, Layers, ShieldAlert, XCircle, ArrowLeft } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './McpInspector.css';

interface McpTool {
  name: string;
  description: string;
  inputSchema: any;
}

interface McpInspectorProps {
  goHome?: () => void;
}

export function McpInspector({ goHome }: McpInspectorProps) {
  const [client, setClient] = useState<Client | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [serverUrl, setServerUrl] = useState('https://mcp-sharepoint-server-440133963879.us-central1.run.app/sse');
  const [tools, setTools] = useState<McpTool[]>([]);
  const [logs, setLogs] = useState<{ id: string, type: 'info' | 'error' | 'request' | 'response', message: string, timestamp: Date }[]>([]);
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [toolInputs, setToolInputs] = useState<Record<string, string>>({});
  const [executingTool, setExecutingTool] = useState<string | null>(null);
  const [copiedResponse, setCopiedResponse] = useState<string | null>(null);

  const addLog = useCallback((type: 'info' | 'error' | 'request' | 'response', message: string) => {
    setLogs(prev => [...prev, {
      id: Math.random().toString(36).substring(7),
      type,
      message,
      timestamp: new Date()
    }]);
  }, []);

  const connect = async () => {
    if (isConnected) {
      if (client) {
        // Disconnect logic not natively supported by basic client without throwing, just reset state
        setClient(null);
      }
      setIsConnected(false);
      setTools([]);
      addLog('info', 'Disconnected from server.');
      return;
    }

    try {
      addLog('info', `Attempting to connect to ${serverUrl}...`);

      const transport = new SSEClientTransport(new URL(serverUrl));
      const mcpClient = new Client({
        name: "antigravity-inspector",
        version: "1.0.0",
      }, {
        capabilities: {}
      });

      await mcpClient.connect(transport);
      setClient(mcpClient);
      setIsConnected(true);
      addLog('info', 'Successfully connected via SSE transport.');

      addLog('request', 'Fetching tools from server...');
      const toolsResponse = await mcpClient.listTools();
      if (toolsResponse && toolsResponse.tools) {
        setTools(toolsResponse.tools as McpTool[]);
        addLog('response', `Received ${toolsResponse.tools.length} tool(s).`);
      } else {
        setTools([]);
        addLog('response', `No tools returned from server.`);
      }

    } catch (error: any) {
      console.error(error);
      setIsConnected(false);
      setClient(null);
      addLog('error', `Connection failed: ${error.message || 'Unknown error'}`);
    }
  };

  const toggleToolExpanded = (name: string) => {
    setExpandedTools(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const executeTool = async (toolName: string) => {
    if (!client) return;

    setExecutingTool(toolName);
    const inputString = toolInputs[toolName] || '{}';
    let argsStr = '';

    try {
      // Basic JSON parsing
      const args = JSON.parse(inputString);
      argsStr = JSON.stringify(args, null, 2);
      addLog('request', `Calling tool [${toolName}] with args: ${argsStr}`);

      const result = await client.callTool({
        name: toolName,
        arguments: args
      });

      const formattedResult = JSON.stringify(result, null, 2);
      addLog('response', `Tool [${toolName}] returned:\n${formattedResult}`);

    } catch (error: any) {
      console.error(error);
      addLog('error', `Tool [${toolName}] execution failed: ${error.message}`);
    } finally {
      setExecutingTool(null);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedResponse(id);
    setTimeout(() => setCopiedResponse(null), 2000);
  };

  const clearLogs = () => setLogs([]);

  return (
    <div className="mcp-inspector-container">
      {/* Sidebar Controls */}
      <div className="inspector-sidebar">
        {goHome && (
          <button className="back-btn" onClick={goHome}>
            <ArrowLeft size={16} /> Back to Proxy
          </button>
        )}
        <div className="sidebar-header">
          <Server size={20} color="var(--pwc-orange)" />
          <h3>MCP Server</h3>
        </div>

        <div className="control-group">
          <label>SSE URL Endpoint</label>
          <input
            type="text"
            value={serverUrl}
            onChange={(e) => setServerUrl(e.target.value)}
            disabled={isConnected}
            placeholder="http://localhost:8080/sse"
          />
        </div>

        <button
          className={`pwc-btn w-full ${isConnected ? 'danger' : ''}`}
          onClick={connect}
        >
          {isConnected ? (
            <><XCircle size={16} /> Disconnect</>
          ) : (
            <><Play size={16} /> Connect</>
          )}
        </button>

        {isConnected && tools.length > 0 && (
          <div className="tools-list-nav">
            <h4 className="flex items-center gap-2 mt-6 mb-2">
              <Layers size={14} /> Available Tools ({tools.length})
            </h4>
            <ul>
              {tools.map(tool => (
                <li key={tool.name} className="truncate text-sm text-gray-300">
                  • {tool.name}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="inspector-main">
        {/* Tools Viewer Pane */}
        <div className="tools-pane">
          <div className="pane-header">
            <h4><ShieldAlert size={16} /> Tool Explorer</h4>
          </div>

          <div className="pane-content scroll-y">
            {!isConnected ? (
              <div className="empty-state">
                <p>Connect to an MCP Server to view available tools.</p>
              </div>
            ) : tools.length === 0 ? (
              <div className="empty-state">
                <p>Connected, but the server exposes no tools.</p>
              </div>
            ) : (
              <div className="tools-accordion">
                {tools.map(tool => (
                  <div key={tool.name} className="tool-card">
                    <div
                      className="tool-card-header"
                      onClick={() => toggleToolExpanded(tool.name)}
                    >
                      <div className="flex items-center gap-2">
                        {expandedTools[tool.name] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        <span className="font-mono text-pwc-orange font-bold font-sm">{tool.name}</span>
                      </div>
                    </div>

                    {expandedTools[tool.name] && (
                      <div className="tool-card-body">
                        <p className="tool-desc text-sm mb-4 text-gray-300">{tool.description}</p>

                        <div className="schema-viewer">
                          <div className="schema-title">Arguments JSON Schema</div>
                          <pre className="text-xs">{JSON.stringify(tool.inputSchema, null, 2)}</pre>
                        </div>

                        <div className="execution-form mt-4">
                          <label className="block text-xs font-bold mb-1 text-gray-400">Input Arguments (JSON)</label>
                          <textarea
                            className="pwc-input text-xs font-mono w-full"
                            rows={4}
                            placeholder='{\n  "arg_name": "value"\n}'
                            value={toolInputs[tool.name] || ''}
                            onChange={(e) => setToolInputs((prev: any) => ({ ...prev, [tool.name]: e.target.value }))}
                          />
                          <button
                            className="pwc-btn secondary text-xs mt-2 py-1 flex items-center gap-1"
                            onClick={() => executeTool(tool.name)}
                            disabled={executingTool === tool.name}
                          >
                            {executingTool === tool.name ? 'Running...' : <><Play size={12} fill="currentColor" /> Run Tool</>}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Logs Terminal Pane */}
        <div className="logs-pane">
          <div className="pane-header flex justify-between">
            <h4>Console Output</h4>
            <button className="text-xs text-gray-400 hover:text-white" onClick={clearLogs}>Clear</button>
          </div>
          <div className="pane-content terminal scroll-y flex-col-reverse flex">
            {logs.length === 0 ? (
              <div className="text-gray-500 text-sm italic">Waiting for activity...</div>
            ) : (
              <div className="logs-stream flex flex-col justify-end min-h-full">
                {logs.map(log => (
                  <div key={log.id} className={`log-entry log-${log.type}`}>
                    <div className="log-meta">
                      <span className="log-time text-xs text-gray-500">{log.timestamp.toLocaleTimeString()}</span>
                      <span className={`log-badge badge-${log.type}`}>{log.type.toUpperCase()}</span>
                    </div>
                    {log.type === 'response' ? (
                      <div className="log-content-wrapper relative overflow-hidden group">
                        <div className="absolute right-0 top-0 pt-1 pr-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button className="bg-gray-800 p-1 rounded border border-gray-600 hover:bg-gray-700" onClick={() => handleCopy(log.message, log.id)}>
                            {copiedResponse === log.id ? <Check size={14} color="#00ff00" /> : <Copy size={14} color="#aaaaaa" />}
                          </button>
                        </div>
                        <pre className="log-message font-mono text-sm max-h-[300px] overflow-y-auto w-full"><ReactMarkdown>{log.message.replace(/\\n/g, '\n')}</ReactMarkdown></pre>
                      </div>
                    ) : (
                      <div className="log-message font-mono text-sm break-words whitespace-pre-wrap">{log.message}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
