import React, { useEffect, useState } from 'react';

interface NewsBubbleProps {
  headline: string | null;
}

export const NewsBubble: React.FC<NewsBubbleProps> = ({ headline }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (headline) {
      setVisible(true);
      // Auto-hide after 15 seconds or keep until replaced?
      // News tickers usually stay up. Let's keep it until replaced or manually cleared if we had a clear.
      // For now, persistent while relevant.
    } else {
      setVisible(false);
    }
  }, [headline]);

  if (!headline && !visible) return null;

  return (
    <div
      className={`absolute top-24 left-8 z-50 max-w-sm transition-all duration-500 transform ${
        visible && headline ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'
      }`}
    >
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md rounded-lg shadow-xl border-l-4 border-red-600 overflow-hidden">
        <div className="bg-red-600 px-4 py-1">
          <span className="text-white text-xs font-bold uppercase tracking-wider flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            Breaking News
          </span>
        </div>
        <div className="p-4">
          <p className="text-gray-900 dark:text-white font-bold text-lg leading-tight">
            {headline}
          </p>
        </div>
      </div>
    </div>
  );
};
