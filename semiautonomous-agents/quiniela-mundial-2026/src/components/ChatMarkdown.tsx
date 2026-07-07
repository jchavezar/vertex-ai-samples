"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

const components: Components = {
  p: ({ children }) => <p className="my-1.5 first:mt-0 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-[var(--ink)]">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="underline decoration-[var(--accent-violet)]/40 underline-offset-2 hover:decoration-[var(--accent-violet)] hover:text-[var(--accent-violet)] break-words"
    >
      {children}
    </a>
  ),
  ul: ({ children }) => <ul className="my-1.5 ml-4 list-disc space-y-0.5 marker:text-[var(--ink-muted)]">{children}</ul>,
  ol: ({ children }) => <ol className="my-1.5 ml-4 list-decimal space-y-0.5 marker:text-[var(--ink-muted)]">{children}</ol>,
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  h1: ({ children }) => <h3 className="font-display font-bold text-[15px] mt-2 mb-1">{children}</h3>,
  h2: ({ children }) => <h3 className="font-display font-bold text-[14px] mt-2 mb-1">{children}</h3>,
  h3: ({ children }) => <h4 className="font-display font-semibold text-[13px] mt-1.5 mb-1">{children}</h4>,
  hr: () => <hr className="my-2 border-[var(--hairline)]" />,
  blockquote: ({ children }) => (
    <blockquote className="my-2 border-l-2 border-[var(--accent-violet)]/40 pl-3 text-[var(--ink-soft)] italic">
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }) => {
    const isBlock = /language-/.test(className || "");
    if (isBlock) {
      return (
        <pre className="my-2 -mx-1 px-3 py-2 rounded-lg bg-[var(--ink)]/95 text-white text-[12px] leading-snug overflow-x-auto">
          <code className={className} {...props}>{children}</code>
        </pre>
      );
    }
    return (
      <code className="px-1 py-0.5 rounded bg-black/[0.06] text-[var(--ink)] text-[12.5px] font-mono break-words" {...props}>
        {children}
      </code>
    );
  },
  table: ({ children }) => (
    <div className="chat-md-table-wrap my-2.5 -mx-2 px-2 overflow-x-auto">
      <table className="chat-md-table w-full border-collapse rounded-xl overflow-hidden ring-1 ring-[var(--hairline)] bg-white shadow-sm">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-gradient-to-r from-[var(--accent-violet)]/12 via-white to-[var(--accent-mint)]/12 text-[var(--ink)]">
      {children}
    </thead>
  ),
  tbody: ({ children }) => <tbody className="divide-y divide-[var(--hairline)]">{children}</tbody>,
  tr: ({ children }) => <tr className="even:bg-black/[0.02] hover:bg-[var(--accent-violet)]/[0.04] transition-colors">{children}</tr>,
  th: ({ children, style }) => (
    <th
      style={style}
      className="text-left font-display font-semibold px-2 py-1.5 text-[10.5px] uppercase tracking-wider text-[var(--ink-soft)] border-b border-[var(--hairline)] leading-tight align-bottom"
    >
      {children}
    </th>
  ),
  td: ({ children, style }) => (
    <td style={style} className="px-2 py-1.5 align-top text-[var(--ink)] text-[12px] leading-snug tabular-nums [&_strong]:font-bold">
      {children}
    </td>
  ),
};

export function ChatMarkdown({ text }: { text: string }) {
  return (
    <div className="chat-md break-words">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {text}
      </ReactMarkdown>
    </div>
  );
}
