import React, { useState } from 'react';
import { Sparkles, Loader, Maximize2, X, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const WidgetSlot = ({ 
  section, 
  override, 
  isAiMode, 
  originalComponent,
  onGenerate,
  tickers
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
            color: 'var(--text-muted)',
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
                  <Sparkles size={12} color="var(--brand)" />
                  <span style={{ fontWeight: 800, fontSize: '11px', color: 'var(--text-primary)' }}>{section} Analysis</span>
                </div>
                {override.model && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '9px', color: 'var(--text-muted)', marginLeft: '20px', fontWeight: 600 }}>
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
          <div className="markdown-body concise-summary" style={{ fontSize: '11px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{summaryContent}</ReactMarkdown>
          </div>
          {isLongContent && (
            <div style={{
              marginTop: 'auto',
              paddingTop: '8px',
              textAlign: 'center',
              fontSize: '10px',
              color: 'var(--brand)',
              fontWeight: 800,
              borderTop: '1px solid var(--border)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
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
                  <Sparkles size={18} color="var(--brand)" />
                  <h2 style={{ fontSize: '16px', margin: 0, color: 'var(--text-primary)' }}>{section} - Full AI Analysis</h2>
                </div>
                <button onClick={() => setIsModalOpen(false)} style={{ color: 'var(--text-muted)', background: 'transparent', border: 'none', cursor: 'pointer' }}>
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
    const isComparison = tickers && tickers.length > 1;
    const buttonText = isComparison
      ? `Compare ${section} (${tickers.join(' vs ')})`
      : `Generate ${section} for ${tickers ? tickers[0] : '...'}`;

    return (
      <div className="card" style={{
        minHeight: '200px', 
        display:'flex', 
        alignItems:'center', 
        justifyContent:'center',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px dashed var(--border)',
        boxShadow: 'none',
        backdropFilter: 'var(--card-blur)'
      }}>
        <button 
           onClick={() => onGenerate(section)}
           style={{
             display:'flex', 
             alignItems:'center', 
             gap: '10px',
             color: 'var(--brand)',
             fontWeight: 800,
             padding: '10px 24px',
             background: 'linear-gradient(145deg, rgba(62, 166, 255, 0.15), rgba(62, 166, 255, 0.05))',
             borderRadius: '999px',
             border: '1px solid rgba(62, 166, 255, 0.3)',
             transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
             boxShadow: '0 4px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1), inset 0 -1px 0 rgba(0,0,0,0.1)',
             fontSize: '11px',
             textTransform: 'uppercase',
             letterSpacing: '0.5px'
           }}
           onMouseEnter={(e) => {
             e.currentTarget.style.transform = 'translateY(-2px)';
             e.currentTarget.style.background = 'linear-gradient(145deg, rgba(62, 166, 255, 0.2), rgba(62, 166, 255, 0.1))';
             e.currentTarget.style.boxShadow = '0 6px 16px rgba(62, 166, 255, 0.25), inset 0 1px 0 rgba(255,255,255,0.15), inset 0 -1px 0 rgba(0,0,0,0.15)';
           }}
           onMouseLeave={(e) => {
             e.currentTarget.style.transform = 'translateY(0)';
             e.currentTarget.style.background = 'linear-gradient(145deg, rgba(62, 166, 255, 0.15), rgba(62, 166, 255, 0.05))';
             e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1), inset 0 -1px 0 rgba(0,0,0,0.1)';
           }}
        >
          <Sparkles size={14} />
          {buttonText}
        </button>
      </div>
    );
  }

  // 3. Fallback: Standard Original Component
  return originalComponent;
};

export default WidgetSlot;
