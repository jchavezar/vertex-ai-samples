import React, { useState, useEffect } from 'react';
import { ShieldCheck, RotateCcw, Clock, CheckCircle2, AlertTriangle, RefreshCw, FileText, Cpu, Server, Activity } from 'lucide-react';

interface BitacoraItem {
  id: string;
  serviceName: string;
  incidentSummary: string;
  appliedPatch: string;
  timestamp: string;
  agent: string;
  mttr: string;
  status: 'RESOLVED' | 'PENDING' | 'REVERTED';
  canRollback: boolean;
}

interface BitacoraData {
  totalIncidents: number;
  resolvedCount: number;
  pendingCount: number;
  revertedCount: number;
  history: BitacoraItem[];
}

export const RemediationBitacoraTab: React.FC<{ isLightMode?: boolean }> = ({ isLightMode = true }) => {
  const [data, setData] = useState<BitacoraData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [rollingBackId, setRollingBackId] = useState<string | null>(null);

  const fetchBitacora = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/bitacora');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result: BitacoraData = await res.json();
      setData(result);
    } catch (err) {
      console.error("Failed to fetch bitácora data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBitacora();
  }, []);

  const handleRollback = async (incidentId: string) => {
    setRollingBackId(incidentId);
    try {
      const res = await fetch('http://127.0.0.1:8088/api/bitacora/rollback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incidentId })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await fetchBitacora();
    } catch (err) {
      console.error("Rollback failed:", err);
    } finally {
      setRollingBackId(null);
    }
  };

  if (isLoading && !data) {
    return (
      <div className="p-12 text-center font-mono text-xs text-slate-500 flex items-center justify-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-cyan-500" />
        <span>Loading Incident Remediation Bitácora Audit Log...</span>
      </div>
    );
  }

  return (
    <div className={`p-6 rounded-3xl border shadow-sm space-y-6 font-mono ${
      isLightMode
        ? 'bg-white border-slate-300 text-slate-950'
        : 'bg-slate-900 border-slate-800 text-white shadow-xl'
    }`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 border-slate-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-slate-950 text-white flex items-center justify-center shadow-md">
            <FileText className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-base font-black tracking-tight uppercase">
              📜 Incident Remediation Bitácora & Rollback Audit Manager
            </h2>
            <p className="text-xs text-slate-500">
              Complete audit trail of resolved vs pending incident patches with 1-click GCP revision rollbacks
            </p>
          </div>
        </div>

        <button
          onClick={fetchBitacora}
          className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 text-xs font-bold flex items-center gap-1.5 cursor-pointer border border-slate-300"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Audit Stream</span>
        </button>
      </div>

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl border bg-slate-50 border-slate-200 space-y-1">
          <div className="text-[11px] text-slate-500 font-bold">Total Ingested Incidents</div>
          <div className="text-2xl font-black text-slate-950">{data?.totalIncidents || 0}</div>
        </div>
        <div className="p-4 rounded-2xl border bg-emerald-50 border-emerald-300 text-emerald-950 space-y-1">
          <div className="text-[11px] text-emerald-800 font-bold">🟢 Remediated & Solved</div>
          <div className="text-2xl font-black text-emerald-700">{data?.resolvedCount || 0}</div>
        </div>
        <div className="p-4 rounded-2xl border bg-amber-50 border-amber-300 text-amber-950 space-y-1">
          <div className="text-[11px] text-amber-800 font-bold">🟡 Pending / Left to Fix</div>
          <div className="text-2xl font-black text-amber-700">{data?.pendingCount || 0}</div>
        </div>
        <div className="p-4 rounded-2xl border bg-rose-50 border-rose-300 text-rose-950 space-y-1">
          <div className="text-[11px] text-rose-800 font-bold">↩️ Reverted via Rollback</div>
          <div className="text-2xl font-black text-rose-700">{data?.revertedCount || 0}</div>
        </div>
      </div>

      {/* Bitácora Audit Trail Table */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Remediation Bitácora Log Stream
        </h3>

        <div className="space-y-3">
          {data?.history.map((item) => {
            const isResolved = item.status === 'RESOLVED';
            const isPending = item.status === 'PENDING';
            const isReverted = item.status === 'REVERTED';
            const isRolling = rollingBackId === item.id;

            return (
              <div
                key={item.id}
                className={`p-4 rounded-2xl border transition-all space-y-3 ${
                  isResolved
                    ? 'bg-emerald-50/40 border-emerald-300 text-slate-950'
                    : isReverted
                      ? 'bg-rose-50/40 border-rose-300 text-slate-950'
                      : 'bg-amber-50/40 border-amber-300 text-slate-950'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-2 border-slate-200">
                  <div className="flex items-center space-x-2.5">
                    <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">
                      {item.id}
                    </span>
                    <span className="text-xs font-black text-slate-950">{item.serviceName}</span>
                    <span className="text-[10px] text-slate-500 font-bold">• Agent: {item.agent}</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-slate-500 font-bold">MTTR: {item.mttr}</span>
                    <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                      isResolved
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : isReverted
                          ? 'bg-rose-100 text-rose-800 border-rose-300'
                          : 'bg-amber-100 text-amber-800 border-amber-300'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="text-xs font-bold text-slate-900">Incident: {item.incidentSummary}</div>
                  <div className="text-[11px] text-slate-700 bg-white p-2.5 rounded-xl border border-slate-200">
                    <strong>Applied Patch:</strong> {item.appliedPatch}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-slate-500">Timestamp: {item.timestamp}</span>

                  {item.canRollback && (
                    <button
                      onClick={() => handleRollback(item.id)}
                      disabled={isRolling}
                      className="px-3.5 py-1.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-md"
                    >
                      {isRolling ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Reverting GCP Revision...</span>
                        </>
                      ) : (
                        <>
                          <RotateCcw className="w-3.5 h-3.5 text-rose-400" />
                          <span>↩️ Rollback Fix to Broken State</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
