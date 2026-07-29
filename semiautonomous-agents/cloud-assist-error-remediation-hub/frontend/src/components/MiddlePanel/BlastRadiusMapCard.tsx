import React from 'react';
import { GcpErrorItem } from '../../types';
import { ShieldAlert, Cpu, Database, Key, Server, ArrowRight, Zap, Layers } from 'lucide-react';

interface BlastRadiusMapCardProps {
  selectedError: GcpErrorItem;
  isLightMode?: boolean;
}

export const BlastRadiusMapCard: React.FC<BlastRadiusMapCardProps> = ({ selectedError, isLightMode = false }) => {
  const getBlastNodes = () => {
    const text = (selectedError.serviceName + " " + selectedError.summary + " " + selectedError.fullText + " " + selectedError.id).toLowerCase();
    
    if (text.includes('lifecycle') || text.includes('revision status update')) {
      return {
        primary: "cloud-run-container-engine (Cloud Run System)",
        path: "/sys/revision/rollout",
        impacted: [
          { name: "Revision Ingress Router", type: "Traffic Splitter", status: "SYNCING (100% Green)", icon: Server },
          { name: "Container Auto-Scaler", type: "Instance Pool Engine", status: "SCALING EVENT", icon: Cpu },
          { name: "Revision Health Monitor", type: "Startup Probe", status: "VERIFYING (HTTP 200)", icon: Layers }
        ],
        riskScore: "LOW (2.1/10)",
        userImpact: "Container Instance Scaling & Traffic Rollout Event"
      };
    } else if (text.includes('k8s') || text.includes('gke') || text.includes('crashloop')) {
      return {
        primary: "payment-service-pod-x78z (GKE Pod)",
        path: "/healthz",
        impacted: [
          { name: "Kubelet Readiness Probe", type: "K8s Ingress Controller", status: "FAILED (HTTP 500)", icon: Server },
          { name: "Payment Container Engine", type: "Pod Instance", status: "CRASHLOOPBACKOFF", icon: Cpu },
          { name: "Service Mesh Proxy", type: "Envoy Sidecar", status: "DEGRADED", icon: Layers }
        ],
        riskScore: "HIGH (8.7/10)",
        userImpact: "Payment Processing Pod Restart Loop"
      };
    } else if (text.includes('storage') || text.includes('gcs') || text.includes('bucket')) {
      return {
        primary: "prod-customer-invoice-exports (Cloud Storage Bucket)",
        path: "gs://prod-customer-invoice-exports",
        impacted: [
          { name: "GCS Objects API", type: "Storage Engine", status: "403 PERMISSION DENIED", icon: Key },
          { name: "Invoice Export Pipeline", type: "Batch Subsystem", status: "BLOCKED", icon: Server },
          { name: "Billing Manager UI", type: "Admin Portal", status: "EXPORT FAILURES", icon: Layers }
        ],
        riskScore: "HIGH (7.8/10)",
        userImpact: "Customer Invoice PDF Downloads Failing"
      };
    } else if (text.includes('storefront') || text.includes('envato') || text.includes('zerodivision')) {
      return {
        primary: "envato-vibe-storefront (Cloud Run)",
        path: "/api/cart/checkout",
        impacted: [
          { name: "Checkout Service API", type: "Ingress Router", status: "BLOCKED (HTTP 500)", icon: Server },
          { name: "Payment Gateway Proxy", type: "Microservice", status: "DEGRADED (Timeout)", icon: Cpu },
          { name: "Inventory Database", type: "Cloud SQL Postgres", status: "HEALTHY (Connections Idle)", icon: Database }
        ],
        riskScore: "HIGH (8.4/10)",
        userImpact: "~1,420 Active Cart Sessions Blocked"
      };
    } else if (text.includes('ledger') || text.includes('cyberpunk') || text.includes('jwt')) {
      return {
        primary: "cyberpunk-ledger-dashboard (Cloud Run)",
        path: "/api/auth/token",
        impacted: [
          { name: "Secret Manager ('JWT_SECRET_KEY')", type: "GCP Secret Store", status: "MISSING BINDING", icon: Key },
          { name: "OAuth Token Authority", type: "Auth Subsystem", status: "HALTED (KeyError)", icon: ShieldAlert },
          { name: "User Session Cache", type: "Memorystore Redis", status: "IDLE", icon: Database }
        ],
        riskScore: "CRITICAL (9.1/10)",
        userImpact: "All Authentication & Token Verification Requests Failing"
      };
    } else if (text.includes('healthcare') || text.includes('medical') || text.includes('oom')) {
      return {
        primary: "healthcare-patient-portal (Cloud Run)",
        path: "/api/reports/mri-scan",
        impacted: [
          { name: "DICOM Image Renderer", type: "Heap Buffer Engine", status: "OOM KILLED (512MB)", icon: Cpu },
          { name: "Patient Records Storage", type: "Cloud Storage Bucket", status: "ACCESSIBLE", icon: Database },
          { name: "EHR Sync Service", type: "Pub/Sub Pipeline", status: "BACKLOGGED", icon: Layers }
        ],
        riskScore: "CRITICAL (9.5/10)",
        userImpact: "Radiology Scan Reports Unreachable"
      };
    } else if (text.includes('scheduler') || text.includes('warmup')) {
      return {
        primary: "envato-vibe-app-warmup (Cloud Scheduler Job)",
        path: "/api/warmup",
        impacted: [
          { name: "Cloud Scheduler Cron", type: "GCP Scheduler Job", status: "FAILED (HTTP 404)", icon: Server },
          { name: "Cloud Run Revision Endpoint", type: "Microservice Ingress", status: "ROUTE MISSING", icon: Cpu },
          { name: "Warmup Cache Subsystem", type: "Application Cache", status: "COLD START DELAY", icon: Layers }
        ],
        riskScore: "MEDIUM (6.5/10)",
        userImpact: "Automated Warmup Cron Job Failing on Target Route /api/warmup"
      };
    } else {
      return {
        primary: "realtime-logistics-tracker (Cloud Run)",
        path: "/api/fleet/status",
        impacted: [
          { name: "Cloud SQL Postgres Pool", type: "Database Cluster", status: "CONNECTION REFUSED", icon: Database },
          { name: "GPS Ingestion Workers", type: "Cloud Run Pool", status: "RETRY EXHAUSTION", icon: Server },
          { name: "Telemetry Dashboard UI", type: "Frontend Client", status: "STALE COORDINATES", icon: Layers }
        ],
        riskScore: "HIGH (8.2/10)",
        userImpact: "42 Delivery Fleet Vehicles Off-Grid"
      };
    }
  };

  const blastData = getBlastNodes();

  return (
    <div className={`p-5 rounded-2xl border shadow-sm space-y-4 ${
      isLightMode
        ? 'bg-white border-slate-300 text-slate-950 font-sans'
        : 'bg-slate-900 border-slate-800 text-white shadow-xl'
    }`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-3.5 border-slate-200">
        <div className="flex items-center space-x-3">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${
            isLightMode ? 'bg-rose-50 border-rose-300 text-rose-800 font-bold' : 'bg-rose-500/20 border-rose-500/40 text-rose-400'
          }`}>
            <ShieldAlert className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className={`text-sm font-extrabold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>
              Visual Incident "Blast Radius" & Systemic Dependency Map
            </h3>
            <p className={`text-xs ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
              Real-time cascading impact analysis across GCP Microservices & Cloud Infrastructure
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className={`text-[10px] font-mono font-bold px-3 py-1 rounded-full border ${
            isLightMode ? 'bg-rose-100 text-rose-800 border-rose-300' : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
          }`}>
            BLAST RISK: {blastData.riskScore}
          </span>
        </div>
      </div>

      {/* Visual Impact Flow Graph */}
      <div className={`p-4 rounded-xl border space-y-4 ${
        isLightMode ? 'bg-[#f8fafc] border-slate-300' : 'bg-black/60 border-slate-800'
      }`}>
        <div className="text-xs font-mono font-bold text-slate-700 flex items-center gap-2">
          <Zap className="w-3.5 h-3.5 text-amber-500" />
          <span>Incident Origin Target: <code className="text-rose-700 font-bold">{blastData.primary}</code></span>
        </div>

        {/* Node Connection Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative">
          {blastData.impacted.map((node, idx) => {
            const NodeIcon = node.icon;
            const isCritical = node.status.includes('BLOCKED') || node.status.includes('CRITICAL') || node.status.includes('MISSING') || node.status.includes('REFUSED') || node.status.includes('KILLED');
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border flex flex-col justify-between space-y-2 transition-all ${
                  isLightMode
                    ? isCritical
                      ? 'bg-rose-50/80 border-rose-300 text-slate-900 shadow-sm'
                      : 'bg-white border-slate-300 text-slate-900'
                    : isCritical
                      ? 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                      : 'bg-slate-900 border-slate-800 text-slate-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <NodeIcon className={`w-4 h-4 ${isCritical ? 'text-rose-600' : 'text-slate-600'}`} />
                    <span className="text-xs font-mono font-bold">{node.name}</span>
                  </div>
                  <span className={`w-2 h-2 rounded-full ${isCritical ? 'bg-rose-600 animate-ping' : 'bg-emerald-500'}`}></span>
                </div>
                <div className="text-[11px] font-mono text-slate-600">{node.type}</div>
                <div className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border inline-block ${
                  isCritical
                    ? 'bg-rose-100 text-rose-800 border-rose-300'
                    : 'bg-slate-100 text-slate-800 border-slate-300'
                }`}>
                  {node.status}
                </div>
              </div>
            );
          })}
        </div>

        <div className={`p-3 rounded-lg border text-xs font-mono flex items-center justify-between ${
          isLightMode ? 'bg-white border-slate-300 text-slate-900' : 'bg-slate-900 border-slate-800 text-slate-300'
        }`}>
          <span className="text-slate-600 font-semibold">User Experience Impact:</span>
          <span className="text-rose-700 font-extrabold">{blastData.userImpact}</span>
        </div>
      </div>
    </div>
  );
};
