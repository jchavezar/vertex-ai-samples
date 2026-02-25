// Initialize Lenis for smooth scrolling
const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smooth: true,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// Register GSAP ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// Custom Cursor Logic
const cursor = document.querySelector('.cursor-follower');

document.addEventListener('mousemove', (e) => {
    gsap.to(cursor, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.1,
        ease: 'power2.out'
    });
});

document.addEventListener('mousedown', () => {
    gsap.to(cursor, { scale: 0.5, duration: 0.1 });
});

document.addEventListener('mouseup', () => {
    gsap.to(cursor, { scale: 1, duration: 0.1 });
});

// Parallax Effects via GSAP
gsap.utils.toArray('.section').forEach(section => {
    gsap.to(section, {
        scrollTrigger: {
            trigger: section,
            start: "top bottom",
            end: "bottom top",
            scrub: true
        },
        backgroundPosition: "50% 100%", // Subtle parallax if bg image
        ease: "none"
    });
});

// Hero Parallax
gsap.to('.hero-image-wrapper', {
    scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: 'bottom top',
        scrub: true
    },
    y: 100,
    rotation: 5
});

// Flowing Text Animation
gsap.to('.flowing-text', {
    xPercent: -50,
    ease: "none",
    scrollTrigger: {
        trigger: ".philosophy",
        start: "top bottom",
        end: "bottom top",
        scrub: 1
    }
});

// Liquid Mask Animation on Scroll
gsap.to('.liquid-mask', {
    clipPath: 'circle(70% at 50% 50%)',
    scrollTrigger: {
        trigger: '.bio',
        start: 'top center',
        end: 'bottom center',
        scrub: 1
    }
});

// Infinite Scroll Simulation (Cloning items for demo)
const portfolioSection = document.querySelector('.portfolio');
const items = document.querySelectorAll('.portfolio-item');

// Clone items to simulate infinite list
items.forEach(item => {
    const clone = item.cloneNode(true);
    portfolioSection.appendChild(clone);
    const clone2 = item.cloneNode(true);
    portfolioSection.appendChild(clone2);
});
