import React, { useEffect, useRef } from 'react';

interface AudioVisualizerCanvasProps {
  isActive: boolean;
  isSpeaking: boolean;
  colorScheme?: 'blue' | 'emerald' | 'fuchsia';
}

export const AudioVisualizerCanvas: React.FC<AudioVisualizerCanvasProps> = ({
  isActive,
  isSpeaking,
  colorScheme = 'blue',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      const numBars = 48;
      const barWidth = width / numBars - 2;

      for (let i = 0; i < numBars; i++) {
        let barHeight = 6;
        if (isActive || isSpeaking) {
          // Dynamic frequency calculation
          const multiplier = isSpeaking ? 0.9 : 0.6;
          const sinVal = Math.sin(phase + i * 0.25);
          const cosVal = Math.cos(phase * 1.5 + i * 0.15);
          const noise = Math.sin(i * 0.8 + phase * 2.2);
          const amplitude = Math.max(0.1, (sinVal + cosVal + noise + 3) / 6);
          barHeight = Math.max(8, amplitude * (height * 0.85) * multiplier);
        } else {
          // Idle gentle wave
          barHeight = 6 + Math.sin(phase + i * 0.2) * 3;
        }

        const x = i * (barWidth + 2);
        const y = (height - barHeight) / 2;

        // Gradient styling
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        if (colorScheme === 'emerald') {
          gradient.addColorStop(0, '#059669');
          gradient.addColorStop(0.5, '#10b981');
          gradient.addColorStop(1, '#047857');
        } else if (colorScheme === 'fuchsia') {
          gradient.addColorStop(0, '#c026d3');
          gradient.addColorStop(0.5, '#e879f9');
          gradient.addColorStop(1, '#9333ea');
        } else {
          gradient.addColorStop(0, '#1d4ed8');
          gradient.addColorStop(0.5, '#38bdf8');
          gradient.addColorStop(1, '#2563eb');
        }

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 4);
        ctx.fill();
      }

      phase += (isActive || isSpeaking) ? 0.12 : 0.03;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isActive, isSpeaking, colorScheme]);

  return (
    <div className="w-full flex items-center justify-center p-3 bg-slate-100/80 rounded-xl border border-slate-200 shadow-inner">
      <canvas
        ref={canvasRef}
        width={720}
        height={90}
        className="w-full max-w-2xl h-16 object-contain"
      />
    </div>
  );
};
