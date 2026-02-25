# Comprehensive Codebase Refactoring & Modernization Report (Jan 24, 2026)

**Context:** "Antigravity" Stock Terminal Application (FastAPI + React).
**Target Architecture:** Agentic AI with React 19 + Vercel AI SDK (Protocol v1).
**Models:** Gemini 3.0 Pro/Flash (Native Structured Outputs).

---

## 1. Executive Vision: The "Zero-Parsing" Architecture

The current codebase suffers from **Protocol Fragility**. You are currently treating LLM output as a raw string and using Regex (`[CHART]...[/CHART]`) to extract meaning. This is the 2023 way of building AI apps.

In 2026, we strictly separate **Content** (Text) from **Data** (Tool Calls, Charts, Widgets).
*   **Text** flows through standard streams.
*   **Data** flows through structured channels (Server-Sent Events with specific Type Codes).
*   **State** is managed by robust libraries (Zustand/TanStack Query), not manual `useEffect` loops.

This report provides the fundamental knowledge base to execute this transformation.

---

## 2. The Vercel AI SDK Data Protocol (Deep Dive)

To replace your manual `TextDecoder` loop, you must understand what the AI SDK expects from your FastAPI backend. The SDK uses a **Data Stream Protocol** over SSE (Server-Sent Events).

### 2.1 The Protocol Specification
The backend streams line-delimited events. Each line starts with a **Type Code** and a **Payload**.

| Code | Type | Payload Format | Usage |
| :--- | :--- | :--- | :--- |
| `0:` | **Text Part** | `0:"Hello"` | Standard text chunks for the chat bubble. |
| `2:` | **Data Part** | `2:[{"chart": ...}]` | Arbitrary JSON data (Widgets, Charts, Auth Status). |
| `9:` | **Tool Call** | `9:{"toolCallId": "...", "toolName": "...", "args": {}}` | The standard way to trigger client-side or server-side tools. |
| `e:` | **Error** | `e:{"error": "..."}` | Stream error handling. |

### 2.2 Why this matters for Antigravity?
Currently, your "Healer" functions (`fix_leaked_data_blocks`) try to find JSON inside the `0:` text stream.
**Refactoring Goal:** Your backend agents should yield `2:` events for widgets and `0:` events for text. The frontend `useChat` hook will separate them automatically.

---

## 3. Backend Implementation (FastAPI + Pydantic V2)

We need a standardized way to yield these protocol parts from FastAPI.

### 3.1 Protocol Helper (`backend/protocol.py`)
*Create this file to manage the serialization.*

```python
import json
from typing import Any

class AIStreamProtocol:
    @staticmethod
    def text(content: str) -> str:
        """Type 0: Text Part"""
        return f'0:{json.dumps(content)}\n'

    @staticmethod
    def data(payload: Any) -> str:
        """Type 2: Data Part (Widgets, Charts)"""
        # The SDK expects an array of data objects for 'data' events
        return f'2:{json.dumps([payload])}\n'

    @staticmethod
    def tool_call(call_id: str, name: str, args: dict) -> str:
        """Type 9: Tool Call"""
        payload = {"toolCallId": call_id, "toolName": name, "args": args}
        return f'9:{json.dumps(payload)}\n'
        
    @staticmethod
    def error(message: str) -> str:
        """Type e: Error"""
        return f'e:{json.dumps(message)}\n'
```

### 3.2 Structured Output Agent (`backend/agent.py`)
*Use Gemini 3.0's native schema enforcement to guarantee valid widget data, then stream it.*

```python
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import Literal, Union, List
from backend.protocol import AIStreamProtocol

# 1. Define the Schema (The Contract)
class LineChart(BaseModel):
    type: Literal["line_chart"]
    title: str
    series: List[dict]

class TextResponse(BaseModel):
    type: Literal["text"]
    content: str

class AgentResponse(BaseModel):
    # Gemini will strictly adhere to this union
    part: Union[LineChart, TextResponse]

# 2. The Generator
async def stream_agent_response(user_query: str):
    # Configure Gemini with Pydantic Schema
    model = genai.GenerativeModel("gemini-1.5-flash") # Or "gemini-3.0-pro"
    
    # Generate content stream with strict schema
    response = model.generate_content(
        user_query,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=AgentResponse
        ),
        stream=True
    )
    
    for chunk in response:
        # In a real scenario, you parse the partial JSON or wait for full object.
        # For simplicity, assume we process complete objects or use a parser.
        # Note: 'chunk.text' might be partial JSON.
        pass 
        # Implementation detail: You likely need to accumulate text until valid JSON
        # or use the non-streaming mode for the widget generation part to guarantee validity.
```

---

## 4. Frontend Architecture (React 19 + AI SDK)

The "God Component" `RightSidebar.jsx` must be dismantled. We will use **Zustand** for global dashboard state and **AI SDK** for the chat stream.

### 4.1 Global State (`src/store/dashboardStore.ts`)
*Stop prop-drilling `setChartOverride` through 5 layers of components.*

