
css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Typography - The "Geist" Feel */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: 'JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', monospace;

  /* CORE PALETTE: "Architectural Void" */
  --bg-app: #030303;           /* True Void */
  --bg-panel: #0a0a0a;         /* Surface Level 1 */
  --bg-card: #111111;          /* Surface Level 2 */
  
  /* BORDERS: "The Photon Edge" */
  --border: #333333;           /* Standard structural border */
  --border-subtle: #222222;    /* Grid lines */
  --border-highlight: #555555; /* Hover state */
  
  /* TEXT: High Contrast & Precision */
  --text-primary: #ededed;     /* Almost white */
  --text-secondary: #a1a1aa;   /* Zinc 400 */
  --text-muted: #52525b;       /* Zinc 600 - Metadata */
  
  /* ACCENTS: "Glow" */
  --brand: #ffffff;            /* Vercel-style white brand */
  --accent: #29bc9b;           /* Subtle Mint (Stock Up) */
  --danger: #f55a4e;           /* Subtle Coral (Stock Down) */
  --blue-glow: #3291ff;        /* Vercel Blue */
  
  /* SPACING & Layout */
  --header-height: 64px;
}

/* Base Styles */
@layer base {
  body {
    @apply bg-[var(--bg-app)] text-[var(--text-primary)] antialiased leading-relaxed overflow-x-hidden;
    font-family: var(--font-sans);
    letter-spacing: -0.015em; /* Tight tracking like Geist */
  }

  /* The "Grid" Background */
  body::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(to right, var(--border-subtle) 1px, transparent 1px),
      linear-gradient(to bottom, var(--border-subtle) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
    opacity: 0.15;
    pointer-events: none;
    z-index: -1;
  }
}

/* Utilities */
@layer utilities {
  .tracking-tighter-hero {
    letter-spacing: -0.04em;
  }
  
  .text-glow {
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
  }
}

/* Components - The "Architectural" System */
@layer components {
  /* 
     Base Card: No more blurry glass. 
     Now: Solid, dark, precise 1px borders.
  */
  .arch-card {
    @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] relative overflow-hidden;
  }

  /* Hover "Spotlight" Simulation */
  .arch-card:hover {
    border-color: var(--border-highlight);
    box-shadow: 0 0 30px -10px rgba(255, 255, 255, 0.1);
  }

  /* Inner Content Padding */
  .arch-inner {
    @apply p-6;
  }

  /* Terminal/Code Look */
  .font-mono-numbers {
    font-family: var(--font-mono);
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
  }
  
  /* Buttons */
  .btn-arch {
    @apply px-4 py-2 rounded-md font-medium text-sm transition-all;
    background: var(--text-primary);
    color: var(--bg-app);
    border: 1px solid var(--text-primary);
  }
  
  .btn-arch:hover {
    background: transparent;
    color: var(--text-primary);
  }
  
  .btn-arch-ghost {
    @apply px-4 py-2 rounded-md font-medium text-sm transition-all;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-secondary);
  }
  
  .btn-arch-ghost:hover {
    border-color: var(--text-primary);
    color: var(--text-primary);
  }
}

/* Scrollbar - Minimal */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: var(--bg-app);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Recharts Overrides for Dark Mode */
.recharts-cartesian-grid-horizontal line,
.recharts-cartesian-grid-vertical line {
  stroke: var(--border-subtle) !important;
  stroke-opacity: 0.5;
}

.recharts-tooltip-cursor {
  stroke: var(--text-muted) !important;
  stroke-dasharray: 3 3;
}
"""

with open('frontend/src/index.css', 'w') as f:
    f.write(css_content)

print("Successfully wrote index.css")
