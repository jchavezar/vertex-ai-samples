# 🎨 Modern Cave Design Tokens

## Color Palette (Mineral & Earth)
- **Primary Background**: `#dcd7cd` (Bleached Bone)
- **Main Text**: `#2a2826` (Obsidian)
- **Monolith Black**: `#1a1918` (Basalt)
- **Accent Gray**: `#c9c4b9` (Concrete)

## Typography
- **Monospace (Secondary/Utility)**: 
  ```css
  font-family: 'Courier New', Courier, monospace;
  letter-spacing: 0.1rem;
  text-transform: uppercase;
  ```
- **Display (Hero/Headers)**:
  ```css
  font-family: 'Inter', sans-serif; /* High-quality sans */
  font-weight: 900;
  line-height: 0.8;
  letter-spacing: -0.05em;
  ```

## Layout
- **Container**: `100vw` / `100vh` panels only.
- **Sectioning**: Mandatory horizontal scroll via `flex-nowrap`.
- **Spacing**: Use `vw` and `vh` units to maintain a monolithic, viewport-filling feel.
