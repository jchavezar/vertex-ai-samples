
import OriginalJsPDFConstructor from 'jspdf'; 
import autoTable from 'jspdf-autotable';
import { ReportSection, ReportContentItem, ChartData } from '../types'; 

interface Font {
  fontName: string;
  fontStyle: string;
}

// This interface defines the methods from jsPDF that are used in this module.
// It's typed to ensure compatibility with the jsPDF library instance.
// Overloads for color methods (setTextColor, setFillColor, setDrawColor) are
// defined to match the actual jsPDF library signatures to ensure type safety
// during the assertion `new OriginalJsPDFConstructor(...) as jsPDFWithAutoTable`.
interface LocalJsPDFMasterInterface {
  setFontSize(size: number): this;
  setFont(fontName: string, fontStyle?: string, fontWeight?: string | number): this;
  
  // Updated setTextColor to match jsPDF overloads
  setTextColor(colorName: string): this;
  setTextColor(ch1: number): this; // For grayscale
  setTextColor(ch1: number, ch2: number, ch3: number): this; // For RGB

  splitTextToSize(text: string | string[], maxWidth: number, options?: any): string[];
  text(text: string | string[], x: number, y: number, options?: any, transform?: any, angle?: number): this;
  getFontSize(): number;
  getFont(): Font; 
  internal: {
    pageSize: {
      height: number; 
      width: number;  
    };
    // Fix: Removed getNumberOfPages from internal as it's a top-level method on jsPDF instance
    // getNumberOfPages(): number; 
  };
  addPage(format?: string, orientation?: string): this;
  getTextWidth(text: string | string[]): number;

  // Updated setFillColor to match jsPDF overloads
  setFillColor(colorName: string): this;
  setFillColor(ch1: number): this; // For grayscale
  setFillColor(ch1: number, ch2: number, ch3: number, ch4?: number): this; // General numeric (RGB, RGBA, CMYK)

  // Updated setDrawColor to match jsPDF overloads
  setDrawColor(colorName: string): this;
  setDrawColor(ch1: number): this; // For grayscale
  setDrawColor(ch1: number, ch2: number, ch3: number, ch4?: number): this; // General numeric (RGB, RGBA, CMYK)

  roundedRect(x: number, y: number, w: number, h: number, rx: number, ry: number, style: string): this;
  setPage(pageNumber: number): this;
  output(type: 'blob', options?: any): Blob;
  getNumberOfPages(): number; // This is the correct top-level method
  rect(x: number, y: number, w: number, h: number, style?: string): this; // Added for drawing lines
  line(x1: number, y1: number, x2: number, y2: number): this; // Added for drawing lines
}

interface jsPDFWithAutoTable extends LocalJsPDFMasterInterface {
  lastAutoTable?: { 
    finalY?: number; 
  };
}

// Titles that indicate the section is primarily AI commentary and should get special styling
const AI_COMMENTARY_SECTION_TITLES_PDF = [
  "Key AI-Generated Insights",
  "Data Structure Interpretation",
  "Overall Performance Trends", 
  "Location Performance Overview",
  "Add On Contribution Analysis",
  "Further Considerations & Questions"
];

const isSectionAiCommentaryForPdf = (title: string): boolean => {
  return AI_COMMENTARY_SECTION_TITLES_PDF.some(aiTitle => 
      title.includes(aiTitle) || 
      (aiTitle === "Overall Performance Trends" && title.includes("Performance Trends"))
  );
};

const sanitizeAiTextForPdf = (text?: string): string => {
  if (!text) return '';
  return text.replace(/\*\*(.*?)\*\*/g, '$1');
};

const purpleRGB = { r: 107, g: 70, b: 193 }; // Adjusted for a slightly richer purple text: text-purple-700
const lightPurpleBgRGB = { r: 243, g: 232, b: 255 }; // Corresponds to bg-purple-50 or bg-fuchsia-50
const purpleBorderRGB = { r: 196, g: 181, b: 253 }; // Corresponds to border-purple-300

