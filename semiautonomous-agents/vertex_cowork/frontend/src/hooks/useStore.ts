// Global state management with Zustand

import { create } from "zustand";
import type { Agent, ChatMessage, MCPServer, Model } from "../types";

interface AgentNexusState {
  // Models
  models: Model[];
  selectedModel: Model | null;
  setModels: (models: Model[]) => void;
  setSelectedModel: (model: Model | null) => void;

  // MCP Servers
  mcpServers: MCPServer[];
  setMcpServers: (servers: MCPServer[]) => void;
  addMcpServer: (server: MCPServer) => void;
  updateMcpServer: (serverId: string, updates: Partial<MCPServer>) => void;

  // Agents
  agents: Agent[];
  selectedAgent: Agent | null;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  removeAgent: (agentId: string) => void;
  setSelectedAgent: (agent: Agent | null) => void;

  // Chat
  chatMessages: Record<string, ChatMessage[]>;
  addChatMessage: (agentId: string, message: ChatMessage) => void;
  clearChatMessages: (agentId: string) => void;

  // UI State
  isLoading: boolean;
  error: string | null;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStore = create<AgentNexusState>((set) => ({
  // Models
  models: [],
  selectedModel: null,
  setModels: (models) => set({ models }),
  setSelectedModel: (model) => set({ selectedModel: model }),

  // MCP Servers
  mcpServers: [],
  setMcpServers: (servers) => set({ mcpServers: servers }),
  addMcpServer: (server) =>
    set((state) => ({ mcpServers: [...state.mcpServers, server] })),
  updateMcpServer: (serverId, updates) =>
    set((state) => ({
      mcpServers: state.mcpServers.map((s) =>
        s.server_id === serverId ? { ...s, ...updates } : s
      ),
    })),

  // Agents
  agents: [],
  selectedAgent: null,
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  removeAgent: (agentId) =>
    set((state) => ({
      agents: state.agents.filter((a) => a.agent_id !== agentId),
    })),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),

  // Chat
  chatMessages: {},
  addChatMessage: (agentId, message) =>
    set((state) => ({
      chatMessages: {
        ...state.chatMessages,
        [agentId]: [...(state.chatMessages[agentId] || []), message],
      },
    })),
  clearChatMessages: (agentId) =>
    set((state) => ({
      chatMessages: {
        ...state.chatMessages,
        [agentId]: [],
      },
    })),

  // UI State
  isLoading: false,
  error: null,
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
