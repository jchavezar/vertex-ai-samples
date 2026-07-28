import React, { useRef } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut, getElementAtEvent } from 'react-chartjs-2';
import { Orbit } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function CategoryBreakdownChart({ data = [], onSelectCategory }) {
  const chartRef = useRef(null);
  const categories = data.filter(d => d.primary_category !== 'Refund & Credit');
  const labels = categories.map(c => c.primary_category);
  const amounts = categories.map(c => c.total_amount);

  const colors = [
    '#8b5cf6', // Violet
    '#06b6d4', // Cyan
    '#f43f5e', // Rose
    '#10b981', // Emerald
    '#f59e0b', // Amber
    '#3b82f6', // Blue
    '#ec4899', // Pink
    '#6366f1'  // Indigo
  ];

  const chartData = {
    labels,
    datasets: [
      {
        data: amounts,
        backgroundColor: colors.slice(0, labels.length),
        borderColor: 'rgba(15, 23, 42, 0.8)',
        borderWidth: 2,
        hoverOffset: 8
      }
    ]
  };

  const handleDoughnutClick = (event) => {
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
      legend: {
        position: 'right',
        labels: {
          color: '#cbd5e1',
          font: { size: 11, weight: '500' },
          usePointStyle: true,
          boxWidth: 8,
          padding: 12
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(6, 182, 212, 0.4)',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context) => {
            const item = categories[context.dataIndex];
            return ` ${context.label}: $${context.raw.toLocaleString()} (${item.percentage}%)`;
          },
          footer: () => `✨ Click segment to explore Spend Galaxy!`
        }
      }
    },
    cutout: '68%'
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100">AI Category Distribution</h3>
          <p className="text-xs text-slate-400">Share of spending by primary categories</p>
        </div>

        {onSelectCategory && (
          <button
            onClick={() => onSelectCategory(labels[0] || 'Dining & Food Delivery')}
            className="p-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/20 transition-all cursor-pointer"
            title="Explore Spend Galaxy"
          >
            <Orbit className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="h-64 w-full flex items-center justify-center cursor-pointer">
        <Doughnut ref={chartRef} data={chartData} options={options} onClick={handleDoughnutClick} />
      </div>
    </div>
  );
}
