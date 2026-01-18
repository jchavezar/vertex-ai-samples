import React from 'react';
import { Sparkles, Loader } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const WidgetSlot = ({ 
  section, 
  override, 
  isAiMode, 
  originalComponent,
  onGenerate 
}) => {
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
    return (
      <div className="card" style={{minHeight: '200px', maxHeight: '400px', overflowY:'auto', display: 'flex', flexDirection: 'column'}}>
        <div className="section-title" style={{ justifyContent: 'flex-start', gap: '8px' }}>
          <Sparkles size={14} color="#004b87" />
          {section} (AI Analysis)
        </div>
        <div className="markdown-body" style={{fontSize: '12px', lineHeight: '1.6', color: '#333'}}>
           <ReactMarkdown>{override.content}</ReactMarkdown>
        </div>
      </div>
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
             padding: '12px 20px',
             background: '#fff',
             borderRadius: '24px',
             border: '1px solid #d1d9e0',
             transition: 'all 0.2s',
             boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
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
           <Sparkles size={16} />
           Generate {section}
        </button>
      </div>
    );
  }

  // 3. Fallback: Standard Original Component
  return originalComponent;
};

export default WidgetSlot;
