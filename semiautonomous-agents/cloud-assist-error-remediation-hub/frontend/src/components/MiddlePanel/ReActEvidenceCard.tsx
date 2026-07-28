import React, { useState } from 'react';
import { EvidenceItem } from '../../types';
import { Terminal, CheckCircle2, XCircle, Activity, Lightbulb, Wrench, Check, ArrowRight } from 'lucide-react';

interface ReActEvidenceCardProps {
  evidence: EvidenceItem[];
  isLightMode?: boolean;
}

export const ReActEvidenceCard: React.FC<ReActEvidenceCardProps> = ({ evidence, isLightMode = false }) => {
  const [appliedFixes, setAppliedFixes] = useState<{ [key: string]: boolean }>({});

  if (evidence.length === 0) return null;

  const getRecommendation = (ev: EvidenceItem) => {
    const title = ev.title.toLowerCase();
    const text = ev.text.toLowerCase();

    if (title.includes('memory') || text.includes('oomkilled') || text.includes('512m')) {
      return {
        shortAction: "Expand Container RAM to 1024MB",
        recommendation: "Increase Cloud Run container memory allocation from 512MiB to 1024MiB, or inject stream chunking buffer patch in app/reports/mri.py.",
        actionCommand: "gcloud run services update healthcare-patient-portal --memory=1024MiB --region=us-central1"
      };
    } else if (title.includes('secret') || text.includes('keyerror') || text.includes('jwt')) {
      return {
        shortAction: "Bind JWT_SECRET_KEY Secret",
        recommendation: "Bind missing Secret Manager secret 'JWT_SECRET_KEY' to Cloud Run service revision, or apply os.environ.get fallback patch.",
        actionCommand: "gcloud run services update cyberpunk-ledger-dashboard --update-secrets=JWT_SECRET_KEY=jwt-secret:latest --region=us-central1"
      };
    } else if (title.includes('connection') || text.includes('postgres') || text.includes('pool')) {
      return {
        shortAction: "Expand Connection Pool to 100",
        recommendation: "Increase Cloud SQL max_connections from 20 to 100 and apply exponential backoff retry logic in postgres.py pool getter.",
        actionCommand: "gcloud sql instances patch vtxdemos-postgres --database-flags=max_connections=100"
      };
    } else {
      return {
        shortAction: "Inject Safe Item Count Guard",
        recommendation: "Inject ZeroDivisionGuard safe item count validation before computing discount_ratio in checkout.py.",
        actionCommand: "gcloud run deploy envato-vibe-storefront --image=gcr.io/vtxdemos/storefront:healed --region=us-central1"
      };
    }
  };

  const handleApplyFix = (key: string) => {
    setAppliedFixes((prev) => ({ ...prev, [key]: true }));
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
              Autonomous ReAct Diagnostic Trace & Observer Insights
            </h2>
            <p className={`text-xs ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
              Live checks & gcloud telemetry queries executed by Cloud Assist observers
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
          const isFixApplied = appliedFixes[itemKey];

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

              {/* INLINE GEMINI RECOMMENDATION & REMEDIATION BOX */}
              <div className={`mt-3 p-3.5 rounded-xl border space-y-2.5 font-mono ${
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
                    onClick={() => handleApplyFix(itemKey)}
                    disabled={isFixApplied}
                    className={`px-4 py-2 rounded-xl text-xs font-black flex items-center gap-2 transition-all cursor-pointer shadow-md ${
                      isFixApplied
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                        : isLightMode
                          ? 'bg-slate-950 hover:bg-slate-800 text-white border border-slate-900'
                          : 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {isFixApplied ? (
                      <>
                        <Check className="w-4 h-4 text-emerald-600" />
                        <span>Fix Applied ({rec.shortAction})</span>
                      </>
                    ) : (
                      <>
                        <Wrench className="w-4 h-4 text-amber-400" />
                        <span>⚡ Fix: {rec.shortAction} &rarr; Apply</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
