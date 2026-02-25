gsap.registerPlugin(ScrollTrigger);

// Loader
window.addEventListener('load', () => {
    gsap.to('.loader-overlay', {
        yPercent: -100,
        duration: 1,
        ease: 'power4.inOut',
        delay: 0.5
    });
});

// Horizontal Scroll Setup
const wrapper = document.querySelector('.horizontal-scroll-wrapper');
const panels = gsap.utils.toArray('.panel');

gsap.to(panels, {
    xPercent: -100 * (panels.length - 1),
    ease: "none",
    scrollTrigger: {
        trigger: ".horizontal-scroll-wrapper",
        pin: true,
        scrub: 1,
        snap: 1 / (panels.length - 1),
        // base vertical scrolling on how wide the container is so it feels natural.
        end: () => "+=" + wrapper.offsetWidth
    }
});

// Parallax for Hero Image inside mask
gsap.to('.cave-mask img', {
    x: -100, // Move image slightly horizontally as we scroll
    scrollTrigger: {
        trigger: '.hero',
        containerAnimation: null, // It's the first panel, so standard trigger works or we bind to container?
        // Actually for horizontal scroll pinned, internal animations need containerAnimation
        // BUT hero is first, so we can just use scrub on the main tween? 
        // Simpler: Animating based on main scroll
        trigger: '.horizontal-scroll-wrapper',
        start: 'top top',
        end: 'bottom bottom',
        scrub: true
    }
});

// Animate shapes in Bio section
// Note: containerAnimation property is needed for ScrollTrigger sections inside a horizontal scroll
const scrollTween = gsap.getTweensOf(panels)[0];

gsap.from('.shaping-mask', {
    scale: 0.8,
    rotation: -5,
    opacity: 0,
    scrollTrigger: {
        trigger: '.bio',
        containerAnimation: scrollTween,
        start: 'left center',
        toggleActions: 'play none none reverse'
    }
});

gsap.from('.project-card', {
    y: 100,
    opacity: 0,
    stagger: 0.1,
    scrollTrigger: {
        trigger: '.projects',
        containerAnimation: scrollTween,
        start: 'left center',
        toggleActions: 'play none none reverse'
    }
});

// Lenis for smooth touch feeling (even though we are faking horizontal with scroll)
const lenis = new Lenis({
    orientation: 'vertical',
    gestureOrientation: 'vertical',
    smooth: true,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}

requestAnimationFrame(raf);
