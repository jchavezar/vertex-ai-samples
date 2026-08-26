import React, { useState } from 'react';
import type { ArtifactData } from '../types';
import { BarChart2 } from 'lucide-react';

interface InteractiveChartProps {
  artifact: ArtifactData;
}

const DEFAULT_COLORS = ['#0ea5e9', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export const InteractiveChart: React.FC<InteractiveChartProps> = ({ artifact }) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [activeDatasetIndex, setActiveDatasetIndex] = useState<number>(0);

  const labels = artifact.labels || ['Q1', 'Q2', 'Q3', 'Q4'];
  const datasets = artifact.datasets || [
    { label: 'Series A', data: [40, 65, 85, 110], color: '#0ea5e9' },
    { label: 'Series B', data: [35, 50, 60, 75], color: '#6366f1' },
  ];

  const chartType = artifact.chart_type || 'bar';

  // Compute scale
  const allValues = datasets.flatMap((d) => d.data);
  const maxVal = Math.max(...allValues, 10);
  const minVal = Math.min(...allValues, 0);
  const range = maxVal - minVal || 1;

  const width = 500;
  const height = 240;
  const padding = { top: 25, right: 20, bottom: 35, left: 50 };
  const graphWidth = width - padding.left - padding.right;
  const graphHeight = height - padding.top - padding.bottom;

  const getY = (val: number) => {
    const norm = (val - minVal) / range;
    return height - padding.bottom - norm * graphHeight;
  };

  const getX = (idx: number) => {
    if (labels.length <= 1) return padding.left + graphWidth / 2;
    return padding.left + (idx / (labels.length - 1)) * graphWidth;
  };

  return (
    <div className="space-y-4">
      {/* KPI Highlights Bar */}
      {artifact.kpi_highlights && artifact.kpi_highlights.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          {artifact.kpi_highlights.map((kpi, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between shadow-2xs min-w-0 overflow-hidden"
            >
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider truncate block">
                {kpi.label}
              </span>
              <div className="flex items-baseline justify-between mt-1 gap-1 min-w-0">
                <span className="text-sm sm:text-base font-bold text-slate-900 font-mono truncate">
                  {kpi.value}
                </span>
                {kpi.trend && (
                  <span className="text-[9px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 shrink-0 whitespace-nowrap">
                    {kpi.trend}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Chart Container */}
      <div className="p-3.5 rounded-xl border border-slate-200 bg-white shadow-xs space-y-3">
        {/* Title and Dataset Toggle */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
          <div>
            <h4 className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
              <BarChart2 className="w-3.5 h-3.5 text-cyan-600" />
              <span>{artifact.title}</span>
            </h4>
            {artifact.subtitle && (
              <p className="text-[11px] text-slate-500 mt-0.5">{artifact.subtitle}</p>
            )}
          </div>

          {/* Dataset Legend Pills */}
          <div className="flex items-center space-x-2 flex-wrap">
            {datasets.map((ds, idx) => {
              const color = ds.color || DEFAULT_COLORS[idx % DEFAULT_COLORS.length];
              return (
                <button
                  key={idx}
                  onClick={() => setActiveDatasetIndex(idx)}
                  className={`text-[10px] px-2 py-1 rounded-md font-medium border flex items-center space-x-1.5 transition-all cursor-pointer ${
                    activeDatasetIndex === idx
                      ? 'bg-slate-900 text-white border-slate-900 shadow-2xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span>{ds.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Chart SVG Visualizer */}
        <div className="relative w-full overflow-x-auto select-none">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="w-full h-auto max-h-64 overflow-visible"
          >
            {/* Horizontal Gridlines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
              const y = padding.top + pct * graphHeight;
              const val = maxVal - pct * range;
              return (
                <g key={i}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={width - padding.right}
                    y2={y}
                    stroke="#f1f5f9"
                    strokeWidth="1"
                    strokeDasharray={pct === 1 ? undefined : '3,3'}
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 3}
                    textAnchor="end"
                    fontSize="9"
                    fill="#94a3b8"
                    fontFamily="monospace"
                  >
                    {val >= 1000000
                      ? `$${(val / 1000000).toFixed(1)}M`
                      : val >= 1000
                      ? `$${(val / 1000).toFixed(0)}k`
                      : val.toFixed(0)}
                  </text>
                </g>
              );
            })}

            {/* X-Axis Category Labels */}
            {labels.map((label, idx) => {
              const x = chartType === 'bar'
                ? padding.left + (idx + 0.5) * (graphWidth / labels.length)
                : getX(idx);
              return (
                <text
                  key={idx}
                  x={x}
                  y={height - padding.bottom + 16}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#64748b"
                  fontWeight={hoveredIndex === idx ? '600' : '400'}
                >
                  {label}
                </text>
              );
            })}

            {/* Render BAR Chart */}
            {chartType === 'bar' && (
              <g>
                {labels.map((_, colIdx) => {
                  const colWidth = graphWidth / labels.length;
                  const groupWidth = colWidth * 0.75;
                  const barWidth = groupWidth / datasets.length;
                  const groupStartX = padding.left + colIdx * colWidth + (colWidth - groupWidth) / 2;

                  return (
                    <g key={colIdx} onMouseEnter={() => setHoveredIndex(colIdx)} onMouseLeave={() => setHoveredIndex(null)}>
                      {/* Column hover band */}
                      {hoveredIndex === colIdx && (
                        <rect
                          x={padding.left + colIdx * colWidth}
                          y={padding.top}
                          width={colWidth}
                          height={graphHeight}
                          fill="#f8fafc"
                          opacity="0.8"
                        />
                      )}

                      {datasets.map((ds, dsIdx) => {
                        const val = ds.data[colIdx] || 0;
                        const barX = groupStartX + dsIdx * barWidth;
                        const barY = getY(val);
                        const barH = height - padding.bottom - barY;
                        const color = ds.color || DEFAULT_COLORS[dsIdx % DEFAULT_COLORS.length];

                        return (
                          <rect
                            key={dsIdx}
                            x={barX + 2}
                            y={barY}
                            width={Math.max(barWidth - 4, 3)}
                            height={Math.max(barH, 2)}
                            rx="3"
                            fill={color}
                            opacity={hoveredIndex === colIdx ? 1 : 0.85}
                            className="transition-all duration-200 cursor-pointer"
                          />
                        );
                      })}
                    </g>
                  );
                })}
              </g>
            )}

            {/* Render LINE / AREA Chart */}
            {(chartType === 'line' || chartType === 'area') && (
              <g>
                {datasets.map((ds, dsIdx) => {
                  const color = ds.color || DEFAULT_COLORS[dsIdx % DEFAULT_COLORS.length];
                  const points = ds.data.map((val, idx) => `${getX(idx)},${getY(val)}`).join(' ');

                  const areaPath = `${points} ${getX(ds.data.length - 1)},${height - padding.bottom} ${getX(0)},${height - padding.bottom}`;

                  return (
                    <g key={dsIdx}>
                      {chartType === 'area' && (
                        <polygon
                          points={areaPath}
                          fill={color}
                          opacity={activeDatasetIndex === dsIdx ? '0.18' : '0.06'}
                        />
                      )}
                      <polyline
                        points={points}
                        fill="none"
                        stroke={color}
                        strokeWidth={activeDatasetIndex === dsIdx ? '2.5' : '1.5'}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      {ds.data.map((val, pIdx) => {
                        const cx = getX(pIdx);
                        const cy = getY(val);
                        return (
                          <circle
                            key={pIdx}
                            cx={cx}
                            cy={cy}
                            r={hoveredIndex === pIdx ? '4.5' : '3'}
                            fill="#ffffff"
                            stroke={color}
                            strokeWidth="2"
                            onMouseEnter={() => setHoveredIndex(pIdx)}
                            onMouseLeave={() => setHoveredIndex(null)}
                            className="transition-all cursor-pointer"
                          />
                        );
                      })}
                    </g>
                  );
                })}
              </g>
            )}
          </svg>

          {/* Interactive Tooltip Card */}
          {hoveredIndex !== null && (
            <div className="absolute top-2 right-2 bg-slate-900/90 backdrop-blur-md text-white px-2.5 py-1.5 rounded-lg shadow-lg text-[11px] font-mono border border-slate-700 pointer-events-none">
              <div className="text-slate-400 font-semibold mb-0.5">{labels[hoveredIndex]}</div>
              {datasets.map((ds, i) => (
                <div key={i} className="flex items-center justify-between space-x-3">
                  <span className="text-slate-300">{ds.label}:</span>
                  <span className="font-bold text-cyan-300">
                    ${(ds.data[hoveredIndex] || 0).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
