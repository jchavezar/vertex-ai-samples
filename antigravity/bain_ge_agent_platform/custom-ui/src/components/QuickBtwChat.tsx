import React from 'react';

export function QuickBtwChat({ setChatInput }: { setChatInput: (s: string) => void }) {
  return (
    <div className="autocomplete-dropdown absolute bottom-[calc(100%-0.5px)] left-6 right-6 bg-[#f4f3ef] border border-[#d8d6d0] border-b-0 z-50 rounded-none">
      <button 
        type="button"
        onClick={() => setChatInput('/btw ')}
        className="w-full flex items-baseline gap-3 p-3 text-left hover:bg-[#faf9f6] rounded-none transition-colors"
      >
        <span className="font-mono font-bold text-xs bg-[#faf9f6] border border-[#d8d6d0] px-1.5 py-0.5 rounded-none">/btw</span>
        <span className="text-xs text-[#7c7a75]">Type <kbd className="font-mono bg-[#faf9f6] border border-[#d8d6d0] px-1 py-0.5 text-[10px] rounded-none">/btw</kbd> for instant web-grounded reference</span>
      </button>
    </div>
  );
}
