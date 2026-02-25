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
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '24px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            color: 'var(--brand)',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: 'var(--glass-shadow)',
            backdropFilter: 'var(--card-blur)'
          }}
          onMouseEnter={(e) => {
             e.currentTarget.style.transform = 'translateY(-2px)';
             e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,75,135,0.15)';
            e.currentTarget.style.borderColor = 'var(--brand)';
            e.currentTarget.style.backgroundColor = 'var(--brand-light)';
          }}
          onMouseLeave={(e) => {
             e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.backgroundColor = 'var(--bg-card)';
          }}
        >
          <Sparkles size={18} />
          <span>Generate {action} via AI</span>
        </button>
      ))}
    </div>
  );
};

export default AiActionButtons;
