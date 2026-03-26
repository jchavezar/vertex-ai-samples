import { gcpConfig, agentConfig } from "./authConfig";

/**
 * Exchange Entra ID token for GCP access token via Workforce Identity Federation
 */
export async function exchangeTokenForGcp(entraIdToken: string): Promise<string> {
  const audience = `//iam.googleapis.com/locations/${gcpConfig.location}/workforcePools/${gcpConfig.workforcePoolId}/providers/${gcpConfig.providerId}`;

  const response = await fetch("https://sts.googleapis.com/v1/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:token-exchange",
      audience: audience,
      scope: "https://www.googleapis.com/auth/cloud-platform",
      requested_token_type: "urn:ietf:params:oauth:token-type:access_token",
      subject_token_type: "urn:ietf:params:oauth:token-type:id_token",
      subject_token: entraIdToken,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`STS token exchange failed: ${error}`);
  }

  const data = await response.json();
  return data.access_token;
}

/**
 * Create a session on Agent Engine
 */
export async function createSession(
  gcpToken: string,
  userId: string,
  userToken: string
): Promise<string> {
  const url = `https://${agentConfig.location}-aiplatform.googleapis.com/v1/projects/${agentConfig.projectId}/locations/${agentConfig.location}/reasoningEngines/${agentConfig.agentEngineId}:query`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${gcpToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      class_method: "create_session",
      input: {
        user_id: userId,
        state: {
          USER_TOKEN: userToken,
        },
      },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create session: ${error}`);
  }

  const data = await response.json();
  return data.output?.id || data.id;
}

/**
 * Send a query to Agent Engine and stream the response
 */
export async function* streamQuery(
  gcpToken: string,
  sessionId: string,
  userId: string,
  message: string
): AsyncGenerator<string> {
  const url = `https://${agentConfig.location}-aiplatform.googleapis.com/v1/projects/${agentConfig.projectId}/locations/${agentConfig.location}/reasoningEngines/${agentConfig.agentEngineId}:streamQuery`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${gcpToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      class_method: "stream_query",
      input: {
        session_id: sessionId,
        user_id: userId,
        message: message,
      },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Query failed: ${error}`);
  }

  // Handle streaming response
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse JSON lines from buffer
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const data = JSON.parse(line);
        // Extract text content from response
        if (data.content?.parts) {
          for (const part of data.content.parts) {
            if (part.text) {
              yield part.text;
            }
          }
        }
      } catch {
        // Not JSON, might be SSE format
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.content?.parts) {
              for (const part of data.content.parts) {
                if (part.text) {
                  yield part.text;
                }
              }
            }
          } catch {
            // Skip unparseable lines
          }
        }
      }
    }
  }
}

/**
 * Streaming query - yields text chunks as they arrive
 */
export async function* queryStream(
  gcpToken: string,
  sessionId: string,
  userId: string,
  message: string
): AsyncGenerator<string> {
  const url = `https://${agentConfig.location}-aiplatform.googleapis.com/v1/projects/${agentConfig.projectId}/locations/${agentConfig.location}/reasoningEngines/${agentConfig.agentEngineId}:streamQuery`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${gcpToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      input: {
        session_id: sessionId,
        user_id: userId,
        message: message,
      },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Query failed: ${error}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        let data = JSON.parse(line);
        if (Array.isArray(data)) data = data[0];

        // Extract and yield text chunks
        const text = extractText(data);
        if (text) yield text;
      } catch {
        // Skip non-JSON
      }
    }
  }
}

function extractText(data: unknown): string | null {
  if (!data || typeof data !== 'object') return null;
  const obj = data as Record<string, unknown>;

  // Direct content.parts
  if (obj.content && typeof obj.content === 'object') {
    const content = obj.content as Record<string, unknown>;
    if (Array.isArray(content.parts)) {
      for (const part of content.parts) {
        if (part && typeof part === 'object' && 'text' in part) {
          return (part as { text: string }).text;
        }
      }
    }
  }

  // Wrapped in output
  if (obj.output) {
    const output = typeof obj.output === 'string' ? JSON.parse(obj.output) : obj.output;
    return extractText(output);
  }

  return null;
}

/**
 * Non-streaming fallback
 */
export async function query(
  gcpToken: string,
  sessionId: string,
  userId: string,
  message: string
): Promise<string> {
  let result = "";
  for await (const chunk of queryStream(gcpToken, sessionId, userId, message)) {
    result = chunk; // Keep last chunk (final response)
  }
  return result || "No response received";
}
