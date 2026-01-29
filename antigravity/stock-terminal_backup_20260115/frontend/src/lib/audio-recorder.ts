import { EventEmitter } from './event-emitter';

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

export class AudioRecorder extends EventEmitter {
  stream: MediaStream | null = null;
  audioContext: AudioContext | null = null;
  processor: ScriptProcessorNode | null = null;
  input: MediaStreamAudioSourceNode | null = null;
  sampleRate: number = 16000; // API expects 16kHz typical for speech, or we can send 24k

  constructor(sampleRate = 16000) {
    super();
    this.sampleRate = sampleRate;
  }

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.audioContext = new AudioContext({ sampleRate: this.sampleRate });
    this.input = this.audioContext.createMediaStreamSource(this.stream);

    // Use ScriptProcessor for recording (simpler than Worklet for just capturing)
    // Buffer size 4096 gives ~250ms latency usually, for lower latency use smaller buffer (512/1024)
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

    this.processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      this.processAudio(inputData);
    };

    this.input.connect(this.processor);
    this.processor.connect(this.audioContext.destination); // Needed for Chrome to activate script processor
  }

  processAudio(inputData: Float32Array) {
    // Downsample/Convert to PCM16
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
      // Clamp and scale
      let s = Math.max(-1, Math.min(1, inputData[i]));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Convert to base64 string
    const base64 = arrayBufferToBase64(pcm16.buffer);

    this.emit('data', base64);
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.input) {
      this.input.disconnect();
      this.input = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}
