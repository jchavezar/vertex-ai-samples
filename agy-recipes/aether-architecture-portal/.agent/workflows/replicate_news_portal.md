---
description: Replicate the Verge-inspired interactive news chat portal with local Express proxy backend, Vertex AI Gemini integration, Google Search grounding, and viewport-locked light theme layout.
---

1. **Verify Local Environment Runtimes**
   Ensure that Node.js (v22+ recommended), npm (10+ recommended), and Python 3 are installed on the local system by running:
   ```bash
   node -v && npm -v && python3 --version
   ```

2. **Scaffold React Vite Application**
   Initialize a new React frontend application in a directory named `news-chat-portal` in non-interactive mode:
   ```bash
   npx -y create-vite@latest news-chat-portal --template react --no-interactive
   ```
   Navigate into the directory and install default dependencies:
   ```bash
   cd news-chat-portal
   npm install
   ```

3. **Configure Ironclad Gitignore for Zero-Leak Security**
   Open the `.gitignore` file in the project root and append the following mandatory block to prevent accidental credential leakage:
   ```gitignore
   # Data & Secrets (MANDATORY)
   .env
   .env.*
   !.env.example
   *.pem
   *.key
   *.p12
   *.pfx
   client_secret*.json
   credentials.json
   *_token.json
   ```