```typescript
import { create } from 'zustand';

interface ChartData {
  title: string;
  chartType: 'line' | 'bar' | 'pie';
  data: any[];
}

interface DashboardState {
  activeChart: ChartData | null;
  setActiveChart: (chart: ChartData | null) => void;
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  activeChart: null,
  setActiveChart: (chart) => set({ activeChart: chart }),
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
```

### 4.2 The Custom Hook (`src/hooks/useTerminalChat.ts`)
*This replaces the massive `useEffect` loop in RightSidebar.*

```typescript
import { useChat } from 'ai/react';
import { useDashboardStore } from '../store/dashboardStore';
import { useEffect } from 'react';

export function useTerminalChat() {
  const setActiveChart = useDashboardStore((s) => s.setActiveChart);

  const { messages, input, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: 'http://localhost:8001/chat',
    
    // AI SDK Protocol: 'data' contains the accumulated Type 2 events
    onFinish: (message, options) => {
        // Optional: telemetry or cleanup
    }
  });

  // Reactive Data Processor
  // Whenever the backend sends a Type 2 (Data) event, we check if it's a chart
  useEffect(() => {
    if (!data) return;
    
    // Get the latest data block
    const latestBlock = data[data.length - 1]; 
    
    // Check our Pydantic schema type
    if (latestBlock && latestBlock.type === 'line_chart') {
       setActiveChart(latestBlock); // Automatically updates the Main Dashboard
    }
  }, [data, setActiveChart]);

  return { messages, input, handleInputChange, handleSubmit, isLoading };
}
```

### 4.3 Component Decomposition (Atomic Design)
Refactor `RightSidebar.jsx` into:

1.  **`ChatContainer`** (Layout only)
2.  **`MessageList`** (Renders `messages.map(...)`)
3.  **`ToolInvocation`** (Renders active tool states like "Searching FactSet...")
4.  **`ChatInput`** (Input field + Attachments)

**Example `MessageList.tsx`:**
```tsx
import { Message } from 'ai';

export const MessageList = ({ messages }: { messages: Message[] }) => {
  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto">
      {messages.map((m) => (
        <div key={m.id} className={`message ${m.role}`}>
          <div className="prose">{m.content}</div>
          
          {/* Render Tool Invocations (Type 9 Events) */}
          {m.toolInvocations?.map((tool) => (
            <div key={tool.toolCallId} className="tool-badge bg-blue-100 p-2 rounded">
               {tool.toolName === 'FactSet_Prices' ? 'Fetching Prices...' : 'Processing...'}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
```

---

## 5. Testing Strategy (2026 Standards)

How do you verify this works without clicking around?

### 5.1 Backend Stream Testing (`pytest`)
You can't just assert the status code. You must consume the generator.

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_stream_protocol():
    async with AsyncClient(base_url="http://test") as ac:
        async with ac.stream("POST", "/chat", json={"message": "Show Apple prices"}) as response:
            events = [line async for line in response.aiter_lines()]
            
            # Assert we got the Protocol headers
            assert response.headers["content-type"] == "text/event-stream"
            
            # Assert we got a Data part (The Chart)
            # Expecting: 2:[{"type": "line_chart", ...}]
            data_events = [e for e in events if e.startswith("2:")]
            assert len(data_events) > 0
            assert "line_chart" in data_events[0]
```

### 5.2 Frontend Stream Testing (Vitest + MSW)
Mock the streaming endpoint to return the protocol strings.

```javascript
// mocks/handlers.js
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('http://localhost:8001/chat', () => {
    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder();
        // Simulate Protocol v1 Stream
        controller.enqueue(encoder.encode('0:"Here is the "\n'));
        controller.enqueue(encoder.encode('0:"chart."\n'));
        controller.enqueue(encoder.encode('2:[{"type":"line_chart","title":"AAPL"}]\n'));
        controller.close();
      }
    });
    
    return new HttpResponse(stream, {
      headers: { 'Content-Type': 'text/event-stream' }
    });
  })
];
```

---

## 6. Migration Checklist

1.  **Backend:**
    *   [ ] Install `pydantic>=2.0`.
    *   [ ] Implement `AIStreamProtocol` helper class.
    *   [ ] Update `main.py` chat endpoint to use `StreamingResponse` with the protocol format.
    *   [ ] Remove `fix_leaked_data_blocks` (Healer).

2.  **Frontend:**
    *   [ ] Install `ai` (Vercel AI SDK), `zustand`, `clsx`, `tailwind-merge`.
    *   [ ] Create `dashboardStore.ts`.
    *   [ ] Create `useTerminalChat.ts`.
    *   [ ] Deconstruct `RightSidebar.jsx` into smaller components.
    *   [ ] Remove manual `fetch` / `TextDecoder` logic.

3.  **Validation:**
    *   [ ] Run `pytest` with stream consumption.
    *   [ ] Verify Chart Widgets update automatically via the `2:` data channel.