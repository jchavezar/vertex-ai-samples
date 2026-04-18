console.log('Sovereign Elements Loaded');

document.querySelector('.search-bar input').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = '';
    
    if (query.length > 2) {
        const mockResults = [
            'Abstract Template',
            'Corporate Mockup',
            'Neon UI Kit',
            'Glassmorphism Assets'
        ];
        
        const filtered = mockResults.filter(item => item.toLowerCase().includes(query));
        
        if (filtered.length > 0) {
            suggestions.style.display = 'block';
            filtered.forEach(item => {
                const div = document.createElement('div');
                div.textContent = item;
                div.className = 'suggestion-item';
                div.addEventListener('click', () => {
                    e.target.value = item;
                    suggestions.style.display = 'none';
                });
                suggestions.appendChild(div);
            });
        }
    } else {
        suggestions.style.display = 'none';
    }
});

