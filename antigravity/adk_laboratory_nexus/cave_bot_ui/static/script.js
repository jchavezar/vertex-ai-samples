gsap.registerPlugin(ScrollTrigger);

// 1. Lenis Smooth Scroll
const lenis = new Lenis({
    lerp: 0.1,
    orientation: 'vertical',
    gestureOrientation: 'vertical',
    smooth: true,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// 2. Horizontal Scroll Logic
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
        end: () => "+=" + wrapper.offsetWidth
    }
});

// 3. Entrance Animation for Chat
gsap.to('.panel-sculpt', {
    opacity: 1,
    y: 0,
    duration: 1.5,
    ease: "power4.out",
    scrollTrigger: {
        trigger: '.chat-section',
        containerAnimation: gsap.getTweensOf(panels)[0], // Link to horizontal scroll
        start: 'left center',
    }
});

// 4. Chat Functionality
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Append User Message
    appendMessage(text, 'user');
    userInput.value = '';

    // Typing indicator
    const typingId = 'typing-' + Date.now();
    appendMessage('...', 'bot', typingId);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();

        // Replace typing with bot message
        document.getElementById(typingId).remove();

        if (data.is_structured) {
            renderDesignCard(data.response);
        } else {
            appendMessage(data.response, 'bot');
        }
    } catch (err) {
        document.getElementById(typingId).innerText = "The void is silent. (Error)";
    }
}

function renderDesignCard(advice) {
    const card = document.createElement('div');
    card.className = 'message bot design-card';
    card.innerHTML = `
        <div class="pillar-tag">${advice.pillar}</div>
        <p>${advice.suggestion}</p>
        <div class="hint">${advice.implementation_hint}</div>
    `;
    chatMessages.appendChild(card);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendMessage(text, role, id = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    if (id) msgDiv.id = id;
    msgDiv.innerText = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 5. Scroll Isolation Logic
// Prevent Lenis from handling scroll events when hovering over the chat
const chatContainer = document.querySelector('.chat-container');

chatContainer.addEventListener('mouseenter', () => {
    lenis.stop();
});

chatContainer.addEventListener('mouseleave', () => {
    lenis.start();
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
