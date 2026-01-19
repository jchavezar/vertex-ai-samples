"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  ChevronRight,
  BarChart3,
  Layout,
  CheckCircle2,
  Loader2,
  Image as ImageIcon,
  ExternalLink,
  ChevronLeft,
  X,
  Database,
  Cloud,
  Network
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const MODELS = [
  { id: "projects/vtxdemos/locations/global/publishers/google/models/gemini-3-pro-preview", label: "Gemini 3 Pro" },
  { id: "projects/vtxdemos/locations/global/publishers/google/models/gemini-3-flash-preview", label: "Gemini 3 Flash" },
  { id: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
  { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [extractorModel, setExtractorModel] = useState(MODELS[1].id); // Default Gemini 3 Flash
  const [supportingModel, setSupportingModel] = useState(MODELS[1].id);
  const [showWorkflow, setShowWorkflow] = useState(false);
  const [timer, setTimer] = useState(0);
  const [lastJobTime, setLastJobTime] = useState<number | null>(null);

  React.useEffect(() => {
    let interval: any;
    if (isUploading) {
      setTimer(0);
      interval = setInterval(() => {
        setTimer(prev => prev + 1);
      }, 1000);
    } else {
      if (timer > 0) setLastJobTime(timer);
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isUploading]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('extractor_model', extractorModel);
    formData.append('supporting_model', supportingModel);

    try {
      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setResults(data);
      setActivePageIndex(0);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to process PDF. Make sure the backend is running at localhost:8000');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 lg:p-16 max-w-7xl mx-auto">
      {/* Workflow Overlay */}
      <AnimatePresence>
        {showWorkflow && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-md"
            onClick={() => setShowWorkflow(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="glass-panel w-full max-w-4xl p-8 max-h-[90vh] overflow-y-auto relative"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowWorkflow(false)}
                className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
                <Network className="text-blue-500" />
                Advanced Agentic Workflow
              </h2>

              <div className="space-y-12 relative before:absolute before:left-6 before:top-4 before:bottom-4 before:w-0.5 before:bg-gradient-to-b before:from-blue-500 before:via-purple-500 before:to-transparent">
                {[
                  { title: "Multimodal Ingestion", desc: "PDF content is logically split into high-resolution images.", icon: <FileText className="text-blue-400" /> },
                  { title: "Parallel Extraction", desc: "For each page, an independent Gemini 3/2.5 agent is spawned to identify visual data structures.", icon: <Loader2 className="text-purple-400" /> },
                  { title: "Deep Visual Analytics", desc: "Gemini 3 Pro analyzes chart axes, legends, and data points, generating precise bounding boxes.", icon: <BarChart3 className="text-cyan-400" /> },
                  { title: "Cross-Agent Quality Evaluation", desc: "A separate Supporting Agent verifies confidence scores and summarizes the extraction fidelity.", icon: <CheckCircle2 className="text-green-400" /> },
                  { title: "Persistent Synthesis", desc: "Data is flattened and stored in BigQuery, while annotated artifacts are preserved in GCS.", icon: <Database className="text-amber-400" /> },
                ].map((step, i) => (
                  <div key={i} className="flex gap-6 items-start relative pl-4">
                    <div className="z-10 w-12 h-12 rounded-full bg-black border-2 border-blue-500/50 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
                      {step.icon}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{step.title}</h3>
                      <p className="text-gray-400 mt-1">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3 mb-4"
          >
            <div className="p-2 bg-blue-600 rounded-lg">
              <BarChart3 className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">ChartVision Pro</h1>
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-6"
          >
            Extract Intelligence from PDFs <br />with Gemini 3 Pro
          </motion.h2>
        </div>

        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowWorkflow(true)}
          className="px-6 py-3 rounded-xl border border-blue-500/30 bg-blue-500/10 text-blue-400 font-semibold flex items-center gap-2 hover:bg-blue-500/20 transition-all mb-4"
        >
          <Network className="w-5 h-5" />
          View Workflow Diagram
        </motion.button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Left Column: Upload & Config */}
        <div className="lg:col-span-5 space-y-6">
          <section className="glass-panel p-8 space-y-6">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Upload className="w-5 h-5 text-blue-400" />
              Configuration
            </h3>

            {/* Model Selectors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase">Extractor Model</label>
                <select
                  value={extractorModel}
                  onChange={(e) => setExtractorModel(e.target.value)}
                  className="w-full bg-black/40 border border-gray-700 rounded-lg p-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                >
                  {MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase">Supporting Agents</label>
                <select
                  value={supportingModel}
                  onChange={(e) => setSupportingModel(e.target.value)}
                  className="w-full bg-black/40 border border-gray-700 rounded-lg p-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                >
                  {MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
                </select>
              </div>
            </div>

            <div
              className={cn(
                "border-2 border-dashed border-gray-700 rounded-2xl p-10 transition-all cursor-pointer flex flex-col items-center gap-4 hover:border-blue-500/50 hover:bg-white/5",
                file && "border-blue-500/50 bg-blue-500/5"
              )}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                className="hidden"
                accept="application/pdf"
                onChange={onFileChange}
              />
              {file ? (
                <>
                  <FileText className="w-12 h-12 text-blue-400" />
                  <div className="text-center">
                    <p className="font-medium text-white">{file.name}</p>
                    <p className="text-sm text-gray-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="p-4 bg-gray-900 rounded-full">
                    <Upload className="w-8 h-8 text-gray-400" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium">Drop your PDF here</p>
                    <p className="text-sm text-gray-500">or click to browse files</p>
                  </div>
                </>
              )}
            </div>

            <button
              disabled={!file || isUploading}
              onClick={handleUpload}
              className={cn(
                "w-full py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all",
                file && !isUploading
                  ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20"
                  : "bg-gray-800 text-gray-500 cursor-not-allowed"
              )}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing... {timer}s
                </>
              ) : (
                <>
                  Analyze Workflow
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>

            {lastJobTime !== null && (
              <div className="flex items-center justify-center gap-2 text-xs text-gray-400 font-mono">
                <CheckCircle2 className="w-3 h-3 text-green-500" />
                Last Job: {lastJobTime}s
              </div>
            )}
          </section>

          {/* Persistence Links */}
          <AnimatePresence>
            {results && (
              <motion.section
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel p-6 space-y-4"
              >
                <h4 className="text-sm font-bold text-gray-500 uppercase flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  Persistence Status
                </h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg border border-gray-800">
                    <div className="flex items-center gap-3">
                      <Database className="text-orange-400 w-5 h-5" />
                      <div>
                        <p className="text-xs font-bold text-white">BigQuery</p>
                        <p className="text-[10px] text-gray-400">{results.bq_status}</p>
                      </div>
                    </div>
                    <a href={results.bq_link} target="_blank" className="p-2 hover:bg-white/10 rounded-lg">
                      <ExternalLink className="w-4 h-4 text-blue-400" />
                    </a>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-black/30 rounded-lg border border-gray-800">
                    <div className="flex items-center gap-3">
                      <Cloud className="text-blue-400 w-5 h-5" />
                      <div>
                        <p className="text-xs font-bold text-white">Cloud Storage</p>
                        <p className="text-[10px] text-gray-400">{results.gcs_urls[activePageIndex] || "Stored in GCS"}</p>
                      </div>
                    </div>
                    <a href={results.gcs_urls[activePageIndex]} target="_blank" className="p-2 hover:bg-white/10 rounded-lg">
                      <ExternalLink className="w-4 h-4 text-blue-400" />
                    </a>
                  </div>
                </div>
              </motion.section>
            )}
          </AnimatePresence>
        </div>

        {/* Right Column: Visualization */}
        <div className="lg:col-span-7">
          <AnimatePresence mode="wait">
            {!results && !isUploading && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex flex-col items-center justify-center border border-gray-800 rounded-3xl bg-white/[0.02] p-12 text-center"
              >
                <Layout className="w-16 h-16 text-gray-700 mb-6" />
                <h4 className="text-xl font-medium text-gray-500">No Analysis results yet</h4>
                <p className="text-gray-600 mt-2">Configure models and upload a PDF to begin.</p>
              </motion.div>
            )}

            {isUploading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full space-y-6"
              >
                <div className="aspect-[4/3] w-full rounded-3xl bg-gray-900 overflow-hidden relative border border-gray-800">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-shimmer" style={{ backgroundSize: '200% 100%' }} />
                  <div className="flex flex-col items-center justify-center h-full gap-4">
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                    <p className="text-gray-500 animate-pulse">Running Agentic Extractions...</p>
                  </div>
                </div>
              </motion.div>
            )}

            {results && (
              <motion.div
                key="results"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-8"
              >
                {/* Bounding Box Viewer */}
                <div className="relative group">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                      <ImageIcon className="w-5 h-5 text-purple-400" />
                      Visual Annotated Feed
                    </h3>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setActivePageIndex(prev => Math.max(0, prev - 1))}
                        disabled={activePageIndex === 0}
                        className="p-1 hover:bg-white/10 rounded disabled:opacity-30"
                      >
                        <ChevronLeft />
                      </button>
                      <span className="text-sm text-gray-400 font-mono">P{activePageIndex + 1} / {results.annotated_images.length}</span>
                      <button
                        onClick={() => setActivePageIndex(prev => Math.min(results.annotated_images.length - 1, prev + 1))}
                        disabled={activePageIndex === results.annotated_images.length - 1}
                        className="p-1 hover:bg-white/10 rounded disabled:opacity-30"
                      >
                        <ChevronRight />
                      </button>
                    </div>
                  </div>

                  <div className="rounded-2xl overflow-hidden border border-gray-700 bg-black/40 backdrop-blur-sm p-4">
                    <img
                      src={`http://localhost:8000${results.annotated_images[activePageIndex]}`}
                      alt="Annotated Result"
                      className="w-full h-auto object-contain rounded-lg shadow-2xl"
                    />
                  </div>
                </div>

                {/* Data Points */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[...results.results.charts, ...results.results.tables].map((item: any, i: number) => (
                    <div key={i} className="glass-panel p-6 border-l-4 border-l-blue-500 hover:bg-white/10 transition-colors">
                      <div className="flex justify-between items-start mb-4">
                        <span className="text-xs font-bold uppercase tracking-widest text-blue-400">
                          {item.chart_bounding_box ? "Chart" : "Table"} • P{item.page_number}
                        </span>
                        <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-300 text-[10px] font-bold">
                          {(item.confidence * 100).toFixed(0)}% Conf
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 line-clamp-3 mb-4">{item.description}</p>

                      {item.extracted_data && (
                        <div className="bg-black/40 rounded-lg p-3 overflow-x-auto border border-white/5 scrollbar-thin">
                          <table className="w-full text-[10px] min-w-[300px]">
                            <thead>
                              <tr className="border-b border-gray-800">
                                {item.extracted_data.headers.map((h: string, hi: number) => (
                                  <th key={hi} className="text-left py-2 px-2 text-gray-500 uppercase tracking-tighter break-words max-w-[120px]">{h}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {item.extracted_data.rows.slice(0, 5).map((row: any[], ri: number) => (
                                <tr key={ri} className="border-b border-white/5 last:border-0 hover:bg-white/10 transition-colors">
                                  {row.map((cell: any, ci: number) => (
                                    <td key={ci} className="py-2 px-2 text-gray-300 break-words max-w-[150px]">{cell}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {item.extracted_data.rows.length > 5 && (
                            <p className="text-[10px] text-gray-600 mt-2 text-center">+{item.extracted_data.rows.length - 5} additional rows</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <style jsx global>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite linear;
        }
      `}</style>
    </main>
  );
}
