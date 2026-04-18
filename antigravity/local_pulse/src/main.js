import './style.css';

let activeSpots = [];
const API_BASE_URL = 'http://localhost:8555'; // Using verified port 8555

const chatHistory = [
  { role: 'ai', text: "Hello! I'm your Local Pulse Concierge. Looking for a specific vibe or activity today?" }
];

// DOM Elements
let appEl;
let modalEl;

function init() {
  appEl = document.querySelector('#app');
  
  appEl.innerHTML = `
    <header>
      <div class="logo">LOCAL PULSE</div>
      <div class="search-container">
        <input type="text" id="search-input" placeholder="Search a vibe... 'cyberpunk sushi' or 'quiet park'..." />
        <button class="search-btn" id="search-btn">Scan</button>
      </div>
      <div class="controls">
        <button class="filter-btn active" data-filter="all">All Vibes</button>
        <button class="filter-btn" data-filter="food">Glow Food</button>
        <button class="filter-btn" data-filter="nature">Lush Escape</button>
        <button class="filter-btn" data-filter="cafe">Acoustic Cafes</button>
      </div>
    </header>

    <main>
      <div class="pulse-grid" id="grid"></div>
    </main>

    <div class="chat-container">
      <div class="chat-bubble" id="chat-toggle">💬</div>
      <div class="chat-window" id="chat-window">
        <div class="chat-header">
          <div class="chat-title"><span class="status-dot"></span> Vibe Concierge</div>
          <button class="chat-close" id="chat-close">✕</button>
        </div>
        <div class="chat-messages" id="chat-messages"></div>
        <div class="chat-input-area">
          <input type="text" id="chat-input" placeholder="Ask about spots..." />
          <button class="chat-send" id="chat-send">➔</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal" id="modal">
      <div class="modal-content">
        <div class="modal-hero">
          <img id="modal-img" src="" alt="">
          <button class="modal-close" id="modal-close-btn">✕</button>
        </div>
        <div class="modal-body">
          <h2 id="modal-title" class="modal-title"></h2>
          <div class="modal-meta" id="modal-meta"></div>
          <div class="modal-summary" id="modal-summary"></div>
          <div class="review-section" id="modal-reviews"></div>
        </div>
      </div>
    </div>
  `;

  // Set default search
  document.querySelector('#search-input').value = 'Miami';
  handleSearch();

  renderChat();
  setupEvents();
}

function renderGrid(data) {
  const grid = document.querySelector('#grid');
  grid.innerHTML = '';

  data.forEach(spot => {
    const card = document.createElement('div');
    card.className = 'card';
    card.setAttribute('data-id', spot.id);
    
    card.innerHTML = `
      <img src="${spot.image || `/images/placeholder_${spot.category && ['food', 'nature', 'cafe'].includes(spot.category) ? spot.category : 'nature'}.png`}" class="card-image" alt="${spot.title}">
      <div class="card-header">
        <div class="card-title">${spot.title}</div>
        <div class="card-rating">⭐ ${spot.rating || 'N/A'}</div>
      </div>
      <p class="card-desc">${spot.desc}</p>
      <div class="card-tags">
        ${spot.tags.map(tag => `<span class="tag ${tag}">${tag === 'insta' ? 'Instagram' : tag === 'tube' ? 'YouTube' : 'Blog'}</span>`).join('')}
      </div>
    `;

    card.addEventListener('click', () => openModal(spot));
    grid.appendChild(card);
  });
}

function renderChat() {
  const container = document.querySelector('#chat-messages');
  container.innerHTML = '';
  chatHistory.forEach(msg => {
    const el = document.createElement('div');
    el.className = `msg ${msg.role}`;
    el.innerText = msg.text;
    container.appendChild(el);
  });
  container.scrollTop = container.scrollHeight;
}

function setupEvents() {
  // Search
  document.querySelector('#search-btn').addEventListener('click', handleSearch);
  document.querySelector('#search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
  });

  // Filters
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      const filter = e.target.getAttribute('data-filter');
      if (filter === 'all') {
        renderGrid(activeSpots);
      } else {
        renderGrid(activeSpots.filter(s => s.category === filter));
      }
    });
  });

  // Chat Toggle
  document.querySelector('#chat-toggle').addEventListener('click', toggleChat);
  document.querySelector('#chat-close').addEventListener('click', toggleChat);

  // Chat Send
  document.querySelector('#chat-send').addEventListener('click', sendChatMessage);
  document.querySelector('#chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });

  // Modal Close
  document.querySelector('#modal-close-btn').addEventListener('click', closeModal);
  document.querySelector('#modal').addEventListener('click', (e) => {
    if (e.target === document.querySelector('#modal')) closeModal();
  });
}

