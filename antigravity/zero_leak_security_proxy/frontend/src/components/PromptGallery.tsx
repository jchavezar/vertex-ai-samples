import React from 'react';
import { Lightbulb, Database, FileText, Lock, Building, Users } from 'lucide-react';

interface PromptGalleryProps {
  onSelectPrompt: (prompt: string) => void;
  isLoading: boolean;
}

const CATEGORIES = [
  {
    title: "Audit & Compliance",
    icon: <Lock size={20} />,
    color: "var(--pwc-orange)",
    prompts: [
      "What internal control weaknesses are most commonly found in tech companies?",
      "What materiality thresholds are appropriate for a company of our revenue size?",
      "How did other companies fix revenue recognition control weaknesses?"
    ]
  },
  {
    title: "Executive Compensation",
    icon: <Users size={20} />,
    color: "var(--pwc-rose)",
    prompts: [
      "What is a competitive compensation structure for a CFO at a growth-stage tech company?",
      "What equity vesting schedules are standard for C-suite executives?",
      "What compensation structures have reduced executive turnover?"
    ]
  },
  {
    title: "Enterprise Contracts",
    icon: <FileText size={20} />,
    color: "var(--pwc-yellow)",
    prompts: [
      "What SLA terms and credits are standard in enterprise software agreements?",
      "What termination fee structures are typical for multi-year contracts?",
      "How have companies negotiated better SLA terms with vendors?"
    ]
  },
  {
    title: "Security & Risk",
    icon: <Database size={20} />,
    color: "var(--pwc-orange)",
    prompts: [
      "What are the most critical security vulnerabilities in enterprise environments?",
      "What should our incident response process look like?",
      "What zero trust implementations have been successful in healthcare?"
    ]
  },
  {
    title: "M&A Strategy",
    icon: <Building size={20} />,
    color: "var(--pwc-red)",
    prompts: [
      "What valuation multiples are appropriate for a SaaS company with 40% growth?",
      "What synergy categories should we model in our acquisition analysis?",
      "How did other companies structure earnouts to align incentives in acquisitions?"
    ]
  }
];

export const PromptGallery: React.FC<PromptGalleryProps> = ({ onSelectPrompt, isLoading }) => {
  return (
    <div className="prompt-gallery-container">
      <div className="gallery-header">
        <Lightbulb className="gallery-icon" size={24} />
        <h2>Consulting Intelligence Hub</h2>
        <p>Select a strategic query to securely extract generalized insights from our confidential knowledge base.</p>
      </div>

      <div className="gallery-grid">
        {CATEGORIES.map((category, idx) => (
          <div key={idx} className="gallery-category-card">
            <div className="category-card-header" style={{ color: category.color }}>
              {category.icon}
              <h3>{category.title}</h3>
            </div>
            <div className="category-prompts">
              {category.prompts.map((prompt, pIdx) => (
                <button
                  key={pIdx}
                  className="prompt-pill"
                  onClick={() => onSelectPrompt(prompt)}
                  disabled={isLoading}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
