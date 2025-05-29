import React from 'react';
import { FileUpload } from './FileUpload';
import { HomeViewStateType } from '../types';

interface SidebarProps {
  onFileSelect: (file: File) => void;
  onAnalyze: () => void;
  onGeneratePdf: () => void;
  isFileUploaded: boolean;
  isAnalyzed: boolean;
  isLoading: boolean;
  currentView: HomeViewStateType; 
  onSetView: (view: HomeViewStateType) => void; 
}

const SidebarButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { icon?: string, active?: boolean }> = ({ children, icon, active, ...props }) => (
  <button
    {...props}
    className={`w-full flex items-center justify-center text-sm font-medium px-4 py-3 rounded-lg transition-colors duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-dj-blue
                ${props.disabled ? 'bg-dj-light-gray text-dj-text-secondary cursor-not-allowed' : 
                                   active ? 'bg-dj-blue text-dj-white' :
                                   'bg-dj-secondary-blue/80 text-dj-text-primary hover:bg-dj-blue hover:text-dj-white' 
                                 }
                ${props.className?.includes('bg-dj-gray') && !props.disabled && !active ? 'hover:bg-opacity-80' : ''} 
              `}
  >
    {icon && <span className="material-symbols-outlined mr-2 text-base">{icon}</span>}
    {children}
  </button>
);


export const Sidebar: React.FC<SidebarProps> = ({
  onFileSelect,
  onAnalyze,
  onGeneratePdf,
  isFileUploaded,
  isAnalyzed,
  isLoading,
  currentView,
  onSetView,
}) => {
  
  const chatButtonText = "Chat with AI"; 

  return (
    <aside className="w-72 md:w-80 bg-chat-input-bg p-5 shadow-lg flex-shrink-0 overflow-y-auto border-r border-dj-light-gray">
      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-dj-text-secondary uppercase tracking-wider mb-3">Insight Engine</h3>
          <p className="text-xs text-dj-text-secondary/80 mb-3">Upload, Analyze, Preview & Chat.</p>
        </div>

        <section className="space-y-2">
          <h4 className="text-dj-text-primary font-medium">1. Upload</h4>
          <FileUpload onFileSelect={onFileSelect} disabled={isLoading} />
        </section>

        <section className="space-y-2">
          <h4 className="text-dj-text-primary font-medium">2. Analyze</h4>
          <SidebarButton 
            onClick={onAnalyze} 
            disabled={!isFileUploaded || isLoading} 
            icon="monitoring"
            active={currentView === HomeViewStateType.REPORT_DISPLAY && isAnalyzed}
          >
            {isLoading && isAnalyzed ? 'Analyzing...' : 'Analyze Data'}
          </SidebarButton>
        </section>

        <section className="space-y-2">
          <h4 className="text-dj-text-primary font-medium">3. PDF Report</h4>
          <SidebarButton 
            onClick={onGeneratePdf} 
            disabled={!isAnalyzed || isLoading} 
            icon="picture_as_pdf"
            active={currentView === HomeViewStateType.PDF_PREVIEW}
          >
            {isLoading && currentView === HomeViewStateType.PDF_PREVIEW ? 'Generating PDF...' : 'Generate & View PDF'}
          </SidebarButton>
        </section>

        <section className="space-y-2">
          <h4 className="text-dj-text-primary font-medium">4. Interact</h4>
          <SidebarButton 
            onClick={() => onSetView(HomeViewStateType.MODERN_CHAT)} 
            disabled={isLoading && currentView === HomeViewStateType.MODERN_CHAT} 
            icon="chat"
            active={currentView === HomeViewStateType.MODERN_CHAT}
          >
            {isLoading && currentView === HomeViewStateType.MODERN_CHAT ? 'Loading Chat...' : chatButtonText}
          </SidebarButton>
        </section>
      </div>
    </aside>
  );
};