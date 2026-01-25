import { useChat } from 'ai/react';
import { useEffect } from 'react';
import { useDashboardStore, WidgetData } from '../store/dashboardStore';

export function useTerminalChat() {
  const setActiveWidget = useDashboardStore((s) => s.setActiveWidget);

  const { messages, input, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: 'http://localhost:8085/chat',
    
    // AI SDK Protocol: 'data' contains the accumulated Type 2 events
    onFinish: (message) => {
        console.log("Chat finished:", message);
    }
  });

  // Reactive Data Processor
  // Whenever the backend sends a Type 2 (Data) event, we check if it's a widget
  useEffect(() => {
    if (!data) return;
    
    // Get the latest data block
    // The data array accumulates all data parts sent during the session
    const latestBlock = data[data.length - 1]; 
    console.log("Received Data Block:", latestBlock);
    
    // Check our Pydantic schema type match
    // The protocol wraps the payload in an array (e.g., 2:[{...}])
    // But useChat 'data' property flattens this, it depends on the SDK version.
    // In SDK 3.0+, 'data' is an array of JSON objects received.
    
    if (latestBlock && typeof latestBlock === 'object') {
        const widget = latestBlock as any;
        if (widget.type === 'chart' || widget.type === 'stats') {
            setActiveWidget(widget as WidgetData); 
        }
    }
  }, [data, setActiveWidget]);

  return { messages, input, handleInputChange, handleSubmit, isLoading };
}
