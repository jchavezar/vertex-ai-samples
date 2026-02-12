# 📦 Modern Cave Boilerplate (HTML/CSS)

## HTML Structure
```html
<div class="loader-overlay">LOADING VOID</div>

<nav class="monolith-nav">
    <div class="logo">MNLTH</div>
</nav>

<div class="horizontal-scroll-wrapper">
    <section class="panel hero">
        <h1 class="hero-title">TITLE</h1>
    </section>
    <section class="panel content" id="next">
        <!-- Content here -->
    </section>
</div>
```

## CSS Core
```css
:root {
    --bg: #dcd7cd;
    --text: #2a2826;
    --monolith: #1a1918;
}

body {
    background-color: var(--bg);
    color: var(--text);
    overflow-x: hidden;
}

.horizontal-scroll-wrapper {
    display: flex;
    flex-wrap: nowrap;
    width: 300%; /* Adjust per panel count */
    height: 100vh;
}

.panel {
    width: 100vw;
    height: 100vh;
    flex-shrink: 0;
}
```
