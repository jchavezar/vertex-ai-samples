import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { MessageItem } from './components/MessageItem';
import { ChatSuggestions } from './components/ChatSuggestions';
import { ChatInput } from './components/ChatInput';
import { Message, ModelInfo, ChatConfig, GroundingData } from './types/chat';
import { fetchModels, streamChatMessage, resetSession } from './services/api';

const DEFAULT_INSTRUCTION =
  'Eres un asistente virtual inteligente, empático, preciso y profesional creado con Google ADK (Agent Development Kit). Responde siempre de forma estructurada, clara y con un tono amable. Utiliza formato Markdown.';

export const App: React.FC = () => {
  const [userId] = useState(() => `user_${Math.random().toString(36).substring(2, 9)}`);
  const [sessionId, setSessionId] = useState(() => `sess_${Math.random().toString(36).substring(2, 9)}`);
  
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [config, setConfig] = useState<ChatConfig>({
    model: 'gemini-2.5-flash',
    instruction: DEFAULT_INSTRUCTION,
    enableSearch: false
  });

  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const abortStreamRef = useRef<(() => void) | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Load models on initial render
  useEffect(() => {
    fetchModels().then((data) => {
      setModels(data.models);
      if (data.default) {
        setConfig((prev) => ({ ...prev, model: data.default }));
      }
    });
  }, []);

  // Auto-scroll on new messages or streaming chunks
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const userMessage: Message = {
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    const assistantMsgId = `msg_asst_${Date.now()}`;
    const assistantPlaceholder: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };

    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setIsStreaming(true);

    let accumulatedContent = '';
    let currentGrounding: GroundingData | undefined = undefined;

    const stopFn = await streamChatMessage({
      message: text,
      userId,
      sessionId,
      model: config.model,
      instruction: config.instruction,
      enableSearch: config.enableSearch,
      onChunk: (chunk: string) => {
        accumulatedContent += chunk;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? { ...msg, content: accumulatedContent, isStreaming: true, activeTool: undefined }
              : msg
          )
        );
      },
      onToolCall: (toolName: string) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId ? { ...msg, activeTool: toolName } : msg
          )
        );
      },
      onGrounding: (data: GroundingData) => {
        currentGrounding = data;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId ? { ...msg, grounding: data } : msg
          )
        );
      },
      onDone: () => {
        setIsStreaming(false);
        abortStreamRef.current = null;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: accumulatedContent || '_(Respuesta completada)_',
                  isStreaming: false,
                  activeTool: undefined,
                  grounding: currentGrounding
                }
              : msg
          )
        );
      },
      onError: (errMessage: string) => {
        setIsStreaming(false);
        abortStreamRef.current = null;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: `Error al generar respuesta: ${errMessage}`,
                  isStreaming: false,
                  error: true,
                  activeTool: undefined
                }
              : msg
          )
        );
      }
    });

    abortStreamRef.current = stopFn;
  };

  const handleStopStreaming = () => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
      setIsStreaming(false);
    }
  };

  const handleResetSession = () => {
    if (isStreaming) handleStopStreaming();
    resetSession(userId, sessionId);
    setSessionId(`sess_${Math.random().toString(36).substring(2, 9)}`);
    setMessages([]);
  };

  const activeModelInfo = models.find((m) => m.id === config.model);

  return (
    <div className="flex h-screen bg-[#ffffff] overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        models={models}
        config={config}
        onChangeConfig={(newCfg) => setConfig((prev) => ({ ...prev, ...newCfg }))}
        onResetSession={handleResetSession}
        messageCount={messages.length}
        sessionId={sessionId}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#ffffff] h-full">
        <Header
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          activeModel={activeModelInfo}
          isSearchEnabled={config.enableSearch}
        />

        {/* Messages Stream Container */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 flex flex-col justify-between">
          <div className="max-w-3xl w-full mx-auto flex-1 flex flex-col justify-start">
            {messages.length === 0 ? (
              <ChatSuggestions onSelectPrompt={handleSendMessage} />
            ) : (
              <div className="py-2 space-y-1">
                {messages.map((msg) => (
                  <MessageItem key={msg.id} message={msg} />
                ))}
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>
        </main>

        {/* Input Bar */}
        <div className="bg-white/80 backdrop-blur-xs pt-2">
          <ChatInput
            onSendMessage={handleSendMessage}
            onStopStreaming={handleStopStreaming}
            isStreaming={isStreaming}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
