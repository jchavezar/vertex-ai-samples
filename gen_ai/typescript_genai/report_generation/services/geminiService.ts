
import { GoogleGenAI, Chat, GenerateContentResponse } from "@google/genai";
import { ParsedSpreadsheetData, SpreadsheetDataArray, ReportSection, ReportContentItem, ChartData } from '../types'; 

const apiKey = process.env.API_KEY;
if (!apiKey) {
  console.error("API_KEY for Gemini is not set in environment variables.");
}
const ai = new GoogleGenAI({ apiKey: apiKey || "MISSING_API_KEY" }); 
const TEXT_MODEL_NAME = 'gemini-2.5-flash-preview-04-17';

const MAX_ROWS_IN_CHAT_SYSTEM_PROMPT_PREVIEW = 10;
const MAX_CELL_LENGTH_IN_CHAT_SYSTEM_PROMPT_PREVIEW = 50;
const MAX_ROWS_FOR_ANALYSIS_PROMPT = 75; // Consistent with spreadsheetParser

const formatDataForPrompt = (data: SpreadsheetDataArray): string => {
  return JSON.stringify(data.map(row => row.map(cell => {
    if (typeof cell === 'string' && cell.length > 100) { // Truncate long strings for the prompt
      return cell.substring(0, 97) + "...";
    }
    return cell;
  })));
};

