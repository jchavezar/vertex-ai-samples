// API client for Vertex Cowork backend

import axios from "axios";
import type {
  Agent,
  AgentCreateRequest,
  ChatResponse,
  FrameworkInfo,
  MCPServer,
  Model,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Models API
export const modelsApi = {
  list: async (provider?: string): Promise<Model[]> => {
    const params = provider ? { provider } : {};
    const { data } = await api.get("/api/models", { params });
    return data;
  },

  get: async (modelId: string): Promise<Model> => {
    const { data } = await api.get(`/api/models/${modelId}`);
    return data;
  },
};

// MCP Servers API
export const mcpApi = {
  list: async (): Promise<MCPServer[]> => {
    const { data } = await api.get("/api/mcp-servers");
    return data;
  },

  register: async (server: {
    server_id: string;
    name: string;
    transport: string;
    command?: string;
    url?: string;
    config?: Record<string, unknown>;
  }): Promise<MCPServer> => {
    const { data } = await api.post("/api/mcp-servers", server);
    return data;
  },

  connect: async (serverId: string): Promise<MCPServer> => {
    const { data } = await api.post(`/api/mcp-servers/${serverId}/connect`);
    return data;
  },

  disconnect: async (serverId: string): Promise<void> => {
    await api.post(`/api/mcp-servers/${serverId}/disconnect`);
  },

  getContext: async (serverId: string): Promise<{
    server_id: string;
    user?: { login: string; name: string };
    repos?: Array<{ name: string; full_name: string; description: string; language: string; stars: number }>;
  }> => {
    const { data } = await api.get(`/api/mcp-servers/${serverId}/context`);
    return data;
  },
};

// Agents API
export const agentsApi = {
  list: async (framework?: string): Promise<Agent[]> => {
    const params = framework ? { framework } : {};
    const { data } = await api.get("/api/agents", { params });
    return data;
  },

  get: async (agentId: string): Promise<Agent> => {
    const { data } = await api.get(`/api/agents/${agentId}`);
    return data;
  },

  create: async (agent: AgentCreateRequest): Promise<Agent> => {
    const { data } = await api.post("/api/agents", agent);
    return data;
  },

  delete: async (agentId: string): Promise<void> => {
    await api.delete(`/api/agents/${agentId}`);
  },

  chat: async (
    agentId: string,
    message: string,
    sessionId?: string
  ): Promise<ChatResponse> => {
    const { data } = await api.post(`/api/agents/${agentId}/chat`, {
      message,
      session_id: sessionId,
      stream: false,
    });
    return data;
  },

  chatStream: (
    agentId: string,
    message: string,
    onChunk: (chunk: string) => void,
    sessionId?: string
  ): EventSource => {
    const eventSource = new EventSource(
      `${API_BASE}/api/agents/${agentId}/chat?message=${encodeURIComponent(
        message
      )}&session_id=${sessionId || ""}&stream=true`
    );

    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        eventSource.close();
        return;
      }
      onChunk(event.data);
    };

    return eventSource;
  },
};

// Frameworks API
export const frameworksApi = {
  list: async (): Promise<FrameworkInfo[]> => {
    const { data } = await api.get("/api/frameworks");
    return data;
  },
};

// Quick Chat API (with optional MCP servers and history)
export const quickChatApi = {
  send: async (
    message: string,
    modelId: string = "gemini-2.5-flash",
    systemPrompt: string = "You are a helpful AI assistant.",
    sessionId?: string,
    mcpServers?: string[],
    history?: Array<{ role: string; content: string }>
  ): Promise<ChatResponse> => {
    const { data } = await api.post("/api/chat", {
      message,
      model_id: modelId,
      system_prompt: systemPrompt,
      session_id: sessionId,
      history: history || [],
      mcp_servers: mcpServers || [],
    });
    return data;
  },
};

export default api;
