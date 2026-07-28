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

export default function ExpenseTypeChart({ data = [], onSelectCategory }) {
  const chartRef = useRef(null);
  const filtered = data.filter(d => d.expense_type !== 'Refund/Credit');
  const labels = filtered.map(d => d.expense_type);
  const amounts = filtered.map(d => d.total_amount);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Total Spent ($)',
        data: amounts,
        backgroundColor: [
          'rgba(139, 92, 246, 0.85)', // Violet (Lifestyle/Luxury)
          'rgba(6, 182, 212, 0.85)',  // Cyan (Food & Dining)
          'rgba(16, 185, 129, 0.85)', // Emerald (Essential)
          'rgba(245, 158, 11, 0.85)', // Amber (Subscription)
          'rgba(59, 130, 246, 0.85)', // Blue (Travel)
          'rgba(236, 72, 153, 0.85)'  // Pink (Healthcare)
        ],
        hoverBackgroundColor: [
          'rgba(139, 92, 246, 1)',
          'rgba(6, 182, 212, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(236, 72, 153, 1)'
        ],
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
        ticks: { color: '#94a3b8', font: { size: 11, weight: '500' } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: {
          color: '#64748b',
          font: { size: 11 },
          callback: (value) => `$${value}`
        }
      }
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100">Expense Intent & Behavioral Breakdown</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
              Interactive
            </span>
          </div>
          <p className="text-xs text-slate-400">Classifying spending into Luxury, Dining, Essentials, Subscriptions & Travel</p>
        </div>

        {onSelectCategory && (
          <button
            onClick={() => onSelectCategory(labels[0] || 'Essential')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-violet-600/30 to-indigo-600/30 hover:from-violet-600/50 hover:to-indigo-600/50 border border-violet-500/40 text-violet-200 text-xs font-semibold shadow-md transition-all cursor-pointer"
          >
            <Orbit className="w-4 h-4 text-violet-400 animate-spin" />
            Explore Galaxy
          </button>
        )}
      </div>

      <div className="h-64 w-full cursor-pointer">
        <Bar ref={chartRef} data={chartData} options={options} onClick={handleBarClick} />
      </div>
    </div>
  );
}
