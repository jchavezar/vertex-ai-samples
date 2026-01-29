
css_content = r"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --font-sans: 'Outfit', 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Roboto Mono', monospace;

  /* Light Theme (Default) - "Frost Crystal" */
    --bg-app: #f8fafc;
    /* Slate 50 - Cleanest White/Grey */
    --bg-card: rgba(255, 255, 255, 0.7);
    /* Frosted Glass */
    --bg-popover: #ffffff;
    --border: #e2e8f0;
    /* Slate 200 */
    --border-hover: #cbd5e1;
    /* Slate 300 */
    --border-light: #f1f5f9;

  --text-primary: #334155;
    /* Slate 700 - Soft Executive Grey */
    --text-secondary: #64748b;
    /* Slate 500 */
    --text-muted: #94a3b8;
    /* Slate 400 */

  --brand: #0ea5e9;
    /* Sky 500 */
    --brand-gradient: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
    --brand-light: #f0f9ff;

  /* Jewel Tones (Light Mode Optimized) */
    --green: #10b981;
    /* Emerald 500 - Minty but visible */
    --green-bg: #d1fae5;
    --red: #f43f5e;
      /* Rose 500 - Soft but clear */
      --red-bg: #ffe4e6;

  --header-height: 56px;
  --sidebar-width: 260px;
  --sub-sidebar-width: 200px;
  --glass-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.02),
        0 2px 4px -1px rgba(0, 0, 0, 0.02),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.9);
        --card-blur: blur(20px) saturate(180%);

  --bg-msg-user: #f0f9ff;
    --text-msg-user: #0369a1;
    --border-msg-user: #bae6fd;
    --bg-msg-assistant: #ffffff;
    --text-msg-assistant: #334155;
  --border-msg-assistant: #e2e8f0;
}

.dark {
  /* Executive "Rich Void" Theme (Dark) */
    --bg-app: #020617;
    /* Slate 950 */
    /* Deep Navy/Black Void */
    --bg-card: rgba(20, 25, 40, 0.6);
    /* Slightly blue-tinted glass */
    --bg-popover: rgba(10, 15, 25, 0.95);
    
    --border: rgba(255, 255, 255, 0.12);
      /* Increased visibility for structure */
      --border-hover: rgba(255, 255, 255, 0.25);
      --border-light: rgba(255, 255, 255, 0.08);

    --text-primary: #ffffff;
      /* Pure White for contrast */
    --text-secondary: #94a3b8; /* Slate 400 */
    --text-muted: #64748b; /* Slate 500 */

    /* Saturated Signals (Executive Readability) */
      --brand: #22d3ee;
      /* Cyber Teal (Cyan 400) */
      --brand-glow: rgba(34, 211, 238, 0.3);
    
      --accent: #3b82f6;
      /* Electric Blue (Blue 500) */
      --accent-foreground: #ffffff;
    
      --success: #00ff9d;
      /* Neon Mint - High Saturation */
      --success-foreground: #00331b;
    
      --warning: #fbbf24;
      /* Amber 400 */
      --warning-foreground: #451a03;
    
      --destructive: #ff3333;
      /* Neon Red - High Saturation */
      --destructive-foreground: #450a0a;
    
      /* True Glass Vars */
      --glass-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      /* Heavy floating shadow */
      --card-blur: blur(20px);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.2);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.4);
}

.dark ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

@layer base {
  body {
    @apply bg-[var(--bg-app)] text-[var(--text-primary)] antialiased;
    font-family: 'Geist Sans', 'SF Pro Display', var(--font-sans);
    margin: 0;
    padding: 0;
    overflow-x: hidden;
      background: #020617;
      /* Slate 950 */
      position: relative;
    }
    
    body::before {
      content: '';
      position: fixed;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle at center, rgba(34, 211, 238, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.03) 0%, transparent 40%);
      background-size: 100% 100%;
      animation: meshMove 20s ease-in-out infinite alternate;
      pointer-events: none;
      z-index: -1;
    }
    
    /* Liquid Feel - Moving Mesh Animation */
    @keyframes meshMove {
      0% {
        transform: translate(0, 0) scale(1);
      }
    
      100% {
        transform: translate(-2%, -2%) scale(1.05);
      }
    }
    
    #root {
      margin: 0;
      padding: 0;
    min-height: 100vh;
      width: 100%;
  }
}

@layer utilities {
  .text-hero {
    @apply text-7xl font-bold tracking-tighter;
  }
}

@layer components {
  /* Common Glass Base */
  .glass-base {
    @apply bg-[var(--bg-card)] border border-t-white/10 border-l-white/10 border-r-white/5 border-b-white/5;
    backdrop-filter: var(--card-blur);
    box-shadow: var(--glass-shadow);
  }

  .card {
    @apply glass-base rounded-2xl p-5 transition-all duration-300;
  }
    
  .glass-panel {
    @apply glass-base;
  }

  .card:hover {
    @apply border-white/20;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
    transform: translateY(-2px);
  }
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

/* 
  EMERGENCY PURGE: Shadow DOM Glow & Vignette 
  These target the search-defiant #preact-border-shadow-host
*/
#preact-border-shadow-host {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

[id*="preact-border-shadow"] {
  display: none !important;
}

.animate-breathing {
  animation: none !important;
}

/* Ensure all decorative vignettes are non-blocking */
div[class*="vignette"],
div[class*="glow-overlay"] {
  display: none !important;
  pointer-events: none !important;
}
"""

import os
with open('frontend/src/index.css', 'w') as f:
    f.write(css_content.strip())
print("Successfully wrote index.css")
