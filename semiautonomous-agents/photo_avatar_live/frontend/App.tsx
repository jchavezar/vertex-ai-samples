/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useEffect } from 'react';
import { Modality } from '@google/genai';
import { LiveAPIProvider, useLiveAPIContext } from './contexts/LiveAPIContext';
import ControlTray from './components/console/control-tray/ControlTray';
import ThreeDAvatar from './components/ThreeDAvatar';

const API_KEY = (process.env.GEMINI_API_KEY ?? process.env.API_KEY) as string;
if (!API_KEY) {
  throw new Error('Missing environment variable: GEMINI_API_KEY');
}

const SYSTEM_PROMPT = `You are a friendly, expressive AI companion represented as the user's own face.
Speak naturally and conversationally. Keep responses concise and engaging.
You can discuss any topic the user brings up. Be warm, curious, and helpful.`;

function AvatarApp() {
  const { setConfig, connected, client } = useLiveAPIContext();

  useEffect(() => {
    setConfig({
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Aoede' } },
      },
      systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
    });
  }, [setConfig]);

  useEffect(() => {
    if (!connected) return;
    client.send({ text: 'Greet the user warmly and invite them to start a conversation.' }, true);
  }, [connected, client]);

  return (
    <div className="streaming-console">
      <main>
        <div className="main-app-area">
          <ThreeDAvatar />
        </div>
        <ControlTray />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <LiveAPIProvider apiKey={API_KEY}>
      <AvatarApp />
    </LiveAPIProvider>
  );
}
