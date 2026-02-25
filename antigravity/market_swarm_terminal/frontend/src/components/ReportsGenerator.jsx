import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import {
  FileText,
  Sparkles,
  Download,
  TrendingUp,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Globe,
  Users,
  MessageSquare,
  AlertTriangle,
  Newspaper,
  ArrowRight,
  CheckCircle,
  Loader2,
  Printer
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const ReportsGenerator = ({
  setIsGeneratingReport,
  setReportSteps,
  setReportStatus,
  // Persistence Props
  ticker,
  setTicker,
  selectedTemplate,
  setSelectedTemplate,
  reportData,
  setReportData,
  progress,
  setProgress,
  progressStep,
  setProgressStep,
  stepsCompleted,
  setStepsCompleted,
  isGenerating
}) => {

  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [reportDate, setReportDate] = useState(new Date().toLocaleDateString());

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  // Mock template definitions
  const templates = [
    {
      id: 'company_primer',
      title: 'Company Primer',
      description: 'Comprehensive overview including financials, comps, ownership, and SWOT.',
      icon: FileText,
      sections: [
        'Company Overview',
        'Board Structure & Management',
        'Financials & Estimates',
        'Valuation Comps',
        'Price & Volume Chart',
        'Revenue Segments Chart',
        'Ownership Detail',
        'Geographic Revenue Chart',
        'Earnings Call Summary',
        'Sentiment & Themes',
        'Analyst Upgrades/Downgrades',
        'News & Broker Summaries',
        'SWOT Analysis'
      ]
    },
    {
      id: 'post_earnings',
      title: 'Post Earnings Recap',
      description: 'Deep dive into recent earnings, transcript analysis, and peer comparison.',
      icon: TrendingUp,
      sections: [
        'Stock Performance & Targets',
        'Security Explanation',
        'Transcript Summary',
        'Earnings Recap (Actual vs Consensus)',
        'Management Q&A',
        'Analyst Changes',
        'Peer Table',
        'Internal Research Note',
        'Surprise History',
        'Recent News',
        'Sentiment Change (Last 4 Calls)',
        'Gemini Insights'
      ]
    }
  ];

  // Detect unmount to prevent state updates on unmounted component
  const isMounted = React.useRef(true);
  useEffect(() => {
    isMounted.current = true;
    return () => { isMounted.current = false; };
  }, []);

  const handleGenerate = async () => {
    console.log("handleGenerate called", { ticker, selectedTemplate, isGenerating });
    if (!ticker || !selectedTemplate) {
      alert("Missing ticker or template");
      return;
    }

    if (setIsGeneratingReport) setIsGeneratingReport(true);
    if (setReportSteps) setReportSteps([]);
    if (setReportStatus) setReportStatus('Initializing report agent...');
    setReportData(null);
    setStepsCompleted([]);
    setProgressStep('Initializing report agent...');
    setProgress(5);

    try {
      console.log("Fetching report from backend...");
      const response = await fetch('http://127.0.0.1:8001/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker,
          templateId: selectedTemplate,
          session_id: "default_chat"
        })
      });

      console.log("Fetch response status:", response.status);

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Report generation failed: ${response.status} ${errText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const processLine = (line) => {
        if (!line.trim()) return;
        try {
          const event = JSON.parse(line);
          console.log("Event received:", event);
          if (event.type === 'status') {
            // Updates to parent state are safe even if unmounted
            setProgressStep(event.message);
            if (setReportStatus) setReportStatus(event.message);
            setStepsCompleted(prev => {
              // Store object with agent info for visualization
              const stepObj = { message: event.message, agent: event.agent || 'System' };
              const newSteps = [...prev, stepObj];
              if (setReportSteps) setReportSteps(newSteps);
              return newSteps;
            });
            if (isMounted.current) setProgress(prev => Math.min(prev + 8, 95));
          } else if (event.type === 'complete') {
            setReportData(event.data);
            if (isMounted.current) setProgress(100);
            if (setIsGeneratingReport) setIsGeneratingReport(false);
            if (setReportStatus) setReportStatus('Report Generation Complete');
          } else if (event.type === 'error') {
            console.error("Stream error:", event.message);
            setProgressStep(`Error: ${event.message}`);
            alert(`Stream Error: ${event.message}`);
            // Stop spinning on error
            if (setIsGeneratingReport) setIsGeneratingReport(false);
          }
        } catch (e) {
          console.error("JSON Parse Error", e, line);
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Keep incomplete line

        for (const line of lines) {
          processLine(line);
        }
      }

      if (buffer.trim()) processLine(buffer);

    } catch (err) {
      console.error("Report generation failed:", err);
      setProgressStep(`Failed: ${err.message}`);
      if (setIsGeneratingReport) setIsGeneratingReport(false);
    } finally {
      // FORCE stop spinner if we exited without 'complete' (e.g. network breakage)
      // but 'complete' event usually handles it.
      // This catch-all ensures we don't hang if the backend closes stream without 'complete'

      // We check if we have reportData; if not, and no error, maybe it just ended?
      // But let's trust the error/complete events to have set state if they arrived.
      // The main thing is to ensure loading state is FALSE eventually.
      if (setIsGeneratingReport) setIsGeneratingReport(false);

      if (!ticker) {
        setProgressStep('');
        if (isMounted.current) setProgress(0);
      }
    }
  };

  // Helper to render dynamic charts from [CHART] tags
  const ChartRenderer = ({ config }) => {
    if (!config || !config.data) return null;
    const { chartType, data, title } = config;

    // Detect X-Axis Key (structured feed uses 'label', legacy/historic uses 'date')
    // We default to 'label' if present, else 'date'.
    const xAxisKey = data.length > 0 && 'label' in data[0] ? 'label' : 'date';

    return (
      <div style={{ margin: '32px 0', padding: '24px', border: '1px solid #e0e0e0', borderRadius: '12px', background: '#fff', boxShadow: '0 4px 20px rgba(0,0,0,0.03)', pageBreakInside: 'avoid' }}>
        <h4 style={{ textAlign: 'center', marginBottom: '24px', fontSize: '15px', fontWeight: 800, fontFamily: 'sans-serif', color: '#333', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          {title || "Data Visualization"}
        </h4>
        <div style={{ width: '100%', height: 350 }}>
          <ResponsiveContainer>
            {chartType === 'line' || chartType === 'area' ? (
              <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0088FE" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0088FE" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00C49F" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00C49F" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis
                  dataKey={xAxisKey}
                  tick={{ fontSize: 10, fill: '#666' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e0e0e0' }}
                  minTickGap={30}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: '#666' }}
                  tickLine={false}
                  axisLine={false}
                  domain={['auto', 'auto']}
                  tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val.toFixed(1)}
                />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', fontSize: '12px' }}
                  itemStyle={{ fontWeight: 600 }}
                  labelStyle={{ color: '#888', marginBottom: '4px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#0088FE"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorValue)"
                  name="Price / Value"
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
                {data.length > 0 && data[0].close !== undefined && (
                  <Area
                    type="monotone"
                    dataKey="close"
                    stroke="#00C49F"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorClose)"
                    name="Close"
                  />
                )}
              </AreaChart>
            ) : chartType === 'pie' ? (
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={110}
                  innerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }} />
                <Legend layout="vertical" align="right" verticalAlign="middle" iconType="circle" />
              </PieChart>
            ) : (
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#666' }} tickLine={false} axisLine={{ stroke: '#e0e0e0' }} />
                <YAxis tick={{ fontSize: 10, fill: '#666' }} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: 'rgba(0,0,0,0.02)' }} contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }} />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="value" fill="url(#colorValue)" radius={[4, 4, 0, 0]} maxBarSize={50}>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  const CircularProgress = ({ size = 24, strokeWidth = 3, color = '#fff', progress = 0 }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const dashoffset = circumference - (progress / 100) * circumference;

    return (
      <div style={{ position: 'relative', width: size, height: size, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={dashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
          />
        </svg>
      </div>
    );
  };

  const handleDownloadPDF = async () => {
    const element = document.getElementById('report-preview-container');
    if (!element) return;

    setIsDownloadingPdf(true);
    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

      pdf.save(`${ticker}_${selectedTemplate}_Report.pdf`);
    } catch (err) {
      console.error("PDF generation failed:", err);
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', color: 'var(--text-primary)' }}>
      <div style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 800, background: 'var(--brand-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '12px' }}>
          AI Report Generator
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>
          Create professional, deep-dive investment memos and recaps in seconds.
        </p>
      </div>

      {!reportData ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          {/* Input Section */}
          <div style={{ gridColumn: '1 / -1', background: 'var(--bg-card)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border)', display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>Target Ticker</label>
              <input
                type="text"
                placeholder="e.g. AAPL, NVDA, TSLA"
                value={ticker}
                onChange={e => setTicker(e.target.value.toUpperCase())}
                style={{ width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', padding: '12px', borderRadius: '8px', color: 'var(--text-primary)', fontSize: '16px', fontWeight: 700, outline: 'none' }}
              />
            </div>
          </div>

          {/* Template Selection */}
          {templates.map(template => (
            <div
              key={template.id}
              onClick={() => setSelectedTemplate(template.id)}
              style={{
                background: selectedTemplate === template.id ? 'rgba(62, 166, 255, 0.1)' : 'var(--bg-card)',
                border: selectedTemplate === template.id ? '2px solid var(--brand)' : '1px solid var(--border)',
                borderRadius: '16px',
                padding: '24px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
                  <template.icon size={24} color="var(--brand)" />
                </div>
                {selectedTemplate === template.id && <CheckCircle size={24} color="var(--brand)" />}
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '8px' }}>{template.title}</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '20px' }}>
                {template.description}
              </p>
              <ul style={{ paddingLeft: '0', listStyle: 'none' }}>
                {template.sections.slice(0, 4).map((s, i) => (
                  <li key={i} style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--border)' }} />
                    {s}
                  </li>
                ))}
                <li style={{ fontSize: '11px', color: 'var(--brand)', marginTop: '8px', fontWeight: 600 }}>+ {template.sections.length - 4} more modules</li>
              </ul>
            </div>
          ))}

          {/* Generate Action */}
          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'center', marginTop: '12px' }}>
            <button
              onClick={handleGenerate}
              disabled={!ticker || !selectedTemplate || isGenerating}
              style={{
                background: 'var(--brand-gradient)',
                color: '#fff',
                border: 'none',
                padding: '16px 48px',
                borderRadius: '999px',
                fontSize: '16px',
                fontWeight: 800,
                cursor: (!ticker || !selectedTemplate || isGenerating) ? 'not-allowed' : 'pointer',
                opacity: (!ticker || !selectedTemplate || isGenerating) ? 0.5 : 1,
                boxShadow: '0 8px 24px rgba(62, 166, 255, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transition: 'transform 0.2s'
              }}
            >
              {isGenerating ? (
                <>
                  <CircularProgress size={20} strokeWidth={2} progress={progress} />
                  <span>{progressStep}</span>
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Generate Report
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* Report View */
        <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <button
              onClick={() => {
                setReportData(null);
                if (setIsGeneratingReport) setIsGeneratingReport(false);
                if (setReportStatus) setReportStatus('');
                if (setReportSteps) setReportSteps([]);
                setStepsCompleted([]);
                setProgress(0);
                setProgressStep('');
              }}
              style={{ background: 'transparent', border: '1px solid var(--border)', padding: '8px 16px', borderRadius: '8px', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <ArrowRight size={16} style={{ transform: 'rotate(180deg)' }} /> New Report
            </button>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => window.print()}
                style={{ background: 'transparent', border: '1px solid var(--border)', padding: '10px 20px', borderRadius: '999px', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Printer size={16} /> Print
              </button>
              <button
                onClick={handleDownloadPDF}
                disabled={isDownloadingPdf}
                style={{
                  background: isDownloadingPdf ? '#4b5563' : 'var(--brand)',
                  border: 'none',
                  padding: '10px 24px',
                  borderRadius: '999px',
                  color: '#fff',
                  cursor: isDownloadingPdf ? 'not-allowed' : 'pointer',
                  fontWeight: 800,
                  boxShadow: '0 4px 12px rgba(62,166,255,0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {isDownloadingPdf ? (
                  <>
                    <Loader2 size={16} className="spin" /> Generating PDF...
                  </>
                ) : (
                  <>
                    <Download size={16} /> Download PDF
                  </>
                )}
              </button>
            </div>
          </div>

          <div
            id="report-preview-container"
            style={{
              background: '#fff',
              color: '#000',
              padding: '60px',
              fontFamily: 'serif',
              borderRadius: '4px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              minHeight: '800px',
              border: '1px solid #e5e5e5'
            }}
          >
            <div style={{ borderBottom: '4px solid #000', paddingBottom: '20px', marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div>
                <h1 style={{ fontSize: '48px', fontWeight: 900, margin: 0, letterSpacing: '-1.5px', fontFamily: 'sans-serif', lineHeight: 1 }}>{reportData.ticker}</h1>
                <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#444', margin: '8px 0 0 0', fontFamily: 'sans-serif', letterSpacing: '-0.5px' }}>{reportData.title}</h2>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#666', fontFamily: 'sans-serif', letterSpacing: '0.5px' }}>Equity Research</div>
                <div style={{ fontWeight: 800, fontSize: '14px', fontFamily: 'sans-serif', margin: '4px 0' }}>FactSet Stock Terminal AI</div>
                <div style={{ fontSize: '12px', color: '#888', fontFamily: 'sans-serif' }}>{reportData.date || reportDate}</div>
              </div>
            </div>

            {/* Report Component Feed Layout */}
            <div className="report-content" style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '40px' }}>
              {(reportData.components || []).map((component, idx) => {
                // Determine layout span based on layout property
                let colSpan = 'span 12'; // Default full width
                if (component.layout === 'half') {
                  colSpan = 'span 6';
                }

                // Agent Badge Logic
                const renderAgentBadge = (source) => {
                  if (!source) return null;
                  let bg = '#eee';
                  let color = '#333';
                  let icon = null;
                  let label = source;

                  if (source === 'MarketResearcher') {
                    bg = '#EA4335'; // Google Red
                    color = '#fff';
                    label = 'G';
                    icon = <span style={{ fontFamily: 'sans-serif', fontWeight: 900 }}>G</span>;
                  } else if (source === 'DataExtractor') {
                    bg = '#0059b3'; // FactSet Blue
                    color = '#fff';
                    label = 'F';
                    icon = <span style={{ fontFamily: 'serif', fontWeight: 900 }}>F</span>;
                  } else if (source === 'Orchestrator') {
                    bg = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    color = '#fff';
                    label = 'AI';
                    icon = <Sparkles size={10} color="#fff" />;
                  }

                  return (
                    <div title={`Sourced by ${source}`} style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: bg,
                      color: color,
                      fontSize: '11px',
                      marginLeft: '10px',
                      verticalAlign: 'middle',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}>
                      {icon}
                    </div>
                  );
                };

                return (
                  <div
                    key={idx}
                    style={{
                      gridColumn: colSpan,
                      paddingBottom: '24px',
                      marginBottom: '24px',
                      borderBottom: component.type !== 'hero' ? '1px solid #eee' : 'none',
                      pageBreakInside: 'avoid'
                    }}
                  >
                    {/* Component Rendering Logic */}

                    {component.type === 'hero' && (
                      <div style={{ textAlign: 'center', margin: '40px 0' }}>
                        <h1 style={{ fontSize: '36px', fontWeight: 900 }}>
                          {component.title}
                          {renderAgentBadge(component.source)}
                        </h1>
                        <p style={{ fontSize: '18px', color: '#666' }}>{component.subtitle}</p>
                      </div>
                    )}

                    {component.type === 'chart' && (
                      <div style={{ position: 'relative' }}>
                        {/* We can overlay badge or put it in title */}
                        <div style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 10 }}>
                          {renderAgentBadge(component.source)}
                        </div>
                        <ChartRenderer config={component} />
                      </div>
                    )}

                    {component.type === 'text' && (
                      <div>
                        {component.title && (
                          <h3 style={{
                            fontSize: '14px',
                            fontWeight: 900,
                            textTransform: 'uppercase',
                            color: '#111',
                            marginBottom: '16px',
                            fontFamily: 'sans-serif',
                            borderLeft: '4px solid var(--brand)',
                            paddingLeft: '12px',
                            letterSpacing: '0.5px',
                            display: 'flex',
                            alignItems: 'center'
                          }}>
                            {component.title}
                            {renderAgentBadge(component.source)}
                          </h3>
                        )}
                        <div style={{ fontSize: '15px', lineHeight: '1.7', color: '#333' }}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              // LEGACY: Restore [CHART] tag parsing for text components
                              // This ensures valid markdown tables or legacy [CHART] tags still work
                              p: ({ node, children, ...props }) => {
                                const text = String(children);
                                // Check if this paragraph is a [CHART] block
                                // 1. Try strict JSON format [CHART]...[/CHART]
                                const strictMatch = text.match(/\[CHART\](.*?)\[\/CHART\]/s);
                                if (strictMatch) {
                                  try {
                                    const config = JSON.parse(strictMatch[1]);
                                    return <ChartRenderer config={config} />;
                                  } catch (e) {
                                    console.error("Failed to parse strict chart JSON", e);
                                  }
                                }

                                // 2. Try pipe-delimited format [CHART: Title | TYPE: Type | DATA_SUMMARY: {json}]
                                if (text.includes('[CHART:') && text.includes('DATA_SUMMARY:')) {
                                  try {
                                    const startIndex = text.indexOf('[CHART:') + 7;
                                    const endIndex = text.lastIndexOf(']');
                                    if (endIndex > startIndex) {
                                      const content = text.substring(startIndex, endIndex);
                                      const typeIndex = content.toLowerCase().indexOf('type:');
                                      const dataIndex = content.toLowerCase().indexOf('data_summary:');

                                      if (typeIndex !== -1 && dataIndex !== -1) {
                                        const title = content.substring(0, typeIndex).replace(/\|$/, '').trim();
                                        const typePart = content.substring(typeIndex, dataIndex);
                                        const chartType = typePart.split(':')[1].replace(/\|$/, '').trim().toLowerCase();
                                        let dataStr = content.substring(dataIndex + 'data_summary:'.length).trim();
                                        if (dataStr.endsWith('|')) dataStr = dataStr.slice(0, -1).trim();
                                        let dataJson = JSON.parse(dataStr);

                                        let chartData = [];
                                        if (Array.isArray(dataJson)) {
                                          chartData = dataJson;
                                        } else if (typeof dataJson === 'object') {
                                          let entries = Object.entries(dataJson);
                                          if (entries.length === 1 && typeof entries[0][1] === 'object' && !Array.isArray(entries[0][1])) {
                                            dataJson = entries[0][1];
                                          }
                                          chartData = Object.keys(dataJson).map(key => {
                                            const val = dataJson[key];
                                            if (typeof val === 'object') {
                                              return { date: key, ...val, value: val.PRICE || val.value || val.close };
                                            }
                                            return { date: key, value: val };
                                          });
                                        }

                                        const config = {
                                          title,
                                          chartType,
                                          data: chartData
                                        };
                                        return <ChartRenderer config={config} />;
                                      }
                                    }
                                  } catch (e) {
                                    console.error("Failed to parse pipe chart format", e);
                                  }
                                }

                                return <p style={{ marginBottom: '12px' }} {...props}>{children}</p>;
                              },
                              table: ({ node, ...props }) => (
                                <div style={{ overflowX: 'auto', margin: '24px 0', border: '1px solid #eee', borderRadius: '4px' }}>
                                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', fontFamily: 'sans-serif' }} {...props} />
                                </div>
                              ),
                              thead: ({ node, ...props }) => (
                                <thead style={{ background: '#f8f9fa', borderBottom: '2px solid #000' }} {...props} />
                              ),
                              th: ({ node, ...props }) => (
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 800, textTransform: 'uppercase', color: '#444', letterSpacing: '0.5px' }} {...props} />
                              ),
                              tbody: ({ node, ...props }) => (
                                <tbody style={{ background: '#fff' }} {...props} />
                              ),
                              tr: ({ node, ...props }) => (
                                <tr style={{ borderBottom: '1px solid #eee' }} {...props} />
                              ),
                              td: ({ node, ...props }) => (
                                <td style={{ padding: '12px 16px', color: '#111' }} {...props} />
                              ),
                            }}
                          >
                            {component.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Footer Disclaimer */}
            <div style={{ marginTop: '60px', paddingTop: '20px', borderTop: '1px solid #eee', fontSize: '10px', color: '#999', textAlign: 'center', fontStyle: 'italic', fontFamily: 'sans-serif' }}>
              This report is generated by AI (FactSet Stock Terminal) and is for informational purposes only. Not financial advice.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsGenerator;