export const analyzeSpreadsheetData = async (
  parsedData: ParsedSpreadsheetData
): Promise<ReportSection[]> => {
  const { fileName, sheetName, sampleForAnalysis, detectedHeaders } = parsedData;

  if (!sampleForAnalysis || sampleForAnalysis.length === 0) {
    return [{ title: "No Data", content: [{ type: 'paragraph', text: "The spreadsheet appears to be empty or no data was suitable for analysis."}] }];
  }
  
  const sampleDataString = formatDataForPrompt(sampleForAnalysis);
  const headersString = detectedHeaders.join(', ');

  const prompt = `
    You are a highly creative and insightful data analysis expert, acting as an expert financial AI assistant. Your goal is to provide a comprehensive and actionable report based on the following spreadsheet data from a file named "${fileName}", sheet "${sheetName}".
    The detected headers are: [${headersString || 'No headers detected, first row likely data'}].
    The data sample (up to ${MAX_ROWS_FOR_ANALYSIS_PROMPT} rows) is provided as a JSON 2D array:
    ${sampleDataString}

    Your response MUST be a JSON object containing an array called "reportSections".
    Each object in "reportSections" must have a "title" (string) and a "content" (array of ReportContentItem objects).
    A ReportContentItem object must have a "type" (string: "paragraph", "list", "table", "chart") and corresponding data:
    - For "paragraph": "text" (string).
    - For "list": "items" (array of strings).
    - For "table": "headers" (array of strings) and "rows" (array of arrays of strings/numbers). You MUST include "insights" (array of paragraph/list ReportContentItem objects) directly related to THIS TABLE. These insights should be your expert financial AI commentary, interpreting the table's data, highlighting key points, their significance, and providing actionable advice or further questions based SOLELY on this table's data. Phrase this commentary naturally, as if you are explaining the table. Do NOT use lead-ins like "The AI highlights..." or "This table shows...".
    - For "chart": "chartData" (object with "type" ['bar', 'line', 'pie', 'doughnut'], "title" [string, optional], "labels" [array of strings], and "datasets" [array of objects with "label" (string) and "data" (array of numbers)]). Keep charts simple and directly derivable from the provided data.

    CRITICAL INSTRUCTIONS:
    1.  AVOID using double asterisks (**) for bolding text in your textual content (paragraphs, list items). The UI will handle styling. Use standard paragraphs and markdown-style lists (e.g., "- item").
    2.  For EACH analytical section you generate (listed below), you MUST include rich AI commentary, detailed insights, and actionable recommendations. Do not just present data; interpret it thoroughly as an expert financial AI assistant.

    Structure your report with the following sections, ensuring exact titles as specified for AI commentary sections:
    -   "Key AI-Generated Insights": This is the MOST IMPORTANT section.
        -   Provide a high-level summary of the most significant findings, patterns, and anomalies.
        -   Offer actionable recommendations and strategic advice based on these insights. Be creative.
        -   Highlight any surprising or noteworthy observations.
    -   "Data Structure Interpretation":
        -   Briefly describe the structure of the data (e.g., time series, categorical), discuss data quality, and any assumptions made. Include your AI commentary.
    -   "Overall Performance Trends": (Include if relevant to the data)
        -   Analyze overall trends in key metrics (e.g., volume, revenue over time).
        -   Use tables and simple charts (bar, line) if appropriate.
        -   CRITICAL: Include detailed AI commentary explaining the trends, their implications, and any recommendations.
    -   "Location Performance Overview": (Include if location-specific data is present and relevant)
        -   Compare performance across different locations/segments.
        -   Use tables and charts if appropriate.
        -   CRITICAL: Include detailed AI commentary on location-specific findings, disparities, and strategic advice.
    -   "Add On Contribution Analysis": (Include if 'add-on' or similar distinct metrics are present and relevant)
        -   Analyze the contribution and performance of add-on products/services relative to core metrics.
        -   CRITICAL: Include detailed AI commentary on this aspect.
    -   "Further Considerations & Questions":
        -   Pose insightful questions that arise from the analysis or suggest areas for further investigation.
        -   Include AI commentary on potential next steps or data to gather.

    If a suggested section (like "Location Performance Overview", "Add On Contribution Analysis", or even "Overall Performance Trends") is not relevant to the provided data, omit that specific section.
    Ensure all generated textual content is your direct AI commentary.
    
    Example of a chartData object for a "chart" type ReportContentItem:
    {
      "type": "bar",
      "title": "Sales per Category",
      "labels": ["Electronics", "Books", "Clothing"],
      "datasets": [{ "label": "Total Sales", "data": [1500, 800, 1200] }]
    }
    
    Strict JSON Adherence: The entire output MUST be a single, valid JSON object. 
    - Ensure all strings are double-quoted and properly escaped (e.g., \\" for a quote within a string, \\\\ for a literal backslash). 
    - All numbers (e.g., in table cells, chart data) MUST be standard JSON numbers (e.g., 123.45, -78, 0, 500). They MUST NOT be strings.
    - CRITICAL FOR NUMBERS: Numeric values MUST NOT contain any formatting (like parentheses, currency symbols, commas for thousands separators) OR any mathematical expressions/calculations (e.g., do NOT output "value": (100/2) or "value": "50 (USD)"). The value must be a plain number like 50 or 123.45.
    - No Trailing Commas: Be extremely careful not to include trailing commas in JSON arrays or objects.
    - Verify Nested Structures: Double-check the syntax of all nested objects and arrays within 'reportSections' and 'content' items.
    
    Be insightful and provide practical value. Acknowledge limitations due to the sample size where appropriate.
    If the data quality is poor or insufficient for meaningful analysis, state this clearly in the "Key AI-Generated Insights" and "Data Structure Interpretation" sections.
    Ensure valid JSON output adhering to the specified structure.
  `;

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: TEXT_MODEL_NAME,
      contents: [{ role: "user", parts: [{text: prompt}] }],
      config: {
        responseMimeType: "application/json",
        // thinkingConfig: { thinkingBudget: 0 } // Removed for higher quality JSON generation
      }
    });

    let jsonStr = response.text.trim();
    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = jsonStr.match(fenceRegex);
    if (match && match[2]) {
      jsonStr = match[2].trim();
    }
    
    const result = JSON.parse(jsonStr);
    if (result && result.reportSections && Array.isArray(result.reportSections)) {
        return result.reportSections as ReportSection[];
    }
    throw new Error("Invalid response format from AI: 'reportSections' array not found or is not an array.");

  } catch (error) {
    console.error("Error analyzing spreadsheet data with Gemini:", error);
    const message = error instanceof Error ? error.message : String(error);
    // Check if the error is a JSON parsing error to provide a more specific message.
    if (error instanceof SyntaxError && message.toLowerCase().includes('json')) {
        return [{
           title: "Analysis Error",
           content: [{
               type: 'paragraph',
               text: `Failed to generate analysis. The AI's response was not valid JSON: ${message}. This can sometimes happen with complex data. Please try analyzing again. If the problem persists, the spreadsheet data might be too complex or unusual for the AI to process correctly into the required report format.`
           }]
        }];
    }
    return [{ 
      title: "Analysis Error", 
      content: [{ 
        type: 'paragraph', 
        text: `Failed to generate analysis. Gemini API returned an error or unexpected response: ${message}. This could be due to network issues, API key problems, or the AI model not understanding the request with the provided data. Please check your data or try again later.` 
      }] 
    }];
  }
};

