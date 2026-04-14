// MCP Server Manager Component - Premium design

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Server,
  Plus,
  X,
  Plug,
  PlugZap,
  Terminal,
  Globe,
  Radio,
  Wrench,
  Database,
  Loader2,
  AlertCircle,
  Check,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import type { MCPServer } from "../types";
import { mcpApi } from "../utils/api";
import { useStore } from "../hooks/useStore";
import clsx from "clsx";

const TRANSPORT_OPTIONS = [
  {
    value: "stdio" as const,
    label: "STDIO",
    description: "Run as subprocess",
    icon: Terminal,
  },
  {
    value: "sse" as const,
    label: "SSE",
    description: "Server-Sent Events",
    icon: Radio,
  },
  {
    value: "http" as const,
    label: "HTTP",
    description: "REST API",
    icon: Globe,
  },
];

export function MCPServerManager() {
  const { mcpServers, setMcpServers, addMcpServer, updateMcpServer } = useStore();

  const [showAddForm, setShowAddForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [connectingId, setConnectingId] = useState<string | null>(null);
  const [expandedServer, setExpandedServer] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    server_id: "",
    name: "",
    transport: "stdio" as "stdio" | "sse" | "http",
    command: "",
    url: "",
  });

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      const servers = await mcpApi.list();
      setMcpServers(servers);
    } catch (err) {
      console.error("Failed to load MCP servers:", err);
    }
  };

  const handleAddServer = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const server = await mcpApi.register(formData);
      addMcpServer(server);
      setShowAddForm(false);
      setFormData({
        server_id: "",
        name: "",
        transport: "stdio",
        command: "",
        url: "",
      });
    } catch (err) {
      console.error("Failed to add MCP server:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async (serverId: string) => {
    setConnectingId(serverId);
    try {
      const server = await mcpApi.connect(serverId);
      updateMcpServer(serverId, {
        connected: true,
        tools: server.tools,
        resources: server.resources,
      });
      setExpandedServer(serverId);
    } catch (err) {
      console.error("Failed to connect to MCP server:", err);
    } finally {
      setConnectingId(null);
    }
  };

  const handleDisconnect = async (serverId: string) => {
    setConnectingId(serverId);
    try {
      await mcpApi.disconnect(serverId);
      updateMcpServer(serverId, { connected: false });
    } catch (err) {
      console.error("Failed to disconnect from MCP server:", err);
    } finally {
      setConnectingId(null);
    }
  };

  const connectedCount = mcpServers.filter((s) => s.connected).length;
  const totalToolsCount = mcpServers.reduce((acc, s) => acc + (s.tools?.length || 0), 0);

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: "Total Servers", value: mcpServers.length, icon: Server, color: "accent-primary" },
          { label: "Connected", value: connectedCount, icon: PlugZap, color: "accent-success" },
          { label: "Available Tools", value: totalToolsCount, icon: Wrench, color: "accent-secondary" },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl bg-${stat.color}/20 flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}`} />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-sm text-dark-400">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">MCP Servers</h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className={clsx(
              "flex items-center gap-2 px-4 py-2 rounded-xl transition-all",
              showAddForm
                ? "bg-dark-700 text-dark-300"
                : "btn-primary"
            )}
          >
            {showAddForm ? (
              <>
                <X className="w-4 h-4" />
                Cancel
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" />
                Add Server
              </>
            )}
          </button>
        </div>

        {/* Add Server Form */}
        <AnimatePresence>
          {showAddForm && (
            <motion.form
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={handleAddServer}
              className="mb-6 p-6 bg-dark-800/50 rounded-xl border border-dark-700/50 space-y-6 overflow-hidden"
            >
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Server ID
                  </label>
                  <input
                    type="text"
                    value={formData.server_id}
                    onChange={(e) => setFormData({ ...formData, server_id: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                    className="input-modern"
                    placeholder="filesystem-server"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input-modern"
                    placeholder="Filesystem Server"
                    required
                  />
                </div>
              </div>

              {/* Transport Selection */}
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-3">
                  Transport Type
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {TRANSPORT_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, transport: option.value })}
                      className={clsx(
                        "p-4 rounded-xl border text-center transition-all",
                        formData.transport === option.value
                          ? "border-accent-primary bg-accent-primary/10"
                          : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                      )}
                    >
                      <option.icon
                        className={clsx(
                          "w-6 h-6 mx-auto mb-2",
                          formData.transport === option.value ? "text-accent-primary" : "text-dark-400"
                        )}
                      />
                      <div className="font-medium text-white text-sm">{option.label}</div>
                      <div className="text-xs text-dark-500">{option.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Connection Details */}
              {formData.transport === "stdio" ? (
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Command
                  </label>
                  <input
                    type="text"
                    value={formData.command}
                    onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                    className="input-modern font-mono text-sm"
                    placeholder="npx -y @modelcontextprotocol/server-filesystem /path/to/dir"
                  />
                  <p className="text-xs text-dark-500 mt-2">
                    The command to spawn the MCP server process
                  </p>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    URL
                  </label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    className="input-modern"
                    placeholder="http://localhost:3000/mcp"
                  />
                  <p className="text-xs text-dark-500 mt-2">
                    The URL endpoint for the MCP server
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Adding Server...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Add Server
                  </>
                )}
              </button>
            </motion.form>
          )}
        </AnimatePresence>

        {/* Server List */}
        <div className="space-y-3">
          {mcpServers.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-20 h-20 rounded-full bg-dark-800/50 flex items-center justify-center mx-auto mb-4">
                <Server className="w-10 h-10 text-dark-500" />
              </div>
              <h3 className="text-lg font-medium text-dark-300 mb-2">No MCP Servers</h3>
              <p className="text-dark-500 mb-6">Add an MCP server to extend your agents' capabilities</p>
              <button onClick={() => setShowAddForm(true)} className="btn-primary">
                Add Your First Server
              </button>
            </div>
          ) : (
            mcpServers.map((server, i) => (
              <motion.div
                key={server.server_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="rounded-xl border border-dark-700/50 bg-dark-800/30 overflow-hidden"
              >
                {/* Server Header */}
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div
                      className={clsx(
                        "w-12 h-12 rounded-xl flex items-center justify-center",
                        server.connected ? "bg-accent-success/20" : "bg-dark-700/50"
                      )}
                    >
                      <Server
                        className={clsx(
                          "w-6 h-6",
                          server.connected ? "text-accent-success" : "text-dark-400"
                        )}
                      />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white">{server.name}</h3>
                        <span
                          className={clsx(
                            "badge",
                            server.connected ? "badge-success" : "bg-dark-700 text-dark-400"
                          )}
                        >
                          {server.connected ? "Connected" : "Disconnected"}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-dark-400 mt-1">
                        <span className="flex items-center gap-1">
                          {TRANSPORT_OPTIONS.find((t) => t.value === server.transport)?.icon &&
                            (() => {
                              const Icon = TRANSPORT_OPTIONS.find((t) => t.value === server.transport)!.icon;
                              return <Icon className="w-3.5 h-3.5" />;
                            })()}
                          {server.transport.toUpperCase()}
                        </span>
                        <span className="text-dark-600">|</span>
                        <span className="font-mono text-xs">{server.server_id}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {server.connected && (
                      <button
                        onClick={() => setExpandedServer(expandedServer === server.server_id ? null : server.server_id)}
                        className="p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-700/50 transition-all"
                      >
                        {expandedServer === server.server_id ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </button>
                    )}
                    <button
                      onClick={() =>
                        server.connected
                          ? handleDisconnect(server.server_id)
                          : handleConnect(server.server_id)
                      }
                      disabled={connectingId === server.server_id}
                      className={clsx(
                        "flex items-center gap-2 px-4 py-2 rounded-xl transition-all",
                        server.connected
                          ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
                          : "bg-accent-success/10 text-accent-success hover:bg-accent-success/20 border border-accent-success/30"
                      )}
                    >
                      {connectingId === server.server_id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : server.connected ? (
                        <Plug className="w-4 h-4" />
                      ) : (
                        <PlugZap className="w-4 h-4" />
                      )}
                      <span className="text-sm font-medium">
                        {connectingId === server.server_id
                          ? "..."
                          : server.connected
                          ? "Disconnect"
                          : "Connect"}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {server.connected && expandedServer === server.server_id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-dark-700/50 overflow-hidden"
                    >
                      <div className="p-4 space-y-4">
                        {/* Tools */}
                        <div>
                          <div className="flex items-center gap-2 text-sm font-medium text-dark-300 mb-2">
                            <Wrench className="w-4 h-4" />
                            Tools ({server.tools?.length || 0})
                          </div>
                          {server.tools && server.tools.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {server.tools.map((tool) => (
                                <span
                                  key={tool}
                                  className="px-3 py-1.5 bg-accent-primary/10 border border-accent-primary/30 rounded-lg text-sm text-accent-primary font-mono"
                                >
                                  {tool}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-dark-500">No tools available</p>
                          )}
                        </div>

                        {/* Resources */}
                        <div>
                          <div className="flex items-center gap-2 text-sm font-medium text-dark-300 mb-2">
                            <Database className="w-4 h-4" />
                            Resources ({server.resources?.length || 0})
                          </div>
                          {server.resources && server.resources.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {server.resources.map((resource) => (
                                <span
                                  key={resource}
                                  className="px-3 py-1.5 bg-accent-secondary/10 border border-accent-secondary/30 rounded-lg text-sm text-accent-secondary font-mono"
                                >
                                  {resource}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-dark-500">No resources available</p>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default MCPServerManager;
