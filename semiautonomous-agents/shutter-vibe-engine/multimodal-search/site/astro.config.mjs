// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// Published from a subdirectory of a user-pages site.
// Final URL: https://jchavezar.github.io/vertex-ai-samples/multimodal-search/
export default defineConfig({
  site: "https://jchavezar.github.io",
  base: "/vertex-ai-samples/multimodal-search",
  trailingSlash: "ignore",
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
      ],
    }),
  ],
});
