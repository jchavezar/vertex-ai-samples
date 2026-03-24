import React from 'react';
import { motion } from 'framer-motion';
import './ResearchReports.css';

const reports = [
  {
    type: 'RESEARCH REPORT',
    title: 'Talent Reinventors: Delivering value with and for people',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/Talent-Reinventors-Glance-Image-600x848%3Arad-card-full?ts=1768430779679&fit=constrain&dpr=off',
    delay: 0.1
  },
  {
    type: 'RESEARCH REPORT',
    title: 'AI innovation is nonstop. Your cloud foundation should be too.',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/AI-innovation-is-nonstop-Your-Cloud-foundation-should-be-too-Glance-Skim-For-Research-Report-600x848px-v2%3Arad-card-full?ts=1773335539812&fit=constrain&dpr=off',
    delay: 0.2
  },
  {
    type: 'RESEARCH REPORT',
    title: 'The dawn of the agentic deal',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/StrategyMA26_Skim-Glance_600x848px%3Arad-card-full?ts=1773788243617&fit=constrain&dpr=off',
    delay: 0.3
  },
  {
    type: 'PERSPECTIVE',
    title: 'Making self-funding supply chains real',
    image: 'https://dynamicmedia.accenture.com/is/content/accenture/00_IllustrationTemp_SizingDoc_640x452_withgrey-03?ts=1761149682942&$none$&wid=1200&fit=constrain&dpr=off',
    delay: 0.4
  },
  {
    type: 'RESEARCH REPORT',
    title: "Pulse of Change: What's top of mind for today's leaders",
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/Pulse-Of-Change-2026-Glance-Image-600x848%3Arad-card-full?ts=1772218106711&fit=constrain&dpr=off',
    delay: 0.5
  },
  {
    type: 'RESEARCH REPORT',
    title: 'Rewriting platform strategy for agentic AI',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/New-Rules-Platform-Strategy-Glance-Skim-Image-600x848%3Arad-card-full?ts=1767339380562&fit=constrain&dpr=off',
    delay: 0.6
  },
  {
    type: 'PERSPECTIVE',
    title: 'The complexity dividend',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/GS-The-Scale-Paradox-300x212%3Arad-card-half?ts=1758203900556&fit=constrain&dpr=off',
    delay: 0.7
  },
  {
    type: 'RESEARCH REPORT',
    title: 'Sovereign AI: From managing risk to accelerating growth',
    image: 'https://dynamicmedia.accenture.com/is/image/accenture/Glance-Skim-Hero-Image-Based-600x848-1%3Arad-card-full?ts=1763433188832&fit=constrain&dpr=off',
    delay: 0.8
  }
];

const ResearchReports = () => {
  return (
    <section className="reports-section" id="reports-section">
      <div className="reports-container">
        <motion.div 
          className="section-header"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2>Expanding Strategic Horizons</h2>
          <p>Fresh insights to redefine your tax and enterprise value.</p>
        </motion.div>

        <div className="reports-grid">
          {reports.map((report, idx) => (
            <motion.div
              key={idx}
              className="report-card"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: report.delay }}
              whileHover={{ y: -10, transition: { duration: 0.2 } }}
            >
              <div className="card-bg" style={{ 
                backgroundImage: `url(${report.image})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                opacity: 1
              }}></div>
              <div className="card-glass">
                <span className="report-type">{report.type}</span>
                <h3>{report.title}</h3>
                <div className="card-footer">
                  <span className="read-more">Read Insight</span>
                  <span className="arrow">→</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ResearchReports;
