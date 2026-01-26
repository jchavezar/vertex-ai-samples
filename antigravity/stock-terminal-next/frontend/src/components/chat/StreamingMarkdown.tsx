import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface StreamingMarkdownProps {
  content: string;
  isStreaming: boolean;
  className?: string;
}



const SCRAMBLE_CHARS = "ABCDEF0123456789!@#$%^&*()_+";

export const StreamingMarkdown: React.FC<StreamingMarkdownProps> = ({ content, isStreaming, className }) => {
  const [displayedContent, setDisplayedContent] = useState(isStreaming ? '' : content);
  const [scrambleSuffix, setScrambleSuffix] = useState('');
  
  // Use a ref to track the animation loop state
  const stateRef = useRef({
    displayedContent: isStreaming ? '' : content,
    targetContent: content,
    lastFrameTime: 0,
  });

  // Sync ref with props
  useEffect(() => {
    stateRef.current.targetContent = content;
    // If not streaming, align immediately
    if (!isStreaming) {
      setDisplayedContent(content);
      stateRef.current.displayedContent = content;
      setScrambleSuffix('');
    }
  }, [content, isStreaming]);

  useEffect(() => {
    if (!isStreaming) return;

    let animationFrameId: number;

    const animate = (time: number) => {
      const state = stateRef.current;
      const { displayedContent, targetContent, lastFrameTime } = state;

      // Calculate time delta
      const delta = time - lastFrameTime;
      
      // Target frame rate (e.g. 60fps -> 16ms)
      // We throttle slightly to create a "tech" feel, or just go smooth.
      // Let's go perfectly smooth but variable speed.
      
      if (displayedContent.length < targetContent.length) {
        // Determine catch-up speed
        const remaining = targetContent.length - displayedContent.length;
        
        // Dynamic Chunk Size: Faster if we are far behind
        // 1 char per frame if close
        // 3-5 chars per frame if far
        let charsToAdd = 1;
        if (remaining > 50) charsToAdd = 3;
        else if (remaining > 20) charsToAdd = 2;

        // Add text
        const nextContent = targetContent.substring(0, displayedContent.length + charsToAdd);
        state.displayedContent = nextContent;
        setDisplayedContent(nextContent);

        // Scramble Effect:
        // Generate 2-3 random chars to append
        let suffix = "";
        const suffixLen = Math.min(2, remaining);
        for (let i = 0; i < suffixLen; i++) {
          suffix += SCRAMBLE_CHARS[Math.floor(Math.random() * SCRAMBLE_CHARS.length)];
        }
        setScrambleSuffix(suffix);

      } else {
        // Done streaming
        setScrambleSuffix('');
      }

      state.lastFrameTime = time;
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrameId);
  }, [isStreaming]);

  return (
    <div className={`markdown-content relative leading-relaxed ${className || ''}`}>
      <div className="relative">
        {/* Render the stable markdown content */}
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {displayedContent}
        </ReactMarkdown>

        {/* 
            Premium Cursor & Scramble Effect 
            - Scramble text is slightly brighter/different color to simulate decryption.
            - Cursor has a "laser" glow.
        */}
        {isStreaming && displayedContent.length < content.length && (
            <span className="inline-flex items-center ml-0.5 align-baseline">
                {scrambleSuffix && (
                    <span className="text-cyan-400 opacity-80 font-mono text-xs mr-0.5 select-none blur-[0.5px]">
                        {scrambleSuffix}
                    </span>
                )}
                <span 
                    className="w-2.5 h-5 bg-[var(--brand)] inline-block align-middle animate-pulse shadow-[0_0_10px_var(--brand)]"
                    style={{ borderRadius: '1px' }}
                />
            </span>
        )}
      </div>
    </div>
  );
};
