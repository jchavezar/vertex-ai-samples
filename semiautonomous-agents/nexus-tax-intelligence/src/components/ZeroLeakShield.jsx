import React from 'react';
import { motion } from 'framer-motion';
import { Fingerprint, Lock } from 'lucide-react';
import './ZeroLeakShield.css';

const ZeroLeakShield = () => {
  return (
    <motion.section className="zero-leak-section" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
      <div className="zero-leak-accent-line"></div>
      <div className="zero-leak-container">
        <div className="zero-leak-icon">
          <Fingerprint size={36} strokeWidth={1.5} />
          <div className="zero-leak-lock"><Lock size={12} /></div>
        </div>
        <h2 className="zero-leak-heading">Protected by Zero-Leak Security Architecture</h2>
        <p className="zero-leak-description">
          Your data is tokenized and processed exclusively through Vertex AI Agent Engine. Zero public model training. Enterprise trust, guaranteed.
        </p>
      </div>
    </motion.section>
  );
};

export default ZeroLeakShield;
