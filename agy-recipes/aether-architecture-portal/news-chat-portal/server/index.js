import express from 'express';
import cors from 'cors';
import { GoogleAuth } from 'google-auth-library';

const app = express();
const PORT = process.env.PORT || 8001;

app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5000'],
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

app.post('/api/quick', async (req, res) => {
  try {
    const { query } = req.body;

    if (!query) {
      return res.status(400).json({ error: { message: "Invalid request. 'query' parameter is required." } });
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

    const url = `https://aiplatform.googleapis.com/v1/projects/${projectId}/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview:generateContent`;

    console.log(`[Backend] Proxying quick request to Vertex AI (gemini-3.1-flash-lite-preview) project "${projectId}"...`);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        contents: [
          {
            role: 'user',
            parts: [{ text: `${query}\n\nGive a brief, helpful answer.` }]
          }
        ],
        tools: [
          {
            googleSearch: {} // Enables Google Search grounding
          }
        ],
        generationConfig: {
          temperature: 1.0,
          maxOutputTokens: 500
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
    console.error("[Backend] Quick Error:", error);
    res.status(500).json({ error: { message: error.message || "Internal server error." } });
  }
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[Backend] Server listening on port ${PORT}`);
});
