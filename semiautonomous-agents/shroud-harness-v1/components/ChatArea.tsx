"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { Plus, ChevronDown, Mic, ArrowRight, Loader2, Copy, ThumbsUp, ThumbsDown, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { HarnessEngine, HarnessState } from "@/lib/harness";
import { FlowerIcon } from "./FlowerIcon";

interface Message {
  role: "user" | "assistant";
  content: string;
  thought?: string;
  isStreaming?: boolean;
}

export function ChatArea({ 
  onNewArtifact, 
  isArtifactOpen 
}: { 
  onNewArtifact: (type: string, content: string) => void;
  isArtifactOpen: boolean;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [harnessState, setHarnessState] = useState<HarnessState>("idle");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const engine = useMemo(() => new HarnessEngine(setHarnessState), []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || harnessState !== "idle") return;

    const userMsg: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    const history = messages.map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    let fullContent = "";
    await engine.process(input, history, (chunk) => {
      fullContent += chunk;
      
      const thoughtMatch = fullContent.match(/<thought>([\s\S]*?)<\/thought>/);
      const artifactMatch = fullContent.match(/<artifact type='(.*?)' title='(.*?)'>([\s\S]*?)<\/artifact>/);

      if (artifactMatch) {
         onNewArtifact(artifactMatch[1], artifactMatch[3].trim());
      }

      setMessages(prev => {
        const newMsgs = [...prev];
        const last = newMsgs[newMsgs.length - 1];
        last.content = fullContent.replace(/<thought>[\s\S]*?<\/thought>/g, "").replace(/<artifact[\s\S]*?<\/artifact>/g, "");
        last.thought = thoughtMatch ? thoughtMatch[1].trim() : undefined;
        return newMsgs;
      });
    });

    setMessages(prev => {
      const newMsgs = [...prev];
      newMsgs[newMsgs.length - 1].isStreaming = false;
      return newMsgs;
    });
  };

  return (
    <div className={cn(
      "flex flex-col flex-1 h-full transition-all duration-500 ease-in-out bg-[#212121]",
      isArtifactOpen ? "max-w-[50%]" : "max-w-4xl mx-auto w-full"
    )}>
      {/* Message Thread */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-24 space-y-16 no-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full space-y-8 animate-in fade-in zoom-in duration-1000">
            <FlowerIcon />
            <h1 className="text-5xl font-serif text-[#ececec] tracking-tight font-medium opacity-90">Evening, Jesus</h1>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div 
              key={i} 
              className={cn(
                "flex flex-col gap-6 animate-shroud-chat",
                msg.role === "user" ? "items-end" : "items-start"
              )}
            >
               {msg.role === "assistant" && <FlowerIcon isThinking={msg.isStreaming} />}
              
               <div className={cn(
                "max-w-[90%] text-[19px] leading-relaxed",
                msg.role === "user" 
                  ? "bg-[#2f2f2f] text-white p-5 rounded-[24px] shadow-sm" 
                  : "bg-transparent text-[#ececec] font-serif font-light tracking-normal"
              )}>
                {msg.content}
                {msg.isStreaming && <span className="inline-block w-1.5 h-5 bg-[#d97757] ml-2 animate-pulse rounded-full" />}
              </div>

              {msg.role === "assistant" && !msg.isStreaming && (
                <div className="flex items-center gap-6 text-[#9b9b9b] ml-1">
                   <Copy size={16} className="hover:text-white cursor-pointer transition-colors" />
                   <ThumbsUp size={16} className="hover:text-white cursor-pointer transition-colors" />
                   <ThumbsDown size={16} className="hover:text-white cursor-pointer transition-colors" />
                   <RotateCcw size={16} className="hover:text-white cursor-pointer transition-colors" />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Floating Input Harness */}
      <div className="p-8 pb-12">
        <div className="shroud-floating-harness relative max-w-2xl mx-auto border border-[#343434] rounded-[28px] p-4 transition-all duration-300">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend())}
            placeholder="How can I help you today?"
            className="w-full bg-transparent border-none focus:ring-0 focus:outline-none resize-none py-2 px-3 text-[19px] text-white placeholder-[#9b9b9b] max-h-64 overflow-y-auto"
          />
          <div className="flex items-center justify-between mt-5 px-1">
             <div className="flex items-center gap-1">
                <button className="p-2.5 hover:bg-[#3d3d3d] rounded-full transition-colors text-[#9b9b9b]">
                   <Plus size={22} />
                </button>
             </div>
             <div className="flex items-center gap-4 bg-[#212121]/50 p-1.5 px-4 rounded-full border border-[#343434]">
                <div className="flex items-center gap-2 text-[13px] text-[#9b9b9b] font-medium tracking-tight">
                   Sonnet 4.6 <ChevronDown size={14} />
                </div>
                <div className="h-4 w-[1px] bg-[#343434]" />
                <WaveformIcon />
             </div>
          </div>
          
          {input.trim() && (
             <button 
              onClick={handleSend}
              className="absolute right-7 bottom-7 p-2.5 bg-[#d97757] text-white rounded-full shadow-lg hover:scale-110 active:scale-95 transition-all"
            >
              <ArrowRight size={22} />
            </button>
          )}
        </div>
        <div className="text-[11px] text-center text-[#9b9b9b] mt-8 font-medium tracking-tight opacity-50">
           Claude is AI and can make mistakes. Please double-check responses.
        </div>
      </div>
    </div>
  );
}

function WaveformIcon() {
  return (
    <div className="flex items-end gap-[2px] h-3.5 px-1">
      <div className="w-[2px] h-[50%] bg-[#9b9b9b] rounded-full" />
      <div className="w-[2px] h-[100%] bg-[#9b9b9b] rounded-full" />
      <div className="w-[2px] h-[70%] bg-[#9b9b9b] rounded-full" />
      <div className="w-[2px] h-[90%] bg-[#9b9b9b] rounded-full" />
      <div className="w-[2px] h-[40%] bg-[#9b9b9b] rounded-full" />
    </div>
  );
}
