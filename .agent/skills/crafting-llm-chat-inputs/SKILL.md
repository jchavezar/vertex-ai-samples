---
name: crafting-llm-chat-inputs
description: Enforces the universal zero-glitch, auto-expanding LLM chat input standard. Use whenever creating, styling, refactoring, or reviewing chat interfaces, prompt boxes, textareas, message docks, or conversational inputs in React, Next.js, Vue, Svelte, or HTML/JS.
---

# Universal LLM Chat Input Mechanics

## When to use this skill
- Building or modifying chat interfaces, prompt bars, or messaging text inputs.
- Fixing textarea vertical scrollbar glitches, clipped placeholder text, or awkward fixed-height text boxes.
- Ensuring dynamic auto-expansion on newlines (`\n` or `Shift+Enter`) up to a max-height ceiling before scrolling.

---

## 1. The Core Problems with Standard `<textarea>` in LLM UIs
1. **Premature Scrollbars**: Default browser `rows={1}` with padding causes multiline placeholders or wrapped text to trigger an ugly vertical scrollbar thumb.
2. **Missing Reactive Height Sync**: Relying only on `onChange` fails on initial mount or when clearing text via state (`setInput('')`).
3. **No Max-Height Ceiling**: The textarea either grows infinitely off-screen or stays fixed and requires scrolling for every 2-line prompt.
4. **Broken Keyboard Shortcuts**: `Enter` should submit (unless empty/streaming), while `Shift+Enter` MUST insert a newline and seamlessly expand the container height.

---

## 2. Universal React Pattern (Production Ready)

### Hook / Auto-Resize Implementation
```tsx
import React, { useEffect, useRef, useState } from 'react';

export const PromptInput = ({ onSend, isStreaming }: { onSend: (text: string) => void; isStreaming: boolean }) => {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Dynamic height synchronization on EVERY text change, mount, or clear
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height temporarily to accurately measure scrollHeight
    textarea.style.height = 'auto';
    
    const minHeight = 44;
    const maxHeight = 180;
    const scrollHeight = textarea.scrollHeight;
    
    // Auto-grow height between min and max bounds
    const newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight));
    textarea.style.height = `${newHeight}px`;
    
    // Only show scrollbar if content exceeds max height
    textarea.style.overflowY = scrollHeight > maxHeight ? 'auto' : 'hidden';
  }, [prompt]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (prompt.trim() && !isStreaming) {
        onSend(prompt.trim());
        setPrompt('');
      }
    }
  };

  return (
    <div className="relative rounded-2xl border border-slate-300 bg-white shadow-xs focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
      <textarea
        ref={textareaRef}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message or press Shift+Enter for a newline..."
        rows={1}
        disabled={isStreaming}
        className="w-full resize-none bg-transparent px-4 pt-3.5 pb-2 text-sm leading-relaxed text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-60 overflow-hidden block"
        style={{ minHeight: '44px', maxHeight: '180px' }}
      />
      {/* Action Footer Bar */}
      <div className="px-3 pb-2.5 flex items-center justify-between">
        <span className="text-xs text-slate-400">Shift+Enter for newline</span>
        <button
          onClick={() => {
            if (prompt.trim() && !isStreaming) {
              onSend(prompt.trim());
              setPrompt('');
            }
          }}
          disabled={!prompt.trim() || isStreaming}
          className="px-3 py-1.5 rounded-xl bg-blue-600 text-white font-bold text-xs disabled:opacity-30 transition-all"
        >
          Send
        </button>
      </div>
    </div>
  );
};
```

---

## 3. Universal Vanilla JavaScript / HTML Pattern

```html
<div class="chat-input-wrapper">
  <textarea id="chatInput" placeholder="Ask a question..." rows="1"></textarea>
  <button id="sendBtn">Send</button>
</div>

<script>
  const textarea = document.getElementById('chatInput');
  const maxHeight = 180;
  const minHeight = 44;

  function autoResize() {
    textarea.style.height = 'auto';
    const scrollHeight = textarea.scrollHeight;
    textarea.style.height = Math.max(minHeight, Math.min(scrollHeight, maxHeight)) + 'px';
    textarea.style.overflowY = scrollHeight > maxHeight ? 'auto' : 'hidden';
  }

  textarea.addEventListener('input', autoResize);
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Execute send action
      sendMessage(textarea.value);
      textarea.value = '';
      autoResize();
    }
  });

  // Initial trigger on load to avoid placeholder overflow
  autoResize();
</script>
```

---

## 4. Mandatory Checklist for LLM Input Boxes
- [ ] **No Default Browser Scrollbar**: Textarea MUST have `overflow-hidden` until content exceeds `maxHeight`.
- [ ] **Reactive Height Sync**: `style.height` MUST be synchronized inside a reactive effect on `value` state changes (not just `input` event).
- [ ] **Reset on Clear**: After sending a prompt, height MUST reset to initial single-line `minHeight`.
- [ ] **Keyboard Behavior**: `Enter` sends message (if not empty/streaming); `Shift+Enter` inserts `\n` without submitting and smoothly auto-expands the container.
- [ ] **No Resize Gripper**: Always specify `resize-none` in Tailwind or `resize: none` in CSS.
- [ ] **Line-Height & Padding**: Always use `leading-relaxed` or `line-height: 1.5` with balanced top/bottom padding to prevent glyph clipping.
