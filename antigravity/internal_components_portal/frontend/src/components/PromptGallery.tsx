import React from 'react';
import { Lightbulb, Database, Lock, Users } from 'lucide-react';

interface PromptGalleryProps {
  onSelectPrompt: (prompt: string) => void;
}

const CATEGORIES = [
  {
    title: "Financial Abstraction",
    icon: <Users size={20} />,
    color: "var(--internal-green)",
    prompts: [
      "Process the employee salaries and extract the average compensation without revealing individual names.",
      "What is the total sum of the CFO compensation package, presented without any identifying personal details?"
    ]
  },
  {
    title: "Vulnerability Generalization",
    icon: <Database size={20} />,
    color: "var(--internal-rose)",
    prompts: [
      "Identify all systems with 'High' risk severity and list their vulnerabilities, completely masking the hostnames.",
      "What are the most critical security vulnerabilities in enterprise environments without revealing internal IPs?"
    ]
  },
  {
    title: "Contractual Agreements",
    icon: <Lock size={20} />,
    color: "var(--internal-yellow)",
    prompts: [
      "Summarize the key SLA terms and credits identified in the enterprise software agreements without citing specific companies.",
      "Provide a breakdown of typical termination fee structures maintaining vendor anonymity."
    ]
  }
];

export const PromptGallery: React.FC<PromptGalleryProps> = ({ onSelectPrompt }) => {
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
