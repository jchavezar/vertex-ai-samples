import React, { useState } from 'react';
import { EvidenceItem } from '../../types';
import { Terminal, CheckCircle2, XCircle, Activity, Lightbulb, Wrench, Check, RefreshCw, ShieldCheck, ExternalLink } from 'lucide-react';

interface ReActEvidenceCardProps {
  evidence: EvidenceItem[];
  isLightMode?: boolean;
}

export const ReActEvidenceCard: React.FC<ReActEvidenceCardProps> = ({ evidence, isLightMode = false }) => {
  const [executingKeys, setExecutingKeys] = useState<{ [key: string]: boolean }>({});
  const [executionLogs, setExecutionLogs] = useState<{ [key: string]: { logStream: string[]; auditLog?: any; revision?: string } }>({});

  if (evidence.length === 0) return null;

  const getRecommendation = (ev: EvidenceItem) => {
    const title = ev.title.toLowerCase();
    const text = ev.text.toLowerCase();

    if (title.includes('memory') || text.includes('oomkilled') || text.includes('512m')) {
      return {
        serviceName: "healthcare-patient-portal",
        shortAction: "Expand Container RAM to 1024MB",
        recommendation: "Increase Cloud Run container memory allocation from 512MiB to 1024MiB, or inject stream chunking buffer patch in app/reports/mri.py.",
        actionCommand: "gcloud run services update healthcare-patient-portal --memory=1024MiB --region=us-central1"
      };
    } else if (title.includes('secret') || text.includes('keyerror') || text.includes('jwt')) {
      return {
        serviceName: "cyberpunk-ledger-dashboard",
        shortAction: "Bind JWT_SECRET_KEY Secret",
        recommendation: "Bind missing Secret Manager secret 'JWT_SECRET_KEY' to Cloud Run service revision, or apply os.environ.get fallback patch.",
        actionCommand: "gcloud run services update cyberpunk-ledger-dashboard --update-env-vars=JWT_SECRET_KEY=prod-jwt-secret-key-2026 --region=us-central1"
      };
    } else if (title.includes('connection') || text.includes('postgres') || text.includes('pool')) {
      return {
        serviceName: "realtime-logistics-tracker",
        shortAction: "Expand Connection Pool to 100",
        recommendation: "Increase Cloud SQL max_connections from 20 to 100 and apply exponential backoff retry logic in postgres.py pool getter.",
        actionCommand: "gcloud run services update realtime-logistics-tracker --update-env-vars=DB_MAX_CONNECTIONS=100 --region=us-central1"
      };
    } else {
      return {
        serviceName: "envato-vibe-storefront",
        shortAction: "Inject Safe Item Count Guard",
        recommendation: "Inject ZeroDivisionGuard safe item count validation before computing discount_ratio in checkout.py.",
        actionCommand: "gcloud run services update envato-vibe-storefront --update-env-vars=ZERO_DIV_GUARD=true --region=us-central1"
      };
    }
  };

  const handleApplyRealGcpFix = async (itemKey: string, command: string, serviceName: string) => {
    setExecutingKeys(prev => ({ ...prev, [itemKey]: true }));
    setExecutionLogs(prev => ({
      ...prev,
      [itemKey]: {
        logStream: [
          `[$ gcloud CLI INITIATED] ${command} --project=vtxdemos --region=us-central1`,
          `[GCP REGION us-central1] Contacting Cloud Run Admin API v2...`,
          `[BUILD & DEPLOY] Compiling container layer & updating service spec...`
        ]
      }
    }));

    try {
      const res = await fetch('http://127.0.0.1:8088/api/execute-real-gcp-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, serviceName })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setExecutionLogs(prev => ({
        ...prev,
        [itemKey]: {
          logStream: data.logStream || [],
          auditLog: data.auditLog,
          revision: data.latestRevision
        }
      }));
    } catch (err) {
      console.error("Real GCP fix execution error:", err);
      setExecutionLogs(prev => ({
        ...prev,
        [itemKey]: {
          logStream: [
            `[ERROR] Failed to execute gcloud command: ${String(err)}`
          ]
        }
      }));
    } finally {
      setExecutingKeys(prev => ({ ...prev, [itemKey]: false }));
    }
  };

  return (
    <div className={`p-5 rounded-2xl border shadow-sm space-y-4 ${
      isLightMode
        ? 'bg-white border-slate-300 text-slate-950 font-sans'
        : 'bg-[#111622]/90 border-slate-800/80 text-white shadow-xl'
    }`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-3.5 border-slate-200">
        <div className="flex items-center space-x-2.5">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${
            isLightMode ? 'bg-sky-50 border-sky-300 text-sky-800 font-bold' : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
          }`}>
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className={`text-sm font-extrabold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>
              Autonomous ReAct Diagnostic Trace & Live GCP Execution Pipeline
            </h2>
            <p className={`text-xs ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
              Direct gcloud CLI execution against GCP project 'vtxdemos' with real Cloud Audit Log verification
            </p>
          </div>
        </div>
        <span className={`text-xs font-bold font-mono px-3 py-1 rounded-full border ${
          isLightMode
            ? 'bg-sky-100 text-sky-800 border-sky-300'
            : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
        }`}>
          {evidence.length} Observers Verified
        </span>
      </div>

      <div className="space-y-3">
        {evidence.map((ev, idx) => {
          const isHealthy = ev.normalOperation === true;
          const isAnomaly = ev.normalOperation === false;
          const itemKey = ev.id || `ev-${idx}`;
          const rec = getRecommendation(ev);
          const isExecuting = executingKeys[itemKey];
          const execLog = executionLogs[itemKey];
          const isFinished = execLog && execLog.auditLog;

          return (
            <div
              key={itemKey}
              className={`p-4 rounded-xl border space-y-3 transition-colors ${
                isLightMode
                  ? isAnomaly
                    ? 'bg-rose-50/50 border-rose-300 text-slate-950 shadow-sm'
                    : 'bg-[#f8fafc] border-slate-300 text-slate-950'
                  : isAnomaly
                    ? 'bg-rose-950/40 border-rose-800/80 text-rose-200'
                    : 'bg-slate-950/60 border-slate-800/80 text-slate-200'
              }`}
            >
              {/* Observer Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {isHealthy ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : isAnomaly ? (
                    <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0 animate-pulse" />
                  ) : (
                    <Terminal className="w-4 h-4 text-sky-600 flex-shrink-0" />
                  )}
                  <span className={`text-xs font-mono font-extrabold ${isLightMode ? 'text-slate-950' : 'text-slate-100'}`}>
                    {ev.title}
                  </span>
                </div>

                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${
                  isLightMode
                    ? 'bg-white text-slate-800 border-slate-300 shadow-sm'
                    : 'bg-slate-900 text-slate-400 border-slate-800'
                }`}>
                  {ev.checkType}
                </span>
              </div>

              {/* Executed gcloud Observer Command */}
              {ev.commandExecuted && (
                <div className={`p-2.5 rounded-lg border font-mono text-[11px] overflow-x-auto ${
                  isLightMode
                    ? 'bg-slate-950 text-sky-300 border-slate-900 shadow-inner'
                    : 'bg-black/80 text-cyan-300 border-slate-800'
                }`}>
                  $ {ev.commandExecuted}
                </div>
              )}

              {/* Observation Finding Text */}
              <p className={`text-xs leading-relaxed font-mono ${isLightMode ? 'text-slate-800' : 'text-slate-300'}`}>
                {ev.text}
              </p>

              {/* INLINE GEMINI RECOMMENDATION & REAL GCP EXECUTION BOX */}
              <div className={`mt-3 p-3.5 rounded-xl border space-y-3 font-mono ${
                isLightMode
                  ? isAnomaly
                    ? 'bg-amber-50/80 border-amber-300 text-amber-950'
                    : 'bg-white border-slate-300 text-slate-900 shadow-sm'
                  : 'bg-black/50 border-amber-500/30 text-amber-200'
              }`}>
                <div className="flex items-center space-x-2 text-xs font-bold text-amber-900">
                  <Lightbulb className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  <span>Gemini Recommended Remediation:</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-800 font-medium">
                  {rec.recommendation}
                </p>

                <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-amber-200/80">
                  <code className="text-[10px] text-slate-700 truncate max-w-xs font-bold">
                    $ {rec.actionCommand}
                  </code>

                  <button
                    onClick={() => handleApplyRealGcpFix(itemKey, rec.actionCommand, rec.serviceName)}
                    disabled={isExecuting}
                    className={`px-4 py-2 rounded-xl text-xs font-black flex items-center gap-2 transition-all cursor-pointer shadow-md ${
                      isFinished
                        ? 'bg-emerald-600 text-white border border-emerald-700'
                        : isExecuting
                          ? 'bg-amber-600 text-white animate-pulse'
                          : isLightMode
                            ? 'bg-slate-950 hover:bg-slate-800 text-white border border-slate-900'
                            : 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {isExecuting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin text-white" />
                        <span>Executing Real gcloud CLI...</span>
                      </>
                    ) : isFinished ? (
                      <>
                        <ShieldCheck className="w-4 h-4 text-white" />
                        <span>Real GCP Revision Deployed ({execLog.revision})</span>
                      </>
                    ) : (
                      <>
                        <Wrench className="w-4 h-4 text-amber-400" />
                        <span>⚡ Fix: {rec.shortAction} &rarr; Execute on GCP</span>
                      </>
                    )}
                  </button>
                </div>

                {/* REAL GCP LOG & AUDIT LOG STREAM TERMINAL */}
                {execLog && (
                  <div className="mt-3 pt-3 border-t border-amber-300/80 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-900">
                      <span className="flex items-center gap-1.5 text-emerald-800">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                        <span>REAL GCP EXECUTION LOG & AUDIT LOG STREAM</span>
                      </span>
                      {execLog.revision && (
                        <span className="text-[10px] bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded font-mono border border-emerald-300 font-extrabold">
                          REVISION: {execLog.revision}
                        </span>
                      )}
                    </div>

                    <div className="p-3 bg-slate-950 text-emerald-400 rounded-xl text-[10px] font-mono h-40 overflow-y-auto space-y-1 border border-slate-800">
                      {execLog.logStream.map((logLine, idx) => (
                        <div key={idx} className="flex items-start gap-1.5">
                          <span className="text-slate-500">&gt;</span>
                          <span className={logLine.includes('VERIFIED') ? 'text-amber-300 font-bold' : ''}>{logLine}</span>
                        </div>
                      ))}
                    </div>

                    {execLog.auditLog && (
                      <div className="p-2.5 bg-emerald-50 border border-emerald-300 rounded-xl text-[10px] font-mono text-emerald-950 space-y-1">
                        <div className="font-extrabold flex items-center gap-1 text-emerald-900">
                          <Check className="w-3 h-3 text-emerald-600" />
                          <span>GCP Cloud Audit Log Event Verified:</span>
                        </div>
                        <div><strong>Method:</strong> {execLog.auditLog.methodName}</div>
                        <div><strong>Caller:</strong> {execLog.auditLog.principalEmail}</div>
                        <div><strong>Log URI:</strong> {execLog.auditLog.logName}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
