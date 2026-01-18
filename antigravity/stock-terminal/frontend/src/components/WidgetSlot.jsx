import React, { useState } from 'react';
import { Sparkles, Loader, Maximize2, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const WidgetSlot = ({ 
  section, 
  override, 
  isAiMode, 
  originalComponent,
  onGenerate 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 1. AI Content State
  if (override && (override.loading || override.content)) {
    if (override.loading) {
      return (
        <div className="card" style={{
          minHeight: '200px', 
          display:'flex', 
          alignItems:'center', 
          justifyContent:'center',
          flexDirection: 'column',
          gap: '12px'
        }}>
           <Loader className="animate-spin" color="#004b87" size={24} />
           <span style={{color:'#004b87', fontSize:'13px', fontWeight: 500}}>
             Generative AI is analyzing {section}...
           </span>
        </div>
      );
    }

    // Extract only the first paragraph or block of text for the concise summary
    // This helps avoid showing raw tables in the small terminal widget slots
    const getConciseSummary = (content) => {
      if (!content) return "";
      const lines = content.split('\n');
      const paragraph = [];
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
          if (paragraph.length > 0) break; // End of first paragraph
          continue;
        }
        if (trimmed.startsWith('|') || trimmed.startsWith('-')) continue; // Skip table starts
        paragraph.push(line);
        if (paragraph.length > 3) break; // Limit to few lines
      }
      return paragraph.join('\n');
    };

    const summaryContent = getConciseSummary(override.content) || override.content.substring(0, 150) + '...';
    const isLongContent = override.content && override.content.length > 350;

    return (
      <>
        <div
          className="card widget-clickable"
          onClick={() => setIsModalOpen(true)}
          style={{ minHeight: '200px', maxHeight: '300px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
        >
          <div className="section-title" style={{ justifyContent: 'space-between', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={14} color="#004b87" />
              {section} (AI Analysis)
            </div>
            <div className="widget-expand-indicator">
              <Maximize2 size={10} />
              <span>Full View</span>
            </div>
          </div>
          <div className="markdown-body" style={{ fontSize: '11px', lineHeight: '1.5', color: '#333' }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{summaryContent}</ReactMarkdown>
          </div>
          {isLongContent && (
            <div style={{
              marginTop: 'auto',
              paddingTop: '8px',
              textAlign: 'center',
              fontSize: '10px',
              color: '#004b87',
              fontWeight: 600,
              borderTop: '1px solid #f0f0f0'
            }}>
              Click to see full analysis
            </div>
          )}
        </div>

        {/* Full View Modal */}
        {isModalOpen && (
          <div className="widget-modal-overlay" onClick={() => setIsModalOpen(false)}>
            <div className="widget-modal-content" onClick={e => e.stopPropagation()}>
              <div className="widget-modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Sparkles size={18} color="#004b87" />
                  <h2 style={{ fontSize: '16px', margin: 0 }}>{section} - Full AI Analysis</h2>
                </div>
                <button onClick={() => setIsModalOpen(false)} style={{ color: '#666' }}>
                  <X size={24} />
                </button>
              </div>
              <div className="widget-modal-body markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{override.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // 2. AI Mode Empty State (Prompt to Generate)
  if (isAiMode) {
    return (
      <div className="card" style={{
        minHeight: '200px', 
        display:'flex', 
        alignItems:'center', 
        justifyContent:'center',
        background: '#f8f9fa',
        border: '1px dashed #ced4da',
        boxShadow: 'none'
      }}>
        <button 
           onClick={() => onGenerate(section)}
           style={{
             display:'flex', 
             alignItems:'center', 
             gap: '8px', 
             color:'#004b87', 
             fontWeight:600,
             padding: '8px 16px',
             background: '#fff',
             borderRadius: '24px',
             border: '1px solid #d1d9e0',
             transition: 'all 0.2s',
             boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
             fontSize: '11px'
           }}
           onMouseEnter={(e) => {
             e.currentTarget.style.transform = 'translateY(-2px)';
             e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,75,135,0.15)';
           }}
           onMouseLeave={(e) => {
             e.currentTarget.style.transform = 'translateY(0)';
             e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
           }}
        >
          <Sparkles size={14} />
           Generate {section}
        </button>
      </div>
    );
  }

  // 3. Fallback: Standard Original Component
  return originalComponent;
};

export default WidgetSlot;
