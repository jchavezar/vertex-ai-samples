import { useState, useEffect } from 'react';
import { useAgent } from '@/lib/state';

interface TeachingOverlayProps {
  topics: { title: string; status: 'pending' | 'active' | 'completed' }[];
  infoBubble: { text: string; visible: boolean } | null;
  onSelectTopic?: (index: number) => void;
  onCloseBubble: () => void;
}

export default function TeachingOverlay({ topics, infoBubble, onCloseBubble, onSelectTopic }: TeachingOverlayProps) {
  const { current } = useAgent();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  if (current.id !== 'proper-paul') return null;

  return (
    <div className="teaching-overlay" style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: 50
    }}>
      {/* Topics Container */}
      <div style={{
        position: 'absolute',
        top: '60px',
        left: '40px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        pointerEvents: 'auto'
      }}>
        {(topics || []).map((topic, idx) => {
          if (!topic) return null;
          return (
            <button
              key={idx}
              onClick={() => onSelectTopic?.(idx)}
              style={{
                background: topic.status === 'active' ? 'rgba(255, 255, 255, 0.95)' :
                  topic.status === 'completed' ? 'rgba(220, 255, 220, 0.9)' : 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(8px)',
                padding: '16px',
                borderRadius: '16px',
                boxShadow: topic.status === 'active' ? '0 8px 32px rgba(0,0,0,0.15)' : '0 4px 12px rgba(0,0,0,0.05)',
                border: topic.status === 'active' ? '2px solid #4285f4' : '1px solid rgba(255,255,255,0.6)',
                width: '260px',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: topic.status === 'active' ? 'scale(1.05) translateX(10px)' : 'scale(1)',
                opacity: isVisible ? 1 : 0,
                animation: `fadeIn 0.5s ease-out forwards ${idx * 0.1}s`,
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                fontFamily: '"Outfit", sans-serif',
                outline: 'none',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                if (topic.status !== 'active') {
                  e.currentTarget.style.transform = 'scale(1.02) translateX(5px)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                }
              }}
              onMouseLeave={(e) => {
                if (topic.status !== 'active') {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.8)';
                }
              }}
            >
              <span style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: topic.status === 'completed' ? '#34a853' :
                  topic.status === 'active' ? '#4285f4' : '#e0e0e0',
                color: topic.status === 'active' || topic.status === 'completed' ? '#fff' : '#666',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 700,
                flexShrink: 0
              }}>
                {topic.status === 'completed' ? '✓' : idx + 1}
              </span>
              <span style={{
                fontSize: '15px',
                fontWeight: 600,
                color: topic.status === 'completed' ? '#2e7d32' : '#202124',
                lineHeight: '1.3'
              }}>
                {topic.title}
              </span>

              {/* Active Indicator Pulse */}
              {topic.status === 'active' && (
                <span style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#4285f4',
                  boxShadow: '0 0 0 0 rgba(66, 133, 244, 0.7)',
                  animation: 'pulse 1.5s infinite'
                }} />
              )}
            </button>
          );
        })}
      </div>

      {/* Info Bubble */}
      {infoBubble && infoBubble.visible && (
        <div style={{
          position: 'absolute',
          top: '25%',
          right: '5%',
          width: '340px',
          background: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(16px)',
          borderRadius: '24px 24px 4px 24px', // Speech bubble style
          padding: '24px',
          boxShadow: '0 20px 50px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.05)',
          border: '1px solid rgba(255,255,255,0.8)',
          pointerEvents: 'auto',
          animation: 'popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
          transformOrigin: 'bottom right'
        }}>
          <button onClick={onCloseBubble} style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            width: '24px',
            height: '24px',
            background: '#f1f3f4',
            borderRadius: '50%',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#5f6368',
            fontSize: '12px',
            transition: 'all 0.2s'
          }}>✕</button>

          <div style={{
            fontFamily: '"Outfit", sans-serif',
            fontSize: '16px',
            lineHeight: '1.6',
            color: '#3c4043',
            marginTop: '8px'
          }}>
            {infoBubble.text}
          </div>

          {/* Arrow */}
          <div style={{
            position: 'absolute',
            bottom: '-10px',
            right: '24px',
            width: '20px',
            height: '20px',
            background: 'rgba(255, 255, 255, 0.98)',
            transform: 'rotate(45deg)',
            boxShadow: '8px 8px 0px 0px rgba(0,0,0,0.02)', // Soft fake shadow
            zIndex: -1
          }} />
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes popIn {
          from { opacity: 0; transform: scale(0.8) translateY(20px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes pulse {
          0% { transform: translateY(-50%) scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0.7); }
          70% { transform: translateY(-50%) scale(1); box-shadow: 0 0 0 6px rgba(66, 133, 244, 0); }
          100% { transform: translateY(-50%) scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0); }
        }
      `}</style>
    </div>
  );
}
