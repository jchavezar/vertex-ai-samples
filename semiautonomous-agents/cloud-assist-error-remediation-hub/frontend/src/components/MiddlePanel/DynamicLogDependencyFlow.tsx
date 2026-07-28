import React from 'react';
import { GcpErrorItem } from '../../types';
import { ArrowRight, Clock, Server, AlertTriangle, User, Key, Lock, Activity, Cpu, Database, Truck } from 'lucide-react';

interface DynamicLogDependencyFlowProps {
  selectedError: GcpErrorItem;
  isLightMode?: boolean;
}

export const DynamicLogDependencyFlow: React.FC<DynamicLogDependencyFlowProps> = ({ selectedError, isLightMode = false }) => {
  const getFlowData = () => {
    const svc = selectedError.serviceName.toLowerCase();
    const sum = (selectedError.summary + " " + selectedError.fullText).toLowerCase();

    if (svc.includes("scheduler") || selectedError.resourceType.includes("scheduler") || sum.includes("scheduler")) {
      return {
        protocol: "HTTP GET /api/warmup",
        statusCode: "HTTP 404 NOT FOUND",
        nodes: [
          { label: "Cloud Scheduler", sub: "envato-vibe-app-warmup", icon: Clock, type: "UPSTREAM" },
          { label: "Cloud Run Service", sub: "envato-vibe-storefront", icon: Server, type: "TARGET" },
          { label: "Route Handler", sub: "HTTP 404 Not Found", icon: AlertTriangle, type: "DOWNSTREAM", isError: true }
        ]
      };
    } else if (svc.includes("storefront") || sum.includes("zerodivision") || sum.includes("checkout")) {
      return {
        protocol: "HTTP POST /api/cart/checkout",
        statusCode: "HTTP 500 INTERNAL ERROR",
        nodes: [
          { label: "Storefront Web UI", sub: "Client Cart Request", icon: User, type: "UPSTREAM" },
          { label: "Cloud Run Service", sub: "envato-vibe-storefront", icon: Server, type: "TARGET" },
          { label: "ZeroDivisionGuard", sub: "discount_ratio calculation", icon: AlertTriangle, type: "DOWNSTREAM", isError: true }
        ]
      };
    } else if (svc.includes("ledger") || sum.includes("keyerror") || sum.includes("jwt")) {
      return {
        protocol: "IAM Secret Manager Fetch",
        statusCode: "MISSING BINDING",
        nodes: [
          { label: "Fintech API Client", sub: "POST /api/auth/token", icon: Key, type: "UPSTREAM" },
          { label: "Cloud Run Service", sub: "cyberpunk-ledger-dashboard", icon: Server, type: "TARGET" },
          { label: "Secret Manager", sub: "JWT_SECRET_KEY Secret", icon: Lock, type: "DOWNSTREAM", isError: true }
        ]
      };
    } else if (svc.includes("healthcare") || sum.includes("memoryerror") || sum.includes("oomkilled")) {
      return {
        protocol: "DICOM Binary Render",
        statusCode: "OOMKILLED (512MB)",
        nodes: [
          { label: "Hospital EMR Portal", sub: "GET /api/reports/mri-scan", icon: Activity, type: "UPSTREAM" },
          { label: "Cloud Run Service", sub: "healthcare-patient-portal", icon: Server, type: "TARGET" },
          { label: "Container Heap Buffer", sub: "534MB > 512MB Limit", icon: Cpu, type: "DOWNSTREAM", isError: true }
        ]
      };
    } else {
      return {
        protocol: "psycopg2 Connection Pool",
        statusCode: "POOL EXHAUSTED",
        nodes: [
          { label: "Fleet Mobile App", sub: "GET /api/fleet/status", icon: Truck, type: "UPSTREAM" },
          { label: "Cloud Run Service", sub: "realtime-logistics-tracker", icon: Server, type: "TARGET" },
          { label: "Cloud SQL Postgres", sub: "Max Connections (20)", icon: Database, type: "DOWNSTREAM", isError: true }
        ]
      };
    }
  };

  const flow = getFlowData();

  return (
    <div className={`mt-3.5 p-3.5 rounded-xl border transition-colors ${
      isLightMode ? 'bg-[#f8fafc] border-slate-300 font-mono text-xs' : 'bg-black/60 border-slate-800 font-mono text-xs'
    }`}>
      {/* Dynamic Flow Title & Protocol Indicator */}
      <div className="flex justify-between items-center pb-2.5 mb-3 border-b border-slate-200">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
          <span className="font-extrabold tracking-tight text-slate-900">
            Real-Time Log Dependency Flow Graph
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-200 text-slate-800 font-bold border border-slate-300">
            {flow.protocol}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold border border-rose-300">
            {flow.statusCode}
          </span>
        </div>
      </div>

      {/* Visual Flow Nodes */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 relative">
        {flow.nodes.map((node, idx) => {
          const NodeIcon = node.icon;
          return (
            <React.Fragment key={idx}>
              <div className={`flex-1 w-full p-3 rounded-xl border flex items-center space-x-3 transition-all ${
                isLightMode
                  ? node.isError
                    ? 'bg-rose-50 border-rose-300 text-slate-950 shadow-sm'
                    : 'bg-white border-slate-300 text-slate-950 shadow-sm'
                  : node.isError
                    ? 'bg-rose-950/60 border-rose-500/60 text-rose-200'
                    : 'bg-slate-900 border-slate-800 text-white'
              }`}>
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center border flex-shrink-0 ${
                  node.isError
                    ? 'bg-rose-100 text-rose-800 border-rose-300'
                    : 'bg-slate-100 text-slate-900 border-slate-300'
                }`}>
                  <NodeIcon className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-extrabold truncate">{node.label}</div>
                  <div className={`text-[10px] truncate ${node.isError ? 'text-rose-700 font-bold' : 'text-slate-600'}`}>
                    {node.sub}
                  </div>
                </div>
              </div>

              {idx < flow.nodes.length - 1 && (
                <div className="flex items-center justify-center px-1 text-slate-400">
                  <ArrowRight className="w-4 h-4 text-cyan-600 animate-pulse hidden sm:block" />
                  <span className="text-xs font-bold sm:hidden">↓</span>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
