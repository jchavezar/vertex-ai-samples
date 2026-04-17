import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

function InputBar() {
  const [input, setInput] = useState('');
  const sendMessage = useChatStore((s) => s.sendMessage);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [isStreaming]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    sendMessage(trimmed);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="input-bar">
      <span className="input-prompt">{'> '}</span>
      <input
        ref={inputRef}
        className="input-field"
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="..."
        disabled={isStreaming}
        autoFocus
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck={false}
      />
      <button
        className="input-send"
        onClick={handleSubmit}
        disabled={isStreaming || !input.trim()}
      >
        [send]
      </button>
    </div>
  );
}

export default InputBar;
