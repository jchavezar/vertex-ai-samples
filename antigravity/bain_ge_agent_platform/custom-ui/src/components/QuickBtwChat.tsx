export function QuickBtwChat({ setChatInput }: { setChatInput: (s: string) => void }) {
  return (
    <div className="autocomplete-dropdown absolute bottom-[calc(100%-0.5px)] left-4 right-4 bg-white border border-slate-200 z-50 rounded-xl shadow-lg overflow-hidden">
      <button 
        type="button"
        onClick={() => setChatInput('/btw ')}
        className="w-full flex items-baseline gap-2.5 p-3 text-left hover:bg-slate-50 transition-colors cursor-pointer"
      >
        <span className="font-mono font-bold text-xs bg-slate-900 text-white px-2 py-0.5 rounded-md">/btw</span>
        <span className="text-xs text-slate-500">Type <kbd className="font-mono bg-slate-100 border border-slate-200 px-1.5 py-0.5 text-[10px] rounded">/btw</kbd> for instant web-grounded reference</span>
      </button>
    </div>
  );
}
