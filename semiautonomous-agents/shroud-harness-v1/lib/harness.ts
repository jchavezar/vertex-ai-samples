/**
 * Shroud Harness Engine
 * Integrated with the local API Route for Vertex AI.
 */

export type HarnessState = "idle" | "thinking" | "executing";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export class HarnessEngine {
  private state: HarnessState = "idle";

  constructor(private onStateChange: (state: HarnessState) => void) {}

  async process(input: string, messages: Message[], onUpdate: (chunk: string) => void) {
    this.setState("thinking");
    
    const fullHistory: Message[] = [...messages, { role: "user", content: input }];

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: fullHistory }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      this.setState("executing");

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "content_block_delta" && data.delta?.text) {
                onUpdate(data.delta.text);
              }
            } catch (e) {}
          }
        }
      }
    } catch (error: any) {
      console.error("Harness error:", error);
      onUpdate(`\n[Harness Error: ${error.message}. Ensure GCLOUD_TOKEN is valid.]`);
    }

    this.setState("idle");
  }

  private setState(state: HarnessState) {
    this.state = state;
    this.onStateChange(state);
  }
}
