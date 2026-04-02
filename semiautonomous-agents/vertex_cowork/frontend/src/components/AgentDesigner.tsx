// Agent Designer Component - Visual agent builder

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Bot,
  Cpu,
  GitBranch,
  Layers,
  RotateCw,
  Users,
  Zap,
  Server,
  Check,
  ChevronDown,
  AlertCircle,
  Loader2,
  Wand2,
  Brain,
} from "lucide-react";
import type {
  Agent,
  AgentCreateRequest,
  AgentType,
  Framework,
} from "../types";
import { agentsApi, modelsApi, mcpApi, frameworksApi } from "../utils/api";
import { useStore } from "../hooks/useStore";
import clsx from "clsx";

const AGENT_TYPES: { value: AgentType; label: string; description: string; icon: typeof Bot }[] = [
  { value: "llm", label: "LLM Agent", description: "Reasoning agent powered by an LLM", icon: Brain },
  { value: "supervisor", label: "Supervisor", description: "Orchestrates multiple subagents", icon: Users },
  { value: "sequential", label: "Sequential", description: "Runs subagents in order", icon: GitBranch },
  { value: "parallel", label: "Parallel", description: "Runs subagents concurrently", icon: Layers },
  { value: "loop", label: "Loop", description: "Iterative execution agent", icon: RotateCw },
];

const FRAMEWORKS: { value: Framework; label: string; description: string; features: string[] }[] = [
  {
    value: "adk",
    label: "Google ADK",
    description: "Native Vertex AI integration with enterprise features",
    features: ["Native MCP Support", "SequentialAgent", "ParallelAgent", "LoopAgent"],
  },
  {
    value: "langgraph",
    label: "LangGraph",
    description: "Flexible graph-based workflows with state management",
    features: ["StateGraph", "MemorySaver", "Conditional Edges", "Streaming"],
  },
];

interface AgentDesignerProps {
  onAgentCreated?: (agent: Agent) => void;
  existingAgent?: Agent;
}

