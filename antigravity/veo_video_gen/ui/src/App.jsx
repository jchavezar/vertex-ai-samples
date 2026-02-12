
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Play, Loader2, Sparkles, Film, Send, User, Bot, Video, Paperclip, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [attachment, setAttachment] = useState(null); // base64 string
  const [duration, setDuration] = useState(5);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(uuidv4());
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    <div className="min-h-screen bg-cave-950 flex flex-col items-center justify-center p-4 text-white relative overflow-hidden font-sans">
      {/* Background Ambient Effects */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-900/20 rounded-full blur-[100px]" />
      </div>

      <div className="max-w-4xl w-full h-[800px] glass rounded-3xl overflow-hidden shadow-2xl z-10 relative flex flex-col">
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
    </div>
  )
}

export default App
