export class AudioStreamer {
  context: AudioContext;
  gainNode: GainNode;
  workletNode: AudioWorkletNode | null = null;
  isPlaying: boolean = false;
  inputSampleRate: number = 24000; // Gemini default

  constructor(context: AudioContext) {
    this.context = context;
    this.gainNode = this.context.createGain();
    this.gainNode.connect(this.context.destination);
  }

  async initialize() {
    try {
      await this.context.audioWorklet.addModule('/pcm-processor.js');
      this.workletNode = new AudioWorkletNode(this.context, 'pcm-processor');
      this.workletNode.connect(this.gainNode);
    } catch (e) {
      console.error('Failed to load audio worklet:', e);
    }
  }

  addPCM16(chunk: Uint8Array) {
    if (!this.workletNode) {
      console.warn('AudioStreamer: workletNode is missing!');
      return;
    }

    // Convert PCM16 (Uint8Array bytes) to Float32
    const data16 = new Int16Array(chunk.buffer, chunk.byteOffset, chunk.byteLength / 2);
    const float32 = new Float32Array(data16.length);

    for (let i = 0; i < data16.length; i++) {
      float32[i] = data16[i] / 32768;
    }

    console.log(`[AudioStreamer] Queuing ${float32.length} samples. Context State: ${this.context.state}`);
    if (this.context.state === 'suspended') {
      this.context.resume();
    }

    this.workletNode.port.postMessage(float32);
    this.isPlaying = true;
  }

  stop() {
    // To stop immediately, we can disconnect or just replace the node
    if (this.workletNode) {
      // Send a message to clear buffer if we implemented that, or just disconnect
      this.workletNode.disconnect();
      this.gainNode.disconnect();

      // Recreation
      this.gainNode = this.context.createGain();
      this.gainNode.connect(this.context.destination);

      // We need to reconnect worklet? No, usually we want to clear its buffer.
      // Simplest: just recreate the worklet if needed or ask it to clear.
      // For now, let's just silence it.
      this.workletNode = new AudioWorkletNode(this.context, 'pcm-processor');
      this.workletNode.connect(this.gainNode);
    }
    this.isPlaying = false;
  }
}
