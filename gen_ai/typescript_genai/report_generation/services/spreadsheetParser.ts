
import * as XLSX from 'xlsx';
import { ParsedSpreadsheetData, SpreadsheetDataArray } from '../types';

const MAX_HEADER_SCAN_ROWS = 15;
const MIN_STRING_CELL_PERCENT_FOR_HEADER = 0.6; // 60% of cells must be strings for a row to be header candidate
const MAX_ROWS_FOR_AI_SAMPLE = 75;

const isLikelyHeaderCell = (cell: any): boolean => {
  if (cell === null || cell === undefined || String(cell).trim() === '') return false;
  if (typeof cell === 'string') return true;
  return false; // numbers, booleans are less likely in headers
};

const detectHeaders = (data: SpreadsheetDataArray): { headers: string[], rowIndex: number } => {
  for (let i = 0; i < Math.min(data.length, MAX_HEADER_SCAN_ROWS); i++) {
    const row = data[i];
    if (!row || row.length === 0) continue;

    const stringCellCount = row.filter(isLikelyHeaderCell).length;
    if (stringCellCount / row.length >= MIN_STRING_CELL_PERCENT_FOR_HEADER) {
      // Qualifies as a potential header row
      return { headers: row.map(cell => String(cell)), rowIndex: i };
    }
  }
  return { headers: [], rowIndex: -1 }; // No clear header row found
};

export const parseSpreadsheet = async (file: File): Promise<ParsedSpreadsheetData> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const fileData = event.target?.result;
        if (!fileData) {
          throw new Error('File data is empty.');
        }
        const workbook = XLSX.read(fileData, { type: 'array', cellDates: true });
        const firstSheetName = workbook.SheetNames[0];
        if (!firstSheetName) {
          throw new Error('Spreadsheet contains no sheets.');
        }
        const worksheet = workbook.Sheets[firstSheetName];
        
        const jsonDataRaw = XLSX.utils.sheet_to_json<any[]>(worksheet, { header: 1, defval: null });

        const allRows: SpreadsheetDataArray = jsonDataRaw.map(row => 
          row.map(cell => {
            if (cell instanceof Date) {
              return cell.toISOString().split('T')[0]; // Format date as YYYY-MM-DD
            }
            if (typeof cell === 'number' && !isFinite(cell)) return null; // Handle Infinity, NaN
            return cell;
          })
        );

        if (allRows.length === 0) {
          resolve({ 
            fileName: file.name,
            sheetName: firstSheetName,
            allRows: [], 
            detectedHeaders: [], 
            headerRowIndex: -1, 
            sampleForAnalysis: [] 
          });
          return;
        }
        
        const { headers: detectedHeaders, rowIndex: headerRowIndex } = detectHeaders(allRows);
        
        // Provide a raw sample of the data (e.g., first N rows) for AI analysis
        // The AI will be instructed to interpret this raw 2D array.
        const sampleForAnalysis = allRows.slice(0, MAX_ROWS_FOR_AI_SAMPLE);

        resolve({ 
            fileName: file.name,
            sheetName: firstSheetName,
            allRows, 
            detectedHeaders, 
            headerRowIndex, 
            sampleForAnalysis 
        });

      } catch (error) {
        console.error('Error parsing spreadsheet:', error);
        const message = error instanceof Error ? error.message : String(error);
        reject(`Failed to parse spreadsheet: ${message}. Please ensure it's a valid CSV or Excel file.`);
      }
    };
    reader.onerror = (error) => {
      console.error('Error reading file:', error);
      reject('Error reading file. Please try again.');
    };
    reader.readAsArrayBuffer(file);
  });
};