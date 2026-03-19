import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, X, Minimize2, Maximize2, Glasses } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ChatOverlay({ logs = [] }) {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [isMaximized, setIsMaximized] = useState(false);
    const [messages, setMessages] = useState([
        { sender: 'ai', text: "I've been watching you, Cadet. I am Agent Smith. I am parsing your live telemetry stream. It seems you are attempting to authenticate... Let's see how that works out." }
    ]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const chatEndRef = useRef(null);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    // Check if grounding data is present in logs
    const hasGroundedData = logs.some(log => {
        const logStr = typeof log === 'string' ? log : JSON.stringify(log);
        return logStr.includes('StreamAssist') || logStr.includes('Packet') || logStr.includes('Received Chunk');
    });

    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isStreaming) return;

        const userMessage = input.trim();
        setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
        setInput('');
        setIsStreaming(true);
        
        // Add placeholder for AI
        setMessages(prev => [...prev, { sender: 'ai', text: '' }]);

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userMessage,
                    context: logs
                })
            });

            if (!response.body) throw new Error('No response body');
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumText = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6).trim();
                        if (data.includes('[DONE]')) {
                            break;
                        }
                        accumText += data;
                        setMessages(prev => {
                            const newMessages = [...prev];
                            newMessages[newMessages.length - 1] = { sender: 'ai', text: accumText };
                            return newMessages;
                        });
                    }
                }
            }
        } catch (err) {
            setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = { sender: 'ai', text: `Error: ${err.message}` };
                return newMessages;
            });
        } finally {
            setIsStreaming(false);
        }
    };

    return (
        <>
            {/* Floating Button */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.button
                        onClick={() => setIsOpen(true)}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1.1, boxShadow: '0 0 25px rgba(0, 242, 254, 0.6)' }}
                        style={{
                            position: 'fixed', bottom: '2rem', right: '2rem',
                            width: '64px', height: '64px', borderRadius: '50%',
                            background: 'linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)',
                            display: 'flex', justifyContent: 'center', alignItems: 'center',
                            boxShadow: '0 4px 20px rgba(0, 242, 254, 0.3)', border: 'none',
                            cursor: 'pointer', zIndex: 50, color: 'black'
                        }}
                    >
                        <Bot size={40} />
                    </motion.button>
                )}
            </AnimatePresence>

            {/* Chat Container */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 50 }}
                        animate={{ 
                            opacity: 1, 
                            scale: 1,
                            y: 0,
                            width: isMaximized ? '85vw' : '680px',
                            height: isMinimized ? '55px' : (isMaximized ? '85vh' : '650px'),
                            bottom: isMaximized ? '7.5vh' : '2rem',
                            right: isMaximized ? '7.5vw' : '2rem',
                        }}
                        exit={{ opacity: 0, scale: 0.8, y: 50 }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        style={{
                            position: 'fixed',
                            background: '#0d0d14', border: '1px solid rgba(0, 242, 254, 0.15)',
                            borderRadius: '16px', display: 'flex', flexDirection: 'column',
                            overflow: 'hidden', boxShadow: '0 20px 50px rgba(0,0,0,0.7)',
                            zIndex: 50,
                            transformOrigin: 'bottom right'
                        }}
                    >
                        {/* Header */}
                        <div style={{
                            padding: '1rem', background: 'rgba(0, 242, 254, 0.03)',
                            borderBottom: '1px solid rgba(0, 242, 254, 0.1)',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                <motion.div 
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ repeat: Infinity, duration: 2 }}
                                    style={{ 
                                        width: '10px', height: '10px', borderRadius: '50%', 
                                        background: '#00f2fe', boxShadow: '0 0 8px #00f2fe' 
                                    }} 
                                />
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                        <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#00f2fe', letterSpacing: '0.5px' }}>Agent Smith</h3>
                                        <Glasses size={18} style={{ color: '#00f2fe' }} />
                                    </div>
                                    {hasGroundedData && (
                                        <span style={{ fontSize: '0.7rem', color: '#22c55e', display: 'flex', alignItems: 'center', gap: '3px', marginTop: '1px' }}>
                                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }} />
                                            Telemetry Grounded
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '0.8rem', color: '#94a3b8' }}>
                                <button onClick={() => { setIsMaximized(!isMaximized); setIsMinimized(false); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>
                                    {isMaximized ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
                                </button>
                                <button onClick={() => { setIsMinimized(!isMinimized); setIsMaximized(false); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>
                                    <Minimize2 size={18} style={{ transform: isMinimized ? 'rotate(180deg)' : 'none' }} />
                                </button>
                                <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>
                                    <X size={20} />
                                </button>
                            </div>
                        </div>

                        {/* Body */}
                        {!isMinimized && (
                            <>
                                <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {messages.map((msg, i) => (
                                        <div key={i} style={{
                                            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                                            maxWidth: msg.sender === 'user' ? '75%' : '85%',
                                            padding: '1rem',
                                            borderRadius: '12px',
                                            background: msg.sender === 'user' ? '#1e293b' : 'rgba(0, 242, 254, 0.04)',
                                            border: msg.sender === 'user' ? '1px solid #334155' : '1px solid rgba(0, 242, 254, 0.08)',
                                            color: '#e2e8f0',
                                            fontSize: '0.95rem',
                                            lineHeight: '1.5',
                                            boxShadow: msg.sender === 'ai' ? '0 2px 10px rgba(0,0,0,0.2)' : 'none'
                                        }}>
                                            {msg.text || (isStreaming && i === messages.length - 1 && (
                                                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                                                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#00f2fe', animation: 'bounce 0.6s infinite alternate' }}></span>
                                                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#00f2fe', animation: 'bounce 0.6s infinite alternate 0.2s' }}></span>
                                                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#00f2fe', animation: 'bounce 0.6s infinite alternate 0.4s' }}></span>
                                                </div>
                                            ))}
                                        </div>
                                    ))}
                                    <div ref={chatEndRef} />
                                </div>

                                {/* Footer */}
                                <form onSubmit={handleSend} style={{
                                    padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)',
                                    display: 'flex', gap: '0.8rem', background: 'rgba(0,0,0,0.4)'
                                }}>
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        placeholder="Ask about telemetry packets..."
                                        disabled={isStreaming}
                                        style={{
                                            flexGrow: 1, padding: '0.75rem 1rem',
                                            background: 'rgba(255,255,255,0.03)',
                                            border: '1px solid rgba(0, 242, 254, 0.1)',
                                            borderRadius: '8px', color: 'white', fontSize: '0.95rem',
                                            outline: 'none'
                                        }}
                                    />
                                    <button type="submit" disabled={isStreaming} style={{
                                        background: 'linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)', 
                                        color: 'black',
                                        width: '45px', height: '45px', borderRadius: '8px',
                                        display: 'flex', justifyContent: 'center', alignItems: 'center',
                                        border: 'none', cursor: 'pointer',
                                        boxShadow: '0 2px 10px rgba(0, 242, 254, 0.3)',
                                        transition: 'transform 0.2s',
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                    onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                    >
                                        <Send size={20} style={{ marginLeft: '2px' }} />
                                    </button>
                                </form>
                            </>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
            <style>{`
                @keyframes bounce {
                    to { transform: translateY(-4px); opacity: 0.5; }
                }
            `}</style>
        </>
    );
}
