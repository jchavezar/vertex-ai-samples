import React, { useState } from 'react';
import { Sparkles, Loader, Maximize2, X, Bot } from 'lucide-react';
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
        <div className="card ai-glow" style={{
          minHeight: '200px', 
          display: 'flex', 
          flexDirection: 'column',
          padding: '16px'
        }}>
          <div className="section-title" style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={14} className="icon-pulse" />
              <span style={{ fontWeight: 600 }}>{section} Analysis</span>
            </div>
            <Loader className="animate-spin" size={12} color="#8c959f" />
          </div>

          <div className="widget-loading-box shimmer-bg" style={{ width: '90%' }} />
          <div className="widget-loading-box shimmer-bg" style={{ width: '100%' }} />
          <div className="widget-loading-box shimmer-bg" style={{ width: '85%' }} />
          <div className="widget-loading-box shimmer-bg" style={{ width: '95%', marginTop: '12px' }} />
          <div className="widget-loading-box shimmer-bg" style={{ width: '70%' }} />

          <div style={{
            marginTop: 'auto',
            fontSize: '10px',
            color: '#57606a',
            fontStyle: 'italic',
            textAlign: 'center'
          }}>
            Powering up Gemini analysts...
          </div>
        </div>
      );
    }

    // Extract only the first paragraph or block of text for the concise summary
    const getConciseSummary = (content) => {
      if (!content) return "";
      // Remove the specific widget tags if they leaked into the content
      const cleanContent = content.replace(/\[\/?WIDGET:[^\]]+\]/g, '').trim();
      const lines = cleanContent.split('\n');
      const paragraph = [];
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
          if (paragraph.length > 0) break;
          continue;
        }
        if (trimmed.startsWith('|') || trimmed.startsWith('-')) continue;
        paragraph.push(line);
        if (paragraph.length > 3) break;
      }
      return paragraph.join('\n');
    };

    const cleanFullContent = override.content.replace(/\[\/?WIDGET:[^\]]+\]/g, '').trim();
    const summaryContent = getConciseSummary(cleanFullContent) || cleanFullContent.substring(0, 150) + '...';
    const isLongContent = cleanFullContent.length > 350;

    return (
      <>
        <div
          className="card widget-clickable ai-glow"
          onClick={() => setIsModalOpen(true)}
          style={{ minHeight: '200px', maxHeight: '300px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
        >
          <div className="section-title" style={{ justifyContent: 'space-between', gap: '8px', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={12} color="#004b87" />
                  <span style={{ fontWeight: 700, fontSize: '11px' }}>{section} Analysis</span>
                </div>
                {override.model && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '9px', color: '#8c959f', marginLeft: '20px', fontWeight: 500 }}>
                    <Bot size={10} />
                    {override.model}
                  </div>
                )}
              </div>
            </div>
            <div className="widget-expand-indicator">
              <Maximize2 size={10} />
              <span>Full Analysis</span>
            </div>
          </div>
          <div className="markdown-body concise-summary" style={{ fontSize: '11px', lineHeight: '1.4', color: '#333' }}>
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
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{cleanFullContent}</ReactMarkdown>
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
