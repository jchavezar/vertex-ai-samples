import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Square } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  onStopStreaming?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStopStreaming,
  isStreaming,
  disabled
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isStreaming) {
      if (onStopStreaming) onStopStreaming();
      return;
    }
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto px-4 pb-4">
      <div className="relative flex items-end bg-[#ffffff] border border-[#dadce0] focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 rounded-2xl shadow-xs transition p-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isStreaming ? "Generando respuesta..." : "Escribe un mensaje para el agente Google ADK... (Shift + Enter para salto de línea)"}
          rows={1}
          disabled={disabled}
          className="flex-1 bg-transparent border-0 focus:outline-none resize-none text-sm text-[#202124] placeholder-[#5f6368] max-h-44 py-1.5 px-3"
        />

        <div className="shrink-0 pl-1">
          {isStreaming ? (
            <button
              type="button"
              onClick={onStopStreaming}
              className="w-9 h-9 bg-red-600 hover:bg-red-700 text-white rounded-xl flex items-center justify-center transition shadow-xs"
              title="Detener respuesta"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || disabled}
              className="w-9 h-9 bg-blue-600 hover:bg-blue-700 disabled:bg-[#f1f3f4] text-white disabled:text-[#dadce0] rounded-xl flex items-center justify-center transition shadow-xs cursor-pointer disabled:cursor-not-allowed"
              title="Enviar mensaje"
            >
              <ArrowUp className="w-5 h-5 stroke-[2.5]" />
            </button>
          )}
        </div>
      </div>
      <div className="text-[11px] text-center text-[#5f6368] mt-2">
        Google ADK 2.1.0 • Gemini 2.5 Flash / Gemini 3 en Vertex AI
      </div>
    </form>
  );
};