async function handleSearch() {
  const query = document.querySelector('#search-input').value.trim();
  if (!query) return;

  const grid = document.querySelector('#grid');
  grid.innerHTML = '<div class="loading">Scanning the pulse...</div>';

  try {
    const response = await fetch(`${API_BASE_URL}/api/spots?query=${encodeURIComponent(query)}`);
    let data = await response.json();
    
    // Robust parsing for double-encoded JSON
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data);
        if (typeof data === 'string') {
          data = JSON.parse(data);
        }
      } catch (e) {
        grid.innerHTML = `<div class="error">Parse failed: ${e.message}</div>`;
        return;
      }
    }
    
    if (data.error) {
      grid.innerHTML = `<div class="error">Pulse check failed: ${data.error}</div>`;
      return;
    }

    activeSpots = data; // Data is parsed JSON from the two-step process
    renderGrid(activeSpots);
  } catch (error) {
    grid.innerHTML = `<div class="error">Connection to pulse lost: ${error.message}</div>`;
  }
}

function toggleChat() {
  document.querySelector('#chat-window').classList.toggle('active');
}

function sendChatMessage() {
  const input = document.querySelector('#chat-input');
  const text = input.value.trim();
  if (!text) return;

  chatHistory.push({ role: 'user', text });
  renderChat();
  input.value = '';

  // Simulate AI Response
  setTimeout(() => {
    let reply = "I see! Let me check the pulse for that.";
    if (text.toLowerCase().includes('food') || text.toLowerCase().includes('eat')) {
      reply = "For food, I highly recommend the Neon Sakura Sushi Lounge. People love the Truffle Toro!";
    } else if (text.toLowerCase().includes('quiet') || text.toLowerCase().includes('walk')) {
      reply = "The Glass Greenhouse is perfect for a quiet walk. It has bio-luminescent plants!";
    }
    chatHistory.push({ role: 'ai', text: reply });
    renderChat();
  }, 1000);
}

function openModal(spot) {
  const modal = document.querySelector('#modal');
  
  // Fallback for image
  const imgEl = document.querySelector('#modal-img');
  imgEl.src = spot.image || `/images/placeholder_${spot.category && ['food', 'nature', 'cafe'].includes(spot.category) ? spot.category : 'nature'}.png`;
  imgEl.alt = spot.title;

  document.querySelector('#modal-title').innerText = spot.title;
  document.querySelector('#modal-meta').innerText = `${spot.type} • ⭐ ${spot.rating || 'N/A'}`;
  document.querySelector('#modal-summary').innerText = spot.summary;

  const reviewsContainer = document.querySelector('#modal-reviews');
  reviewsContainer.innerHTML = '<h3>Recent Pulses</h3>';
  
  if (spot.reviews && spot.reviews.length > 0) {
    spot.reviews.forEach(r => {
      reviewsContainer.innerHTML += `
        <div class="review-card">
          <div class="review-header">
            <span class="review-author">${r.author}</span>
            <span class="review-date">${r.date}</span>
          </div>
          <p>${r.text}</p>
        </div>
      `;
    });
  } else {
    reviewsContainer.innerHTML += `<p>No recent pulses found for this specific spot, but it is highly recommended by local sources!</p>`;
  }

  // Add Similar Spots UI
  reviewsContainer.innerHTML += `
    <div class="similar-section" style="margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
      <h3>Find Similar Vibes</h3>
      <button class="btn btn-primary" id="btn-find-similar" style="width: 100%; margin-top: 1rem;">Discover Similar Spots</button>
      <div id="similar-loading" class="loading-spinner" style="display: none; text-align: center; margin: 1rem 0;">Scanning similar pulses...</div>
      <div id="similar-grid" class="grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); margin-top: 1rem;"></div>
    </div>
  `;

  modal.classList.add('active');

  // Event listener for similar button
  setTimeout(() => {
    const btn = document.querySelector('#btn-find-similar');
    if (btn) {
      btn.onclick = () => fetchSimilarSpots(spot.title);
    }
  }, 100);
}

function closeModal() {
  document.querySelector('#modal').classList.remove('active');
}

async function fetchSimilarSpots(title) {
  const grid = document.querySelector('#similar-grid');
  const loading = document.querySelector('#similar-loading');
  grid.innerHTML = '';
  loading.style.display = 'block';

  try {
    const response = await fetch(`${API_BASE_URL}/api/spots/similar?title=${encodeURIComponent(title)}`);
    const data = await response.json();
    loading.style.display = 'none';
    
    if (data && data.length > 0) {
      grid.innerHTML = data.map(spot => `
        <div class="similar-card" style="padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
          <small>${spot.title}</small>
        </div>
      `).join('');
    } else {
      grid.innerHTML = '<p>No similar vibes found.</p>';
    }
  } catch (err) {
    loading.style.display = 'none';
    grid.innerHTML = '<p>Search error.</p>';
  }
}

// Start
document.addEventListener('DOMContentLoaded', init);
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  init(); // Fallback if DOM loaded before script
}
