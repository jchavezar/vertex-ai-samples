
import React, { useState, useCallback, useEffect } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ReportDisplay } from '../components/ReportDisplay';
import { Spinner } from '../components/Spinner';
import { ModernChatScreenView } from './ModernChatScreenView';
import { parseSpreadsheet } from '../services/spreadsheetParser';
import { analyzeSpreadsheetData, polishTextWithGemini } from '../services/geminiService'; // Import polishTextWithGemini
import { generatePdfReport } from '../services/pdfGenerator';
import { ParsedSpreadsheetData, ReportSection, AlertType, HomeViewStateType } from '../types';
import { useAlert } from '../contexts/AlertContext';

const GUEST_USERNAME = "Guest"; // Or fetch dynamically if authentication is added
const INITIAL_SYSTEM_INSTRUCTION_GENERAL_CHAT = "You are a helpful AI assistant. Answer general questions. When formatting your response, use markdown for clarity (e.g., lists, bolding).";


export const HomeView: React.FC = () => {
  const { addAlert } = useAlert();

  const [currentView, setCurrentView] = useState<HomeViewStateType>(HomeViewStateType.DASHBOARD);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [parsedSpreadsheetData, setParsedSpreadsheetData] = useState<ParsedSpreadsheetData | null>(null);
  const [reportSections, setReportSections] = useState<ReportSection[] | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>('');

  const isAnalyzed = !!reportSections;

  const resetStateForNewFile = () => {
    setParsedSpreadsheetData(null);
    setReportSections(null);
    setPdfUrl(null);
    setCurrentView(HomeViewStateType.DASHBOARD);
  };

  const handleFileSelect = async (file: File) => {
    if (!file) return;
    setIsLoading(true);
    setLoadingMessage(`Processing "${file.name}"...`);
    resetStateForNewFile(); 
    setUploadedFile(file);

    try {
      const parsed = await parseSpreadsheet(file);
      setParsedSpreadsheetData(parsed);
      if (parsed.allRows.length === 0 || (parsed.allRows.length === 1 && parsed.allRows[0].every(cell => cell === null || String(cell).trim() === ""))) {
        addAlert('Spreadsheet is empty or contains only headers.', AlertType.INFO);
        setCurrentView(HomeViewStateType.DASHBOARD); 
      } else {
        addAlert(`"${file.name}" uploaded successfully. Ready for analysis.`, AlertType.SUCCESS);
        setCurrentView(HomeViewStateType.DASHBOARD); 
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      addAlert(`Error processing file: ${msg}`, AlertType.ERROR);
      setUploadedFile(null); 
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleAnalyzeData = async () => {
    if (!parsedSpreadsheetData) {
      addAlert('Please upload a spreadsheet first.', AlertType.INFO);
      return;
    }
    setIsLoading(true);
    setLoadingMessage(`Analyzing "${parsedSpreadsheetData.fileName}"...`);
    setReportSections(null); 
    setPdfUrl(null);

    try {
      const sections = await analyzeSpreadsheetData(parsedSpreadsheetData);
      setReportSections(sections);
      addAlert('Analysis complete!', AlertType.SUCCESS);
      setCurrentView(HomeViewStateType.REPORT_DISPLAY);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      addAlert(`Analysis failed: ${msg}`, AlertType.ERROR);
      setReportSections([{ title: "Analysis Error", content: [{ type: 'paragraph', text: `Failed to analyze data: ${msg}` }] }]);
      setCurrentView(HomeViewStateType.REPORT_DISPLAY); 
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleGeneratePdf = async () => {
    if (!reportSections) {
      addAlert('Please analyze data first to generate a PDF report.', AlertType.INFO);
      return;
    }
    setIsLoading(true);
    setLoadingMessage('Generating PDF report...');
    setCurrentView(HomeViewStateType.PDF_PREVIEW); 

    try {
      const url = await generatePdfReport(reportSections, uploadedFile?.name || 'report.pdf');
      setPdfUrl(url);
      addAlert('PDF generated successfully! Opening in new tab.', AlertType.SUCCESS);
      window.open(url, '_blank'); 
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      addAlert(`PDF generation failed: ${msg}`, AlertType.ERROR);
      setPdfUrl(null); 
      setCurrentView(HomeViewStateType.REPORT_DISPLAY); 
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handlePolishParagraph = async (
    sectionIndex: number,
    contentItemIndex: number,
    insightIndex: number | null,
    originalText: string
  ) => {
    if (!reportSections || !parsedSpreadsheetData) {
      addAlert('Cannot polish text: report data or spreadsheet data is missing.', AlertType.ERROR);
      return;
    }

    const sectionTitle = reportSections[sectionIndex].title;
    const { fileName, sheetName, sampleForAnalysis } = parsedSpreadsheetData;
    
    const dataSamplePreview = sampleForAnalysis.slice(0, 5); 
    const dataSamplePreviewString = JSON.stringify(dataSamplePreview.map(row => row.map(cell => {
        const cellStr = String(cell === null || cell === undefined ? "" : cell);
        return cellStr.length > 30 ? cellStr.substring(0, 27) + "..." : cellStr;
    })));

    setIsLoading(true);
    setLoadingMessage(`Polishing text in "${sectionTitle}"...`);

    try {
      const polishedText = await polishTextWithGemini(originalText, sectionTitle, fileName, sheetName, dataSamplePreviewString);
      
      const updatedSections = reportSections.map((section, sIdx) => {
        if (sIdx === sectionIndex) {
          const updatedContent = section.content.map((item, cIdx) => {
            if (cIdx === contentItemIndex) {
              if (insightIndex === null && item.type === 'paragraph') {
                return { ...item, text: polishedText };
              } else if (insightIndex !== null && item.type === 'table' && item.insights && item.insights[insightIndex]?.type === 'paragraph') {
                const updatedInsights = item.insights.map((insightItem, iIdx) => {
                  if (iIdx === insightIndex) {
                    return { ...insightItem, text: polishedText };
                  }
                  return insightItem;
                });
                return { ...item, insights: updatedInsights };
              }
            }
            return item;
          });
          return { ...section, content: updatedContent };
        }
        return section;
      });

      setReportSections(updatedSections);
      addAlert('Text polished successfully!', AlertType.SUCCESS);

    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      addAlert(`Failed to polish text: ${msg}`, AlertType.ERROR);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };


  const handleSetView = (view: HomeViewStateType) => {
    if (view === HomeViewStateType.MODERN_CHAT && !uploadedFile) {
        addAlert("Opening general AI chat. Upload a file to chat about its contents.", AlertType.INFO, 4000);
    }
    setCurrentView(view);
  };
  
  const handleExitModernChat = () => {
    setCurrentView(HomeViewStateType.DASHBOARD);
  };

  useEffect(() => {
    const originalBodyBgColor = document.body.style.backgroundColor;
    const originalRootPt = document.getElementById('root')?.style.paddingTop || '';

    if (currentView === HomeViewStateType.MODERN_CHAT) {
      document.body.style.backgroundColor = 'rgb(var(--color-chat-input-bg))';
      if(document.getElementById('root')) {
          (document.getElementById('root') as HTMLElement).style.paddingTop = '0';
      }
    } else {
      document.body.style.backgroundColor = 'rgb(var(--color-dj-background))';
      if(document.getElementById('root')) {
        (document.getElementById('root') as HTMLElement).style.paddingTop = originalRootPt; 
      }
    }
    return () => { 
        document.body.style.backgroundColor = originalBodyBgColor;
        if(document.getElementById('root')) {
          (document.getElementById('root') as HTMLElement).style.paddingTop = originalRootPt;
        }
    }
  }, [currentView]);


  const renderCurrentView = () => {
    switch (currentView) {
      case HomeViewStateType.REPORT_DISPLAY:
        return reportSections ? <ReportDisplay reportSections={reportSections} onPolishParagraph={handlePolishParagraph} /> : <DashboardWelcome />;
      case HomeViewStateType.PDF_PREVIEW:
        return (
          <div className="p-6 text-center">
            <h2 className="text-xl font-semibold mb-4 text-dj-text-primary">PDF Generation</h2>
            {isLoading && <Spinner />}
            {pdfUrl && <p className="text-dj-text-secondary">PDF has been generated and opened in a new tab. <a href={pdfUrl} target="_blank" rel="noopener noreferrer" className="text-dj-blue hover:underline">Open again</a>.</p>}
            {!pdfUrl && !isLoading && <p className="text-dj-text-secondary">Generate a PDF to view it.</p>}
            {reportSections && <p className="mt-4 text-xs text-dj-text-secondary">You can continue viewing the report below while PDF is handled.</p>}
            {reportSections && <ReportDisplay reportSections={reportSections} onPolishParagraph={handlePolishParagraph} />}
          </div>
        );
      case HomeViewStateType.MODERN_CHAT:
        return (
          <ModernChatScreenView 
            initialSystemInstruction={INITIAL_SYSTEM_INSTRUCTION_GENERAL_CHAT}
            spreadsheetContext={parsedSpreadsheetData ? { data: parsedSpreadsheetData.sampleForAnalysis, fileName: parsedSpreadsheetData.fileName} : undefined}
            onExit={handleExitModernChat}
          />
        );
      case HomeViewStateType.DASHBOARD:
      default:
        return <DashboardWelcome uploadedFileName={uploadedFile?.name} isAnalyzed={isAnalyzed} />;
    }
  };
  
  const DashboardWelcome: React.FC<{uploadedFileName?: string, isAnalyzed?: boolean}> = ({uploadedFileName, isAnalyzed: analyzed}) => (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-dj-white rounded-lg shadow">
        <span className="material-symbols-outlined text-6xl text-dj-blue mb-4">insights</span>
        <h1 className="text-2xl font-bold text-dj-text-primary mb-2">Welcome to Excelerate Insights</h1>
        {!uploadedFileName && <p className="text-dj-text-secondary mb-6">Upload a spreadsheet using the sidebar to begin analysis and chat.</p>}
        {uploadedFileName && !analyzed && <p className="text-dj-text-secondary mb-6">File "{uploadedFileName}" is uploaded. Click "Analyze Data" in the sidebar.</p>}
        {uploadedFileName && analyzed && <p className="text-dj-text-secondary mb-6">"{uploadedFileName}" has been analyzed. View the report or chat with the AI.</p>}
        <p className="text-xs text-dj-text-secondary/80">You can also start a general chat with the AI at any time using the "Chat with AI" button.</p>
    </div>
  );

  return (
    <div className={`flex h-full ${currentView === HomeViewStateType.MODERN_CHAT ? '' : 'overflow-hidden'}`}>
      {currentView !== HomeViewStateType.MODERN_CHAT && (
        <Sidebar
          onFileSelect={handleFileSelect}
          onAnalyze={handleAnalyzeData}
          onGeneratePdf={handleGeneratePdf}
          isFileUploaded={!!uploadedFile}
          isAnalyzed={isAnalyzed}
          isLoading={isLoading}
          currentView={currentView}
          onSetView={handleSetView}
        />
      )}
      <div className={`flex-grow ${currentView === HomeViewStateType.MODERN_CHAT ? 'h-full' : 'overflow-y-auto p-0'}`}>
        {isLoading && loadingMessage && currentView !== HomeViewStateType.MODERN_CHAT && (
            <div className="flex items-center justify-center p-4 text-sm text-dj-text-secondary bg-dj-background sticky top-0 z-10">
                <Spinner size="sm" color="text-dj-blue" />
                <span className="ml-2">{loadingMessage}</span>
            </div>
        )}
        {renderCurrentView()}
      </div>
    </div>
  );
};