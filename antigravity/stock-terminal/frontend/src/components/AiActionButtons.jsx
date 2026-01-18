import React from 'react';
import { Sparkles } from 'lucide-react';

const AiActionButtons = ({ ticker }) => {
  const actions = [
    'Profile', 'Trading', 'Valuation', 'Dividends', 'Estimates', 'Insights'
  ];

  const handleAction = (action) => {
    if (window.triggerAgent) {
      window.triggerAgent(`Generate ${action} analysis for ${ticker}`);
    } else {
      console.warn("Agent trigger not available");
      alert("Agent is not ready yet. Please wait a moment.");
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '10px' }}>
      {actions.map(action => (
        <button 
          key={action}
          onClick={() => handleAction(action)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            padding: '16px',
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            color: '#004b87',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}
          onMouseEnter={(e) => {
             e.currentTarget.style.transform = 'translateY(-2px)';
             e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,75,135,0.15)';
             e.currentTarget.style.borderColor = '#004b87';
             e.currentTarget.style.backgroundColor = '#f8fbbd'; // FactSet-ish highlight? Or subtle blue? Let's go subtle blue.
             e.currentTarget.style.backgroundColor = '#f0f7ff';
          }}
          onMouseLeave={(e) => {
             e.currentTarget.style.transform = 'translateY(0)';
             e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
             e.currentTarget.style.borderColor = '#e0e0e0';
             e.currentTarget.style.backgroundColor = '#ffffff';
          }}
        >
          <Sparkles size={18} color="#004b87" />
          <span>Generate {action} via AI</span>
        </button>
      ))}
    </div>
  );
};

export default AiActionButtons;
