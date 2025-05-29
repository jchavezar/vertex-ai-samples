

export type SpreadsheetDataArray = (string | number | boolean | null)[][]; // Date objects are converted to strings

export interface ParsedSpreadsheetData {
  fileName: string;
  sheetName: string;
  allRows: SpreadsheetDataArray; 
  detectedHeaders: string[]; 
  headerRowIndex: number; 
  sampleForAnalysis: SpreadsheetDataArray;
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[]; 
  borderColor?: string | string[];   
  borderWidth?: number;
  fill?: boolean; 
  // Fix: Add tension property for line charts
  tension?: number; 
  // Add other Chart.js dataset properties as needed
}

export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'doughnut'; 
  title?: string; 
  labels: string[];
  datasets: ChartDataset[];
  options?: any; 
}

export interface ReportContentItem {
  type: 'paragraph' | 'list' | 'table' | 'chart'; 
  text?: string;
  items?: string[];
  headers?: string[];
  rows?: (string | number)[][];
  insights?: ReportContentItem[]; 
  chartData?: ChartData; 
}

export interface ReportSection {
  title: string;
  content: ReportContentItem[];
}

export enum AlertType {
  SUCCESS = 'success',
  ERROR = 'error',
  INFO = 'info'
}

export type MessageAuthor = 'user' | 'ai' | 'system';

export interface GroundingChunk {
  web?: {
    uri?: string;
    title?: string;
  };
}

export interface GroundingMetadata {
  groundingChunks?: GroundingChunk[];
}

export interface ChatMessage {
  id: string;
  text: string;
  author: MessageAuthor;
  timestamp: Date;
  groundingMetadata?: GroundingMetadata | null; 
}

export enum HomeViewStateType {
  DASHBOARD = 'dashboard', // Initial view, or after clearing a file
  REPORT_DISPLAY = 'report_display', // View for showing AI-generated analysis report
  PDF_PREVIEW = 'pdf_preview', // View for showing the generated PDF (though actual preview is in new tab)
  MODERN_CHAT = 'modern_chat', // New view for the advanced, Gemini-like chat interface
}