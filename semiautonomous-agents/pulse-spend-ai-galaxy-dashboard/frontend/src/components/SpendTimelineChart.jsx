import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function SpendTimelineChart({ data = [] }) {
  const labels = data.map(d => d.date);
  const grossData = data.map(d => d.gross_spent);
  const refundsData = data.map(d => d.refunds);
  const netData = data.map(d => d.net_spent);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Gross Spent ($)',
        data: grossData,
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.15)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#8b5cf6'
      },
      {
        label: 'Refunds / Credits ($)',
        data: refundsData,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: false,
        borderDash: [5, 5],
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#10b981'
      },
      {
        label: 'Net Spent ($)',
        data: netData,
        borderColor: '#06b6d4',
        backgroundColor: 'transparent',
        borderWidth: 2,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#06b6d4'
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#94a3b8',
          font: { size: 12, weight: '500' },
          usePointStyle: true,
          boxWidth: 8
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
        usePointStyle: true
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#64748b', font: { size: 11 } }
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
    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100">Daily Spending & Refund Timeline</h3>
          <p className="text-xs text-slate-400">Track daily gross purchases vs returned credits throughout July 2026</p>
        </div>
      </div>
      <div className="h-72 w-full">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}
