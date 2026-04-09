import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Props {
  code: string;
  language: string;
}

export default function CodeBlock({ code, language }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block-wrapper">
      <button className="code-copy-btn" onClick={handleCopy}>
        {copied ? 'Copied!' : 'Copy'}
      </button>
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          borderRadius: '10px',
          fontSize: '13px',
          lineHeight: '1.5',
          padding: '16px',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
