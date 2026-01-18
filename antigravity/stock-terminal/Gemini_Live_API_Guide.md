# Gemini Live API Implementation Guide

This guide details the implementation of the Gemini Live API service, based on the `avatars` reference implementation. It allows for real-time multimodal interaction (audio/voice) with Google's Gemini models.

## 1. Prerequisites

Ensure your project has the following dependencies installed in `package.json`:

```json
{
  "dependencies": {
    "@google/genai": "^0.0.21",
    "eventemitter3": "^5.0.1",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "@types/lodash": "^4.17.7"
  }
}
```

## 2. Directory Structure

Recommended structure for the service integration:

```
src/
├── lib/
│   ├── genai-live-client.ts       # Core client wrapper
│   ├── audio-recorder.ts          # Microphone input handling
│   ├── audio-streamer.ts          # Server audio output handling
│   ├── audioworklet-registry.ts   # Worklet management
│   ├── constants.ts               # Configuration constants
│   ├── utils.ts                   # AudioContext helpers
│   └── worklets/                  # Audio processing scripts
│       ├── audio-processing.ts
│       └── vol-meter.ts
├── hooks/
│   └── use-live-api.ts            # React hook for API state
└── contexts/
    └── LiveAPIContext.tsx         # Context provider
```

## 3. Core Components

### 3.1. GenAILiveClient (`lib/genai-live-client.ts`)

This class wraps the Google GenAI SDK to manage the WebSocket connection.

*   **Extends:** `EventEmitter` (to broadcast events like `audio`, `content`, `toolcall`).
*   **Key Methods:**
    *   `connect(config)`: Establishes the WebSocket connection.
    *   `disconnect()`: Closes the connection.
    *   `sendRealtimeInput(chunks)`: Sends audio/video chunks to the server.
    *   `send(parts)`: Sends text parts or control messages.
*   **Events:** `open`, `close`, `audio` (incoming server audio), `content`, `interrupted`.

### 3.2. Audio Handling

**Recording (`lib/audio-recorder.ts`):**
*   Uses `AudioContext` and `AudioWorklet` to capture microphone input.
*   Downsamples input to 16kHz PCM (required by Gemini API).
*   Emits `data` events with base64-encoded PCM audio.

**Streaming (`lib/audio-streamer.ts`):**
*   Receives PCM 16kHz audio from the server.
*   Converts it to `Float32Array` and schedules playback using `AudioBufferSourceNode`.
*   Handles smooth playback and interruption handling.

**Worklets (`lib/worklets/`):**
*   `audio-processing.ts`: Buffers and processes raw audio data from the microphone.
*   `vol-meter.ts`: Calculates volume levels for UI visualization.

## 4. React Integration

### 4.1. useLiveApi Hook (`hooks/use-live-api.ts`)

This hook manages the lifecycle of the `GenAILiveClient` and audio components.

**Key Features:**
*   Instantiates `GenAILiveClient`.
*   Sets up the `AudioStreamer` for output.
*   Binds client events (`open`, `close`, `audio`, `interrupted`).
*   Exposes `client`, `connected`, `connect`, `disconnect`, `volume`.

### 4.2. LiveAPIProvider (`contexts/LiveAPIContext.tsx`)

Wraps the application to provide the API state globally.

```tsx
export const LiveAPIProvider: FC<LiveAPIProviderProps> = ({ apiKey, children }) => {
  const liveAPI = useLiveApi({ apiKey });
  return (
    <LiveAPIContext.Provider value={liveAPI}>
      {children}
    </LiveAPIContext.Provider>
  );
};
```

## 5. Usage Example

### Connect Button & Microphone Control

Inside a component (e.g., `ControlTray.tsx`):

