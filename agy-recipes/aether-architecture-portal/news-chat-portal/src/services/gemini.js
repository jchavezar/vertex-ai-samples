const BACKEND_URL = "http://localhost:8001/api/chat";

export async function sendChatMessage(chatHistory, articleContext = null, allArticles = []) {
  let systemInstructionText = `You are "Aether AI", an expert interactive assistant for a design and architecture journal named Aether. 
Your tone should be authoritative, insightful, and engaging, similar to an architectural critic. 
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

Focus on answering questions directly related to this article, but you can also bring in external context or compare it to other architectural designs or events. If the user asks general questions, you are free to answer those too.
`;
  } else {
    const articlesSummary = allArticles.map((art, idx) => 
      `${idx + 1}. [${art.category}] "${art.title}" by ${art.author} (${art.date}) - Summary: ${art.summary}`
    ).join("\n");

    systemInstructionText += `
The user is looking at the homepage. Here are the current articles featured on the front page:
${articlesSummary}

You can discuss these articles, compare them, summarize them, or help the user decide what to read. You can also chat about general architecture, sustainable materials, urban planning, and design topics.
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
