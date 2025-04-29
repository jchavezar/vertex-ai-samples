// src/app/page.tsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import MainContent from '@/components/MainContent';
import PromptArea from '@/components/PromptArea';
import Footer from '@/components/Footer';

// --- Define the structure for a conversation message ---
export interface ConversationMessage {
    id: number;
    type: 'user' | 'ai' | 'error';
    text: string;
}

// --- Define the expected structure of the backend response ---
interface BackendResponse {
    session_id: string;
    final_response: string | null;
    final_session_state: Record<string, any>; // Or a more specific type if known
}

// --- Function to call your FastAPI backend ---
const callBackendApi = async (
    prompt: string,
    userId: string,
    sessionId: string | null // Allow passing null for new sessions
): Promise<{ responseText: string | null; sessionId: string | null; error?: string }> => {
    const backendUrl = 'http://127.0.0.1:8000/invoke'; // Your FastAPI endpoint

    console.log(`Calling backend API for user: ${userId}, session: ${sessionId || '(new)'}`);

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json', // Explicitly accept JSON
            },
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId, // Send null if no session yet
                query: prompt,
            }),
        });

        if (!response.ok) {
            // Try to get error details from the backend response body
            let errorDetail = `HTTP error! Status: ${response.status}`;
            try {
                const errorJson = await response.json();
                errorDetail = errorJson.detail || errorDetail; // Use detail from FastAPI's HTTPException if available
            } catch (e) {
                // Ignore if response body is not JSON or empty
            }
            console.error("Backend API error:", errorDetail);
            return { responseText: null, sessionId: sessionId, error: `Error from backend: ${errorDetail}` };
        }

        const data: BackendResponse = await response.json();
        console.log("Backend Response:", data);

        // Return the final response text and the session ID (which might be new or the same)
        return {
            responseText: data.final_response,
            sessionId: data.session_id,
        };

    } catch (error) {
        console.error("Error calling Backend API:", error);
        let errorMessage = "An unknown network error occurred while contacting the backend.";
        if (error instanceof Error) {
            errorMessage = `Network or fetch error: ${error.message}`;
        }
        return { responseText: null, sessionId: sessionId, error: errorMessage };
    }
};
// --- End Backend API call function ---

// --- Renamed component to Page for app router ---
export default function Page() {
    const [promptText, setPromptText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversation, setConversation] = useState<ConversationMessage[]>([]);
    const [messageIdCounter, setMessageIdCounter] = useState(0);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null); // State to store session ID
    const conversationEndRef = useRef<HTMLDivElement>(null);

    // Define a user ID (could be dynamic in a real app)
    const userId = "sustainability_app_user_01";

    useEffect(() => {
        conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    const handleInputChange = (value: string) => {
        setPromptText(value);
    };

    const handleSubmit = async () => {
        const trimmedPrompt = promptText.trim();
        if (!trimmedPrompt || isLoading) return;

        const userMessage: ConversationMessage = {
            id: messageIdCounter,
            type: 'user',
            text: trimmedPrompt,
        };

        // Add user message optimistically
        setConversation(prev => [...prev, userMessage]);
        setPromptText('');
        const currentMessageId = messageIdCounter;
        setMessageIdCounter(prev => prev + 1); // Increment for the *next* message slot (AI/Error)
        setIsLoading(true);

        console.log("Sending prompt to backend:", userMessage.text);

        // Call the backend API function
        const { responseText, sessionId: returnedSessionId, error } = await callBackendApi(
            userMessage.text,
            userId,
            currentSessionId // Pass the current session ID (or null if none)
        );

        let responseMessage: ConversationMessage;

        if (error) {
            responseMessage = {
                id: currentMessageId + 1, // Use the next ID slot
                type: 'error',
                text: error,
            };
        } else if (responseText) {
            responseMessage = {
                id: currentMessageId + 1,
                type: 'ai',
                text: responseText,
            };
        } else {
            responseMessage = {
                id: currentMessageId + 1,
                type: 'error',
                text: "Received an empty response from the backend.",
            };
        }

        // Add AI or Error message
        setConversation(prev => [...prev, responseMessage]);

        // Update the session ID state with the one returned from the backend
        if (returnedSessionId) {
            console.log("Updating session ID to:", returnedSessionId);
            setCurrentSessionId(returnedSessionId);
        }

        // Increment ID counter *again* to be ready for the next user message
        setMessageIdCounter(prev => prev + 1);
        setIsLoading(false);
    };

    return (
        <div className="flex flex-col h-screen overflow-hidden bg-gray-100">
            <Header />
            <div className="flex flex-1 overflow-hidden">
                <Sidebar />
                <main className="flex-1 flex flex-col overflow-hidden">
                    <MainContent
                        conversation={conversation}
                        isLoading={isLoading}
                        conversationEndRef={conversationEndRef}
                    />
                    <PromptArea
                        promptText={promptText}
                        isLoading={isLoading}
                        onInputChange={handleInputChange}
                        onSubmit={handleSubmit}
                    />
                </main>
            </div>
            <Footer />
        </div>
    );
};