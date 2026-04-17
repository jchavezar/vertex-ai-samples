import { useEffect, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import MessageBubble from './MessageBubble';
import ThinkingState from './ThinkingState';

const BANNER = `
  ┌─────────────────────────────┐
  │        sockagent v0.1       │
  │   vertex ai terminal chat   │
  └─────────────────────────────┘`;

function ChatView() {
  const messages = useChatStore((s) => s.messages);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const streamingContent = useChatStore((s) => s.streamingContent);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="chat-view">
      {messages.length === 0 && !isStreaming ? (
        <div className="chat-empty">
          <pre>{BANNER}</pre>
          <span className="chat-empty-hint">type a message to begin</span>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isStreaming && streamingContent && (
            <div className="message message-assistant">
              <span className="message-prefix">{'< '}</span>
              <span className="message-content">
                {streamingContent}
                <span className="streaming-cursor">&nbsp;</span>
              </span>
            </div>
          )}
          {isStreaming && !streamingContent && <ThinkingState />}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}

export default ChatView;
