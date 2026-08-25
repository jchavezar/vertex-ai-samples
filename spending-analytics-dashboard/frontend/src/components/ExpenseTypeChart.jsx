import React, { useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, getDatasetAtEvent, getElementAtEvent } from 'react-chartjs-2';
import { Orbit, Sparkles } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const MONARCH_COLORS = {
  'Shopping': { bg: 'rgba(236, 72, 153, 0.85)', hover: 'rgba(236, 72, 153, 1)' }, // Monarch Pink
  'Food & Dining': { bg: 'rgba(249, 115, 22, 0.85)', hover: 'rgba(249, 115, 22, 1)' }, // Monarch Orange
  'Travel & Transportation': { bg: 'rgba(14, 165, 233, 0.85)', hover: 'rgba(14, 165, 233, 1)' }, // Monarch Blue
  'Medical & Healthcare': { bg: 'rgba(16, 185, 129, 0.85)', hover: 'rgba(16, 185, 129, 1)' }, // Monarch Green
  'Housing & Utilities': { bg: 'rgba(234, 179, 8, 0.85)', hover: 'rgba(234, 179, 8, 1)' }, // Monarch Yellow / Gold
  'Subscriptions & Tech': { bg: 'rgba(99, 102, 241, 0.85)', hover: 'rgba(99, 102, 241, 1)' }, // Monarch Indigo
  'Entertainment & Recreation': { bg: 'rgba(217, 70, 239, 0.85)', hover: 'rgba(217, 70, 239, 1)' }, // Monarch Purple
  'Financial & Operations': { bg: 'rgba(100, 116, 139, 0.85)', hover: 'rgba(100, 116, 139, 1)' }, // Monarch Slate
};

const DEFAULT_COLOR_PALETTE = [
  'rgba(236, 72, 153, 0.85)',
  'rgba(249, 115, 22, 0.85)',
  'rgba(14, 165, 233, 0.85)',
  'rgba(16, 185, 129, 0.85)',
  'rgba(234, 179, 8, 0.85)',
  'rgba(99, 102, 241, 0.85)',
  'rgba(217, 70, 239, 0.85)',
  'rgba(100, 116, 139, 0.85)'
];

export default function ExpenseTypeChart({ data = [], onSelectCategory }) {
  const chartRef = useRef(null);
  const filtered = data.filter(d => d.expense_type !== 'Refunds & Credits' && d.expense_type !== 'Refund/Credit' && d.expense_type !== 'Refund');
  const labels = filtered.map(d => d.expense_type);
  const amounts = filtered.map(d => d.total_amount);

  const bgColors = labels.map((l, i) => MONARCH_COLORS[l]?.bg || DEFAULT_COLOR_PALETTE[i % DEFAULT_COLOR_PALETTE.length]);
  const hoverColors = labels.map((l, i) => MONARCH_COLORS[l]?.hover || DEFAULT_COLOR_PALETTE[i % DEFAULT_COLOR_PALETTE.length]);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Total Spent ($)',
        data: amounts,
        backgroundColor: bgColors,
        hoverBackgroundColor: hoverColors,
        borderRadius: 8,
        borderSkipped: false
      }
    ]
  };

  const handleBarClick = (event) => {
    if (!chartRef.current || !onSelectCategory) return;
    const elements = getElementAtEvent(chartRef.current, event);
    if (elements.length > 0) {
      const index = elements[0].index;
      const clickedCategory = labels[index];
      onSelectCategory(clickedCategory);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(139, 92, 246, 0.4)',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context) => ` Total Spent: $${context.raw.toLocaleString()}`,
          footer: () => `✨ Click bar to open Spend Galaxy constellation!`
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { 
          color: '#94a3b8', 
          font: { size: 10.5, weight: '600' },
          maxRotation: 20,
          minRotation: 0
        }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: {
          color: '#64748b',
          font: { size: 11 },
          callback: (value) => `$${value.toLocaleString()}`
        }
      }
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100">Monarch Category Architecture</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              Standard Taxonomy
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Categorized across Shopping, Housing & Utilities, Food & Dining, Travel, Healthcare</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <Orbit className="w-4 h-4 text-indigo-400" />
          <span className="hidden sm:inline">Click bar for Constellation</span>
        </div>
      </div>

      <div className="h-64 w-full cursor-pointer">
        <Bar ref={chartRef} data={chartData} options={options} onClick={handleBarClick} />
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/60 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
        {filtered.slice(0, 4).map((item, idx) => (
          <div 
            key={item.expense_type}
            onClick={() => onSelectCategory && onSelectCategory(item.expense_type)}
            className="p-2 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-indigo-500/40 transition-all cursor-pointer"
          >
            <span className="text-[10px] text-slate-400 block truncate font-medium">{item.expense_type}</span>
            <span className="font-mono font-bold text-slate-200 block text-xs mt-0.5">${item.total_amount.toLocaleString()}</span>
            <span className="text-[9px] text-indigo-400 font-semibold">{item.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
