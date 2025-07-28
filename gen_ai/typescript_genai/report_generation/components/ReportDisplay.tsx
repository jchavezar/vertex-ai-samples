
import React from 'react';
import { ReportSection, ReportContentItem, ChartData } from '../types'; 
import { ChartRenderer } from './ChartRenderer'; 

const AI_COMMENTARY_SECTION_TITLES = [
  "Key AI-Generated Insights",
  "Data Structure Interpretation",
  "Overall Performance Trends", 
  "Location Performance Overview",
  "Add On Contribution Analysis",
  "Further Considerations & Questions"
];

const sanitizeAiText = (text?: string): string => {
  if (!text) return '';
  return text.replace(/\*\*(.*?)\*\*/g, '$1');
};

const renderIndividualContentItem = (
  item: ReportContentItem, 
  sectionIndex: number,
  itemIndexInItsArray: number, // Index of this item within its direct parent's content/insights array
  isParentSectionAiCommentary: boolean, 
  isTableSpecificInsight: boolean,
  onPolishParagraph?: (sectionIdx: number, contentItemIdx: number, insightIdx: number | null, originalText: string) => Promise<void>,
  parentContentItemIndexForInsight?: number // Index of the parent 'table' item if this is an insight
): React.ReactNode => {
  let baseClasses = `text-sm ${isTableSpecificInsight ? 'text-dj-text-primary' : 'text-dj-text-primary'}`;
  let listStyle = 'list-disc list-inside';
  let listItemStyle = 'mb-1';

  if (isParentSectionAiCommentary && !isTableSpecificInsight) {
    baseClasses = 'text-sm text-gray-700'; 
    listStyle = 'list-disc list-inside'; 
    listItemStyle = 'mb-1'; 
  }
  if (isTableSpecificInsight) {
    baseClasses = 'text-sm text-dj-text-primary'; 
    listItemStyle = 'mb-1';
  }

  const sanitizedText = sanitizeAiText(item.text);
  const sanitizedListItems = item.items?.map(sanitizeAiText);

  switch (item.type) {
    case 'paragraph':
      const showPolishButton = onPolishParagraph && item.text && item.text.trim() !== '' && (isParentSectionAiCommentary || isTableSpecificInsight);
      return (
        <div key={`p-${sectionIndex}-${itemIndexInItsArray}-${parentContentItemIndexForInsight || 'top'}`} className={`my-1.5 ${showPolishButton ? 'flex items-start justify-between group' : ''}`}>
          <p className={`${baseClasses} leading-relaxed ${showPolishButton ? 'flex-grow mr-1' : ''}`}>{sanitizedText}</p>
          {showPolishButton && (
            <button
              onClick={async () => {
                if (isTableSpecificInsight && typeof parentContentItemIndexForInsight === 'number') {
                  await onPolishParagraph(sectionIndex, parentContentItemIndexForInsight, itemIndexInItsArray, item.text!);
                } else {
                  await onPolishParagraph(sectionIndex, itemIndexInItsArray, null, item.text!);
                }
              }}
              className="ml-2 mt-0.5 p-1 rounded-full text-purple-500 hover:bg-purple-100 hover:text-purple-700 focus:bg-purple-100 focus:text-purple-700 transition-all duration-150 opacity-0 group-hover:opacity-100 focus:opacity-100 flex-shrink-0"
              title="Refine this text with AI"
              aria-label="Refine this text with AI"
            >
              <span className="material-symbols-outlined text-base leading-none" style={{ fontSize: '18px' }}>auto_fix_high</span>
            </button>
          )}
        </div>
      );
    case 'list':
      return (
        <ul key={`ul-${sectionIndex}-${itemIndexInItsArray}`} className={`${baseClasses} ${listStyle} my-2 space-y-1`}>
          {sanitizedListItems?.map((li, liIndex) => (
            <li key={`li-${sectionIndex}-${itemIndexInItsArray}-${liIndex}`} className={listItemStyle}>{li}</li>
          ))}
        </ul>
      );
    case 'table':
      if (!item.headers || !item.rows) return null;
      return (
        <div key={`table-container-${sectionIndex}-${itemIndexInItsArray}`} className="my-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-dj-light-gray border border-dj-light-gray rounded-md shadow-sm">
            <thead className="bg-slate-50">
              <tr>
                {item.headers.map((header, hIndex) => (
                  <th key={`th-${sectionIndex}-${itemIndexInItsArray}-${hIndex}`} scope="col" className="px-4 py-2 text-left text-xs font-semibold text-dj-text-primary uppercase tracking-wider">
                    {sanitizeAiText(header)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-dj-light-gray">
              {item.rows.map((row, rIndex) => (
                <tr key={`tr-${sectionIndex}-${itemIndexInItsArray}-${rIndex}`} className={`${rIndex % 2 === 0 ? 'bg-white' : 'bg-slate-50/70'} hover:bg-slate-100 transition-colors`}>
                  {row.map((cell, cIndex) => (
                    <td key={`td-${sectionIndex}-${itemIndexInItsArray}-${rIndex}-${cIndex}`} className="px-4 py-2 whitespace-nowrap text-xs text-dj-text-secondary">
                      {typeof cell === 'number' ? cell : sanitizeAiText(String(cell === null || cell === undefined ? '' : cell))}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {item.insights && item.insights.length > 0 && (
            <div className="mt-3 pl-3 border-l-2 border-dj-blue/70 space-y-1">
              {item.insights.map((insight, insIndex) => 
                renderIndividualContentItem(insight, sectionIndex, insIndex , false, true, onPolishParagraph, itemIndexInItsArray)
              )}
            </div>
          )}
        </div>
      );
    case 'chart':
      if (!item.chartData) return null;
      return (
        <div key={`chart-${sectionIndex}-${itemIndexInItsArray}`} className="my-4 p-3 bg-white rounded-lg shadow-md">
          <ChartRenderer chartSpec={item.chartData} />
        </div>
      );
    default:
      console.warn("Unknown ReportContentItem type in ReportDisplay:", item.type, item);
      return null;
  }
};

interface ReportDisplayProps {
  reportSections: ReportSection[];
  onPolishParagraph?: (sectionIndex: number, contentItemIndex: number, insightIndex: number | null, originalText: string) => Promise<void>;
}

export const ReportDisplay: React.FC<ReportDisplayProps> = ({ reportSections, onPolishParagraph }) => {
  if (!reportSections || reportSections.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8 text-center bg-slate-100">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <span className="material-symbols-outlined text-4xl text-dj-text-secondary mb-3">info</span>
          <p className="text-dj-text-secondary">No report data available to display.</p>
          <p className="text-xs text-dj-text-secondary/80 mt-1">Please analyze a file to generate a report.</p>
        </div>
      </div>
    );
  }

  const isAiCommentarySection = (title: string): boolean => {
    return AI_COMMENTARY_SECTION_TITLES.some(aiTitle => 
        title.includes(aiTitle) || 
        (aiTitle === "Overall Performance Trends" && title.includes("Performance Trends"))
    );
  };

  return (
    <div className="p-4 md:p-6 space-y-6 bg-slate-100 min-h-full">
      {reportSections.map((section, sectionIndex) => {
        const sectionIsAiCommentary = isAiCommentarySection(section.title);
        return (
          <section 
            key={`section-${sectionIndex}`} 
            className={`rounded-xl shadow-lg transition-all duration-300 ease-in-out bg-white border 
                        ${sectionIsAiCommentary ? 'border-purple-300' : 'border-slate-300'}`}
          >
            <div className={`px-5 py-4 flex justify-between items-start ${sectionIsAiCommentary ? 'border-b border-purple-200' : 'border-b border-slate-200'}`}>
              <div>
                <h2 className={`text-xl font-semibold ${sectionIsAiCommentary ? 'text-purple-700' : 'text-dj-text-primary'}`}>
                  {sanitizeAiText(section.title)}
                </h2>
                {sectionIsAiCommentary && (
                  <p className="text-xs italic text-purple-600 mt-0.5">AI Generated Commentary & Analysis</p>
                )}
              </div>
              {sectionIsAiCommentary && (
                <span className="ml-3 flex-shrink-0 px-2.5 py-1 bg-purple-600 text-white text-xs font-medium rounded-full shadow-sm">
                  AI Generated
                </span>
              )}
            </div>
            <div className="p-5 space-y-3">
              {section.content.map((item, itemIndex) => 
                renderIndividualContentItem(item, sectionIndex, itemIndex, sectionIsAiCommentary, false, onPolishParagraph)
              )}
            </div>
          </section>
        );
      })}
    </div>
  );
};