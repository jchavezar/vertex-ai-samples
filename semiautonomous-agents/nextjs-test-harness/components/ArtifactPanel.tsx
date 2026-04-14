"use client";

import { X, Maximize2, Copy, Check, Code, FileText, Play } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Artifact {
  type: string;
  content: string;
}

export function ArtifactPanel({ 
  artifact, 
  onClose 
}: { 
  artifact: Artifact; 
  onClose: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const [output, setOutput] = useState<string | null>(null);
  const [executing, setExecuting] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExecute = async () => {
    setExecuting(true);
    setOutput(null);
    try {
      const response = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: artifact.content }),
      });
      const data = await response.json();
      setOutput(data.stdout || data.stderr || "Command executed successfully with no output.");
    } catch (e: any) {
      setOutput(`Execution failed: ${e.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white text-shroud-text">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-shroud-border">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-shroud-ash rounded-md">
            {artifact.type === "code" ? <Code size={16} /> : <FileText size={16} />}
          </div>
          <div>
            <h3 className="text-sm font-semibold">Artifact Preview</h3>
            <p className="text-[10px] text-shroud-subtle uppercase tracking-widest font-bold">Generated just now</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {artifact.type === "shell" && (
             <button 
              onClick={handleExecute}
              disabled={executing}
              className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-shroud-text text-white rounded-md hover:opacity-90 transition-all disabled:opacity-50"
            >
              {executing ? "Running..." : "Run Command"}
              {!executing && <Play size={12} />}
            </button>
          )}
          <button 
            onClick={handleCopy}
            className="p-2 hover:bg-shroud-ash rounded-md text-shroud-subtle transition-colors"
          >
            {copied ? <Check size={16} className="text-green-600" /> : <Copy size={16} />}
          </button>
          <button className="p-2 hover:bg-shroud-ash rounded-md text-shroud-subtle transition-colors">
            <Maximize2 size={16} />
          </button>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-shroud-ash rounded-md text-shroud-subtle transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8 font-mono text-sm leading-relaxed bg-[#fdfdfd]">
        <pre className="whitespace-pre-wrap">
          {artifact.content}
        </pre>
        {output && (
          <div className="mt-8 pt-8 border-t border-shroud-border">
            <div className="text-[10px] font-bold text-shroud-subtle uppercase tracking-widest mb-2">Execution Output</div>
            <pre className={cn(
              "p-4 bg-shroud-ash rounded-md whitespace-pre-wrap text-[11px] leading-tight",
              output.includes("failed") ? "text-red-600" : "text-shroud-text"
            )}>
              {output}
            </pre>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-shroud-border bg-white flex justify-end gap-2">
        <button className="px-3 py-1.5 text-xs font-medium bg-shroud-ash hover:bg-shroud-border rounded-md transition-colors">
          Download
        </button>
        <button className="px-3 py-1.5 text-xs font-medium bg-shroud-text text-white rounded-md hover:opacity-90 transition-opacity">
          Publish
        </button>
      </div>
    </div>
  );
}