const blackRGB = { r: 20, g: 20, b: 20 }; // dj-text-primary
const whiteRGB = { r: 255, g: 255, b: 255 };
const djBlueRGB = { r: 0, g: 93, b: 234 };
const djBackgroundRGB = { r: 248, g: 247, b: 243 }; // Creamy off-white
const grayRGB = { r: 80, g: 80, b: 80 }; // dj-text-secondary
const lightGrayBorderRGB = { r: 224, g: 224, b: 224 }; // dj-light-gray

const renderChartDataAsTable = (doc: jsPDFWithAutoTable, chartData: ChartData, startY: number, margin: number, pageWidth: number): number => {
  let y = startY;
  const chartTitle = sanitizeAiTextForPdf(chartData.title) || `Data Visualization (${chartData.type} chart)`;
  doc.setFontSize(11);
  doc.setFont(doc.getFont().fontName, 'bold');
  doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b);
  const titleLines = doc.splitTextToSize(chartTitle, pageWidth - 2 * margin);
  doc.text(titleLines, margin, y);
  y += titleLines.length * (doc.getFontSize() * 1.2) + 5;

  doc.setFontSize(9);
  doc.setFont(doc.getFont().fontName, 'normal');

  const headers = [sanitizeAiTextForPdf("Label")];
  chartData.datasets.forEach(ds => headers.push(sanitizeAiTextForPdf(ds.label) || "Dataset"));

  const body = chartData.labels.map((label, labelIndex) => {
    const row = [sanitizeAiTextForPdf(String(label))];
    chartData.datasets.forEach(ds => {
      row.push(sanitizeAiTextForPdf(String(ds.data[labelIndex] !== undefined ? ds.data[labelIndex] : 'N/A')));
    });
    return row;
  });

  autoTable(doc, {
    head: [headers],
    body: body,
    startY: y,
    margin: { left: margin, right: margin },
    theme: 'grid',
    headStyles: { fillColor: [djBlueRGB.r, djBlueRGB.g, djBlueRGB.b], textColor: whiteRGB.r, fontStyle: 'bold', fontSize: 9 },
    styles: { fontSize: 8, cellPadding: 3, lineColor: [lightGrayBorderRGB.r, lightGrayBorderRGB.g, lightGrayBorderRGB.b] },
    alternateRowStyles: { fillColor: [djBackgroundRGB.r, djBackgroundRGB.g, djBackgroundRGB.b] },
  });
  
  const finalY = doc.lastAutoTable?.finalY;
  return typeof finalY === 'number' ? finalY + 15 : y + 30; 
};

