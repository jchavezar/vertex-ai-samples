import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquarePlus } from 'lucide-react';
import { clsx } from 'clsx';

interface SuggestionChipsProps {
  suggestions: string[];
  theme?: 'light' | 'dark';
}

export const SuggestionChips: React.FC<SuggestionChipsProps> = ({ suggestions, theme = 'dark' }) => {
  const isDark = theme === 'dark';

  // Directly use the state for sending messages if we had a chat store, 
  // but for now we'll simulate it by dispatching a custom event or 
  // relying on the parent to handle it. Actually, the most robust way 
  // is to use a global event or update a "pending query" in the store.

  const handleSuggestionClick = (text: string) => {
    // Dispatch a custom event that ChatContainer can listen to
    window.dispatchEvent(new CustomEvent('suggestion_click', { detail: { text } }));
  };

  return (
    <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-100 dark:border-white/5">
      {suggestions.map((suggestion, idx) => (
        <motion.button
          key={idx}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: idx * 0.05 }}
          onClick={() => handleSuggestionClick(suggestion)}
          className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all duration-300 transform active:scale-95 group",
            isDark
              ? "bg-blue-500/10 border border-blue-500/20 text-blue-400 hover:bg-blue-500/20 hover:border-blue-500/40"
              : "bg-blue-50 border border-blue-100 text-blue-600 hover:bg-blue-100 hover:border-blue-200 shadow-sm"
          )}
        >
          <MessageSquarePlus size={14} className="opacity-60 transition-transform group-hover:rotate-12" />
          {suggestion}
        </motion.button>
      ))}
    </div>
  );
};
