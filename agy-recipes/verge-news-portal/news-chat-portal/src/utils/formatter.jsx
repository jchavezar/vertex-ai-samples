import React from 'react';

export function formatMarkdown(text) {
  if (!text) return "";

  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts.map((part, index) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const codeLines = part.slice(3, -3).trim().split('\n');
      let language = 'text';
      let code = part.slice(3, -3).trim();

      if (codeLines[0] && !codeLines[0].includes(' ') && codeLines[0].length < 10) {
        language = codeLines[0];
        code = codeLines.slice(1).join('\n');
      }

      return (
        <pre key={index}>
          <code className={`language-${language}`}>{code}</code>
        </pre>
      );
    }

    const lines = part.split('\n');
    let inList = false;
    let listItems = [];
    const elements = [];

    lines.forEach((line, lineIdx) => {
      const trimmedLine = line.trim();

      if (trimmedLine.startsWith('* ') || trimmedLine.startsWith('- ')) {
        inList = true;
        listItems.push(
          <li key={lineIdx}>
            {parseInlineFormatting(trimmedLine.substring(2))}
          </li>
        );
        return;
      }

      if (inList && !trimmedLine.startsWith('* ') && !trimmedLine.startsWith('- ')) {
        elements.push(<ul key={`list-${lineIdx}`}>{listItems}</ul>);
        listItems = [];
        inList = false;
      }

      if (trimmedLine === '') return;

      elements.push(
        <p key={lineIdx}>
          {parseInlineFormatting(line)}
        </p>
      );
    });

    if (inList && listItems.length > 0) {
      elements.push(<ul key={`list-end`}>{listItems}</ul>);
    }

    return <React.Fragment key={index}>{elements}</React.Fragment>;
  });
}

function parseInlineFormatting(text) {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={idx}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}
