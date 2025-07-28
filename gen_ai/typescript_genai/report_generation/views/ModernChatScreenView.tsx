import React, { useState, useCallback, useEffect, useRef } from 'react';
import { ChatGreeting } from '../components/ChatGreeting';
import { ChatMessageDisplay } from '../components/ChatMessageDisplay';
import { AdvancedChatInputArea } from '../components/AdvancedChatInputArea';
import { Spinner } from '../components/Spinner';
import { parseSpreadsheet } from '../services/spreadsheetParser';
import { getGeminiChatInstance } from '../services/geminiService';
import { ParsedSpreadsheetData, AlertType, ChatMessage, MessageAuthor, SpreadsheetDataArray } from '../types';
import { type Chat, type GenerateContentResponse } from '@google/genai';
import { useAlert } from '../contexts/AlertContext';

const GUEST_USERNAME = "Guest";
const GENERAL_ASSISTANT_INSTRUCTION = "You are a helpful AI assistant. Answer general questions. When formatting your response, use markdown for clarity (e.g., lists, bolding).";

interface ModernChatScreenViewProps {
  initialSystemInstruction?: string;
  spreadsheetContext?: { data: SpreadsheetDataArray, fileName: string };
  onExit?: () => void; 
}

export const ModernChatScreenView: React.FC<ModernChatScreenViewProps> = ({ 
  initialSystemInstruction = GENERAL_ASSISTANT_INSTRUCTION, 
  spreadsheetContext,
  onExit
}) => {
  const { addAlert } = useAlert();

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [geminiChatInstance, setGeminiChatInstance] = useState<Chat | null>(null);
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [isSearchModeActive, setIsSearchModeActive] = useState<boolean>(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [currentSpreadsheetContext, setCurrentSpreadsheetContext] = useState(spreadsheetContext);


  const addMessageToChat = useCallback((text: string, author: MessageAuthor, groundingMetadata: ChatMessage['groundingMetadata'] = null) => {
    setChatMessages(prev => [...prev, { id: `${author}-${Date.now()}-${Math.random()}`, text, author, timestamp: new Date(), groundingMetadata }]);
  }, []);

  const initializeChat = useCallback(() => {
    try {
      const instruction = currentSpreadsheetContext 
        ? `Chatting about ${currentSpreadsheetContext.fileName}. Use the provided data.` 
        : initialSystemInstruction;
      const chat = getGeminiChatInstance(instruction, currentSpreadsheetContext);
      setGeminiChatInstance(chat);
      return chat;
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Failed to initialize AI chat.";
      addAlert(msg, AlertType.ERROR);
      addMessageToChat(msg, 'system');
      return null;
    }
  }, [addAlert, initialSystemInstruction, currentSpreadsheetContext, addMessageToChat]);

  useEffect(() => {
    setCurrentSpreadsheetContext(spreadsheetContext); 
  }, [spreadsheetContext]);
  
  useEffect(() => {
    const chatInstance = initializeChat();
    if (chatMessages.length === 0 && chatInstance) {
       const welcomeMsg = currentSpreadsheetContext 
            ? `File "${currentSpreadsheetContext.fileName}" is loaded. Ask me anything about this document.`
            : "Hello! I'm your AI assistant. How can I help you today?";
       addMessageToChat(welcomeMsg, 'system');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initializeChat, currentSpreadsheetContext]); 


  const handleFileSelectFromInput = async (file: File) => {
    if (!file) return;
    setIsLoading(true);
    setLoadingMessage(`Processing "${file.name}" for chat context...`);

    try {
      const parsed = await parseSpreadsheet(file);
      if (!parsed.sampleForAnalysis || parsed.sampleForAnalysis.length === 0 || 
          parsed.sampleForAnalysis.every(row => row.every(cell => cell === null || String(cell).trim() === ''))) {
         addAlert(`"${file.name}" is empty or has no analyzable data. Chat context not changed.`, AlertType.INFO);
         setIsLoading(false);
         return;
      }
      
      const newContext = { data: parsed.sampleForAnalysis, fileName: file.name };
      setCurrentSpreadsheetContext(newContext); 
      
      addMessageToChat(`Switched context to "${file.name}". Ask me anything about this new document.`, 'system');
      addAlert(`Chat context updated to "${file.name}".`, AlertType.SUCCESS);

    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      addAlert(`Error processing file for chat: ${msg}`, AlertType.ERROR);
      addMessageToChat(`Error loading "${file.name}" for chat. Context remains unchanged.`, 'system');
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };
  
  const sendChatMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim()) return;
    
    addMessageToChat(messageText, 'user');
    setIsLoading(true); 
    setLoadingMessage("AI is thinking...");

    let currentChat = geminiChatInstance;
    if (!currentChat) {
        currentChat = initializeChat(); 
        if (!currentChat) {
            addMessageToChat("Error: Chat service is not available. Please try again later.", 'system');
            setIsLoading(false); setLoadingMessage(""); return;
        }
    }

    try {
      let response: GenerateContentResponse;
      if (isSearchModeActive) {
         const { GoogleGenAI } = await import('@google/genai'); 
         const apiKey = process.env.API_KEY;
         const tempAi = new GoogleGenAI({ apiKey: apiKey || "MISSING_API_KEY" });
         response = await tempAi.models.generateContent({
            model: 'gemini-2.5-flash-preview-04-17',
            contents: [{ role: "user", parts: [{text: messageText }] }],
            config: { tools: [{googleSearch: {}}], thinkingConfig: { thinkingBudget: 0 } }
         });
      } else {
        response = await currentChat.sendMessage({ message: messageText });
      }
      
      const groundingMeta = response.candidates?.[0]?.groundingMetadata || null;
      addMessageToChat(response.text, 'ai', groundingMeta);

    } catch (error) {
      const msg = error instanceof Error ? error.message : "AI communication error.";
      addMessageToChat(`Error: ${msg}`, 'system');
      addAlert(msg, AlertType.ERROR);
    } finally {
      setIsLoading(false); setLoadingMessage("");
    }
  }, [geminiChatInstance, addAlert, addMessageToChat, isSearchModeActive, initializeChat]);

  const handleToggleSearchMode = () => {
    const newSearchModeState = !isSearchModeActive;
    setIsSearchModeActive(newSearchModeState);
    addAlert(`Google Search mode ${newSearchModeState ? 'activated' : 'deactivated'}.`, AlertType.INFO, 3000);
  };

  return (
    <div className="flex flex-col h-full max-h-full overflow-hidden bg-chat-input-bg relative">
      <style>{`body { background-color: rgb(var(--color-chat-input-bg)); }`}</style>
      {onExit && (
        <button
          onClick={onExit}
          className="absolute top-4 left-4 p-2 rounded-full hover:bg-action-button-hover-bg transition-colors z-10 focus:outline-none focus-visible:ring-2 focus-visible:ring-dj-blue"
          aria-label="Back to main application"
        >
          <span className="material-symbols-outlined text-icon-color">arrow_back</span>
        </button>
      )}
      <input 
        type="file" 
        ref={fileInputRef} 
        className="hidden" 
        onChange={(e) => e.target.files && e.target.files[0] && handleFileSelectFromInput(e.target.files[0])}
        accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
      />
      
      <div className="flex-shrink-0">
        <ChatGreeting userName={GUEST_USERNAME} />
      </div>
      
      <ChatMessageDisplay messages={chatMessages} />
      
      {isLoading && loadingMessage && (
         <div className="flex items-center justify-center px-4 py-2 text-sm text-text-secondary bg-transparent">
            <Spinner size="sm" color="text-dj-blue" />
            <span className="ml-2">{loadingMessage}</span>
        </div>
      )}
      
      <div className="flex-shrink-0 mt-auto">
        <AdvancedChatInputArea
          onSendText={sendChatMessage}
          isAwaitingResponse={isLoading}
          onPlusButtonClick={triggerFileUpload}
          onSearchButtonClick={handleToggleSearchMode}
          isSearchActive={isSearchModeActive}
          addAlert={addAlert}
        />
      </div>
    </div>
  );
};