export function AgentDesigner({ onAgentCreated, existingAgent }: AgentDesignerProps) {
  const { models, setModels, mcpServers, setMcpServers, agents } = useStore();

  const [formData, setFormData] = useState<AgentCreateRequest>({
    agent_id: existingAgent?.agent_id || "",
    name: existingAgent?.name || "",
    description: existingAgent?.description || "",
    model_id: existingAgent?.model_id || "gemini-2.0-flash",
    framework: existingAgent?.framework || "adk",
    agent_type: existingAgent?.agent_type || "llm",
    system_prompt: existingAgent?.system_prompt || "You are a helpful AI assistant.",
    tools: existingAgent?.tools || [],
    mcp_servers: existingAgent?.mcp_servers || [],
    subagents: existingAgent?.subagents || [],
    max_iterations: 10,
    temperature: 0.7,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [modelsData, mcpData] = await Promise.all([
        modelsApi.list(),
        mcpApi.list(),
      ]);
      setModels(modelsData);
      setMcpServers(mcpData);
    } catch (err) {
      console.error("Failed to load initial data:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const agent = await agentsApi.create(formData);
      onAgentCreated?.(agent);
      setFormData({
        agent_id: "",
        name: "",
        description: "",
        model_id: "gemini-2.0-flash",
        framework: "adk",
        agent_type: "llm",
        system_prompt: "You are a helpful AI assistant.",
        tools: [],
        mcp_servers: [],
        subagents: [],
        max_iterations: 10,
        temperature: 0.7,
      });
      setStep(1);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create agent";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMcpServer = (serverId: string) => {
    setFormData((prev) => ({
      ...prev,
      mcp_servers: prev.mcp_servers?.includes(serverId)
        ? prev.mcp_servers.filter((id) => id !== serverId)
        : [...(prev.mcp_servers || []), serverId],
    }));
  };

  const toggleSubagent = (agentId: string) => {
    setFormData((prev) => ({
      ...prev,
      subagents: prev.subagents?.includes(agentId)
        ? prev.subagents.filter((id) => id !== agentId)
        : [...(prev.subagents || []), agentId],
    }));
  };

  const selectedModel = models.find((m) => m.model_id === formData.model_id);
  const needsSubagents = ["supervisor", "sequential", "parallel", "loop"].includes(formData.agent_type);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: "Framework & Model" },
            { num: 2, label: "Agent Configuration" },
            { num: 3, label: "Tools & Capabilities" },
          ].map((s, i) => (
            <div key={s.num} className="flex items-center">
              <button
                onClick={() => setStep(s.num)}
                className={clsx(
                  "flex items-center gap-3 px-4 py-2 rounded-xl transition-all",
                  step === s.num
                    ? "bg-accent-primary/20 text-accent-primary"
                    : step > s.num
                    ? "text-accent-success"
                    : "text-dark-500"
                )}
              >
                <div
                  className={clsx(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold",
                    step === s.num
                      ? "bg-accent-primary text-white"
                      : step > s.num
                      ? "bg-accent-success text-white"
                      : "bg-dark-800 text-dark-400"
                  )}
                >
                  {step > s.num ? <Check className="w-4 h-4" /> : s.num}
                </div>
                <span className="hidden md:block font-medium">{s.label}</span>
              </button>
              {i < 2 && (
                <div
                  className={clsx(
                    "w-12 lg:w-24 h-0.5 mx-2",
                    step > s.num ? "bg-accent-success" : "bg-dark-800"
                  )}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <AnimatePresence mode="wait">
          {/* Step 1: Framework & Model */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              {/* Framework Selection */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-accent-primary" />
                  Choose Framework
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {FRAMEWORKS.map((fw) => (
                    <button
                      key={fw.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, framework: fw.value })}
                      className={clsx(
                        "p-5 rounded-xl border-2 text-left transition-all duration-200",
                        formData.framework === fw.value
                          ? "border-accent-primary bg-accent-primary/10"
                          : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                      )}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div
                          className={clsx(
                            "w-10 h-10 rounded-lg flex items-center justify-center",
                            formData.framework === fw.value
                              ? "bg-accent-primary/20"
                              : "bg-dark-700/50"
                          )}
                        >
                          {fw.value === "adk" ? (
                            <Zap className="w-5 h-5 text-accent-primary" />
                          ) : (
                            <GitBranch className="w-5 h-5 text-accent-secondary" />
                          )}
                        </div>
                        <div>
                          <h4 className="font-semibold text-white">{fw.label}</h4>
                          <p className="text-xs text-dark-400">{fw.description}</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {fw.features.map((feature) => (
                          <span
                            key={feature}
                            className="px-2 py-0.5 text-xs rounded-md bg-dark-700/50 text-dark-300"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Model Selection */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-accent-primary" />
                  Select Model
                </h3>

                {/* Vertex AI Models */}
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-dark-400 mb-3">Vertex AI Managed</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {models
                      .filter((m) => m.provider === "vertex")
                      .map((model) => (
                        <button
                          key={model.model_id}
                          type="button"
                          onClick={() => setFormData({ ...formData, model_id: model.model_id })}
                          className={clsx(
                            "p-4 rounded-xl border text-left transition-all",
                            formData.model_id === model.model_id
                              ? "border-accent-primary bg-accent-primary/10"
                              : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                          )}
                        >
                          <div className="font-medium text-white text-sm">{model.display_name}</div>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {model.supports_tools && (
                              <span className="badge-success">Tools</span>
                            )}
                            {model.supports_vision && (
                              <span className="badge-primary">Vision</span>
                            )}
                          </div>
                        </button>
                      ))}
                  </div>
                </div>

                {/* Model Garden Models */}
                <div>
                  <h4 className="text-sm font-medium text-dark-400 mb-3">Model Garden</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    {models
                      .filter((m) => m.provider === "model_garden")
                      .map((model) => (
                        <button
                          key={model.model_id}
                          type="button"
                          onClick={() => setFormData({ ...formData, model_id: model.model_id })}
                          className={clsx(
                            "p-4 rounded-xl border text-left transition-all",
                            formData.model_id === model.model_id
                              ? "border-accent-secondary bg-accent-secondary/10"
                              : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                          )}
                        >
                          <div className="font-medium text-white text-sm">{model.display_name}</div>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {model.supports_tools && (
                              <span className="badge-success">Tools</span>
                            )}
                          </div>
                        </button>
                      ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="btn-primary"
                >
                  Continue
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Agent Configuration */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              {/* Basic Info */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-accent-primary" />
                  Agent Identity
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                      Agent ID
                    </label>
                    <input
                      type="text"
                      value={formData.agent_id}
                      onChange={(e) => setFormData({ ...formData, agent_id: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                      className="input-modern"
                      placeholder="my-agent"
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
                      placeholder="My Agent"
                      required
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="textarea-modern"
                    rows={2}
                    placeholder="What does this agent do?"
                  />
                </div>
              </div>

              {/* Agent Type */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-accent-primary" />
                  Agent Type
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {AGENT_TYPES.map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, agent_type: type.value })}
                      className={clsx(
                        "p-4 rounded-xl border text-center transition-all",
                        formData.agent_type === type.value
                          ? "border-accent-primary bg-accent-primary/10"
                          : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                      )}
                    >
                      <type.icon
                        className={clsx(
                          "w-6 h-6 mx-auto mb-2",
                          formData.agent_type === type.value ? "text-accent-primary" : "text-dark-400"
                        )}
                      />
                      <div className="font-medium text-white text-sm">{type.label}</div>
                      <div className="text-xs text-dark-500 mt-1">{type.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* System Prompt */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Wand2 className="w-5 h-5 text-accent-primary" />
                  System Prompt
                </h3>
                <textarea
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                  className="textarea-modern font-mono text-sm"
                  rows={6}
                  placeholder="You are a helpful AI assistant..."
                />
              </div>

              {/* Temperature */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Temperature: <span className="text-accent-primary">{formData.temperature}</span>
                </h3>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-dark-400">Precise</span>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                    className="flex-1 h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-accent-primary"
                  />
                  <span className="text-sm text-dark-400">Creative</span>
                </div>
              </div>

              <div className="flex justify-between">
                <button type="button" onClick={() => setStep(1)} className="btn-secondary">
                  Back
                </button>
                <button type="button" onClick={() => setStep(3)} className="btn-primary">
                  Continue
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Tools & Capabilities */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              {/* MCP Servers */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Server className="w-5 h-5 text-accent-primary" />
                  MCP Servers
                </h3>
                {mcpServers.length === 0 ? (
                  <div className="text-center py-8">
                    <Server className="w-12 h-12 text-dark-600 mx-auto mb-3" />
                    <p className="text-dark-400">No MCP servers registered</p>
                    <p className="text-sm text-dark-500 mt-1">
                      Connect MCP servers to give your agent access to external tools
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {mcpServers.map((server) => (
                      <button
                        key={server.server_id}
                        type="button"
                        onClick={() => toggleMcpServer(server.server_id)}
                        className={clsx(
                          "p-4 rounded-xl border text-left transition-all flex items-center gap-3",
                          formData.mcp_servers?.includes(server.server_id)
                            ? "border-accent-success bg-accent-success/10"
                            : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                        )}
                      >
                        <div
                          className={clsx(
                            "w-10 h-10 rounded-lg flex items-center justify-center",
                            formData.mcp_servers?.includes(server.server_id)
                              ? "bg-accent-success/20"
                              : "bg-dark-700/50"
                          )}
                        >
                          <Server
                            className={clsx(
                              "w-5 h-5",
                              formData.mcp_servers?.includes(server.server_id)
                                ? "text-accent-success"
                                : "text-dark-400"
                            )}
                          />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-white">{server.name}</div>
                          <div className="text-xs text-dark-400">{server.transport}</div>
                        </div>
                        {formData.mcp_servers?.includes(server.server_id) && (
                          <Check className="w-5 h-5 text-accent-success" />
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Subagents */}
              {needsSubagents && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5 text-accent-primary" />
                    Subagents
                  </h3>
                  {agents.filter((a) => a.agent_id !== formData.agent_id).length === 0 ? (
                    <div className="text-center py-8">
                      <Bot className="w-12 h-12 text-dark-600 mx-auto mb-3" />
                      <p className="text-dark-400">No other agents available</p>
                      <p className="text-sm text-dark-500 mt-1">
                        Create other agents first to use them as subagents
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {agents
                        .filter((a) => a.agent_id !== formData.agent_id)
                        .map((agent) => (
                          <button
                            key={agent.agent_id}
                            type="button"
                            onClick={() => toggleSubagent(agent.agent_id)}
                            className={clsx(
                              "p-4 rounded-xl border text-left transition-all flex items-center gap-3",
                              formData.subagents?.includes(agent.agent_id)
                                ? "border-accent-secondary bg-accent-secondary/10"
                                : "border-dark-700/50 hover:border-dark-600 bg-dark-800/30"
                            )}
                          >
                            <div
                              className={clsx(
                                "w-10 h-10 rounded-lg flex items-center justify-center",
                                formData.subagents?.includes(agent.agent_id)
                                  ? "bg-accent-secondary/20"
                                  : "bg-dark-700/50"
                              )}
                            >
                              <Bot
                                className={clsx(
                                  "w-5 h-5",
                                  formData.subagents?.includes(agent.agent_id)
                                    ? "text-accent-secondary"
                                    : "text-dark-400"
                                )}
                              />
                            </div>
                            <div className="flex-1">
                              <div className="font-medium text-white">{agent.name}</div>
                              <div className="text-xs text-dark-400">{agent.framework.toUpperCase()}</div>
                            </div>
                            {formData.subagents?.includes(agent.agent_id) && (
                              <Check className="w-5 h-5 text-accent-secondary" />
                            )}
                          </button>
                        ))}
                    </div>
                  )}
                </div>
              )}

              {/* Summary */}
              <div className="glass-card p-6 border-accent-primary/30">
                <h3 className="text-lg font-semibold text-white mb-4">Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-dark-400">Framework</span>
                    <p className="font-medium text-white mt-1">{formData.framework.toUpperCase()}</p>
                  </div>
                  <div>
                    <span className="text-dark-400">Model</span>
                    <p className="font-medium text-white mt-1">{selectedModel?.display_name}</p>
                  </div>
                  <div>
                    <span className="text-dark-400">Type</span>
                    <p className="font-medium text-white mt-1">
                      {AGENT_TYPES.find((t) => t.value === formData.agent_type)?.label}
                    </p>
                  </div>
                  <div>
                    <span className="text-dark-400">MCP Servers</span>
                    <p className="font-medium text-white mt-1">{formData.mcp_servers?.length || 0}</p>
                  </div>
                </div>
              </div>

              {/* Error Display */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-red-400" />
                    <span className="text-red-400">{error}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="flex justify-between">
                <button type="button" onClick={() => setStep(2)} className="btn-secondary">
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !formData.agent_id || !formData.name}
                  className="btn-primary flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Create Agent
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </form>
    </div>
  );
}

export default AgentDesigner;