export const generatePdfReport = async (
  reportSectionsInput: ReportSection[],
  fileName: string = 'spreadsheet_analysis_report.pdf'
): Promise<string> => {
  const doc = new OriginalJsPDFConstructor({
    orientation: 'p',
    unit: 'pt',
    format: 'a4'
// Fix: Correct type assertion for jsPDF instance to jsPDFWithAutoTable by using 'as unknown'
  }) as unknown as jsPDFWithAutoTable;
  
  const pageHeight = doc.internal.pageSize.height;
  const pageWidth = doc.internal.pageSize.width;
  const margin = 40;
  let yPos = margin;
  const lineSpacing = 1.2;
  const bulletIndent = 15;
  const tableInsightIndent = margin + 10;
  const tableInsightLineX = margin + 3;

  const checkAndAddPage = (neededHeight: number) => {
    if (yPos + neededHeight > pageHeight - margin) {
      doc.addPage();
      yPos = margin;
    }
  };

  doc.setFontSize(22);
  doc.setFont(doc.getFont().fontName, 'bold');
  doc.setTextColor(djBlueRGB.r, djBlueRGB.g, djBlueRGB.b);
  const reportTitle = sanitizeAiTextForPdf("Spreadsheet Analysis Report");
  const titleWidth = doc.getTextWidth(reportTitle);
  doc.text(reportTitle, (pageWidth - titleWidth) / 2, yPos);
  yPos += 30;
  doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b);

  const orderedSections = [...reportSectionsInput]; 

  const renderContentItem = (item: ReportContentItem, currentY: number, isParentSectionAi: boolean, isTableInsight: boolean) => {
    let itemY = currentY;
    const itemContentWidth = pageWidth - (isTableInsight ? tableInsightIndent + margin : (margin * 2) + (isParentSectionAi ? 6 : 0) );
    
    doc.setFontSize(isTableInsight ? 10 : 10); // Table insights are now size 10
    doc.setFont(doc.getFont().fontName, 'normal'); // Table insights are now normal font weight
    doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b); // Table insights use primary text color
    
    const textToRender = sanitizeAiTextForPdf(item.text);
    const listItemsToRender = item.items?.map(sanitizeAiTextForPdf);

    switch (item.type) {
        case 'paragraph':
            if (textToRender) {
                const splitText = doc.splitTextToSize(textToRender, itemContentWidth);
                const textHeight = splitText.length * (doc.getFontSize() * lineSpacing);
                checkAndAddPage(textHeight + (isParentSectionAi && !isTableInsight ? 10 : 5));
                
                const startRectY = itemY - 2;
                if (isParentSectionAi && !isTableInsight) {
                    doc.setFillColor(lightPurpleBgRGB.r, lightPurpleBgRGB.g, lightPurpleBgRGB.b);
                    doc.setDrawColor(purpleBorderRGB.r, purpleBorderRGB.g, purpleBorderRGB.b);
                    doc.roundedRect(margin, startRectY, pageWidth - 2 * margin, textHeight + 4, 3, 3, 'FD');
                    doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b); 
                }
                doc.text(splitText, (isTableInsight ? tableInsightIndent : margin + (isParentSectionAi && !isTableInsight ? 3 : 0)), itemY + (isParentSectionAi && !isTableInsight ? doc.getFontSize() * 0.8 : 0) );
                itemY += textHeight + (isParentSectionAi && !isTableInsight ? 10 : (isTableInsight ? 5 : 10));
            }
            break;
        case 'list':
            if (listItemsToRender) {
                let listBlockHeight = 0;
                listItemsToRender.forEach(listItem => {
                    const text = `• ${listItem}`;
                    const splitText = doc.splitTextToSize(text, itemContentWidth - bulletIndent); 
                    listBlockHeight += splitText.length * (doc.getFontSize() * lineSpacing) + (isTableInsight ? 2 : 5);
                });
                listBlockHeight += (isTableInsight ? 3 : 5) + (isParentSectionAi && !isTableInsight ? 4 : 0);

                checkAndAddPage(listBlockHeight + (isParentSectionAi && !isTableInsight ? 10 : 0));
                const listStartY = itemY;
                const startRectY = itemY - 2;

                if (isParentSectionAi && !isTableInsight) {
                    doc.setFillColor(lightPurpleBgRGB.r, lightPurpleBgRGB.g, lightPurpleBgRGB.b);
                    doc.setDrawColor(purpleBorderRGB.r, purpleBorderRGB.g, purpleBorderRGB.b);
                    doc.roundedRect(margin, startRectY, pageWidth - 2 * margin, listBlockHeight + 4, 3, 3, 'FD');
                    doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b); 
                }
                
                let currentListY = itemY + (isParentSectionAi && !isTableInsight ? (doc.getFontSize() * 0.8) + 2 : 0);

                for (const listItem of listItemsToRender) {
                    const text = `• ${listItem}`;
                    const splitText = doc.splitTextToSize(text, itemContentWidth - bulletIndent);
                    doc.text(splitText, (isTableInsight ? tableInsightIndent : margin + (isParentSectionAi && !isTableInsight ? 7 : 5)), currentListY);
                    currentListY += splitText.length * (doc.getFontSize() * lineSpacing) + (isTableInsight ? 2 : 5);
                }
                itemY = listStartY + listBlockHeight + (isParentSectionAi && !isTableInsight ? 6 : 0);
            }
            break;
    }
    return itemY;
  };

  for (const section of orderedSections) {
    const isAiSection = isSectionAiCommentaryForPdf(section.title);
    const sanitizedSectionTitle = sanitizeAiTextForPdf(section.title);
    
    checkAndAddPage(40); 
    doc.setFontSize(16);
    doc.setFont(doc.getFont().fontName, 'bold');

    if (isAiSection) {
      doc.setTextColor(purpleRGB.r, purpleRGB.g, purpleRGB.b);
      doc.text(sanitizedSectionTitle, margin, yPos);
      yPos += 18; 
      doc.setFontSize(8);
      doc.setFont(doc.getFont().fontName, 'italic');
      doc.setTextColor(purpleRGB.r, purpleRGB.g, purpleRGB.b);
      doc.text("AI Generated Commentary & Analysis", margin, yPos);
      yPos += 12; 
    } else {
      doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b);
      doc.text(sanitizedSectionTitle, margin, yPos);
      yPos += 20;
    }
    doc.setFont(doc.getFont().fontName, 'normal');
    doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b);

    for (const item of section.content) {
      doc.setFontSize(10); 

      switch (item.type) {
        case 'paragraph':
        case 'list':
            yPos = renderContentItem(item, yPos, isAiSection, false); 
            break;
        case 'table':
          if (item.headers && item.rows) {
            checkAndAddPage(50); 
            const tableHeaders = item.headers.map(sanitizeAiTextForPdf);
            const tableRows = item.rows.map(row => row.map(cell => typeof cell === 'number' ? cell : sanitizeAiTextForPdf(String(cell))));

            const tableOptions: any = { 
              startY: yPos,
              head: [tableHeaders],
              body: tableRows,
              margin: { left: margin, right: margin },
              tableWidth: 'auto',
              styles: { fontSize: 8, cellPadding: 3, lineColor: [lightGrayBorderRGB.r,lightGrayBorderRGB.g,lightGrayBorderRGB.b], lineWidth: 0.5, textColor: [blackRGB.r, blackRGB.g, blackRGB.b] },
              headStyles: { fillColor: [djBlueRGB.r, djBlueRGB.g, djBlueRGB.b], textColor: [whiteRGB.r, whiteRGB.g, whiteRGB.b], fontStyle: 'bold', fontSize: 9, cellPadding: 4 },
              alternateRowStyles: { fillColor: [djBackgroundRGB.r, djBackgroundRGB.g, djBackgroundRGB.b] },
            };
            
            autoTable(doc, tableOptions);
            const currentFinalY = doc.lastAutoTable?.finalY;
            yPos = typeof currentFinalY === 'number' ? currentFinalY + 10 : yPos + 30; // Reduced spacing after table

            if (item.insights && item.insights.length > 0) {
                checkAndAddPage(20); 
                const insightStartY = yPos;
                let insightBlockHeight = 0;

                // Calculate height of insights block first
                let tempYPosForCalc = yPos;
                for (const insight of item.insights) {
                  const originalY = tempYPosForCalc;
                  tempYPosForCalc = renderContentItem(insight, tempYPosForCalc, false, true);
                  insightBlockHeight += (tempYPosForCalc - originalY);
                }
                insightBlockHeight = Math.max(insightBlockHeight, 10); // Minimum height for the line

                // Draw blue line
                doc.setDrawColor(djBlueRGB.r, djBlueRGB.g, djBlueRGB.b);
                doc.line(tableInsightLineX, insightStartY - 2, tableInsightLineX, insightStartY + insightBlockHeight - 5); // Adjust line height

                // Render insights with indent
                for (const insight of item.insights) {
                    yPos = renderContentItem(insight, yPos, false, true);
                }
                yPos += 5; 
            }
          }
          break;
        case 'chart':
            if (item.chartData) {
                checkAndAddPage(80); 
                yPos = renderChartDataAsTable(doc, item.chartData, yPos, margin, pageWidth);
                yPos += 10;
            }
            break;
      }
      if (yPos > pageHeight - (margin + 10) ) {
          doc.addPage();
          yPos = margin;
      }
    }
    yPos += 10; 
    doc.setTextColor(blackRGB.r, blackRGB.g, blackRGB.b); 
  }
  
  const pageCount = doc.getNumberOfPages(); 
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100); 
    const pageNumText = `Page ${i} of ${pageCount}`;
    doc.text(pageNumText, pageWidth - margin - doc.getTextWidth(pageNumText), pageHeight - margin / 2);
  }

  const blob = doc.output('blob');
  const blobUrl = URL.createObjectURL(blob);
  
  return Promise.resolve(blobUrl);
};
