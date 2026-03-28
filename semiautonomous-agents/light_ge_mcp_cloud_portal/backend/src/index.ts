import express, { Request, Response } from 'express';
import cors from 'cors';
import { config } from 'dotenv';
import { v1beta1 } from '@google-cloud/aiplatform';

// Load environment variables
config();

const app = express();
app.use(cors({ origin: process.env.FRONTEND_URL || '*' }));
app.use(express.json());

// Initialize Google Cloud AI Platform clients (reused across requests)
const { ReasoningEngineExecutionServiceClient, SessionServiceClient } = v1beta1;
const executionClient = new ReasoningEngineExecutionServiceClient();
const sessionClient = new SessionServiceClient();

// Agent Engine path
const PROJECT = process.env.GOOGLE_CLOUD_PROJECT!;
const LOCATION = process.env.GOOGLE_CLOUD_LOCATION || 'us-central1';
const AGENT_ENGINE_ID = process.env.AGENT_ENGINE_ID!;
const AGENT_PATH = `projects/${PROJECT}/locations/${LOCATION}/reasoningEngines/${AGENT_ENGINE_ID}`;

console.log(`[Server] Agent Engine Path: ${AGENT_PATH}`);

interface ChatRequest {
  message: string;
  sessionId?: string;
}

/**
 * Health check endpoint
 */
app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', agentPath: AGENT_PATH });
});

/**
 * Test endpoint - NO AUTH REQUIRED (for local testing only)
 */
app.post('/api/test', async (req: Request, res: Response) => {
  const { message } = req.body as { message: string };

  if (!message) {
    res.status(400).json({ error: 'Message is required' });
    return;
  }

  console.log(`[Test] Message: "${message}"`);

  try {
    // Set SSE headers for streaming
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Use the correct method name with struct input
    const stream = await executionClient.streamQueryReasoningEngine({
      name: AGENT_PATH,
      input: {
        fields: {
          user_id: { stringValue: 'test-user' },
          message: { stringValue: message }
        }
      }
    });

    for await (const event of stream) {
      const eventData = event as Record<string, unknown>;
      console.log('[Test] Event:', JSON.stringify(eventData).substring(0, 200));
      // Extract text if available
      const content = (eventData as any)?.content;
      if (content?.parts?.[0]?.text) {
        res.write(`data: ${JSON.stringify({ text: content.parts[0].text })}\n\n`);
      } else {
        res.write(`data: ${JSON.stringify({ raw: eventData })}\n\n`);
      }
    }

    res.write('data: [DONE]\n\n');
    res.end();
  } catch (error) {
    console.error('[Test] Error:', error);
    if (res.headersSent) {
      res.write(`data: ${JSON.stringify({ error: String(error) })}\n\n`);
      res.end();
    } else {
      res.status(500).json({ error: String(error) });
    }
  }
});

/**
 * Main chat endpoint - streams responses from Agent Engine
 */
app.post('/api/chat', async (req: Request, res: Response) => {
  const userToken = req.headers.authorization?.split(' ')[1];

  if (!userToken) {
    res.status(401).json({ error: 'Authorization header with Bearer token required' });
    return;
  }

  const { message, sessionId } = req.body as ChatRequest;

  if (!message) {
    res.status(400).json({ error: 'Message is required' });
    return;
  }

  console.log(`[Chat] Message: "${message.substring(0, 50)}..." | Session: ${sessionId || 'new'}`);

  try {
    // Create or reuse session
    let activeSessionId = sessionId;

    if (!activeSessionId) {
      console.log('[Chat] Creating new session with USER_TOKEN in state...');

      const [operation] = await sessionClient.createSession({
        parent: AGENT_PATH,
        session: {
          userId: 'default_user',
          // This is where the JWT token is passed to the agent!
          sessionState: {
            USER_TOKEN: userToken
          } as Record<string, unknown>
        }
      });

      const [session] = await operation.promise();
      activeSessionId = session.name!.split('/').pop()!;
      console.log(`[Chat] Created session: ${activeSessionId}`);
    }

    // Set SSE headers for streaming
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');

    // Send session ID first so frontend can reuse it
    res.write(`data: ${JSON.stringify({ type: 'session', sessionId: activeSessionId })}\n\n`);

    // Stream query to Agent Engine
    console.log(`[Chat] Streaming query to Agent Engine...`);

    const stream = await executionClient.streamQueryReasoningEngine({
      name: AGENT_PATH,
      classMethod: 'async_stream_query',
      input: {
        user_id: 'default_user',
        session_id: activeSessionId,
        message: message
      } as Record<string, unknown>
    });

    // Stream events to client
    for await (const event of stream) {
      // Extract text content from the event
      const eventData = event as Record<string, unknown>;
      res.write(`data: ${JSON.stringify({ type: 'event', data: eventData })}\n\n`);
    }

    // Signal end of stream
    res.write('data: [DONE]\n\n');
    res.end();

    console.log(`[Chat] Stream completed for session: ${activeSessionId}`);

  } catch (error) {
    console.error('[Chat] Error:', error);

    // If headers already sent, send error as SSE
    if (res.headersSent) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: String(error) })}\n\n`);
      res.end();
    } else {
      res.status(500).json({ error: String(error) });
    }
  }
});

/**
 * Get session info
 */
app.get('/api/session/:sessionId', async (req: Request, res: Response) => {
  try {
    const sessionName = `${AGENT_PATH}/sessions/${req.params.sessionId}`;
    const [session] = await sessionClient.getSession({ name: sessionName });
    res.json(session);
  } catch (error) {
    console.error('[Session] Error:', error);
    res.status(500).json({ error: String(error) });
  }
});

/**
 * List all sessions
 */
app.get('/api/sessions', async (_req: Request, res: Response) => {
  try {
    const [sessions] = await sessionClient.listSessions({ parent: AGENT_PATH });
    res.json(sessions);
  } catch (error) {
    console.error('[Sessions] Error:', error);
    res.status(500).json({ error: String(error) });
  }
});

// Start server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`[Server] Running on port ${PORT}`);
  console.log(`[Server] Frontend URL: ${process.env.FRONTEND_URL || '*'}`);
});
