import React from 'react';
import { ShieldAlert, Lock, Fingerprint } from 'lucide-react';
import { motion } from 'framer-motion';
import './ZeroLeakShield.css';

const ZeroLeakShield = () => {
  return (
    <div className="zero-leak-container margin-y-xl">
      <motion.div 
        className="glass-panel security-banner"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className="security-icon-group relative">
          <div className="shield-bg"></div>
          <Fingerprint size={48} className="text-accent shield-icon" />
          <motion.div 
            className="lock-badge align-center justify-center"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <Lock size={12} color="white" />
          </motion.div>
        </div>
        
        <div className="security-content">
          <h3>Protected by Zero-Leak Security Architecture</h3>
          <p>
            Your highly sensitive M&A and tax data is tokenized and processed via Vertex AI Agent Engine. 
            <strong> Absolute isolation. Zero public model training. Total enterprise trust.</strong>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default ZeroLeakShield;
