// src/components/MainContent.tsx
import React from 'react';
// Import the message type definition - adjust path if needed
import { ConversationMessage } from '@/app/page'; // Assuming it's exported from page.tsx

// --- UPDATE THE PROPS INTERFACE ---
interface MainContentProps {
    conversation: ConversationMessage[];
    isLoading: boolean;
    // Add the ref prop here:
    conversationEndRef: React.RefObject<HTMLDivElement | null>;
}

// --- Welcome Content Component (keep as is or customize) ---
const WelcomeContent = () => (
    <div className="p-6">
        <h1 className="text-2xl font-semibold mb-6 text-gray-700">Welcome to the Sustainability Assistant</h1>
        <p className="text-gray-600 mb-6">
            Ask me anything about Deloitte's sustainability tools, ESG goals, climate strategies, or competitor analysis. Here are some examples:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Suggested questions - styled for better readability */}
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200 text-sm text-gray-800 hover:bg-gray-50 cursor-default">
                Which Deloitte tools or assets can assist a potential client in achieving targets related to climate transition risks and strategies?
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200 text-sm text-gray-800 hover:bg-gray-50 cursor-default">
                Outline the pros and cons of leveraging Deloitte services and tools versus using a competitor's services and tools for achieving a climate transition strategy?
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200 text-sm text-gray-800 hover:bg-gray-50 cursor-default">
                How can Deloitte's sustainability tools support a potential manufacturing client in achieving their ESG (Environmental, Social, and Governance) goals?
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200 text-sm text-gray-800 hover:bg-gray-50 cursor-default">
                What are the key sustainability initiatives of [Company Name] and how do they compare to their top 5 competitors?
            </div>
        </div>
    </div>
);


// --- Conversation Display Component (Accepts conversation and isLoading) ---
// Note: It doesn't need the ref directly
const ConversationDisplay: React.FC<Omit<MainContentProps, 'conversationEndRef'>> = ({ conversation, isLoading }) => (
    <div className="space-y-4 pb-4"> {/* Padding at the bottom */}
        {conversation.map((message) => (
            <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
                <div
                    className={`max-w-xl lg:max-w-2xl px-4 py-2 rounded-lg shadow break-words ${ // Added break-words
                        message.type === 'user'
                            ? 'bg-blue-500 text-white'
                            : message.type === 'ai'
                                ? 'bg-white text-gray-800 border border-gray-200'
                                : 'bg-red-100 text-red-700 border border-red-300'
                    }`}
                >
                    {/* Render text preserving line breaks */}
                    {message.text.split('\n').map((line, index, arr) => (
                        <React.Fragment key={index}>
                            {line}
                            {index < arr.length - 1 && <br />}
                        </React.Fragment>
                    ))}
                </div>
            </div>
        ))}
        {/* Loading Indicator */}
        {isLoading && (
            <div className="flex justify-start">
                <div className="px-4 py-2 rounded-lg bg-gray-200 text-gray-600 animate-pulse shadow">
                    Thinking...
                </div>
            </div>
        )}
    </div>
);


// --- MainContent Component ---
// --- UPDATE THE FUNCTION SIGNATURE TO ACCEPT THE REF ---
const MainContent: React.FC<MainContentProps> = ({ conversation, isLoading, conversationEndRef }) => {
    return (
        // This outer div handles the scrolling
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            {/* Conditionally render Welcome or Conversation */}
            {!conversation || conversation.length === 0 ? (
                <WelcomeContent />
            ) : (
                <ConversationDisplay conversation={conversation} isLoading={isLoading} />
            )}
            {/* --- ADD THIS DIV AND ATTACH THE REF --- */}
            {/* This empty div is the target for scrolling */}
            <div ref={conversationEndRef} />
        </div>
    );
};

export default MainContent;