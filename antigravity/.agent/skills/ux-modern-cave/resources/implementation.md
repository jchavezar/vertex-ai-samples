# 🛠️ "Modern Cave" Implementation Guide

## 1. The Horizontal Engine (GSAP)
The "Modern Cave" feel relies on a horizontal journey driven by vertical scrolling.

```javascript
// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

const wrapper = document.querySelector('.horizontal-scroll-wrapper');
const panels = gsap.utils.toArray('.panel');

gsap.to(panels, {
    xPercent: -100 * (panels.length - 1),
    ease: "none",
    scrollTrigger: {
        trigger: ".horizontal-scroll-wrapper",
        pin: true,           // Pins the sections in the viewport
        scrub: 1,            // Smoothly tracks the scrollbar
        snap: 1 / (panels.length - 1),
        end: () => "+=" + wrapper.offsetWidth // Natural scroll length
    }
});
```

## 2. Smooth Scrolling (Lenis)
Essential for the "Premium" feeling.

```javascript
const lenis = new Lenis({
    lerp: 0.1,         // Smoothness factor
    wheelMultiplier: 1, // Sensitivity
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);
```

## 3. "Carved" Typography (CSS)
Use `mix-blend-mode` to make text interact with the background and images.

```css
.hero-title {
    font-size: 10vw;
    text-transform: uppercase;
    mix-blend-mode: difference; /* Inverts colors based on background */
    color: white;
    z-index: 10;
}
```

## 4. Geometric Masking
Create organic, architectural shapes.

```css
.cave-mask {
    clip-path: polygon(15% 0%, 100% 0%, 85% 100%, 0% 100%);
    overflow: hidden;
}

.arch-container {
    border-radius: 200px 200px 0 0; /* Modern Pillar/Arch */
    transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.arch-container:hover {
    border-radius: 0 0 200px 200px; /* Morph transition */
}
```
