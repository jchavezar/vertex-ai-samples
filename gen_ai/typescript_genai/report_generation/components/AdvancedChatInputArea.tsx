import React, { useState } from 'react';
import { AlertType } from '../types';

interface ChatInputActionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: string;
  imgSrc?: string; // For custom icons like Google logo
  label: string;
  isActive?: boolean;
  showLabel?: boolean;
}

const ChatInputActionButton: React.FC<ChatInputActionButtonProps> = ({ icon, imgSrc, label, isActive, showLabel = true, ...props }) => (
  <button
    {...props}
    aria-label={label}
    className={`flex flex-col items-center justify-center p-2 rounded-md min-w-[70px] h-[56px] transition-colors duration-150 group
                ${isActive ? 'bg-dj-blue/10 text-dj-blue' : 'bg-action-button-bg text-action-button-text hover:bg-action-button-hover-bg'}
                disabled:opacity-60 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-dj-blue`}
  >
    {imgSrc ? (
      <img src={imgSrc} alt={`${label} icon`} className="h-5 w-5 mb-0.5" />
    ) : icon && (
      <span className="material-symbols-outlined text-xl mb-0.5 text-icon-color group-hover:text-text-primary transition-colors">
        {icon}
      </span>
    )}
    {showLabel && <span className={`text-xs ${isActive ? 'text-dj-blue font-medium' : 'text-action-button-text group-hover:text-text-primary'}`}>{label}</span>}
  </button>
);


interface AdvancedChatInputAreaProps {
  onSendText: (text: string) => void;
  isAwaitingResponse: boolean;
  onPlusButtonClick: () => void;
  onSearchButtonClick: () => void;
  isSearchActive: boolean;
  addAlert: (message: string, type: AlertType, duration?: number) => void;
}

export const AdvancedChatInputArea: React.FC<AdvancedChatInputAreaProps> = ({
  onSendText,
  isAwaitingResponse,
  onPlusButtonClick,
  onSearchButtonClick,
  isSearchActive,
  addAlert,
}) => {
  const [inputText, setInputText] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    // Auto-resize textarea
    e.target.style.height = 'inherit';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const handleSubmitText = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (inputText.trim() && !isAwaitingResponse) {
      onSendText(inputText.trim());
      setInputText('');
      // Reset textarea height after send
      const textarea = e?.target instanceof HTMLFormElement ? e.target.querySelector('textarea') : null;
      if (textarea) {
        textarea.style.height = 'inherit';
      }
    }
  };
  
  const googleLogoSvg = `data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjQ4cHgiIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAwIDQ4IDQ4Ij4KPGc+CjxwYXRoIGZpbGw9IiNGQkJDMDUiIGQ9Ik05LjgyLDIwLjgydjYuMzZoMTEuMzFjLTAuNTEsMy41MS0zLjY2LDYuMDctNy4zOCw2LjA3Yy01LjY5LDAtMTAuMy00LjU4LTEwLjMtMTAuMjNzNC42MS0xMC4yMywxMC4zLTEwLjIzIGMyLjU5LDAsNS4xOSwwLjkxLDcuMSwzLjE5bDQuNzYtNC43NkMyNi45Myw2LjAxLDIyLjM0LDQsMTcuMjQsNEM5LjgzLDQsMy41LDEwLjEzLDMuNSwxNy41UzkuODMsMzEuMywxNy4yNCwzMS4zIGM2LjYyLDAsMTEuNjYtMy44MSwxMS42Ni0xMS4zMVYyMC44Mkg5LjgyeiIvPgo8cG9seWdvbiBmaWxsPSIjRUFBNTMwIiBwb2ludHM9IjM5LjY0LDIzLjQ5IDM2LjMyLDIwLjE1IDMxLjU5LDI0Ljg4IDMxLjU5LDI0Ljg4IDI5LjY3LDI2LjgxIDM2LjMyLDMzLjQ5IDM2LjMyLDMzLjQ5IDM2LjM1LDMzLjUyIDM5LjY3LTMwLjIgICIvPgo8cG9seWdvbiBmaWxsPSIjNDI4NUY0IiBwb2ludHM9IjQyLjYyLDMwLjE3IDM5LjY0LDIzLjQ5IDM2LjMyLDMzLjQ5IDM2LjMzLDMzLjQ5IDM2LjM1LDMzLjUyIDM5LjY3LDMwLjIgICIvPgo8cG9seWxpbmUgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjM0E3OUUwIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBwb2ludHM9IjMxLjQxLDE2LjE2IDM5LjY0LDIzLjQ5IDM2LjMyLDMzLjQ5ICIvPgo8L2c+Cjwvc3ZnPg==`;


  return (
    <div className="bg-chat-input-bg px-4 pt-3 pb-4 sm:pb-6 w-full shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
      {/* Action buttons below input */}
      <div className="flex justify-start space-x-2 mb-3">
        <ChatInputActionButton
          icon="add_circle_outline"
          onClick={onPlusButtonClick}
          disabled={isAwaitingResponse}
          label="Upload"
        />
        <ChatInputActionButton
          imgSrc={googleLogoSvg}
          onClick={onSearchButtonClick}
          disabled={isAwaitingResponse}
          label="Search"
          isActive={isSearchActive}
        />
         <ChatInputActionButton
          icon="science" 
          onClick={() => addAlert('Deep Research feature is not yet implemented.', AlertType.INFO)}
          disabled={isAwaitingResponse}
          label="Deep Research"
        />
        <ChatInputActionButton
          icon="palette" 
          onClick={() => addAlert('Canvas feature is not yet implemented.', AlertType.INFO)}
          disabled={isAwaitingResponse}
          label="Canvas"
        />
         <ChatInputActionButton
          icon="movie" 
          onClick={() => addAlert('Video feature is not yet implemented.', AlertType.INFO)}
          disabled={isAwaitingResponse}
          label="Video"
        />
      </div>

      {/* Main input area */}
      <form onSubmit={handleSubmitText} className="flex items-end space-x-2 bg-white p-2 rounded-2xl border border-chat-input-border shadow-sm">
        <textarea
          value={inputText}
          onChange={handleInputChange}
          placeholder="Ask Gemini"
          className="flex-grow py-2.5 px-3 bg-transparent border-none resize-none focus:ring-0 outline-none text-sm sm:text-base text-text-primary placeholder-text-secondary min-h-[24px] max-h-36" // min-h set by py-2.5 effectively
          rows={1}
          disabled={isAwaitingResponse}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmitText();
            }
          }}
          aria-label="Chat input"
        />
        <button
          type="submit"
          disabled={isAwaitingResponse || !inputText.trim()}
          aria-label="Send message"
          className={`flex items-center justify-center h-10 w-10 min-w-[40px] rounded-full transition-colors duration-150
                      ${inputText.trim() && !isAwaitingResponse ? 'bg-dj-blue text-white' : 'bg-transparent text-icon-color'} 
                      disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-dj-blue`}
        >
          <span className="material-symbols-outlined text-2xl leading-none">send</span>
        </button>
      </form>
    </div>
  );
};