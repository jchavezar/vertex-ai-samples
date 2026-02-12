
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Play, Loader2, Sparkles, Film, Send, User, Bot, Video, Paperclip, X, Trash2, Terminal, CloudLightning } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [attachment, setAttachment] = useState(null); // base64 string
  const [duration, setDuration] = useState(5);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(uuidv4());

  // Agent Engine State
  const [agents, setAgents] = useState([]);
  const [deploying, setDeploying] = useState(false);
  const [deployStatus, setDeployStatus] = useState({ is_deploying: false, logs: [], error: null });
  const [selectedAgentLogs, setSelectedAgentLogs] = useState(null);
  const [deployStartTime, setDeployStartTime] = useState(null);
  const [deployTimeElapsed, setDeployTimeElapsed] = useState(0);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    let interval;
    if (deployStatus.is_deploying && deployStartTime) {
      interval = setInterval(() => {
        setDeployTimeElapsed(Math.floor((Date.now() - deployStartTime) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [deployStatus.is_deploying, deployStartTime]);

  const fetchAgents = async () => {
    try {
      const res = await axios.get('/api/agents');
      setAgents(res.data.agents || []);
    } catch (err) {
      console.error("Failed to fetch agents", err);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  // Initial greeting
  useEffect(() => {
    setMessages([
      {
        id: 'init',
        role: 'agent',
        text: "Hello! I'm your Veo Video Expert. Tell me what you want to create, and I'll help you craft the perfect prompt.",
        video: null
      }
    ]);
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Remove data URL prefix
        const base64String = reader.result.split(',')[1];
        setAttachment(base64String);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDeployAgent = async () => {
    setDeploying(true);
    setDeployStartTime(Date.now());
    setDeployTimeElapsed(0);
    setDeployStatus({ is_deploying: true, logs: [], error: null });
    try {
      await axios.post('/api/agents/deploy');

      // Start polling status
      const pollInterval = setInterval(async () => {
        try {
          const res = await axios.get('/api/agents/deploy_status');
          const data = res.data;
          setDeployStatus(data);
          if (!data.is_deploying) {
            clearInterval(pollInterval);
            setDeploying(false);
            fetchAgents();
          }
        } catch (e) {
          console.error("Error polling status", e);
        }
      }, 2000);

    } catch (err) {
      console.error("Deploy start failed", err);
      // If already deploying, just start polling
      if (err.response?.status === 400) {
        setDeployStatus({ is_deploying: true, logs: ["Resuming log stream..."], error: null });
        const pollInterval = setInterval(async () => {
          try {
            const res = await axios.get('/api/agents/deploy_status');
            const data = res.data;
            setDeployStatus(data);
            if (!data.is_deploying) {
              clearInterval(pollInterval);
              setDeploying(false);
              fetchAgents();
            }
          } catch (e) {
            console.error("Error polling status", e);
          }
        }, 2000);
      } else {
        setDeploying(false);
        setDeployStatus({ is_deploying: false, logs: [], error: err.message });
      }
    }
  };

  const handleDeleteAgent = async (resourceName) => {
    try {
      // The resource name has slashes, we pass it safely or the backend reconstructs it.
      // Easiest is to encode it or let the backend handle the path.
      // We set up the backend route to capture the remainder of the path: /api/agents/{resource_prefix}/{project}/{location}/{type}/{agent_id}
      await axios.delete(`/api/agents/${resourceName}`);
      await fetchAgents();
      if (selectedAgentLogs?.resource_name === resourceName) {
        setSelectedAgentLogs(null);
      }
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const parseAgentName = (resourceName) => {
    try {
      return resourceName.split('/').pop();
    } catch (e) { return resourceName; }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if ((!input.trim() && !attachment) || loading) return;

    const userMessage = {
      id: uuidv4(),
      role: 'user',
      text: input,
      image: attachment ? `data:image/png;base64,${attachment}` : null
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    // Convert attachment to local variable to send, then clear state
    const currentAttachment = attachment;
    setAttachment(null);
    setLoading(true);

    try {
      // In Vite dev, /api is proxied to http://localhost:8001
      let finalMessage = userMessage.text || (currentAttachment ? "Analyze this image" : "");
      finalMessage += `\n[DURATION: ${duration} seconds]`;

      const response = await axios.post('/api/chat', {
        message: finalMessage,
        image_base64: currentAttachment,
        session_id: sessionId
      });

      const data = response.data;

      const agentMessage = {
        id: uuidv4(),
        role: 'agent',
        text: data.response,
        video: data.video_base64 ? `data:video/mp4;base64,${data.video_base64}` : null
      };

      setMessages(prev => [...prev, agentMessage]);

    } catch (err) {
      console.error(err);
      const errorMessage = {
        id: uuidv4(),
        role: 'agent',
        text: "I encountered an error connecting to the creative matrix. Please try again.",
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cave-950 flex p-4 text-white relative overflow-hidden font-sans gap-4">
      {/* Background Ambient Effects */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-900/20 rounded-full blur-[100px]" />
      </div>

      {/* Sidebar - Agent Management */}
      <div className="w-80 h-[800px] glass rounded-3xl flex flex-col shadow-2xl z-10 overflow-hidden border border-white/5 bg-black/40 backdrop-blur-xl">
        <div className="p-6 border-b border-white/5 flex flex-col gap-4">
          <div className="flex items-center gap-2 text-lg font-bold">
            <CloudLightning className="text-purple-400 w-5 h-5" />
            Agent Engine
          </div>

          <button
            onClick={handleDeployAgent}
            disabled={deploying}
            className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-xl font-medium shadow-lg shadow-purple-500/20 flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50"
          >
            {deploying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {deploying ? 'Deploying...' : 'Deploy ADK Agent'}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-white/10">
          <div className="text-xs font-mono text-stone-500 uppercase tracking-wider mb-4 px-2">Deployed Agents</div>

          {agents.length === 0 && (
            <div className="text-sm text-stone-500 px-2 italic">No agents deployed yet.</div>
          )}

          {agents.map(agent => (
            <div key={agent.resource_name} className="p-3 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors group">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.6)]" title="Online" />
                  <span className="text-sm font-medium truncate w-40" title={agent.resource_name}>
                    {parseAgentName(agent.resource_name)}
                  </span>
                </div>
              </div>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => setSelectedAgentLogs(agent)}
                  className="flex-1 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs text-stone-300 flex items-center justify-center gap-1 transition-colors"
                >
                  <Terminal className="w-3 h-3" /> Logs
                </button>
                <button
                  onClick={() => handleDeleteAgent(agent.resource_name)}
                  className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs flex items-center justify-center transition-colors"
                  title="Delete Agent"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 max-w-4xl h-[800px] glass rounded-3xl overflow-hidden shadow-2xl z-10 relative flex flex-col border border-white/5 bg-black/40 backdrop-blur-xl">
        {/* Header */}
        <div className="h-20 bg-black/20 border-b border-white/5 flex items-center px-8 justify-between backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Veo Expert</h1>
              <div className="flex items-center gap-2 text-xs text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                ONLINE
              </div>
            </div>
          </div>
          <div className="text-xs text-stone-500 font-mono hidden md:block">
            POWERED BY GOOGLE ADK & VEO
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 hover:scrollbar-thumb-white/20">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 
                ${msg.role === 'user' ? 'bg-stone-700' : 'bg-black/50 border border-white/10'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                {msg.text && (
                  <div className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                    ${msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-sm shadow-lg shadow-blue-900/20'
                      : 'bg-white/5 border border-white/5 text-stone-200 rounded-tl-sm backdrop-blur-sm'
                    } ${msg.isError ? 'bg-red-900/20 border-red-500/30 text-red-200' : ''}`}
                  >
                    {msg.text}
                  </div>
                )}
                {msg.image && (
                  <img
                    src={msg.image}
                    alt="User Upload"
                    className="max-w-[200px] rounded-xl border border-white/10 shadow-lg mt-2"
                  />
                )}

                {msg.video && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full aspect-video bg-black rounded-xl overflow-hidden border border-white/10 shadow-2xl mt-2 relative group"
                  >
                    <video
                      src={msg.video}
                      controls
                      autoPlay
                      loop
                      className="w-full h-full object-contain"
                    />
                    <div className="absolute top-3 left-3 px-3 py-1 bg-black/60 backdrop-blur-md rounded-full text-xs font-mono text-green-400 border border-green-500/20 flex items-center gap-2">
                      <Video className="w-3 h-3" /> GENERATED
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4"
            >
              <div className="w-10 h-10 rounded-full bg-black/50 border border-white/10 flex items-center justify-center shrink-0">
                <Loader2 className="w-5 h-5 animate-spin text-stone-500" />
              </div>
              <div className="bg-white/5 border border-white/5 text-stone-400 p-4 rounded-2xl rounded-tl-sm text-sm flex items-center gap-2">
                Thinking...
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-black/20 border-t border-white/5 backdrop-blur-md">
          <form onSubmit={handleSend} className="relative flex items-center gap-4">
            {/* Image Upload Input */}
            <input
              type="file"
              accept="image/*"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />

            {/* Left Controls */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className={`p-3 rounded-xl border transition-all ${attachment
                  ? 'bg-purple-500/20 border-purple-500 text-purple-400'
                  : 'bg-white/5 border-white/10 text-stone-400 hover:bg-white/10'
                  }`}
                title="Upload Image"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              {/* Magic Upload Button (Debug) */}
              <button
                type="button"
                onClick={async () => {
                  try {
                    const res = await axios.get('/api/debug/cat_image');
                    setAttachment(res.data.image_base64);
                  } catch (e) {
                    console.error("Failed to load debug image", e);
                  }
                }}
                className="p-3 rounded-xl border bg-white/5 border-white/10 text-stone-400 hover:bg-white/10 hover:text-yellow-400 transition-all"
                title="Simulate Upload (Cat)"
              >
                <Sparkles className="w-5 h-5" />
              </button>

              {/* Duration Dropdown */}
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="p-3 rounded-xl border bg-white/5 border-white/10 text-stone-400 hover:bg-white/10 focus:outline-none focus:border-blue-500 appearance-none cursor-pointer"
                title="Duration"
              >
                <option value={5}>5s</option>
                <option value={10}>10s</option>
              </select>
            </div>

            {/* Valid Input Field */}
            <div className="relative w-full">
              {attachment && (
                <div className="absolute bottom-full left-0 mb-4 p-2 bg-black/80 backdrop-blur-md border border-white/10 rounded-xl flex items-center gap-3">
                  <img
                    src={`data:image/png;base64,${attachment}`}
                    alt="Preview"
                    className="w-12 h-12 object-cover rounded-lg border border-white/20"
                  />
                  <button
                    type="button"
                    onClick={() => setAttachment(null)}
                    className="p-1 hover:bg-white/20 rounded-full text-stone-400 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={attachment ? "Describe how to animate this image..." : "Describe your video idea..."}
                disabled={loading}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-6 pr-14 text-white placeholder:text-stone-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:bg-white/10 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={(!input.trim() && !attachment) || loading}
              className="absolute right-2 p-2 bg-blue-600 rounded-lg hover:bg-blue-500 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-white shadow-lg shadow-blue-500/20"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </div>
      </div>

      {/* Logs Overlay Panel (conditionally rendered) */}
      <AnimatePresence>
        {selectedAgentLogs && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="w-96 h-[800px] glass rounded-3xl flex flex-col shadow-2xl z-20 overflow-hidden border border-white/5 bg-[#0a0a0a]"
          >
            <div className="h-14 border-b border-white/10 flex items-center justify-between px-4 bg-stone-900">
              <div className="flex items-center gap-2 font-mono text-sm text-green-400">
                <Terminal className="w-4 h-4" />
                {parseAgentName(selectedAgentLogs.resource_name)}
              </div>
              <button onClick={() => setSelectedAgentLogs(null)} className="p-1 hover:bg-white/10 rounded-md text-stone-400">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 p-4 font-mono text-xs text-stone-300 overflow-y-auto whitespace-pre-wrap leading-relaxed">
              {/* Native live inference logs require Cloud Logging integration, but we can display deployment metadata/status for now */}
              <div>[SYSTEM] Connected to Agent Engine Logging Console.</div>
              <div className="text-stone-500 mt-2">Resource: {selectedAgentLogs.resource_name}</div>
              <div className="text-stone-500 text-purple-400 mt-2">Display Name: {selectedAgentLogs.display_name}</div>
              <div className="mt-4 text-green-400">Agent is ONLINE and receiving requests.</div>
              <div className="mt-2">Waiting for new events...</div>

              <div className="mt-8 p-3 rounded-lg bg-blue-900/20 border border-blue-500/20 text-blue-200">
                <span className="font-bold">ADK Deployment Successful</span>
                <br />
                Requirements: google-cloud-aiplatform[adk,agent_engines], google-genai
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Deployment Logs Overlay Panel (conditionally rendered) */}
      <AnimatePresence>
        {(deployStatus.is_deploying || deployStatus.error || (deployStatus.logs.length > 0 && !selectedAgentLogs)) && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="w-96 h-[800px] glass rounded-3xl flex flex-col shadow-2xl z-20 overflow-hidden border border-white/5 bg-[#0a0a0a]"
          >
            <div className="h-14 border-b border-white/10 flex items-center justify-between px-4 bg-stone-900">
              <div className="flex items-center gap-2 font-mono text-sm text-blue-400 w-full">
                <Loader2 className={`w-4 h-4 ${deployStatus.is_deploying ? 'animate-spin' : ''}`} />
                Deployment Progress
                {(deployStatus.is_deploying || deployTimeElapsed > 0) && (
                  <span className="ml-auto text-stone-500 text-xs mt-0.5">
                    {Math.floor(deployTimeElapsed / 60)}:{(deployTimeElapsed % 60).toString().padStart(2, '0')}
                  </span>
                )}
              </div>
              {!deployStatus.is_deploying && (
                <button onClick={() => setDeployStatus({ is_deploying: false, logs: [], error: null })} className="p-1 hover:bg-white/10 rounded-md text-stone-400">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <div className="flex-1 p-4 font-mono text-xs text-stone-400 overflow-y-auto whitespace-pre-wrap leading-relaxed flex flex-col-reverse">
              <div>
                {deployStatus.logs.map((log, i) => (
                  <div key={i} className="mb-1 leading-tight border-b border-white/5 pb-1">{log}</div>
                ))}
                {deployStatus.error && <div className="text-red-400 mt-4 font-bold">ERROR: {deployStatus.error}</div>}
                {!deployStatus.is_deploying && !deployStatus.error && deployStatus.logs.length > 0 && (
                  <div className="text-green-400 mt-4 font-bold">Deployment Complete!</div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  )
}

export default App
