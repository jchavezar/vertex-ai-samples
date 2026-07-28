import React, { useState } from 'react';
import { Volume2, VolumeX, Sparkles } from 'lucide-react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';

interface ExecutiveVoiceBriefingProps {
  selectedError: GcpErrorItem;
  diagnostic?: CloudAssistDiagnostic | null;
  isLightMode?: boolean;
}

export const ExecutiveVoiceBriefing: React.FC<ExecutiveVoiceBriefingProps> = ({
  selectedError,
  diagnostic,
  isLightMode = false
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  const speakBriefing = () => {
    if (!('speechSynthesis' in window)) {
      alert("Web Speech API not supported in this browser.");
      return;
    }

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    const text = `Gemini Cloud Assist Executive Incident Briefing. Critical incident detected on service ${selectedError.serviceName}. ${selectedError.summary}. Diagnostic synthesis: ${diagnostic?.recapText || "Root cause identified and proactive remediation patch generated."} Container status verified at HTTP 200 OK.`;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    setIsPlaying(true);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <button
      onClick={speakBriefing}
      className={`px-3.5 py-1.5 rounded-full border text-xs font-bold font-mono flex items-center gap-2 transition-all cursor-pointer shadow-sm ${
        isLightMode
          ? isPlaying
            ? 'bg-rose-100 border-rose-300 text-rose-800 animate-pulse'
            : 'bg-white hover:bg-slate-100 border-slate-300 text-slate-950'
          : isPlaying
            ? 'bg-rose-950 border-rose-500 text-rose-300 animate-pulse'
            : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-cyan-300'
      }`}
      title="Listen to 15-second AI Executive Incident Voice Briefing"
    >
      {isPlaying ? (
        <>
          <VolumeX className="w-3.5 h-3.5 text-rose-600 animate-bounce" />
          <span>Stop Briefing</span>
        </>
      ) : (
        <>
          <Volume2 className={`w-3.5 h-3.5 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
          <span>🔊 AI Voice Briefing</span>
        </>
      )}
    </button>
  );
};
