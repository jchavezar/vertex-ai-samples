
import React from 'react';

interface ChatGreetingProps {
  userName?: string; 
}

export const ChatGreeting: React.FC<ChatGreetingProps> = ({ userName }) => {
  let greetingText = "Hi!";

  // Subtext removed to match the new design's simplicity for the greeting area
  // It will be replaced by the main chat input placeholder

  return (
    <div className="text-center pt-16 md:pt-24 pb-8 md:pb-12 px-4">
      <h1 
        className="text-5xl md:text-6xl font-bold bg-clip-text text-transparent"
        style={{
          backgroundImage: 'linear-gradient(to right, rgb(var(--color-brand-gradient-from)), rgb(var(--color-brand-gradient-via)), rgb(var(--color-brand-gradient-to)))',
        }}
      >
        {greetingText}
      </h1>
    </div>
  );
};