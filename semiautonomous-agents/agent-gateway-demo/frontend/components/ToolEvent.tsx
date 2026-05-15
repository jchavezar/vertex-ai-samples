"use client";
import { useState } from "react";

export function ToolEvent({ kind, name, body }: { kind: "call" | "result"; name: string; body: any }) {
  const [open, setOpen] = useState(false);
  const color = kind === "call" ? "border-amber-500/40 bg-amber-500/5" : "border-emerald-500/40 bg-emerald-500/5";
  const label = kind === "call" ? "tool call" : "tool result";
  return (
    <div className={`mt-1 rounded border ${color} px-2 py-1 text-xs`}>
      <button onClick={() => setOpen(o => !o)} className="text-left w-full">
        <span className="font-mono opacity-60">{label}</span>
        <span className="mx-1 opacity-40">·</span>
        <span className="font-mono">{name}</span>
        <span className="ml-2 opacity-40">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <pre className="mt-1 whitespace-pre-wrap break-all opacity-80">
          {typeof body === "string" ? body : JSON.stringify(body, null, 2)}
        </pre>
      )}
    </div>
  );
}
