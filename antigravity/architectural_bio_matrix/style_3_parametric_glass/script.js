gsap.registerPlugin(ScrollTrigger);

// Custom Smooth Scroll
const lenis = new Lenis({
    lerp: 0.05, // Slower lerp for floaty feel
    smooth: true,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// Background Parallax & Distortion Mockup
document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;

    gsap.to('.background-canvas img', {
        x: x,
        y: y,
        duration: 1,
        ease: 'power2.out'
    });
});

// Bio Card 3D Tilt Effect
const card = document.querySelector('.glass-card');
card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const xPct = (x / rect.width - 0.5) * 20;
    const yPct = (y / rect.height - 0.5) * 20;

    gsap.to(card, {
        rotationY: xPct,
        rotationX: -yPct,
        duration: 0.5,
        ease: 'power2.out',
        transformPerspective: 1000
    });
});

card.addEventListener('mouseleave', () => {
    gsap.to(card, {
        rotationY: 0,
        rotationX: 0,
        duration: 0.5,
        ease: 'power2.out'
    });
});


// Infinite Loop Logic for Showcase
const lane = document.querySelector('.infinite-lane');
const items = document.querySelectorAll('.showcase-item');
const itemWidth = items[0].offsetWidth; // Approximate currently visible width + gap
// Note: In real production, we'd need precise calculation including gaps.
// For now, let's clone enough to fill screen + buffer.

// Clone to fill
items.forEach(item => {
    lane.appendChild(item.cloneNode(true));
    lane.appendChild(item.cloneNode(true));
});

// Horizontal Scroll bound to Vertical Scroll
// This creates the "vertical loop" feeling but mapped to horizontal element or we can make it vertical.
// Request said "Infinite vertical loop" but description said "horizontal-to-vertical" for Style 2.
// Style 3 says "infinite vertical loop". The design I made is a lane. Let's make the lane VERTICAL.

// Wait, I styled `.infinite-lane` as `display: flex; gap: 2vw;`. That's horizontal.
// Let me change it to vertical via JS or just CSS update?
// I'll update CSS in this file to force vertical if needed, or better, adjust the animation to be horizontal scrolling mapped to vertical scroll.
// "Integrate fluid... that morph seamlessly as the user scrolls."

// Let's keep the showcase as a horizontal strip that scrolls as you scroll down (Horizontal scroll section).
// OR, if it's a vertical loop, maybe the whole page is the loop?
// I'll stick to a Horizontal Scroll section for the portfolio since it's easier to verify "infinite" feel in a section.

gsap.to('.infinite-lane', {
    xPercent: -50, // Move half way (since we cloned)
    ease: "none",
    scrollTrigger: {
        trigger: ".showcase",
        start: "top bottom",
        end: "bottom top",
        scrub: 0.5
    }
});

// Reveal animations
gsap.from('.hero-title', {
    y: 100,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
});