4. **Initialize Mock News Database**
   Create a new file `src/data/news.js` to store the news feed data. Copy and save this content:
   ```javascript
   export const newsArticles = [
     {
       id: "apple-vr-headset-pro",
       category: "REVIEWS",
       title: "Apple Vision Pro 2 review: The future is lighter, but still isolated",
       subtitle: "Apple's second-generation spatial computer fixes the comfort, but the killer app is still missing.",
       summary: "The Apple Vision Pro 2 arrives with a 20% lighter build, dual-chip architecture, and an improved eye-tracking system. Yet, at $3,299, it remains a solitary luxury in search of a shared purpose.",
       content: `Apple’s first Vision Pro was a marvel of engineering that was too heavy to wear for more than an hour. The new Vision Pro 2 solves the physical comfort problem. Weighing in at 480 grams (down from 650 grams), it uses a carbon-fiber chassis and a redesigned Solo Knit Band that distributes weight much more evenly.

   Under the hood, Apple has replaced the M2/R1 combo with the M4 and the new R2 spatial co-processor. The passthrough latency is down to a imperceptible 9 milliseconds, and the micro-OLED displays are 30% brighter with deeper contrast. 

   The software, visionOS 3.0, introduces virtual workspaces that can wrap 360 degrees around you. You can pin a 150-inch virtual Mac display, a Slack workspace, and a floating movie screen in your physical room without any stutter. The eye-tracking has been refined; it now uses machine learning to predict where your gaze is moving, reducing lag to near-zero.

   However, the fundamental question remains: what is this for? Despite the hardware refinements, the Vision Pro 2 is still a solitary experience. There is no shared VR environment that feels natural, and the 'Personas' (digital avatars) still look uncanny, like CGI ghosts. For $3,299, you get the absolute best virtual monitor money can buy, but you are still sitting alone in a room wearing a mask.`,
       author: "Nilay Patel",
       date: "10:15 AM EDT",
       readTime: "8 min read",
       accentColor: "#ff005b",
       imageGradient: "linear-gradient(135deg, #ff005b, #5200ff)"
     },
     {
       id: "gemini-3-agents",
       category: "TECH",
       title: "Google AI launches Gemini 3: Autonomous agents that can browse, code, and execute local tasks",
       subtitle: "The search giant releases its next-generation model with built-in sandbox environments.",
       summary: "Google's new Gemini 3-pro-preview model introduces native tool execution, letting the AI run code, interact with web browsers, and coordinate sub-agents directly in isolated containers.",
       content: `Google today announced the public beta of Gemini 3-pro-preview, its most advanced AI model designed specifically for autonomous agent workflows. Unlike previous models that rely on external wrappers to execute actions, Gemini 3 has a native executor loop built directly into the model's core architecture.

   This means the AI can write code, spin up an isolated Docker container, run the code, analyze the output, and fix its own errors without returning control to the host application. The model also features an integrated headless Chrome instance, allowing it to navigate the web, fill out forms, bypass simple bot checks, and retrieve information dynamically.

   Google's CEO emphasized the security measures taken with this release: 'We have implemented a zero-trust execution sandbox that limits agent operations to virtual file systems. The model cannot access network resources or execute host commands without explicit user permission.'

   Developers can access Gemini 3 via the Google Cloud Vertex AI API. The model supports a 2-million token context window, enabling it to analyze entire codebases or hundreds of pages of documentation in a single prompt. Early testers report a 40% improvement in complex task completion compared to Gemini 1.5 Pro.`,
       author: "Dieter Bohn",
       date: "8:00 AM EDT",
       readTime: "5 min read",
       accentColor: "#5200ff",
       imageGradient: "linear-gradient(135deg, #5200ff, #00f0ff)"
     },
     {
       id: "fusion-power-grid",
       category: "SCIENCE",
       title: "Net energy gain: Helion Energy claims fusion power will feed the grid by 2028",
       subtitle: "A commercial fusion power agreement with Microsoft is entering its final validation phase.",
       summary: "Helion Energy's magneto-inertial fusion generator Polaris has successfully maintained plasma temperatures of 100 million degrees, bringing commercial fusion closer to reality.",
       content: `For decades, nuclear fusion has been '30 years away.' Helion Energy, a startup backed by Sam Altman, claims they will break that curse by 2028. Under a commercial agreement signed with Microsoft, Helion is contracted to deliver at least 50 megawatts of electricity from its fusion power plant, or pay penalties.

   Helion's approach is different from the massive tokamaks used by government projects. Instead of holding a burning plasma in place using giant superconducting magnets, Helion uses a pulsed magneto-inertial fusion system. Their seventh-generation prototype, Polaris, shoots two rings of plasma into a central chamber at over 1 million miles per hour, compressing them with a high-power magnetic field to achieve fusion conditions.

   In recent tests, Polaris sustained plasma temperatures exceeding 100 million degrees Celsius for a record duration. More importantly, Helion's system recovers electricity directly from the expansion of the magnetic field after the fusion reaction, avoiding the need to heat water to run a steam turbine.

   Critics remain skeptical, noting that achieving net electricity (Q-system > 1) and exporting it to the grid involves immense materials science hurdles that Helion hasn't fully solved. But with Microsoft's data center power needs skyrocketing due to AI workloads, the tech giant is betting big on Helion's success.`,
       author: "Elizabeth Lopatto",
       date: "Yesterday",
       readTime: "6 min read",
       accentColor: "#00e5ff",
       imageGradient: "linear-gradient(135deg, #00e5ff, #00ff66)"
     },
     {
       id: "steam-deck-2-leak",
       category: "GAMING",
       title: "Exclusive: Leaked Valve documents reveal Steam Deck 2 specs and release window",
       subtitle: "A custom AMD 'Zen 5c' APU, OLED by default, and a new variable refresh rate display are coming.",
       summary: "Valve is preparing the true successor to the Steam Deck, targeting a Fall 2027 launch with double the graphics performance and significantly improved battery efficiency.",
       content: `Internal design documents from Valve, leaked on an online gaming forum, have revealed the hardware specifications and launch targets for the highly anticipated Steam Deck 2. 

   The documents outline a brand new custom APU developed with AMD, codenamed 'Little Bigfoot.' It features 6 Zen 5c processor cores and a GPU based on the RDNA 4 architecture, offering roughly 2.2 times the raw graphics throughput of the original Steam Deck. 

   The display is listed as a 7.6-inch OLED panel with a 120Hz refresh rate and support for Variable Refresh Rate (VRR) down to 30Hz, solving the screen-tearing issues of the current OLED model. Resolution remains at a battery-friendly 1280x800, which will allow the upgraded GPU to run modern AAA titles at high settings with ease.

   Valve is targeting a target price point of $449 for the base model (which now starts with 256GB NVMe storage) and is aiming for a release window of October or November 2027. Valve has declined to comment on the leak.`,
       author: "Sean Hollister",
       date: "June 7, 2026",
       readTime: "4 min read",
       accentColor: "#ffb800",
       imageGradient: "linear-gradient(135deg, #ffb800, #ff005b)"
     },
     {
       id: "css-grid-level-3",
       category: "DESIGN",
       title: "CSS Grid Level 3: Masonry is finally coming to native web layouts",
       subtitle: "W3C agrees on the syntax, paving the way for browser implementations without external JS libraries.",
       summary: "After years of debate, browser vendors have aligned on the native CSS masonry grid layout, eliminating the need for complex JavaScript calculation scripts.",
       content: `For years, developers wanting a Pinterest-like masonry layout had to rely on heavy JavaScript libraries like Masonry.js or CSS hacks using multi-column properties. That is finally changing. The W3C CSS Working Group has finalized the CSS Grid Layout Module Level 3, introducing the native 'masonry' value for the grid-template-rows and grid-template-columns properties.

   The syntax is elegant:
   \`\`\`css
   .container {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
     grid-template-rows: masonry;
   }
   \`\`\`
   This lets the browser automatically place grid items in the column with the most available space, creating a beautiful masonry layout natively. It supports items spanning multiple columns, and items can be aligned to 'tracks' if needed.

   Performance is where native masonry shines. Because the browser layout engine calculates the offsets during the initial rendering cycle, there are no layout reflows or resizing lag, which often caused visible stuttering in JavaScript-based solutions. Safari and Firefox Nightly have already shipped experimental support, and Chrome is expected to follow by late summer.`,
       author: "Chris Welch",
       date: "June 6, 2026",
       readTime: "3 min read",
       accentColor: "#00ff66",
       imageGradient: "linear-gradient(135deg, #00ff66, #ffb800)"
     }
   ];
   ```

5. **Create the Local Express Proxy Server**
   To bypass browser CORS and authenticate securely via Google Cloud Application Default Credentials (ADC), create a `server` directory and configure the backend service.
   
   Create `server/package.json`:
   ```json
   {
     "name": "news-chat-portal-backend",
     "version": "1.0.0",
     "description": "Backend proxy for news chat portal using Google Cloud ADC",
     "main": "index.js",
     "type": "module",
     "scripts": {
       "start": "node index.js"
     },
     "dependencies": {
       "cors": "^2.8.5",
       "express": "^4.21.2",
       "google-auth-library": "^9.15.0"
     }
   }
   ```
   Install backend dependencies:
   ```bash
   cd server
   npm install
   cd ..
   ```
   
   Create `server/index.js` which performs credential checking, active project overrides, enables googleSearch tools, and routes calls:
   ```javascript
   import express from 'express';
   import cors from 'cors';
   import { GoogleAuth } from 'google-auth-library';

   const app = express();
   const PORT = process.env.PORT || 8001;

   app.use(cors({
     origin: 'http://localhost:5173',
     credentials: true
   }));

   app.use(express.json());

   const auth = new GoogleAuth({
     scopes: 'https://www.googleapis.com/auth/cloud-platform'
   });

   app.post('/api/chat', async (req, res) => {
     try {
       const { contents, systemInstruction } = req.body;

       if (!contents || !Array.isArray(contents)) {
         return res.status(400).json({ error: { message: "Invalid request. 'contents' array is required." } });
       }

       const client = await auth.getClient();
       let projectId = await auth.getProjectId();

       // FALLBACK: Override default sandbox project with the active user project 'vtxdemos'
       if (!projectId || projectId === 'jesusarguelles-sandbox') {
         projectId = 'vtxdemos';
       }

       const tokenResponse = await client.getAccessToken();
       const accessToken = tokenResponse.token;

       if (!projectId || !accessToken) {
         throw new Error("Could not retrieve project credentials via ADC.");
       }

       const region = 'us-central1';
       const model = 'gemini-2.5-flash';
       const url = `https://${region}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${region}/publishers/google/models/${model}:generateContent`;

       console.log(`[Backend] Proxying request to Vertex AI project "${projectId}"...`);

       const response = await fetch(url, {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${accessToken}`
         },
         body: JSON.stringify({
           contents,
           systemInstruction,
           tools: [
             {
               googleSearch: {} // Enables Google Search grounding
             }
           ],
           generationConfig: {
             temperature: 0.7,
             maxOutputTokens: 1024
           }
         })
       });

       if (!response.ok) {
         const errorText = await response.text();
         return res.status(response.status).json({
           error: { message: errorText || `Vertex AI responded with status ${response.status}` }
         });
       }

       const data = await response.json();
       const replyText = data.candidates?.[0]?.content?.parts?.[0]?.text;
       
       if (!replyText) {
         return res.status(500).json({ error: { message: "Empty response from Vertex AI model." } });
       }

       res.json({ 
         text: replyText,
         groundingMetadata: data.candidates?.[0]?.groundingMetadata
       });

     } catch (error) {
       console.error("[Backend] Error:", error);
       res.status(500).json({ error: { message: error.message || "Internal server error." } });
     }
   });

   app.listen(PORT, () => {
     console.log(`[Backend] Server listening on port ${PORT}`);
   });
   ```

6. **Create the Frontend API Service**
   Create a new file `src/services/gemini.js` to handle sending requests to the local Express proxy backend:
   ```javascript
   const BACKEND_URL = "http://localhost:8001/api/chat";

   export async function sendChatMessage(chatHistory, articleContext = null, allArticles = []) {
     let systemInstructionText = `You are "Verge AI", a brilliant, witty, and tech-savvy interactive news assistant for a cloned version of The Verge. 
   Your tone should be analytical, sharp, and engaging, similar to a tech journalist. 
   Use markdown for structure (bolding, lists, code snippets). Keep paragraphs relatively short.

   You are assisting the user as they browse the homepage.
   `;

     if (articleContext) {
       systemInstructionText += `
   The user is currently reading and asking questions about this specific article:
   TITLE: "${articleContext.title}"
   AUTHOR: ${articleContext.author}
   DATE: ${articleContext.date}
   SUMMARY: ${articleContext.summary}

   FULL ARTICLE CONTENT:
   ${articleContext.content}

   Focus on answering questions directly related to this article, but you can also bring in external context or compare it to other tech events. If the user asks general questions, you are free to answer those too.
   `;
     } else {
       const articlesSummary = allArticles.map((art, idx) => 
         `${idx + 1}. [${art.category}] "${art.title}" by ${art.author} (${art.date}) - Summary: ${art.summary}`
       ).join("\n");

       systemInstructionText += `
   The user is looking at the homepage. Here are the current articles featured on the front page:
   ${articlesSummary}

   You can discuss these articles, compare them, summarize them, or help the user decide what to read. You can also chat about any other general science, technology, design, and culture topic.
   `;
     }

     const apiContents = chatHistory.map(msg => ({
       role: msg.role === "user" ? "user" : "model",
       parts: [{ text: msg.content }]
     }));

     try {
       const response = await fetch(BACKEND_URL, {
         method: "POST",
         headers: {
           "Content-Type": "application/json"
         },
         body: JSON.stringify({
           contents: apiContents,
           systemInstruction: {
             parts: [{ text: systemInstructionText }]
           }
         })
       });

       if (!response.ok) {
         const errorData = await response.json().catch(() => ({}));
         const errorMessage = errorData.error?.message || `Server error ${response.status}`;
         throw new Error(errorMessage);
       }

       const data = await response.json();
       
       if (!data.text) {
         throw new Error("Empty response received from the chat proxy.");
       }

       return {
         text: data.text,
         groundingMetadata: data.groundingMetadata
       };
     } catch (error) {
       console.error("Chat Service Error:", error);
       throw error;
     }
   }
   ```

7. **Create React Markdown HTML Formatter**
   Write a custom React renderer utility to parse and format markdown responses securely without depending on heavy third-party packages.
   
   Create `src/utils/formatter.jsx`:
   ```jsx
   import React from 'react';

   export function formatMarkdown(text) {
     if (!text) return "";

     const parts = text.split(/(```[\s\S]*?```)/g);

     return parts.map((part, index) => {
       if (part.startsWith('```') && part.endsWith('```')) {
         const codeLines = part.slice(3, -3).trim().split('\n');
         let language = 'text';
         let code = part.slice(3, -3).trim();

         if (codeLines[0] && !codeLines[0].includes(' ') && codeLines[0].length < 10) {
           language = codeLines[0];
           code = codeLines.slice(1).join('\n');
         }

         return (
           <pre key={index}>
             <code className={`language-${language}`}>{code}</code>
           </pre>
         );
       }

       const lines = part.split('\n');
       let inList = false;
       let listItems = [];
       const elements = [];

       lines.forEach((line, lineIdx) => {
         const trimmedLine = line.trim();

         if (trimmedLine.startsWith('* ') || trimmedLine.startsWith('- ')) {
           inList = true;
           listItems.push(
             <li key={lineIdx}>
               {parseInlineFormatting(trimmedLine.substring(2))}
             </li>
           );
           return;
         }

         if (inList && !trimmedLine.startsWith('* ') && !trimmedLine.startsWith('- ')) {
           elements.push(<ul key={`list-${lineIdx}`}>{listItems}</ul>);
           listItems = [];
           inList = false;
         }

         if (trimmedLine === '') return;

         elements.push(
           <p key={lineIdx}>
             {parseInlineFormatting(line)}
           </p>
         );
       });

       if (inList && listItems.length > 0) {
         elements.push(<ul key={`list-end`}>{listItems}</ul>);
       }

       return <React.Fragment key={index}>{elements}</React.Fragment>;
     });
   }

   function parseInlineFormatting(text) {
     const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

     return parts.map((part, idx) => {
       if (part.startsWith('**') && part.endsWith('**')) {
         return <strong key={idx}>{part.slice(2, -2)}</strong>;
       }
       if (part.startsWith('`') && part.endsWith('`')) {
         return <code key={idx}>{part.slice(1, -1)}</code>;
       }
       return part;
     });
   }
   ```

8. **Implement Verge Styles and Light Theme Layout**
   Edit `src/index.css` to build the typography, responsive CSS variables, grid lines, and locked-viewport scrolling behaviors.
   
   Replace `src/index.css` content:
   ```css
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;0,900;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

   :root {
     /* Colors - Light Theme */
     --bg-dark: #ffffff;
     --bg-card: #f9f9fb;
     --bg-input: #f2f2f7;
     --bg-chat-user: #e9e9eb;
     --bg-chat-bot: #f5f5f9;
     
     --text-main: #121212;
     --text-sub: #48484a;
     --text-muted: #8e8e93;
     
     --border-dark: #e5e5ea;
     --border-light: #d1d1d6;
     
     --accent-verge: #ff005b; /* The Verge Pink */
     --accent-purple: #5200ff; /* Verge Purple */
     --accent-cyan: #0088cc;
     --accent-green: #008f3a;
     --accent-orange: #d97706;

     /* Typography */
     --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
     --font-serif: 'Playfair Display', Georgia, Cambria, "Times New Roman", Times, serif;
     --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

     /* Transitions */
     --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
   }

   * {
     box-sizing: border-box;
     margin: 0;
     padding: 0;
   }

   body {
     background-color: var(--bg-dark);
     color: var(--text-main);
     font-family: var(--font-sans);
     -webkit-font-smoothing: antialiased;
     -moz-osx-font-smoothing: grayscale;
     overflow: hidden;
     height: 100vh;
   }

   ::-webkit-scrollbar {
     width: 6px;
     height: 6px;
   }

   ::-webkit-scrollbar-track {
     background: var(--bg-dark);
   }

   ::-webkit-scrollbar-thumb {
     background: var(--border-light);
     border-radius: 3px;
   }

   ::-webkit-scrollbar-thumb:hover {
     background: var(--text-muted);
   }

   .app-container {
     display: flex;
     flex-direction: column;
     height: 100vh;
     overflow: hidden;
     position: relative;
   }

   .verge-header {
     border-bottom: 2px solid var(--accent-verge);
     background-color: var(--bg-dark);
     position: sticky;
     top: 0;
     z-index: 100;
   }

   .header-top {
     display: flex;
     justify-content: space-between;
     align-items: center;
     padding: 1rem 2rem;
     border-bottom: 1px solid var(--border-dark);
   }

   .verge-logo-container {
     display: flex;
     align-items: center;
     gap: 0.5rem;
   }

   .logo-main {
     font-family: var(--font-serif);
     font-weight: 900;
     font-size: 2.2rem;
     letter-spacing: -2px;
     color: var(--text-main);
     text-transform: uppercase;
     text-decoration: none;
     font-style: italic;
     display: flex;
     align-items: center;
   }

   .logo-main span {
     color: var(--accent-verge);
   }

   .logo-sub {
     font-family: var(--font-sans);
     font-weight: 800;
     font-size: 0.65rem;
     color: var(--bg-dark);
     background-color: var(--text-main);
     padding: 2px 4px;
     letter-spacing: 2px;
     text-transform: uppercase;
     border-radius: 2px;
   }

   .header-meta {
     display: flex;
     align-items: center;
     gap: 1.5rem;
     font-size: 0.8rem;
     color: var(--text-sub);
   }

   .meta-item {
     display: flex;
     align-items: center;
     gap: 0.25rem;
   }

   .chat-toggle-btn {
     background-color: var(--accent-verge);
     color: white;
     border: none;
     padding: 0.5rem 1rem;
     font-family: var(--font-sans);
     font-weight: 700;
     font-size: 0.8rem;
     letter-spacing: 0.5px;
     cursor: pointer;
     display: flex;
     align-items: center;
     gap: 0.5rem;
     transition: var(--transition);
   }

   .chat-toggle-btn:hover {
     background-color: white;
     color: black;
   }

   .nav-bar {
     display: flex;
     justify-content: center;
     padding: 0.75rem 2rem;
     background-color: var(--bg-dark);
     border-bottom: 1px solid var(--border-dark);
     overflow-x: auto;
   }

   .nav-links {
     display: flex;
     gap: 2rem;
     list-style: none;
   }

   .nav-link {
     color: var(--text-sub);
     text-decoration: none;
     font-size: 0.75rem;
     font-weight: 700;
     letter-spacing: 1.5px;
     text-transform: uppercase;
     transition: var(--transition);
     position: relative;
     white-space: nowrap;
   }

   .nav-link:hover, .nav-link.active {
     color: var(--text-main);
   }

   .nav-link.active::after {
     content: '';
     position: absolute;
     bottom: -13px;
     left: 0;
     width: 100%;
     height: 2px;
     background-color: var(--accent-verge);
   }

   .main-content {
     display: grid;
     grid-template-columns: 1fr;
     flex: 1;
     height: calc(100vh - 120px);
     overflow: hidden;
     transition: var(--transition);
   }

   .main-content.chat-open {
     grid-template-columns: 1fr 450px;
   }

   @media (max-width: 1100px) {
     .main-content.chat-open {
       grid-template-columns: 1fr;
     }
   }

   .news-section {
     padding: 2rem;
     height: 100%;
     overflow-y: auto;
     border-right: 1px solid var(--border-dark);
   }

   .news-container {
     max-width: 1200px;
     margin: 0 auto;
     display: flex;
     flex-direction: column;
     gap: 2.5rem;
   }

   .hero-grid {
     display: grid;
     grid-template-columns: 3fr 2fr;
     gap: 2rem;
     border-bottom: 1px solid var(--border-light);
     padding-bottom: 2.5rem;
   }

   @media (max-width: 768px) {
     .hero-grid {
       grid-template-columns: 1fr;
     }
   }

   .hero-featured {
     display: flex;
     flex-direction: column;
     gap: 1rem;
     cursor: pointer;
   }

   .hero-image-placeholder {
     height: 400px;
     position: relative;
     overflow: hidden;
     border: 1px solid var(--border-light);
   }

   .card-image-gradient {
     width: 100%;
     height: 100%;
     transition: transform 0.5s ease;
     opacity: 0.85;
   }

   .hero-featured:hover .card-image-gradient {
     transform: scale(1.03);
     opacity: 1;
   }

   .category-tag {
     position: absolute;
     top: 1rem;
     left: 1rem;
     color: var(--bg-dark);
     font-size: 0.7rem;
     font-weight: 800;
     padding: 0.25rem 0.5rem;
     letter-spacing: 1px;
   }

   .hero-meta {
     display: flex;
     gap: 1rem;
     font-size: 0.75rem;
     color: var(--text-muted);
     font-weight: 600;
   }

   .hero-headline {
     font-family: var(--font-serif);
     font-size: 2.5rem;
     line-height: 1.1;
     font-weight: 900;
     letter-spacing: -1px;
     color: var(--text-main);
     transition: var(--transition);
   }

   .hero-featured:hover .hero-headline {
     color: var(--accent-verge);
     text-decoration: underline;
     text-underline-offset: 4px;
   }

   .hero-subtitle {
     color: var(--text-sub);
     font-size: 1.05rem;
     line-height: 1.5;
   }

   .hero-side-list {
     display: flex;
     flex-direction: column;
     justify-content: space-between;
     gap: 1.5rem;
   }

   .side-article-item {
     display: flex;
     flex-direction: column;
     gap: 0.5rem;
     padding-bottom: 1.5rem;
     border-bottom: 1px solid var(--border-dark);
     cursor: pointer;
   }

   .side-article-item:last-child {
     border-bottom: none;
     padding-bottom: 0;
   }

   .side-item-category {
     font-size: 0.65rem;
     font-weight: 800;
     letter-spacing: 1.5px;
   }

   .side-item-headline {
     font-family: var(--font-serif);
     font-size: 1.3rem;
     line-height: 1.2;
     font-weight: 700;
     color: var(--text-main);
     transition: var(--transition);
   }

   .side-article-item:hover .side-item-headline {
     color: var(--accent-verge);
     text-decoration: underline;
   }

   .side-item-meta {
     font-size: 0.7rem;
     color: var(--text-muted);
     font-weight: 600;
   }

   .news-feed-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
     gap: 2rem;
   }

   .feed-card {
     display: flex;
     flex-direction: column;
     gap: 0.8rem;
     padding-bottom: 1.5rem;
     border-bottom: 1px solid var(--border-dark);
     cursor: pointer;
   }

   .feed-image {
     height: 200px;
     position: relative;
     overflow: hidden;
     border: 1px solid var(--border-light);
   }

   .feed-card:hover .card-image-gradient {
     transform: scale(1.03);
     opacity: 1;
   }

   .feed-category {
     font-size: 0.65rem;
     font-weight: 800;
     letter-spacing: 1.5px;
     margin-top: 0.2rem;
   }

   .feed-headline {
     font-family: var(--font-serif);
     font-size: 1.5rem;
     line-height: 1.25;
     font-weight: 700;
     color: var(--text-main);
     transition: var(--transition);
   }

   .feed-card:hover .feed-headline {
     color: var(--accent-verge);
     text-decoration: underline;
   }

   .feed-summary {
     color: var(--text-sub);
     font-size: 0.85rem;
     line-height: 1.45;
   }

   .feed-meta {
     font-size: 0.7rem;
     color: var(--text-muted);
     font-weight: 600;
     margin-top: auto;
   }

   .chat-drawer {
     background-color: var(--bg-card);
     border-left: 1px solid var(--border-light);
     display: flex;
     flex-direction: column;
     height: 100%;
     position: relative;
     top: 0;
     overflow: hidden;
     z-index: 90;
   }

   .chat-header {
     padding: 1.2rem;
     border-bottom: 1px solid var(--border-light);
     display: flex;
     justify-content: space-between;
     align-items: center;
     background-color: var(--bg-dark);
   }

   .chat-header-title {
     display: flex;
     align-items: center;
     gap: 0.5rem;
   }

   .chat-header-title h3 {
     font-family: var(--font-sans);
     font-weight: 800;
     font-size: 0.95rem;
     letter-spacing: 0.5px;
     color: var(--text-main);
   }

   .chat-header-title .gemini-badge {
     background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
     color: white;
     font-size: 0.6rem;
     font-weight: 900;
     padding: 2px 6px;
     border-radius: 4px;
     letter-spacing: 1px;
   }

   .chat-close-btn {
     background: none;
     border: none;
     color: var(--text-sub);
     font-size: 1.2rem;
     cursor: pointer;
     transition: var(--transition);
   }

   .chat-close-btn:hover {
     color: var(--text-main);
   }

   .active-context-panel {
     background-color: rgba(82, 0, 255, 0.08);
     border-bottom: 1px solid rgba(82, 0, 255, 0.25);
     padding: 0.75rem 1.2rem;
     display: flex;
     justify-content: space-between;
     align-items: center;
     font-size: 0.75rem;
   }

   .context-info {
     display: flex;
     align-items: center;
     gap: 0.5rem;
     overflow: hidden;
     text-overflow: ellipsis;
     white-space: nowrap;
   }

   .context-icon {
     color: var(--accent-purple);
     font-weight: 700;
   }

   .context-title {
     font-weight: 600;
     color: var(--text-main);
   }

   .clear-context-btn {
     background: none;
     border: none;
     color: var(--text-muted);
     cursor: pointer;
     font-size: 0.7rem;
     text-decoration: underline;
   }

   .clear-context-btn:hover {
     color: var(--text-sub);
   }

   .chat-messages-container {
     flex: 1;
     padding: 1.2rem;
     overflow-y: auto;
     display: flex;
     flex-direction: column;
     gap: 1rem;
     background-color: var(--bg-dark);
   }

   .message-wrapper {
     display: flex;
     flex-direction: column;
     max-width: 85%;
   }

   .message-wrapper.user {
     align-self: flex-end;
   }

   .message-wrapper.bot {
     align-self: flex-start;
   }

   .message-sender {
     font-size: 0.65rem;
     font-weight: 700;
     letter-spacing: 0.5px;
     margin-bottom: 0.25rem;
     color: var(--text-muted);
   }

   .message-wrapper.user .message-sender {
     text-align: right;
   }

   .message-bubble {
     padding: 0.8rem 1rem;
     border-radius: 8px;
     font-size: 0.85rem;
     line-height: 1.45;
     word-break: break-word;
   }

   .message-wrapper.user .message-bubble {
     background-color: var(--bg-chat-user);
     color: var(--text-main);
     border-bottom-right-radius: 2px;
     border: 1px solid var(--border-light);
   }

   .message-wrapper.bot .message-bubble {
     background-color: var(--bg-chat-bot);
     color: var(--text-main);
     border-bottom-left-radius: 2px;
     border-left: 3px solid var(--accent-purple);
     border-top: 1px solid var(--border-dark);
     border-right: 1px solid var(--border-dark);
     border-bottom: 1px solid var(--border-dark);
   }

   .message-bubble p {
     margin-bottom: 0.5rem;
   }

   .message-bubble p:last-child {
     margin-bottom: 0;
   }

   .message-bubble code {
     font-family: var(--font-mono);
     font-size: 0.75rem;
     background-color: #f2f2f7;
     padding: 2px 4px;
     border-radius: 3px;
     color: var(--accent-cyan);
   }

   .message-bubble pre {
     background-color: #1e1e1e;
     padding: 0.75rem;
     border-radius: 6px;
     overflow-x: auto;
     margin: 0.5rem 0;
     border: 1px solid var(--border-light);
     color: white;
   }

   .message-bubble pre code {
     background: none;
     padding: 0;
     color: inherit;
   }

   .loading-bubble {
     display: flex;
     align-items: center;
     gap: 0.25rem;
     padding: 0.6rem 1rem;
     background-color: var(--bg-chat-bot);
     border-radius: 8px;
     border-bottom-left-radius: 2px;
     border-left: 3px solid var(--accent-purple);
     width: fit-content;
   }

   .dot {
     width: 6px;
     height: 6px;
     background-color: var(--text-muted);
     border-radius: 50%;
     animation: bounce 1.4s infinite ease-in-out both;
   }

   .dot:nth-child(1) { animation-delay: -0.32s; }
   .dot:nth-child(2) { animation-delay: -0.16s; }

   @keyframes bounce {
     0%, 80%, 100% { transform: scale(0); }
     40% { transform: scale(1.0); }
   }

   .chat-input-container {
     padding: 1rem 1.2rem;
     border-top: 1px solid var(--border-light);
     background-color: var(--bg-card);
   }

   .chat-input-form {
     display: flex;
     gap: 0.5rem;
   }

   .chat-input-field {
     flex: 1;
     background-color: var(--bg-input);
     border: 1px solid var(--border-light);
     color: var(--text-main);
     padding: 0.75rem 1rem;
     border-radius: 4px;
     font-family: var(--font-sans);
     font-size: 0.85rem;
     transition: var(--transition);
   }

   .chat-input-field:focus {
     outline: none;
     border-color: var(--accent-purple);
   }

   .chat-send-btn {
     background-color: var(--accent-purple);
     color: white;
     border: none;
     padding: 0.75rem 1.2rem;
     border-radius: 4px;
     font-weight: 700;
     cursor: pointer;
     transition: var(--transition);
   }

   .chat-send-btn:hover {
     background-color: white;
     color: black;
     border: 1px solid var(--border-light);
   }

   .chat-send-btn:disabled {
     background-color: var(--border-dark);
     color: var(--text-muted);
     cursor: not-allowed;
   }

   .chat-empty-state {
     display: flex;
     flex-direction: column;
     justify-content: center;
     align-items: center;
     height: 100%;
     text-align: center;
     padding: 2rem;
     gap: 1.5rem;
   }

   .chat-empty-icon {
     font-size: 2.5rem;
     background: linear-gradient(135deg, var(--accent-purple), var(--accent-verge));
     -webkit-background-clip: text;
     -webkit-text-fill-color: transparent;
     font-weight: 900;
   }

   .chat-empty-text h4 {
     font-size: 1rem;
     font-weight: 700;
     margin-bottom: 0.5rem;
   }

   .chat-empty-text p {
     font-size: 0.8rem;
     color: var(--text-sub);
     max-width: 280px;
   }

   .chat-suggestions {
     display: flex;
     flex-direction: column;
     gap: 0.5rem;
     width: 100%;
     max-width: 320px;
   }

   .suggestion-btn {
     background-color: var(--bg-input);
     border: 1px solid var(--border-light);
     color: var(--text-sub);
     padding: 0.6rem 0.8rem;
     border-radius: 4px;
     font-size: 0.75rem;
     font-weight: 600;
     text-align: left;
     cursor: pointer;
     transition: var(--transition);
   }

   .suggestion-btn:hover {
     background-color: var(--border-dark);
     color: var(--text-main);
     border-color: var(--text-muted);
   }
   ```

9. **Clear Out Default App.css**
   Clear any default CSS rules by resetting `src/App.css`:
   ```css
   /* App component styles */
   ```

10. **Implement Core React Interface**
    Replace `src/App.jsx` entirely to handle state routing, layout structure, context bindings, quick actions, and grounding metadata rendering:
    ```jsx
    import { useState, useEffect, useRef } from 'react';
    import { newsArticles } from './data/news';
    import { sendChatMessage } from './services/gemini';
    import { formatMarkdown } from './utils/formatter';
    import './App.css';

    function App() {
      const [selectedArticle, setSelectedArticle] = useState(null);
      const [activeCategory, setActiveCategory] = useState('ALL');
      const [isChatOpen, setIsChatOpen] = useState(true);
      const [chatHistory, setChatHistory] = useState([]);
      const [chatInput, setChatInput] = useState('');
      const [isGenerating, setIsGenerating] = useState(false);
      const [errorMessage, setErrorMessage] = useState('');
      const [liveTime, setLiveTime] = useState(new Date().toLocaleTimeString());

      const chatBottomRef = useRef(null);

      useEffect(() => {
        const timer = setInterval(() => {
          setLiveTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
        }, 1000);
        return () => clearInterval(timer);
      }, []);

      useEffect(() => {
        if (chatBottomRef.current) {
          chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
        }
      }, [chatHistory, isGenerating]);

      const filteredArticles = activeCategory === 'ALL'
        ? newsArticles
        : newsArticles.filter(art => art.category === activeCategory);

      const handleSelectArticle = (article) => {
        setSelectedArticle(article);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      };

      const handleDiscussArticle = (article) => {
        setSelectedArticle(article);
        setIsChatOpen(true);
        
        const introMsg = {
          role: 'bot',
          content: `I've loaded the article **"${article.title}"** into my active context. Ask me anything about it! For example, you can ask me to:
    * Summarize the main points
    * Analyze the author's arguments
    * Compare this news to current industry standards`
        };
        
        setChatHistory(prev => [...prev, {
          role: 'system_notification',
          content: `Focused on article: ${article.title}`
        }, introMsg]);
      };

      const handleClearContext = () => {
        setSelectedArticle(null);
        setChatHistory(prev => [...prev, {
          role: 'system_notification',
          content: 'Cleared active article context. Now discussing general homepage news.'
        }]);
      };

      const handleSendMessage = async (e) => {
        if (e) e.preventDefault();
        if (!chatInput.trim() || isGenerating) return;

        const userMessageText = chatInput.trim();
        const newUserMessage = { role: 'user', content: userMessageText };
        
        setChatHistory(prev => [...prev, newUserMessage]);
        setChatInput('');
        setIsGenerating(true);
        setErrorMessage('');

        try {
          const historyForApi = [...chatHistory, newUserMessage]
            .filter(msg => msg.role === 'user' || msg.role === 'bot');

          const result = await sendChatMessage(
            historyForApi,
            selectedArticle,
            newsArticles
          );

          setChatHistory(prev => [...prev, { 
            role: 'bot', 
            content: result.text,
            groundingMetadata: result.groundingMetadata
          }]);
        } catch (error) {
          console.error(error);
          setErrorMessage(error.message || 'Something went wrong when connecting to Gemini.');
        } finally {
          setIsGenerating(false);
        }
      };

      const handleQuickPrompt = (promptText) => {
        setChatInput(promptText);
        setTimeout(() => {
          const inputEl = document.querySelector('.chat-input-field');
          if (inputEl) inputEl.focus();
        }, 50);
      };

      const featuredArticle = newsArticles[0];
      const sideArticles = newsArticles.slice(1, 4);
      const remainingArticles = newsArticles.slice(4);

      return (
        <div className="app-container">
          <header className="verge-header">
            <div className="header-top">
              <div className="verge-logo-container">
                <a href="#" className="logo-main" onClick={() => setSelectedArticle(null)}>
                  THE VERGE<span>.</span>
                </a>
                <div className="logo-sub">Chat Portal</div>
              </div>

              <div className="header-meta">
                <div className="meta-item">
                  <strong>EST. 2011</strong>
                </div>
                <div className="meta-item">
                  <span>⏰</span> {liveTime}
                </div>
                <button 
                  className="chat-toggle-btn" 
                  onClick={() => setIsChatOpen(!isChatOpen)}
                  style={{ backgroundColor: isChatOpen ? '#222' : 'var(--accent-verge)' }}
                >
                  💬 {isChatOpen ? 'Close Chat' : 'Open Chat'}
                </button>
              </div>
            </div>

            <nav className="nav-bar">
              <ul className="nav-links">
                {['ALL', 'TECH', 'REVIEWS', 'SCIENCE', 'GAMING', 'DESIGN'].map(cat => (
                  <li key={cat}>
                    <a 
                      href="#" 
                      className={`nav-link ${activeCategory === cat ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        setActiveCategory(cat);
                        setSelectedArticle(null);
                      }}
                    >
                      {cat}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </header>

          <main className={`main-content ${isChatOpen ? 'chat-open' : ''}`}>
            <section className="news-section">
              <div className="news-container">
                {selectedArticle ? (
                  <article className="single-article-view" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <button 
                      className="modal-btn-secondary" 
                      onClick={() => setSelectedArticle(null)}
                      style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', cursor: 'pointer' }}
                    >
                      ← Back to Homepage
                    </button>

                    <header className="article-header" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '1.5rem' }}>
                      <div style={{ color: selectedArticle.accentColor, fontWeight: 800, fontSize: '0.8rem', letterSpacing: '2px', marginBottom: '0.5rem' }}>
                        {selectedArticle.category}
                      </div>
                      <h1 className="article-title" style={{ fontFamily: 'var(--font-serif)', fontSize: '3rem', fontWeight: 900, lineHeight: 1.1, margin: '0.5rem 0' }}>
                        {selectedArticle.title}
                      </h1>
                      <p className="article-subtitle" style={{ fontSize: '1.25rem', color: 'var(--text-sub)', lineHeight: 1.4, margin: '1rem 0' }}>
                        {selectedArticle.subtitle}
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        <div>
                          By <strong style={{ color: 'var(--text-main)' }}>{selectedArticle.author}</strong> | {selectedArticle.date}
                        </div>
                        <div>{selectedArticle.readTime}</div>
                      </div>
                    </header>

                    <div 
                      style={{ 
                        background: `linear-gradient(90deg, ${selectedArticle.accentColor}22, rgba(0,0,0,0))`,
                        borderLeft: `4px solid ${selectedArticle.accentColor}`,
                        padding: '1.2rem', 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        gap: '1rem'
                      }}
                    >
                      <div>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.2rem' }}>Want to interact with this article?</h4>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-sub)' }}>Ask Verge AI to summarize, explain technical concepts, or critique the ideas.</p>
                      </div>
                      <button 
                        className="chat-toggle-btn"
                        style={{ backgroundColor: selectedArticle.accentColor, whiteSpace: 'nowrap' }}
                        onClick={() => handleDiscussArticle(selectedArticle)}
                      >
                        💬 Discuss Article
                      </button>
                    </div>

                    <div className="hero-image-placeholder" style={{ height: '350px' }}>
                      <div className="card-image-gradient" style={{ background: selectedArticle.imageGradient }}></div>
                    </div>

                    <div className="article-body-content" style={{ fontFamily: 'var(--font-sans)', fontSize: '1.1rem', lineHeight: '1.7', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                      {selectedArticle.content.split('\n\n').map((paragraph, idx) => (
                        <p key={idx}>{paragraph}</p>
                      ))}
                    </div>
                  </article>
                ) : (
                  <>
                    {activeCategory === 'ALL' ? (
                      <>
                        <div className="hero-grid">
                          <div className="hero-featured" onClick={() => handleSelectArticle(featuredArticle)}>
                            <div className="hero-image-placeholder">
                              <div className="card-image-gradient" style={{ background: featuredArticle.imageGradient }}></div>
                              <span className="category-tag" style={{ backgroundColor: featuredArticle.accentColor }}>
                                {featuredArticle.category}
                              </span>
                            </div>
                            <div className="hero-meta">
                              <span>{featuredArticle.author}</span> • <span>{featuredArticle.date}</span>
                            </div>
                            <h2 className="hero-headline">{featuredArticle.title}</h2>
                            <p className="hero-subtitle">{featuredArticle.summary}</p>
                          </div>

                          <div className="hero-side-list">
                            {sideArticles.map(art => (
                              <div key={art.id} className="side-article-item" onClick={() => handleSelectArticle(art)}>
                                <span className="side-item-category" style={{ color: art.accentColor }}>
                                  {art.category}
                                </span>
                                <h3 className="side-item-headline">{art.title}</h3>
                                <div className="side-item-meta">
                                  <span>{art.author}</span> • <span>{art.date}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="news-feed-grid">
                          {remainingArticles.map(art => (
                            <div key={art.id} className="feed-card" onClick={() => handleSelectArticle(art)}>
                              <div className="feed-image">
                                <div className="card-image-gradient" style={{ background: art.imageGradient }}></div>
                                <span className="category-tag" style={{ backgroundColor: art.accentColor }}>
                                  {art.category}
                                </span>
                              </div>
                              <span className="feed-category" style={{ color: art.accentColor }}>
                                {art.category}
                              </span>
                              <h3 className="feed-headline">{art.title}</h3>
                              <p className="feed-summary">{art.summary}</p>
                              <div className="feed-meta">
                                <span>{art.author}</span> • <span>{art.date}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <div className="news-feed-grid">
                        {filteredArticles.map(art => (
                          <div key={art.id} className="feed-card" onClick={() => handleSelectArticle(art)}>
                            <div className="feed-image">
                              <div className="card-image-gradient" style={{ background: art.imageGradient }}></div>
                              <span className="category-tag" style={{ backgroundColor: art.accentColor }}>
                                {art.category}
                              </span>
                            </div>
                            <span className="feed-category" style={{ color: art.accentColor }}>
                              {art.category}
                            </span>
                            <h3 className="feed-headline">{art.title}</h3>
                            <p className="feed-summary">{art.summary}</p>
                            <div className="feed-meta">
                              <span>{art.author}</span> • <span>{art.date}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </section>

            {isChatOpen && (
              <aside className="chat-drawer">
                <div className="chat-header">
                  <div className="chat-header-title">
                    <h3>VERGE AI</h3>
                    <span className="gemini-badge">GEMINI 2.5 FLASH</span>
                  </div>
                  <button className="chat-close-btn" onClick={() => setIsChatOpen(false)}>×</button>
                </div>

                <div className="active-context-panel">
                  <div className="context-info">
                    <span className="context-icon">💡</span>
                    {selectedArticle ? (
                      <span className="context-title">Reading: {selectedArticle.title}</span>
                    ) : (
                      <span className="context-title">Browsing: Homepage Articles</span>
                    )}
                  </div>
                  {selectedArticle && (
                    <button className="clear-context-btn" onClick={handleClearContext}>
                      Clear Context
                    </button>
                  )}
                </div>

                <div className="chat-messages-container">
                  {chatHistory.length === 0 ? (
                    <div className="chat-empty-state">
                      <div className="chat-empty-icon">⌘</div>
                      <div className="chat-empty-text">
                        <h4>Interact with the news</h4>
                        <p>Select any article on the left or use the prompts below to chat about today's headlines.</p>
                      </div>

                      <div className="chat-suggestions">
                        <button className="suggestion-btn" onClick={() => handleQuickPrompt("Summarize all the news articles on the homepage in 3 bullet points.")}>
                          📝 Summarize today's headlines
                        </button>
                        <button className="suggestion-btn" onClick={() => handleQuickPrompt("What are the key details of Google's new Gemini 3 autonomous agents?")}>
                          🤖 Tell me about Gemini 3 agents
                        </button>
                        <button className="suggestion-btn" onClick={() => handleQuickPrompt("Which article has the biggest impact on clean energy?")}>
                          ⚡ Find articles on green tech
                        </button>
                      </div>
                    </div>
                  ) : (
                    chatHistory.map((msg, index) => {
                      if (msg.role === 'system_notification') {
                        return (
                          <div key={index} style={{ textAlign: 'center', margin: '0.5rem 0', fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px dotted var(--border-light)', paddingTop: '0.5rem' }}>
                            {msg.content}
                          </div>
                        );
                      }
                      
                      return (
                        <div key={index} className={`message-wrapper ${msg.role === 'user' ? 'user' : 'bot'}`}>
                          <span className="message-sender">
                            {msg.role === 'user' ? 'YOU' : 'VERGE AI'}
                          </span>
                          <div className="message-bubble">
                            {msg.role === 'bot' ? formatMarkdown(msg.content) : msg.content}
                            
                            {msg.role === 'bot' && msg.groundingMetadata && (
                              <div className="grounding-info" style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dotted var(--border-light)', fontSize: '0.75rem' }}>
                                {msg.groundingMetadata.webSearchQueries && msg.groundingMetadata.webSearchQueries.length > 0 && (
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-sub)', marginBottom: '0.4rem' }}>
                                    <span>🔍</span>
                                    <span>Searched: <em>"{msg.groundingMetadata.webSearchQueries.join(', ')}"</em></span>
                                  </div>
                                )}
                                {msg.groundingMetadata.groundingChunks && msg.groundingMetadata.groundingChunks.length > 0 && (
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                                    <div style={{ fontWeight: 700, fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Sources & Citations:</div>
                                    <ul style={{ listStyle: 'none', paddingLeft: 0, display: 'flex', flexWrap: 'wrap', gap: '0.25rem 0.75rem' }}>
                                      {msg.groundingMetadata.groundingChunks
                                        .filter((chunk, idx, self) => 
                                          chunk.web && self.findIndex(c => c.web && c.web.uri === chunk.web.uri) === idx
                                        )
                                        .map((chunk, cIdx) => (
                                          <li key={cIdx}>
                                            <a href={chunk.web.uri} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-purple)', textDecoration: 'underline', fontWeight: 500 }}>
                                              {chunk.web.title || "Source link"}
                                            </a>
                                          </li>
                                        ))
                                      }
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}

                  {isGenerating && (
                    <div className="message-wrapper bot">
                      <span className="message-sender">VERGE AI</span>
                      <div className="loading-bubble">
                        <span className="dot"></span>
                        <span className="dot"></span>
                        <span className="dot"></span>
                      </div>
                    </div>
                  )}

                  {errorMessage && (
                    <div style={{ backgroundColor: 'rgba(255, 0, 91, 0.1)', color: 'var(--accent-verge)', padding: '0.8rem', borderRadius: '4px', fontSize: '0.8rem', border: '1px solid rgba(255, 0, 91, 0.3)' }}>
                      <strong>Error:</strong> {errorMessage}
                    </div>
                  )}
                  <div ref={chatBottomRef} />
                </div>

                <div className="chat-input-container">
                  <form onSubmit={handleSendMessage} className="chat-input-form">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder={selectedArticle ? "Ask about this article..." : "Ask about today's tech..."}
                      className="chat-input-field"
                      disabled={isGenerating}
                    />
                    <button type="submit" className="chat-send-btn" disabled={!chatInput.trim() || isGenerating}>
                      Send
                    </button>
                  </form>
                </div>
              </aside>
            )}
          </main>
        </div>
      );
    }

    export default App;
    ```

11. **Configure Web Entry Point**
    Update `index.html` to add standard browser document descriptors and search titles:
    ```html
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="Browse and interact with today's tech, science, and design news using Verge AI, an interactive news reader powered by Google Gemini." />
        <title>The Verge - Interactive AI News Chat Portal</title>
      </head>
      <body>
        <div id="root"></div>
        <script type="module" src="/src/main.jsx"></script>
      </body>
    </html>
    ```

12. **Start the Systems and Verify Flows**
    - Compile the production bundle `npm run build` to confirm compilation is solid.
    - Start the local backend on port `8001`:
      ```bash
      cd server && npm start
      ```
    - Start the local frontend dev server on port `5173`:
      ```bash
      npm run dev
      ```
    - Test the chat grounding using a live browser: ask *"What hour is the World Cup 2026 opening ceremony in Mexico scheduled for?"* and confirm that it performs a Google search and returns grounded answers with active hyperlinked citations.
