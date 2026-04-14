/**
 * Vertex AI Claude Predictor
 * Optimized for the 'claude-sonnet-4-6' model on Vertex AI.
 */

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export class VertexPredictor {
  private endpoint = "https://aiplatform.googleapis.com/v1/projects/vtxdemos/locations/global/publishers/anthropic/models/claude-sonnet-4-6:rawPredict";

  async streamPredict(messages: Message[], onChunk: (chunk: string) => void) {
    // In a real scenario, this token would be passed via headers or fetched from metadata
    // For this harness, we'll simulate the token or assume a pre-authorized environment.
    // NOTE: In production, use the Google Cloud SDK or a secure proxy.
    
    const requestPayload = {
      anthropic_version: "vertex-2023-10-16",
      messages: messages.map(m => ({
        role: m.role,
        content: [{ type: "text", text: m.content }]
      })),
      max_tokens: 4096,
      temperature: 1,
      stream: true,
    };

    try {
      const response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.GCLOUD_TOKEN}`, // We'll set this via a script
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        throw new Error(`Vertex AI Error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        // Claude streams typically come in events. We'll extract the 'text' field.
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "content_block_delta" && data.delta?.text) {
                onChunk(data.delta.text);
              }
            } catch (e) {
              // Ignore incomplete JSON chunks
            }
          }
        }
      }
    } catch (error) {
      console.error("Prediction failed:", error);
      onChunk("\n[Error: Could not connect to Vertex AI. Check your GCLOUD_TOKEN.]");
    }
  }
}
