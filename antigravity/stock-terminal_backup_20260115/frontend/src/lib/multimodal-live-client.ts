import { EventEmitter } from './event-emitter';

export class MultimodalLiveClient extends EventEmitter {
  ws: WebSocket | null = null;
  config: any;
  url: string;

  constructor({ apiKey, url }: { apiKey?: string; url?: string }) {
    super();
    // Default to production endpoint if only apiKey provided
    if (apiKey) {
      const host = "generativelanguage.googleapis.com";
      const path = "google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent";
      this.url = `wss://${host}/ws/${path}?key=${apiKey}`;
    } else {
      this.url = url || "";
    }
  }

  connect(config: any) {
    if (!this.url) {
      return Promise.reject(new Error("No URL or API Key provided"));
    }

    return new Promise<void>((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log("WebSocket connected");
        this.sendSetup(config);
        this.emit('valid', true);
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        this.emit('error', err);
        reject(err);
      };

      this.ws.onclose = () => {
        console.log("WebSocket closed");
        this.emit('close');
      };
    });
  }

  sendSetup(config: any) {
    const setupMessage = {
      setup: config
    };
    this.send(setupMessage);
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  sendRealtimeInput(chunks: { mimeType: string; data: string }[]) {
    this.send({
      realtimeInput: {
        mediaChunks: chunks
      }
    });
  }

  handleMessage(event: MessageEvent) {
    let data;
    try {
      if (event.data instanceof Blob) {
        // Usually we expect text/json frame, but if binary...
        // JSON is expected for BidiGenerateContent
        return;
      }
      data = JSON.parse(event.data);
    } catch (e) {
      console.error("Failed to parse message", e);
      return;
    }

    if (data.serverContent) {
      this.emit('content', data.serverContent);
    } else if (data.toolCall) {
      this.emit('toolCall', data.toolCall);
    }
    // Handle other message types like setupComplete if useful
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