```tsx
import { useLiveAPIContext } from '../../contexts/LiveAPIContext';
import { AudioRecorder } from '../../lib/audio-recorder';
import { useEffect, useState } from 'react';

function ControlTray() {
  const { client, connected, connect, disconnect } = useLiveAPIContext();
  const [audioRecorder] = useState(() => new AudioRecorder());
  const [muted, setMuted] = useState(false);

  // Set configuration before connecting
  useEffect(() => {
    setConfig({
      model: "models/gemini-2.0-flash-exp",
      generationConfig: {
        responseModalities: "audio",
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: "Aoede" } }
        }
      },
      systemInstruction: {
        parts: [{ text: "You are a helpful assistant." }],
      },
    });
  }, [setConfig]);

  // Handle microphone input
  useEffect(() => {
    const onData = (base64: string) => {
      // Send audio chunks to Gemini
      client.sendRealtimeInput([{
        mimeType: 'audio/pcm;rate=16000',
        data: base64,
      }]);
    };

    if (connected && !muted) {
      audioRecorder.on('data', onData).start();
    } else {
      audioRecorder.stop();
    }

    return () => {
      audioRecorder.off('data', onData);
    };
  }, [connected, client, muted, audioRecorder]);

  return (
    <div>
      <button onClick={connected ? disconnect : connect}>
        {connected ? 'Disconnect' : 'Connect'}
      </button>
      <button onClick={() => setMuted(!muted)}>
        {muted ? 'Unmute' : 'Mute'}
      </button>
    </div>
  );
}
```

## 6. Implementation Checklist

1.  [ ] **Install Dependencies**: `npm install @google/genai eventemitter3 lodash`
2.  [ ] **Copy Library Files**: Move `lib/` contents (client, audio utils, worklets) to your project.
3.  [ ] **Create Hook**: Implement `useLiveApi.ts`.
4.  [ ] **Create Context**: Implement `LiveAPIContext.tsx`.
5.  [ ] **Wrap App**: Add `<LiveAPIProvider>` to your root component.
6.  [ ] **UI Integration**: Build a control component to trigger `connect()` and manage the `AudioRecorder`.

## 7. Troubleshooting

*   **AudioContext Issues**: Browsers require user interaction (click/keydown) before `AudioContext` can start. Ensure `connect` is called from a user event handler.
*   **Sample Rate**: Gemini expects **16kHz** input. The `AudioRecorder` and worklets must handle downsampling if the system rate is higher (e.g., 44.1kHz or 48kHz).
*   **API Key**: Ensure a valid `REACT_APP_GEMINI_API_KEY` or equivalent environment variable is set.

## 8. Critical Integration Fixes

If you are migrating from an existing setup or encountering connection issues, verify the following:

### 8.1. Hook Name Collision (`use-live-api.ts`)

**Issue:** If your project already has a `hooks/use-live-api.ts` that re-exports context (common in `stock-terminal`), overwriting it with the implementation logic will break imports in components like `RightSidebar.jsx`.

**Fix:**
1.  Rename the implementation hook (the one from `avatars`) to `hooks/use-live-api-impl.ts`.
2.  Restore `hooks/use-live-api.ts` to simply export the context:
    ```typescript
    import { useLiveAPI } from '../contexts/LiveAPIContext';
    export { useLiveAPI };
    ```
3.  Update `LiveAPIContext.tsx` to import the logic from the new filename:
    ```typescript
    import { useLiveApi } from '../hooks/use-live-api-impl';
    ```

### 8.2. Missing Environment Variable

**Issue:** The connection fails immediately or credentials are missing.
**Fix:** Create a `.env` file in your frontend root directory:
```bash
VITE_GEMINI_API_KEY=your_api_key_here
```
Ensure your `LiveAPIContext.tsx` reads this correctly (e.g., using `import.meta.env.VITE_GEMINI_API_KEY`).

### 8.3. Package Version Mismatch

**Issue:** `GenAILiveClient` fails with "LiveClient is not a constructor" or type errors.
**Fix:** The `avatars` reference uses a specific version of the Google GenAI SDK. Ensure your `package.json` matches:
```json
"dependencies": {
  "@google/genai": "^0.0.21"  // NOT ^1.x.x
}
```
If you have a newer version installed (e.g., `^1.37.0`), downgrade or adjust the `genai-live-client.ts` code to match the new SDK signature.
