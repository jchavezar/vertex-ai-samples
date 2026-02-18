import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, CheckCircle2, Database, Brain, FileText, Zap } from 'lucide-react';

const steps = [
  { id: 'upload', icon: FileText, label: 'Uploading Document' },
  { id: 'extract', icon: Brain, label: 'Parallel Extraction via ADK' },
  { id: 'embed', icon: Zap, label: 'Generating Vector Embeddings' },
  { id: 'sync', icon: Database, label: 'Syncing to BigQuery & Feature Store' },
];

interface UploadOverlayProps {
  isProcessing: boolean;
}

export const UploadOverlay: React.FC<UploadOverlayProps> = ({ isProcessing }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    if (!isProcessing) {
      setCurrentStepIndex(0);
      return;
    }

    // Simulate progress through the steps since we don't have SSE yet
    // Average time is ~30 seconds for the entire pipeline
    const intervals = [
      setTimeout(() => setCurrentStepIndex(1), 2000),   // Upload fast
      setTimeout(() => setCurrentStepIndex(2), 15000),  // Extraction takes ~13s
      setTimeout(() => setCurrentStepIndex(3), 25000),  // Embeddings take ~10s
    ];

    return () => intervals.forEach(clearTimeout);
  }, [isProcessing]);

  return (
    <AnimatePresence>
      {isProcessing && (
        <motion.div
          className="upload-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="upload-content">
            <motion.div
              className="pulse-ring"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.1, 0.3, 0.1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />

            <h2 className="overlay-title">Nexus Pipeline Active</h2>

            <div className="steps-container">
              {steps.map((step, index) => {
                const isCompleted = index < currentStepIndex;
                const isCurrent = index === currentStepIndex;
                const isPending = index > currentStepIndex;
                const Icon = step.icon;

                return (
                  <motion.div
                    key={step.id}
                    className={`step-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${isPending ? 'pending' : ''}`}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: index * 0.2 }}
                  >
                    <div className="step-icon">
                      {isCompleted ? <CheckCircle2 className="text-accent-green" /> :
                        isCurrent ? <Loader2 className="animate-spin text-accent-cyan" /> :
                          <Icon className="text-text-secondary" />}
                    </div>
                    <span className="step-label">{step.label}</span>
                  </motion.div>
                );
              })}
            </div>

            <motion.div
              className="processing-status"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              Gemini 2.5 Flash is analyzing your document...
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
