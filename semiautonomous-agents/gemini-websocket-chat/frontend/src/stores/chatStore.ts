import { create } from 'zustand';
import type { Message, Session, ModelKey, WSMessage } from '../types';
import { createWebSocket, sendWSMessage, fetchSessions } from '../api/client';

interface ChatState {
  // State
  messages: Message[];
  sessions: Session[];
  currentSessionId: string | null;
  model: ModelKey;
  isStreaming: boolean;
  streamingContent: string;
  ws: WebSocket | null;
  sidebarOpen: boolean;

  // Actions
  setModel: (model: ModelKey) => void;
  toggleSidebar: () => void;
  loadSessions: () => Promise<void>;
  selectSession: (id: string) => void;
  newSession: () => void;
  sendMessage: (content: string) => void;
  initWebSocket: () => void;
}

let msgCounter = 0;

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessions: [],
  currentSessionId: null,
  model: '2.5-flash',
  isStreaming: false,
  streamingContent: '',
  ws: null,
  sidebarOpen: false,

  setModel: (model) => set({ model }),

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  loadSessions: async () => {
    try {
      const sessions = await fetchSessions();
      set({ sessions });
    } catch {
      // Backend might not be ready yet
    }
  },

  selectSession: (id) => {
    set({ currentSessionId: id, messages: [], sidebarOpen: false });
    // TODO: load session messages from backend in future phase
  },

  newSession: () => {
    set({ currentSessionId: null, messages: [], sidebarOpen: false });
  },

  initWebSocket: () => {
    const existing = get().ws;
    if (existing && existing.readyState === WebSocket.OPEN) return;

    const ws = createWebSocket(
      (msg: WSMessage) => {
        const state = get();

        switch (msg.type) {
          case 'session':
            set({ currentSessionId: msg.session_id || null });
            break;

          case 'chunk':
            set({ streamingContent: state.streamingContent + (msg.content || '') });
            break;

          case 'done': {
            const assistantMsg: Message = {
              id: `msg-${++msgCounter}`,
              role: 'assistant',
              content: state.streamingContent,
              timestamp: Date.now(),
              model: state.model,
            };
            set({
              messages: [...state.messages, assistantMsg],
              isStreaming: false,
              streamingContent: '',
            });
            // Refresh session list
            get().loadSessions();
            break;
          }

          case 'error':
            set({
              isStreaming: false,
              streamingContent: '',
              messages: [
                ...state.messages,
                {
                  id: `msg-${++msgCounter}`,
                  role: 'assistant',
                  content: `[error] ${msg.content}`,
                  timestamp: Date.now(),
                },
              ],
            });
            break;
        }
      },
      () => {
        set({ ws: null });
        // Reconnect after 2s
        setTimeout(() => get().initWebSocket(), 2000);
      },
    );

    set({ ws });
  },

  sendMessage: (content: string) => {
    const { ws, model, currentSessionId, messages } = get();

    const userMsg: Message = {
      id: `msg-${++msgCounter}`,
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    set({
      messages: [...messages, userMsg],
      isStreaming: true,
      streamingContent: '',
    });

    if (ws && ws.readyState === WebSocket.OPEN) {
      sendWSMessage(ws, content, currentSessionId || undefined, model);
    } else {
      // Reconnect and retry
      get().initWebSocket();
      setTimeout(() => {
        const newWs = get().ws;
        if (newWs && newWs.readyState === WebSocket.OPEN) {
          sendWSMessage(newWs, content, currentSessionId || undefined, model);
        }
      }, 1000);
    }
  },
}));
