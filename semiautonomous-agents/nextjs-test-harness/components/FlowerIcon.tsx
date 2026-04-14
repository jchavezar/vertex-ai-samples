"use client";

import { motion } from "framer-motion";

export function FlowerIcon({ isThinking }: { isThinking?: boolean }) {
  return (
    <motion.svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      animate={isThinking ? { rotate: 360 } : { rotate: 0 }}
      transition={isThinking ? { duration: 4, repeat: Infinity, ease: "linear" } : { duration: 0.5 }}
      className="text-shroud-accent"
    >
      {/* 12-petal flower/sun burst icon */}
      <path d="M16 4V8M16 24V28M4 16H8M24 16H28M7.5 7.5L10.3 10.3M21.7 21.7L24.5 24.5M7.5 24.5L10.3 21.7M21.7 10.3L24.5 7.5" 
            stroke="currentColor" 
            strokeWidth="2.5" 
            strokeLinecap="round"/>
    </motion.svg>
  );
}
