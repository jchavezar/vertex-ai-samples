import { useRef, useEffect, useState } from 'react';
import { useAgent } from '@/lib/state';

export type Ingredient = string;

interface IngredientsBubbleProps {
  recipeName: string;
  ingredients: Ingredient[];
  onClose: () => void;
}

export default function IngredientsBubble({ recipeName, ingredients, onClose }: IngredientsBubbleProps) {
  const { current } = useAgent();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  if (current.id !== 'chef-shane') return null;

  return (
    <div 
      className={`ingredients-bubble ${isVisible ? 'visible' : ''}`}
      style={{
        position: 'absolute',
        top: '20%',
        right: '10%',
        width: '300px',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '24px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        transform: isVisible ? 'scale(1) translateY(0)' : 'scale(0.9) translateY(20px)',
        opacity: isVisible ? 1 : 0,
        transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        zIndex: 100,
        border: '1px solid rgba(255, 255, 255, 0.5)',
      }}
    >
        <button 
        onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 400);
        }}
        style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#666',
            padding: '4px',
        }}
        >
        ✕
        </button>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '16px',
        borderBottom: '2px solid #f0f0f0',
        paddingBottom: '12px',
      }}>
        <span style={{ fontSize: '24px', marginRight: '12px' }}>🍳</span>
        <h3 style={{ 
          margin: 0, 
          fontSize: '18px', 
          color: '#2c3e50',
          fontFamily: '"Outfit", sans-serif',
          fontWeight: 600
        }}>
          {recipeName}
        </h3>
      </div>
      
      <ul style={{ 
        listStyle: 'none', 
        padding: 0, 
        margin: 0,
        maxHeight: '300px',
        overflowY: 'auto'
      }}>
        {ingredients.map((ingredient, idx) => (
          <li 
            key={idx}
            style={{
              padding: '8px 0',
              borderBottom: idx < ingredients.length - 1 ? '1px solid #f5f5f5' : 'none',
              color: '#4a5568',
              fontSize: '15px',
              fontFamily: '"Inter", sans-serif',
              display: 'flex',
              alignItems: 'center',
              animation: `fadeIn 0.3s ease-out forwards ${idx * 0.1}s`,
              opacity: 0,
              transform: 'translateY(5px)'
            }}
          >
            <span style={{ 
              width: '6px', 
              height: '6px', 
              background: '#48bb78', 
              borderRadius: '50%',
              marginRight: '12px',
              flexShrink: 0
            }} />
            {ingredient}
          </li>
        ))}
      </ul>
      <style>{`
        @keyframes fadeIn {
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
