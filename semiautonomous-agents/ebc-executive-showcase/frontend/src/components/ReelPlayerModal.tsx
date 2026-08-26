import React, { useState, useEffect, useRef } from 'react';
import { StoryboardPanel } from '../types';
import { X, Play, Pause, SkipForward, SkipBack, Volume2, VolumeX, Sparkles } from 'lucide-react';

interface ReelPlayerModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaignTitle: string;
  slogan: string;
  panels: StoryboardPanel[];
}

export const ReelPlayerModal: React.FC<ReelPlayerModalProps> = ({
  isOpen,
  onClose,
  campaignTitle,
  slogan,
  panels,
}) => {
  const [currentPanelIndex, setCurrentPanelIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(6);

  const timerRef = useRef<any>(null);
  const activePanel = panels[currentPanelIndex] || panels[0];

  const speakText = (text: string) => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-MX';
    utterance.rate = 1.05;

    const voices = window.speechSynthesis.getVoices();
    const spanishVoice = voices.find(v => v.lang.startsWith('es'));
    if (spanishVoice) utterance.voice = spanishVoice;

    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    if (!isOpen) {
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
      clearInterval(timerRef.current);
      return;
    }

    setCurrentPanelIndex(0);
    setIsPlaying(true);
    setSecondsRemaining(panels[0]?.duration_seconds || 6);

    if (voiceEnabled && panels[0]) {
      speakText(panels[0].voiceover_script);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen || !isPlaying) {
      clearInterval(timerRef.current);
      return;
    }

    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          setCurrentPanelIndex((curr) => {
            const next = (curr + 1) % panels.length;
            const nextPanel = panels[next];
            if (voiceEnabled && nextPanel) {
              speakText(nextPanel.voiceover_script);
            }
            return next;
          });
          return panels[(currentPanelIndex + 1) % panels.length]?.duration_seconds || 6;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [isOpen, isPlaying, currentPanelIndex, panels, voiceEnabled]);

  if (!isOpen || panels.length === 0) return null;

  const handleNext = () => {
    const next = (currentPanelIndex + 1) % panels.length;
    setCurrentPanelIndex(next);
    setSecondsRemaining(panels[next].duration_seconds || 6);
    if (voiceEnabled) speakText(panels[next].voiceover_script);
  };

  const handlePrev = () => {
    const prev = (currentPanelIndex - 1 + panels.length) % panels.length;
    setCurrentPanelIndex(prev);
    setSecondsRemaining(panels[prev].duration_seconds || 6);
    if (voiceEnabled) speakText(panels[prev].voiceover_script);
  };

  const handleTogglePlay = () => {
    if (isPlaying) {
      if ('speechSynthesis' in window) window.speechSynthesis.pause();
      setIsPlaying(false);
    } else {
      if ('speechSynthesis' in window) window.speechSynthesis.resume();
      setIsPlaying(true);
    }
  };

  const handleToggleVoice = () => {
    if (voiceEnabled) {
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
      setVoiceEnabled(false);
    } else {
      setVoiceEnabled(true);
      if (activePanel) speakText(activePanel.voiceover_script);
    }
  };

  const getPanelGradient = (idx: number) => {
    switch (idx) {
      case 0: return 'from-slate-900 via-slate-800 to-indigo-950';
      case 1: return 'from-blue-950 via-indigo-900 to-slate-900';
      case 2: return 'from-indigo-950 via-blue-900 to-slate-900';
      case 3: return 'from-slate-900 via-emerald-950 to-slate-950';
      default: return 'from-slate-900 via-slate-800 to-slate-950';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-md p-4 sm:p-6">
      <div className="relative w-full max-w-5xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50/90">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-fuchsia-100 text-fuchsia-700 flex items-center justify-center font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-fuchsia-700">
                Reproductor de Reel Cinemático Directivo
              </span>
              <h3 className="text-base sm:text-lg font-extrabold text-slate-900">
                {campaignTitle}
              </h3>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-all"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bars for the 4 Panels */}
        <div className="grid grid-cols-4 gap-2 px-6 pt-4 bg-slate-950">
          {panels.map((p, idx) => (
            <div key={idx} className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  idx < currentPanelIndex
                    ? 'w-full bg-fuchsia-500'
                    : idx === currentPanelIndex
                    ? 'bg-gradient-to-r from-blue-400 to-fuchsia-400'
                    : 'w-0'
                }`}
                style={{
                  width: idx === currentPanelIndex
                    ? `${((p.duration_seconds - secondsRemaining) / p.duration_seconds) * 100}%`
                    : undefined
                }}
              />
            </div>
          ))}
        </div>

        {/* Cinematic Reel Screen */}
        <div className={`relative flex-1 min-h-[380px] sm:min-h-[460px] bg-gradient-to-br ${getPanelGradient(currentPanelIndex)} text-white p-8 flex flex-col justify-between overflow-hidden shadow-inner`}>
          
          {/* Top Panel Metadata */}
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-fuchsia-600/90 text-white shadow-sm">
                {activePanel.visual_badge} • Panel {activePanel.panel_number} de 4
              </span>
              <span className="text-xs font-medium text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded-full">
                {activePanel.artwork_theme}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold bg-black/40 px-3 py-1 rounded-full border border-white/10">
                00:0{secondsRemaining}s
              </span>
            </div>
          </div>

          {/* Center Cinematic Display */}
          <div className="text-center my-auto space-y-6 z-10 max-w-3xl mx-auto">
            <div className="inline-block px-4 py-1.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-xs sm:text-sm font-black uppercase tracking-widest text-cyan-300">
              {activePanel.title}
            </div>

            <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-white drop-shadow-md leading-tight">
              "{activePanel.on_screen_text}"
            </h2>

            <div className="p-4 rounded-2xl bg-black/40 backdrop-blur-md border border-white/10 text-slate-200 text-sm sm:text-base font-medium max-w-2xl mx-auto shadow-lg text-left">
              <span className="text-xs uppercase font-extrabold text-fuchsia-300 block mb-1">
                Visual Cinemático Renderizado:
              </span>
              {activePanel.visual_description}
            </div>
          </div>

          {/* Bottom Voiceover Subtitle Strip */}
          <div className="z-10 bg-black/60 backdrop-blur-md p-4 rounded-2xl border border-white/10 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-300 flex items-center justify-center shrink-0">
                <Volume2 className="w-4 h-4 animate-pulse" />
              </div>
              <p className="text-sm sm:text-base font-semibold text-white">
                <span className="text-xs uppercase font-bold text-blue-400 block">Locución en Off:</span>
                "{activePanel.voiceover_script}"
              </p>
            </div>
          </div>

          <div className="absolute -bottom-20 -right-20 w-96 h-96 bg-fuchsia-600/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -top-20 -left-20 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />
        </div>

        {/* Player Controls Footer */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-50 border-t border-slate-200">
          <div className="flex items-center gap-2">
            <button
              onClick={handleToggleVoice}
              className={`p-2.5 rounded-xl border text-sm font-bold flex items-center gap-1.5 ${
                voiceEnabled
                  ? 'bg-blue-50 text-blue-700 border-blue-200'
                  : 'bg-slate-200 text-slate-500 border-slate-300'
              }`}
            >
              {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              <span className="hidden sm:inline">{voiceEnabled ? 'Voz Activa' : 'Sin Voz'}</span>
            </button>
          </div>

          {/* Play / Next / Prev */}
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrev}
              className="p-3 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 shadow-sm"
            >
              <SkipBack className="w-5 h-5" />
            </button>

            <button
              onClick={handleTogglePlay}
              className="p-3.5 rounded-2xl bg-blue-700 text-white hover:bg-blue-800 shadow-md"
            >
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>

            <button
              onClick={handleNext}
              className="p-3 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 shadow-sm"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          <div className="text-right">
            <span className="text-xs font-bold text-slate-500 block">Slogan de Campaña</span>
            <span className="text-sm font-black text-slate-800">"{slogan}"</span>
          </div>
        </div>

      </div>
    </div>
  );
};
