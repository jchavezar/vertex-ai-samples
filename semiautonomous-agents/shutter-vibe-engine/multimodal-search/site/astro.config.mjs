// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// Tiny remark plugin: turn ```mermaid fenced blocks into raw <pre class="mermaid">,
// bypassing ExpressiveCode so the client-side mermaid script renders them as SVG.
function remarkMermaid() {
  const escape = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const walk = (node) => {
    if (!node || !Array.isArray(node.children)) return;
    node.children.forEach((child, i) => {
      if (child.type === "code" && child.lang === "mermaid") {
        node.children[i] = { type: "html", value: `<pre class="mermaid">${escape(child.value)}</pre>` };
      } else {
        walk(child);
      }
    });
  };
  return (tree) => walk(tree);
}

// Published from a subdirectory of a user-pages site.
// Final URL: https://jchavezar.github.io/vertex-ai-samples/multimodal-search/
export default defineConfig({
  site: "https://jchavezar.github.io",
  base: "/vertex-ai-samples/multimodal-search",
  trailingSlash: "ignore",
  markdown: {
    remarkPlugins: [remarkMermaid],
  },
  integrations: [
    starlight({
      title: "Vibe Search",
      tagline: "Multimodal vibe search, built on Vertex AI",
      logo: { src: "./src/assets/spark.svg", replacesTitle: false },
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/shutter-vibe-engine/multimodal-search" },
        { icon: "linkedin", label: "LinkedIn", href: "https://www.linkedin.com/in/jchavezar/" },
      ],
      customCss: ["./src/styles/custom.css"],
      sidebar: [
        { label: "The story", link: "/" },
        { label: "How it works", link: "/how-it-works/" },
        { label: "Replicate", link: "/replicate/" },
        { label: "Architecture", link: "/architecture/" },
      ],
      editLink: {
        baseUrl: "https://github.com/jchavezar/vertex-ai-samples/edit/main/semiautonomous-agents/shutter-vibe-engine/multimodal-search/site/",
      },
      lastUpdated: true,
      pagination: false,
      head: [
        {
          tag: "meta",
          attrs: { name: "description", content: "Type a vibe — get the photo, video, music, SFX and graphic that share that mood. A reference implementation of multimodal vibe search on Vertex AI." },
        },
        {
          tag: "script",
          attrs: { type: "module" },
          content: `
            import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
            const theme = document.documentElement.dataset.theme === "dark" ? "dark" : "default";
            mermaid.initialize({ startOnLoad: false, theme, securityLevel: "loose" });
            const render = async () => {
              const blocks = document.querySelectorAll("pre.mermaid:not([data-processed])");
              if (!blocks.length) return;
              await mermaid.run({ nodes: blocks });
            };
            document.addEventListener("DOMContentLoaded", render);
            document.addEventListener("astro:page-load", render);
          `,
        },
      ],
    }),
  ],
});
