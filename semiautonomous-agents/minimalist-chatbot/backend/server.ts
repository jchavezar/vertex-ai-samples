import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { execSync } from "child_process";
import { Readable } from "stream";

// Load env variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 8001;

// Configuration
const REASONING_ENGINE_ID = "7437175815114063872";
const PROJECT_ID = "254356041555";
const LOCATION = "us-west1";

app.use(cors());
app.use(express.json());

// Resilient token retrieval
function getGcpAccessToken(): string {
  if (process.env.GCLOUD_TOKEN) {
    return process.env.GCLOUD_TOKEN;
  }
  try {
    // Attempt ADC print-access-token first (standard development approach)
    return execSync("gcloud auth application-default print-access-token", { encoding: "utf-8" }).trim();
  } catch (e) {
    try {
      // Fallback to active gcloud user token
      return execSync("gcloud auth print-access-token", { encoding: "utf-8" }).trim();
    } catch (err) {
      console.error(">>> [Authentication Error] Could not retrieve GCP OAuth access token via gcloud. Calls to Vertex AI will fail.");
      return "";
    }
  }
}

// Health check
app.get("/api/health", (req, res) => {
  try {
    const token = getGcpAccessToken();
    res.json({
      status: "healthy",
      engine: `projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}`,
      authConfigured: token.length > 0,
      tokenPreview: token ? `${token.substring(0, 10)}...` : "None"
    });
  } catch (e: any) {
    res.status(500).json({ status: "unhealthy", error: e.message });
  }
});

// Create Session endpoint
app.post("/api/session", async (req, res) => {
  const { user_id = "default-user" } = req.body;
  const token = getGcpAccessToken();

  if (!token) {
    return res.status(500).json({ error: "GCP OAuth token is missing. Please authenticate with gcloud." });
  }

  const queryEndpoint = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}:query`;

  try {
    console.log(`>>> [Session] Creating remote session for user: ${user_id}`);
    const response = await fetch(queryEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        class_method: "async_create_session",
        input: { user_id }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.warn(`>>> [Session] async_create_session API failed (${response.status}): ${errorText}. Falling back to local UUID generation.`);
      // Fallback to local session ID in case the engine doesn't implement or require state creation
      const mockSessionId = `session-${Math.random().toString(36).substring(2, 15)}`;
      return res.json({ session_id: mockSessionId, user_id, fallback: true });
    }

    const data = await response.json() as any;
    // Extract session ID from response
    const sessionId = data.output?.id || data.output?.session_id || data.session_id || `session-${Math.random().toString(36).substring(2, 15)}`;
    console.log(`>>> [Session] Remote session initialized successfully: ${sessionId}`);
    res.json({ session_id: sessionId, user_id });
  } catch (error: any) {
    console.warn(`>>> [Session] Network error creating session: ${error.message}. Falling back.`);
    const mockSessionId = `session-${Math.random().toString(36).substring(2, 15)}`;
    res.json({ session_id: mockSessionId, user_id, fallback: true });
  }
});

// SSE Streaming Chat proxy
app.post("/api/chat", async (req, res) => {
  const { message, session_id, user_id = "default-user" } = req.body;

  if (!message) {
    return res.status(400).json({ error: "Message is required." });
  }
  if (!session_id) {
    return res.status(400).json({ error: "session_id is required." });
  }

  const token = getGcpAccessToken();
  if (!token) {
    return res.status(500).json({ error: "GCP OAuth token is missing. Please authenticate with gcloud." });
  }

  const streamEndpoint = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}:streamQuery?alt=sse`;

  console.log(`>>> [Chat] Streaming query for session: ${session_id}`);

  // Set standard SSE response headers
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  try {
    const isFallbackSession = session_id.startsWith("session-");
    const inputPayload: any = {
      user_id,
      message
    };

    if (!isFallbackSession) {
      inputPayload.session_id = session_id;
    } else if (req.body.session_events) {
      inputPayload.session_events = req.body.session_events;
    }

    const apiResponse = await fetch(streamEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        class_method: "async_stream_query",
        input: inputPayload
      })
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      console.error(`>>> [Chat Error] Vertex AI API call failed (${apiResponse.status}):`, errorText);
      res.write(`data: ${JSON.stringify({ type: "error", error: `Vertex AI API Error (${apiResponse.status}): ${errorText}` })}\n\n`);
      res.end();
      return;
    }

    if (!apiResponse.body) {
      res.write(`data: ${JSON.stringify({ type: "error", error: "Empty stream body from Vertex AI." })}\n\n`);
      res.end();
      return;
    }

    let buffer = "";
    const decoder = new TextDecoder();

    for await (const chunk of apiResponse.body as any) {
      buffer += decoder.decode(chunk, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // keep incomplete line in buffer

      for (const line of lines) {
        if (!line.trim()) continue;

        // Strip "data: " prefix if present
        let cleanLine = line;
        if (line.startsWith("data:")) {
          cleanLine = line.substring(5).trim();
        }

        if (!cleanLine) continue;

        try {
          const parsed = JSON.parse(cleanLine);
          
          // Check for content or function calls
          const content = parsed.content;
          const usage = parsed.usage_metadata;

          if (usage) {
            res.write(`data: ${JSON.stringify({ type: "usage", usage })}\n\n`);
          }

          if (content && content.parts) {
            for (const part of content.parts) {
              // Standard text response chunk
              if (part.text && !part.thought) {
                res.write(`data: ${JSON.stringify({ type: "text", text: part.text })}\n\n`);
              }
              // Thinking/reasoning block
              if (part.thought || (part.text && part.thought === true)) {
                res.write(`data: ${JSON.stringify({ type: "thought", thought: part.text || "" })}\n\n`);
              }
              // Tool execution events (highly premium feature)
              if (part.function_call) {
                res.write(`data: ${JSON.stringify({
                  type: "tool_call",
                  tool: {
                    name: part.function_call.name,
                    args: part.function_call.args
                  }
                })}\n\n`);
              }
              if (part.function_response) {
                res.write(`data: ${JSON.stringify({
                  type: "tool_result",
                  result: {
                    name: part.function_response.name,
                    response: part.function_response.response
                  }
                })}\n\n`);
              }
            }
          }
        } catch (err) {
          // Sometimes it might not be JSON, just pipe through or ignore if heartbeat
          if (line.includes("heartbeat") || line.includes("keep-alive")) {
            // Heartbeat
          } else {
            console.debug(">>> [Chat Debug] Non-JSON or incomplete line:", line);
          }
        }
      }
    }

    res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
    res.end();
    console.log(`>>> [Chat] Streaming completed for session: ${session_id}`);

  } catch (error: any) {
    console.error(">>> [Chat Error] Connection failed:", error.message);
    res.write(`data: ${JSON.stringify({ type: "error", error: error.message })}\n\n`);
    res.end();
  }
});

app.listen(PORT, () => {
  console.log(`
======================================================
  Minimalist Chatbot Backend Server Deployed Locally
======================================================
  Port:            ${PORT}
  Endpoint URI:    http://localhost:${PORT}
  Target Engine:   projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}
======================================================
  `);
});
