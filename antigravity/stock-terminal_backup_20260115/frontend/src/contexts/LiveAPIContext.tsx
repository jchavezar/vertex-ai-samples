import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { MultimodalLiveClient } from '../lib/multimodal-live-client';
import { AudioStreamer } from '../lib/audio-streamer';
import { AudioRecorder } from '../lib/audio-recorder';

interface LiveAPIContextType {
  connected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  volume: number;
}

const LiveAPIContext = createContext<LiveAPIContextType | undefined>(undefined);

export const LiveAPIProvider = ({ children }: { children: React.ReactNode }) => {
  const [connected, setConnected] = useState(false);
  const [volume, setVolume] = useState(0);

  const clientRef = useRef<MultimodalLiveClient | null>(null);
  const streamerRef = useRef<AudioStreamer | null>(null);
  const recorderRef = useRef<AudioRecorder | null>(null);

  const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

  useEffect(() => {
    if (!apiKey) return;

    const client = new MultimodalLiveClient({ apiKey });
    clientRef.current = client;

    // Handle incoming audio
    client.on('content', (content) => {
      if (content.modelTurn && content.modelTurn.parts) {
        content.modelTurn.parts.forEach((part: any) => {
          if (part.inlineData && part.inlineData.mimeType.startsWith('audio/pcm')) {
            // base64 to Uint8Array
            const binaryString = atob(part.inlineData.data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
              bytes[i] = binaryString.charCodeAt(i);
            }
            console.log(`[LiveAPI] Received audio chunk: ${bytes.length} bytes`);
            streamerRef.current?.addPCM16(bytes);
          }
        });
      }
    });

    client.on('close', () => {
      setConnected(false);
    });

    return () => {
      client.disconnect();
    };
  }, [apiKey]);

  const connect = useCallback(async () => {
    if (!apiKey) {
      alert("Gemini API Key is missing! Please set VITE_GEMINI_API_KEY in frontend/.env");
      return;
    }
    if (!clientRef.current) return;

    // Initialize Audio
    const ctx = new AudioContext({ sampleRate: 24000 });
    const streamer = new AudioStreamer(ctx);
    await streamer.initialize();
    streamerRef.current = streamer;

    const recorder = new AudioRecorder();
    recorderRef.current = recorder;

    recorder.on('data', (base64) => {
      console.log(`[LiveAPI] Sending audio chunk: ${base64.length} chars`);
      clientRef.current?.sendRealtimeInput([{
        mimeType: "audio/pcm;rate=16000",
        data: base64
      }]);
    });

    await recorder.start();

    const config = {
      model: "models/gemini-2.0-flash-exp",
      generationConfig: {
        responseModalities: ["audio"],
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: "Aoede" } }
        }
      }
    };

    await clientRef.current.connect(config);
    setConnected(true);

    // Send initial greeting to trigger audio response
    setTimeout(() => {
      clientRef.current?.send({
        clientContent: {
          turns: [{
            parts: [{ text: "Hello, are you there?" }],
            role: "user"
          }],
          turnComplete: true
        }
      });
    }, 1000);
  }, []);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
    recorderRef.current?.stop();
    streamerRef.current?.stop();
    setConnected(false);
  }, []);

  return (
    <LiveAPIContext.Provider value={{ connected, connect, disconnect, volume }}>
      {children}
    </LiveAPIContext.Provider>
  );
};

export const useLiveAPI = () => {
  const context = useContext(LiveAPIContext);
  if (!context) {
    throw new Error('useLiveAPI must be used within a LiveAPIProvider');
  }
  return context;
};
