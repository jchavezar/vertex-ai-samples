
import React, { useRef, useEffect } from 'react';
import { ChatMessage, MessageAuthor, GroundingChunk } from '../types';

interface ChatMessageDisplayProps {
  messages: ChatMessage[];
}

export const ChatMessageDisplay: React.FC<ChatMessageDisplayProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const getMessageBubbleClasses = (author: MessageAuthor) => {
    switch (author) {
      case 'user':
        return 'bg-chat-user-bg text-chat-user-text self-end rounded-t-xl rounded-l-xl';
      case 'ai':
        return 'bg-chat-ai-bg text-chat-ai-text self-start rounded-t-xl rounded-r-xl';
      case 'system':
        return 'bg-transparent text-chat-system-text self-center text-xs italic text-center my-2 px-2 py-1';
      default:
        return 'bg-chat-ai-bg text-chat-ai-text self-start';
    }
  };

  const renderGroundingSources = (groundingChunks: GroundingChunk[] | undefined) => {
    if (!groundingChunks || groundingChunks.length === 0) return null;
    
    const webSources = groundingChunks.filter(chunk => chunk.web && chunk.web.uri);
    if (webSources.length === 0) return null;

    return (
      <div className="mt-2 pt-2 border-t border-chat-ai-text/20">
        <p className="text-xs font-semibold mb-1 text-chat-ai-text/80">Sources:</p>
        <ul className="list-disc list-inside space-y-1">
          {webSources.map((chunk, index) => (
            <li key={`grounding-${index}`} className="text-xs">
              <a 
                href={chunk.web!.uri} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-dj-blue hover:underline"
                title={chunk.web!.uri}
              >
                {chunk.web!.title || chunk.web!.uri}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="flex-grow p-4 md:p-6 space-y-3 overflow-y-auto"> 
      {messages.map((msg) => (
        <div 
          key={msg.id} 
          className={`flex ${msg.author === 'user' ? 'justify-end' : msg.author === 'system' ? 'justify-center' : 'justify-start'}`}
          aria-live={msg.author === 'ai' ? 'polite' : undefined}
        >
          <div
            className={`max-w-[80%] md:max-w-[70%] p-3 shadow-sm break-words ${getMessageBubbleClasses(msg.author)}`}
          >
            <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
            {msg.author === 'ai' && msg.groundingMetadata && renderGroundingSources(msg.groundingMetadata.groundingChunks)}
            {msg.author !== 'system' && (
               <p className={`text-xs mt-1.5 ${msg.author === 'user' ? 'text-chat-user-text/70 text-right' : 'text-chat-ai-text/70 text-left'}`}>
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};