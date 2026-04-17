import { useState, useEffect } from 'react';

const SPINNER_FRAMES = ['/', '-', '\\', '|'];
const PHRASES = [
  'Thinking...',
  'Calling tools...',
  'Running on VM...',
  'Processing...',
  'Generating...',
];

function ThinkingState() {
  const [frame, setFrame] = useState(0);
  const [phrase, setPhrase] = useState(0);

  useEffect(() => {
    const spinnerInterval = setInterval(() => {
      setFrame((f) => (f + 1) % SPINNER_FRAMES.length);
    }, 120);

    const phraseInterval = setInterval(() => {
      setPhrase((p) => (p + 1) % PHRASES.length);
    }, 2400);

    return () => {
      clearInterval(spinnerInterval);
      clearInterval(phraseInterval);
    };
  }, []);

  return (
    <div className="thinking">
      <span className="thinking-spinner">{SPINNER_FRAMES[frame]}</span>
      <span className="thinking-text">{PHRASES[phrase]}</span>
    </div>
  );
}

export default ThinkingState;
