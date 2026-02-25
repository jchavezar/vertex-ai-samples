import React, { useState } from 'react';
import { FileText, Award, Layers } from 'lucide-react';

interface CitationProps {
  id: string;
  chunkData: any;
  isActive: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

export const Citation: React.FC<CitationProps> = ({ id, chunkData, isActive, onClick, children }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Calculate similarity percentage (1 - cosine distance)
  // BigQuery distance 0-2 for cosine. Most relevant are usually 0.1-0.5
  const distance = chunkData?.distance || 0;
  const similarity = Math.max(0, Math.min(100, Math.round((1 - distance) * 100)));

  return (
    <span
      className="citation-container"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        className={`citation-pill ${isActive ? 'active' : ''} ${isHovered ? 'hovered' : ''}`}
      >
        <FileText size={11} style={{ marginRight: '4px' }} />
        [{children}]
      </span>

      {isHovered && chunkData && (
        <div className="next-gen-preview">
          <div className="preview-glass-content">
            <div className="preview-header">
              <div className="source-info">
                <span className="source-index">Source [{id}]</span>
                <span className="source-meta">Page {chunkData.page_number} • {chunkData.document_name}</span>
              </div>
              <div className="similarity-badge">
                <Award size={14} className="score-icon" />
                <span>{similarity}% Match</span>
              </div>
            </div>

            <div className="score-track">
              <div className="score-fill" style={{ width: `${similarity}%` }}></div>
            </div>

            <div className="preview-body">
              <p>{chunkData.content}</p>
            </div>

            <div className="preview-footer">
              <Layers size={12} />
              <span>Vector Identity: {chunkData.chunk_id?.split('_').pop()?.substring(0, 8)}...</span>
            </div>
          </div>
          <div className="preview-glow"></div>
        </div>
      )}
    </span>
  );
};
