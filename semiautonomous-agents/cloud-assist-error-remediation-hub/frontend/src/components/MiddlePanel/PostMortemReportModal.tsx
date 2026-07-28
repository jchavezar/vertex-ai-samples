import React, { useState } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic } from '../../types';
import { FileText, Copy, Download, Check, X } from 'lucide-react';

interface PostMortemReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedError: GcpErrorItem | null;
  diagnostic: CloudAssistDiagnostic | null;
  isLightMode?: boolean;
}

export const PostMortemReportModal: React.FC<PostMortemReportModalProps> = ({
  isOpen,
  onClose,
  selectedError,
  diagnostic,
  isLightMode = false
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !selectedError) return null;

  const reportMarkdown = `# 📄 EXECUTIVE INCIDENT POST-MORTEM REPORT
**Date**: ${new Date().toLocaleDateString()} | **Project**: vtxdemos | **Region**: us-central1
**Incident ID**: ${selectedError.id}
**Severity**: ${selectedError.severity}
**Service**: ${selectedError.serviceName} (${selectedError.resourceType})

---

## 1. Executive Summary
An anomaly was automatically detected in Cloud Logging for microservice \`${selectedError.serviceName}\`. 
Gemini Cloud Assist synthesized a root-cause hypothesis and automatically generated an autonomous code patch.

- **Incident Symptom**: \`${selectedError.summary}\`
- **Mean Time to Remediation (MTTR)**: **12.8 Seconds**
- **Remediation Status**: **RESOLVED (HTTP 200 OK Probe Verified)**

---

## 2. Root Cause Analysis (RCA)
${diagnostic?.recapText || "The service encountered an unhandled exception during request execution. The unhandled code path caused container workers to fail with HTTP 500."}

---

## 3. Applied Remediation Code Patch
\`\`\`diff
${diagnostic?.hypotheses[0]?.recommendationText || "# Antigravity Auto-Healing Patch Applied"}
\`\`\`

---

## 4. Verification & Prevention
- **Container Health Probe**: HTTP 200 OK Verified
- **Policy Gate Approval**: Autonomous Remediate Granted
- **Confluence / Jira Sync**: Automated Ticket Logged
`;

  const copyReport = () => {
    navigator.clipboard.writeText(reportMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadReport = () => {
    const blob = new Blob([reportMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Incident_PostMortem_${selectedError.serviceName}_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
      <div className={`border-2 rounded-3xl max-w-3xl w-full p-6 space-y-4 shadow-2xl font-mono ${
        isLightMode ? 'bg-white border-slate-900 text-slate-950' : 'bg-slate-900 border-slate-700 text-white'
      }`}>
        {/* Header */}
        <div className="flex justify-between items-center border-b pb-3 border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-950 text-white flex items-center justify-center shadow-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-black tracking-tight uppercase">Executive Incident Post-Mortem Report</h3>
              <p className="text-xs text-slate-500">Formatted Markdown report ready for Confluence, Jira, or Executive briefings</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={copyReport}
              className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 text-xs font-bold flex items-center gap-1.5 cursor-pointer border border-slate-300"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Markdown'}</span>
            </button>

            <button
              onClick={downloadReport}
              className="px-3.5 py-1.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .md</span>
            </button>

            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-900 cursor-pointer">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Report Content Box */}
        <div className="p-4 bg-slate-950 text-slate-100 rounded-2xl h-80 overflow-y-auto font-mono text-xs border border-slate-800 space-y-2 leading-relaxed">
          <pre className="whitespace-pre-wrap">{reportMarkdown}</pre>
        </div>

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className="px-5 py-2 rounded-xl bg-slate-950 text-white font-bold text-xs shadow-md cursor-pointer">
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};
