// Chat Interface Component - Premium chat experience

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Bot,
  User,
  Trash2,
  Wrench,
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  Zap,
} from "lucide-react";
import type { Agent, ChatMessage } from "../types";
import { agentsApi } from "../utils/api";
import { useStore } from "../hooks/useStore";
import clsx from "clsx";

interface ChatInterfaceProps {
  agent: Agent;
}

export function ChatInterface({ agent }: ChatInterfaceProps) {
  const { chatMessages, addChatMessage, clearChatMessages } = useStore();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const messages = chatMessages[agent.agent_id] || [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [agent.agent_id]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    addChatMessage(agent.agent_id, userMessage);
    setInput("");
    setIsLoading(true);

    try {
      const response = await agentsApi.chat(agent.agent_id, input.trim(), sessionId);

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.content,
        tool_calls: response.tool_calls,
        timestamp: new Date(),
      };

      addChatMessage(agent.agent_id, assistantMessage);
    } catch (err) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Failed to get response"}`,
        timestamp: new Date(),
      };
      addChatMessage(agent.agent_id, errorMessage);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-220px)] glass-card overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-dark-700/50">
        <div className="flex items-center gap-4">
          <div className={clsx(
            "w-12 h-12 rounded-xl flex items-center justify-center",
            agent.framework === "adk" ? "bg-accent-primary/20" : "bg-accent-secondary/20"
          )}>
            <Bot className={clsx(
              "w-6 h-6",
              agent.framework === "adk" ? "text-accent-primary" : "text-accent-secondary"
            )} />
          </div>
          <div>
            <h3 className="font-semibold text-white text-lg">{agent.name}</h3>
            <div className="flex items-center gap-2 text-sm">
              <span className={clsx(
                "badge",
                agent.framework === "adk" ? "badge-primary" : "badge-secondary"
              )}>
                {agent.framework.toUpperCase()}
              </span>
              <span className="text-dark-400">{agent.model_id}</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => clearChatMessages(agent.agent_id)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-dark-400 hover:text-red-400 hover:bg-red-400/10 transition-all"
        >
          <Trash2 className="w-4 h-4" />
          <span className="text-sm">Clear</span>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        <AnimatePresence initial={false}>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full text-center"
            >
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center mb-6">
                <Sparkles className="w-10 h-10 text-accent-primary" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Start chatting with {agent.name}
              </h3>
              <p className="text-dark-400 max-w-md">
                This agent is powered by {agent.model_id} and uses the {agent.framework.toUpperCase()} framework.
                {agent.mcp_servers?.length > 0 && ` It has access to ${agent.mcp_servers.length} MCP server(s).`}
              </p>
            </motion.div>
          )}

          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={clsx(
                "flex gap-4",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === "assistant" && (
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-accent-primary" />
                </div>
              )}

              <div
                className={clsx(
                  "max-w-[75%] rounded-2xl p-4 group relative",
                  msg.role === "user"
                    ? "message-user"
                    : "message-assistant"
                )}
              >
                {/* Message Content */}
                <div className="text-dark-100 whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>

                {/* Tool Calls */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-dark-600/30">
                    <div className="flex items-center gap-2 text-xs text-dark-400 mb-2">
                      <Wrench className="w-3.5 h-3.5" />
                      Tools Used
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.tool_calls.map((tc, tcIdx) => (
                        <span
                          key={tcIdx}
                          className="px-3 py-1 bg-dark-700/50 rounded-lg text-xs text-dark-300 font-mono"
                        >
                          {tc.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Message Footer */}
                <div className="flex items-center justify-between mt-3 pt-2">
                  <span className="text-xs text-dark-500">
                    {formatTime(msg.timestamp)}
                  </span>

                  {msg.role === "assistant" && (
                    <button
                      onClick={() => copyToClipboard(msg.content, idx)}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-dark-700/50 transition-all"
                    >
                      {copiedIndex === idx ? (
                        <Check className="w-4 h-4 text-accent-success" />
                      ) : (
                        <Copy className="w-4 h-4 text-dark-400" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {msg.role === "user" && (
                <div className="w-10 h-10 rounded-xl bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-accent-primary" />
                </div>
              )}
            </motion.div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-4"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-accent-primary" />
              </div>
              <div className="message-assistant px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex space-x-1.5">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2.5 h-2.5 bg-accent-primary rounded-full"
                        animate={{
                          y: [0, -8, 0],
                          opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                          duration: 0.8,
                          repeat: Infinity,
                          delay: i * 0.15,
                        }}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-dark-400">Thinking...</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-dark-700/50 bg-dark-900/30">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message your agent..."
              className="textarea-modern pr-12 min-h-[56px] max-h-[200px]"
              rows={1}
              disabled={isLoading}
              style={{
                height: 'auto',
                minHeight: '56px',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 200) + 'px';
              }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className={clsx(
              "w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-200",
              input.trim() && !isLoading
                ? "bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-lg shadow-accent-primary/25 hover:shadow-glow hover:scale-105"
                : "bg-dark-800 text-dark-500 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <RotateCcw className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Quick tips */}
        <div className="flex items-center justify-center gap-4 mt-3 text-xs text-dark-500">
          <span>Press <kbd className="px-1.5 py-0.5 bg-dark-800 rounded text-dark-400">Enter</kbd> to send</span>
          <span>Press <kbd className="px-1.5 py-0.5 bg-dark-800 rounded text-dark-400">Shift + Enter</kbd> for new line</span>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
