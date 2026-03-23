import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Table, Maximize2, X } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
  chatMode?: 'default' | 'wide' | 'overlay' | string;
}

const TableWithOverlay = ({ children, chatMode, ...props }: { children: React.ReactNode, chatMode?: string, [key: string]: unknown }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (chatMode === 'default') {
    return (
      <>
        <div style={{ margin: '16px 0', padding: '12px 16px', border: '1px solid var(--internal-glass-border)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255,255,255,0.05)' }}>
          <span style={{ fontSize: '0.9rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Table size={16} color="var(--internal-green)" /> Data Table
          </span>
          <button 
            onClick={() => setIsOpen(true)} 
            style={{ 
              padding: '6px 12px', background: 'var(--internal-green)', color: 'white', border: 'none', 
              borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
              display: 'flex', alignItems: 'center'
            }}
          >
            <Maximize2 size={14} style={{ marginRight: '6px' }} />
            Expand Table
          </button>
        </div>
        
        {isOpen && createPortal(
          <div className="table-overlay-modal" onClick={() => setIsOpen(false)}>
            <div className="table-overlay-content" onClick={e => e.stopPropagation()}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--internal-border)', paddingBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Table size={18} color="var(--internal-green)" /> Detailed Data View
                </h3>
                <button 
                  onClick={() => setIsOpen(false)} 
                  style={{ background: 'transparent', border: 'none', color: 'var(--internal-grey)', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '4px' }}
                  onMouseOver={(e: React.MouseEvent<HTMLButtonElement>) => e.currentTarget.style.background = 'rgba(0,0,0,0.05)'}
                  onMouseOut={(e: React.MouseEvent<HTMLButtonElement>) => e.currentTarget.style.background = 'transparent'}
                >
                  <X size={20} />
                </button>
              </div>
              <div className="premium-table-wrapper" style={{ margin: 0, maxHeight: 'calc(80vh - 60px)', overflowY: 'auto', border: 'none', boxShadow: 'none' }}>
                <table className="premium-table" {...props}>{children}</table>
              </div>
            </div>
          </div>,
          document.getElementById('portal-root')!
        )}
      </>
    );
  }

  // Not default mode, or already expanded
  return (
    <div className="premium-table-wrapper">
      <table className="premium-table" {...props}>{children}</table>
    </div>
  );
};

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, chatMode = 'default' }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        table: ({ children, ...props }) => (
          <TableWithOverlay chatMode={chatMode} {...props}>
            {children}
          </TableWithOverlay>
        ),
        thead: ({ ...props }) => (
          <thead className="premium-thead" {...props} />
        ),
        th: ({ ...props }) => (
          <th className="premium-th" {...props} />
        ),
        td: ({ ...props }) => (
          <td className="premium-td" {...props} />
        ),
        tbody: ({ ...props }) => (
          <tbody className="premium-tbody" {...props} />
        )
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
