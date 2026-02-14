import { useChat } from '@ai-sdk/react';
import { useEffect } from 'react';
import { useDashboardStore } from '../store/dashboardStore';
import type { ProjectCardData } from '../store/dashboardStore';

export function useTerminalChat(token: string | null) {
  const addProjectCard = useDashboardStore((s) => s.addProjectCard);
  const clearCards = useDashboardStore((s) => s.clearCards);

  const { messages, input, handleInputChange, handleSubmit, data, isLoading } = useChat({
    api: '/chat',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });

  // Listen for Type 2 Data events 
  useEffect(() => {
    if (!data || data.length === 0) return;
    const latest = data[data.length - 1];

    // Handle Vercel AI SDK array parsing
    if (Array.isArray(latest)) {
      const payload = latest[0] as any;
      if (payload && payload.type === 'project_card' && payload.data) {
        addProjectCard(payload.data as ProjectCardData);
      }
    } else {
      const payload = latest as any;
      if (payload && payload.type === 'project_card' && payload.data) {
        addProjectCard(payload.data as ProjectCardData);
      }
    }
  }, [data, addProjectCard]);

  const customHandleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearCards();
    handleSubmit(e);
  };

  return { messages, input, handleInputChange, handleSubmit: customHandleSubmit, isLoading, hasData: !!data && data.length > 0 };
}