export const polishTextWithGemini = async (
  originalText: string,
  sectionTitle: string,
  fileName: string,
  sheetName: string,
  dataSamplePreviewString: string
): Promise<string> => {
  const prompt = `
You are an expert editor and AI assistant specializing in financial analysis.
Your task is to refine the following text segment, or offer a different perspective if more valuable.
The text is part of a larger financial analysis report.
Context: File "${fileName}", Sheet "${sheetName}".
The text is from a report section titled: "${sectionTitle}".
The original data sample being analyzed (first few rows, truncated for brevity) is:
${dataSamplePreviewString}

Original text to refine:
"${originalText}"

Instructions:
1.  Provide a polished version of this text. Ensure it is clear, concise, insightful, and maintains a professional, analytical tone suitable for a financial report.
2.  Alternatively, if you believe a different perspective, a deeper question, or a more actionable insight would be more valuable for this specific piece of text, provide that.
3.  Your response MUST BE ONLY the revised text for the paragraph.
4.  Do NOT include any preamble like "Here's a polished version:", "An alternative perspective could be:", or any markdown formatting like headings or lists unless the original text was a list item formatted as a paragraph.
5.  AVOID using double asterisks (**) for bolding. The UI handles styling.
6.  The refined text should be a direct replacement for the original paragraph.
`;

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: TEXT_MODEL_NAME,
      contents: [{ role: "user", parts: [{text: prompt}] }],
      // No specific responseMimeType, expecting plain text.
      // Omitting thinkingConfig to potentially allow for higher quality refinement.
    });
    return response.text.trim();
  } catch (error) {
    console.error("Error polishing text with Gemini:", error);
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to polish text: ${message}`);
  }
};


export const getGeminiChatInstance = (
  baseSystemInstruction: string,
  spreadsheetContext?: { data: SpreadsheetDataArray, fileName: string }
): Chat => {
  let systemInstructionToUse = baseSystemInstruction;

  if (spreadsheetContext && spreadsheetContext.data && spreadsheetContext.data.length > 0) {
    const { data, fileName } = spreadsheetContext;
    
    const sampleForSystemPromptPreview = data.slice(0, MAX_ROWS_IN_CHAT_SYSTEM_PROMPT_PREVIEW).map(row =>
        row.map(cell => {
            const cellStr = String(cell === null || cell === undefined ? "" : cell);
            return cellStr.length > MAX_CELL_LENGTH_IN_CHAT_SYSTEM_PROMPT_PREVIEW
                ? cellStr.substring(0, MAX_CELL_LENGTH_IN_CHAT_SYSTEM_PROMPT_PREVIEW - 3) + "..."
                : cellStr;
        })
    );

    systemInstructionToUse = `You are an AI assistant. The user has uploaded a document titled "${fileName}".
You have been provided with the content of this document.
Your primary goal is to answer questions and perform tasks based on the information contained WITHIN THIS DOCUMENT.
Refer to the document's content when formulating your responses.
If the information is not in the document, state that clearly. Do not make up information.
Use markdown for clarity. AVOID using double asterisks (**) for bolding.

Here is a preview of the document's data (up to ${MAX_ROWS_IN_CHAT_SYSTEM_PROMPT_PREVIEW} rows, content truncated):
${JSON.stringify(sampleForSystemPromptPreview, null, 2)}
${data.length > MAX_ROWS_IN_CHAT_SYSTEM_PROMPT_PREVIEW ? `(...the full data provided to you contains ${data.length} rows)` : ''}

The full spreadsheet data (JSON 2D Array) for your context is:
${JSON.stringify(data)}
`;
  }

  try {
    const chat = ai.chats.create({
      model: TEXT_MODEL_NAME,
      config: {
        systemInstruction: systemInstructionToUse,
        thinkingConfig: { thinkingBudget: 0 } // Retained for chat as it's more interactive
      },
    });
    return chat;
  } catch (error) {
    console.error("Error creating Gemini Chat instance:", error);
    const message = error instanceof Error ? error.message : "Unknown error initializing chat.";
    throw new Error(`Failed to initialize AI chat: ${message}`);
  }
};
