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
