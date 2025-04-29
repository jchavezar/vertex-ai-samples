// src/components/PromptArea.tsx
'use client'; // Keep this if needed, but state is now in parent

import React from 'react';
import { FaMicrophone, FaPaperPlane } from 'react-icons/fa';

interface PromptAreaProps {
    promptText?: string;
    isLoading: boolean;
    onInputChange: (value: string) => void; // Function to update parent state
    onSubmit: () => void; // Function to trigger submission in parent
}

const PromptArea: React.FC<PromptAreaProps> = ({
                                                   promptText="",
                                                   isLoading,
                                                   onInputChange,
                                                   onSubmit
                                               }) => {

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) { // Allow Shift+Enter for newlines if needed later
            event.preventDefault(); // Prevent default form submission/newline
            onSubmit();
        }
    };

    return (
        // Keep the container styling, ensure it doesn't grow/shrink unexpectedly
        <div className="w-full shrink-0"> {/* Added shrink-0 */}
            <div className="h-16 bg-white border-t border-gray-200 flex items-center px-4 sm:px-8"> {/* Adjusted padding */}
                <div className="flex-1 flex items-center border border-gray-300 rounded-full px-4 py-2 mr-3 sm:mr-4 text-gray-400 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
                    <input
                        type="text"
                        placeholder="Ask a question"
                        className="flex-1 outline-none bg-transparent text-gray-800 placeholder-gray-500"
                        onChange={(e) => {
                            if (typeof onInputChange === 'function') {
                                onInputChange(e.target.value);
                            }
                        }}
                        onKeyDown={handleKeyDown}
                        value={promptText} // Controlled input
                        disabled={isLoading} // Disable input while loading
                    />
                    <FaMicrophone className={`text-gray-500 ml-2 ${isLoading ? 'cursor-not-allowed' : 'cursor-pointer hover:text-gray-700'}`} /> {/* Style microphone */}
                </div>
                <button
                    className={`bg-blue-600 text-white rounded-full p-3 transition-colors duration-200 ${
                        (!promptText.trim() || isLoading)
                            ? 'opacity-50 cursor-not-allowed'
                            : 'hover:bg-blue-700'
                    }`}
                    onClick={onSubmit} // Call parent's handler
                    disabled={!promptText.trim() || isLoading} // Disable button correctly
                >
                    <FaPaperPlane />
                </button>
            </div>
            {/* <div className="bg-gray-800 text-white px-4 py-1 text-xs flex items-center justify-end">
                 <button className="bg-red-600 hover:bg-red-700 text-white px-2 py-0.5 rounded text-xs flex items-center">
                     N <span className="ml-1 text-sm">✕</span> Issue X
                 </button>
            </div> */}
        </div>
    );
};

export default PromptArea;