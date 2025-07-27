
import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto'; // Using auto import for Chart.js v3+
import { ChartData } from '../types';

interface ChartRendererProps {
  chartSpec: ChartData;
}

const DEFAULT_PALETTE = [
  '#FE7C8F', // Pinkish Red (Location A in image)
  '#42A5F5', // Bright Blue (Location B in image)
  '#FFD54F', // Soft Yellow (Location C in image)
  '#4DB6AC', // Muted Teal (Location D in image)
  '#BA68C8', // Light Purple (Location E in image)
  '#FFB74D', // Orange
  '#A1887F', // Brownish Grey
  '#90A4AE', // Blue Grey
];

export const ChartRenderer: React.FC<ChartRendererProps> = ({ chartSpec }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !chartSpec) return;

    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }
    
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) {
        console.error("Failed to get canvas context for chart.");
        return;
    }

    try {
        chartRef.current = new Chart(ctx, {
            type: chartSpec.type,
            data: {
                labels: chartSpec.labels,
                datasets: chartSpec.datasets.map((ds, datasetIndex) => {
                    let bgColors = ds.backgroundColor;
                    let borderColors = ds.borderColor;
                    let currentBorderWidth = ds.borderWidth;

                    if (chartSpec.type === 'bar') {
                        if (!bgColors) {
                            if (chartSpec.datasets.length === 1 && chartSpec.labels) {
                                 bgColors = chartSpec.labels.map((_, barIndex) => DEFAULT_PALETTE[barIndex % DEFAULT_PALETTE.length]);
                            } else {
                                bgColors = DEFAULT_PALETTE[datasetIndex % DEFAULT_PALETTE.length];
                            }
                        }
                        if (!borderColors) {
                            borderColors = 'rgba(0,0,0,0)'; 
                        }
                        currentBorderWidth = currentBorderWidth !== undefined ? currentBorderWidth : 0;

                    } else if (chartSpec.type === 'line') {
                        if (!bgColors) {
                            bgColors = DEFAULT_PALETTE[datasetIndex % DEFAULT_PALETTE.length];
                        }
                        if (!borderColors) {
                            borderColors = bgColors; 
                        }
                        currentBorderWidth = currentBorderWidth !== undefined ? currentBorderWidth : 2;
                        ds.tension = ds.tension !== undefined ? ds.tension : 0.1;

                    } else if (chartSpec.type === 'pie' || chartSpec.type === 'doughnut') {
                        if (!bgColors) {
                            bgColors = chartSpec.labels ? chartSpec.labels.map((_, sliceIndex) => DEFAULT_PALETTE[sliceIndex % DEFAULT_PALETTE.length]) : DEFAULT_PALETTE;
                        }
                        if (!borderColors) {
                            borderColors = '#FFFFFF'; 
                        }
                        currentBorderWidth = currentBorderWidth !== undefined ? currentBorderWidth : 1;
                    } else { 
                        if (!bgColors) {
                            bgColors = DEFAULT_PALETTE[datasetIndex % DEFAULT_PALETTE.length];
                        }
                        if (!borderColors) {
                            borderColors = bgColors;
                        }
                        currentBorderWidth = currentBorderWidth !== undefined ? currentBorderWidth : 1;
                    }

                    return {
                        ...ds,
                        backgroundColor: bgColors,
                        borderColor: borderColors,
                        borderWidth: currentBorderWidth,
                        fill: ds.fill !== undefined ? ds.fill : (chartSpec.type === 'line' ? false : undefined),
                    };
                }),
            },
            options: {
                responsive: true,
                maintainAspectRatio: true, 
                plugins: {
                    legend: {
                        position: 'top' as const,
                        align: 'end' as const,
                        labels: {
                            font: {
                                family: 'Inter, sans-serif',
                                size: 11,
                            },
                            color: 'rgb(var(--color-dj-text-primary))',
                            boxWidth: 15,
                            padding: 20,
                        }
                    },
                    title: {
                        display: !!chartSpec.title,
                        text: chartSpec.title || '',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 16,
                            weight: '600' as const,
                        },
                        color: 'rgb(var(--color-dj-text-primary))',
                        padding: {
                            top: 10,
                            bottom: 25
                        },
                        align: 'start' as const,
                    },
                    tooltip: {
                        titleFont: { family: 'Inter, sans-serif', size: 12, weight: '600' as const },
                        bodyFont: { family: 'Inter, sans-serif', size: 11 },
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#FFFFFF',
                        borderColor: 'rgba(0,0,0,0.1)',
                        borderWidth: 1,
                        padding: 10,
                        cornerRadius: 4,
                    }
                },
                scales: (chartSpec.type === 'bar' || chartSpec.type === 'line') ? {
                    y: {
                        beginAtZero: true,
                        ticks: { 
                            font: { family: 'Inter, sans-serif', size: 11 },
                            color: 'rgb(var(--color-dj-text-secondary))',
                            padding: 5,
                        },
                        grid: {
                          color: 'rgba(0, 0, 0, 0.25)', // Darker, solid horizontal grid lines
                          drawTicks: true,
                        },
                        border: {
                          display: false, // Hide the main Y-axis line
                        }
                    },
                    x: {
                        ticks: { 
                            font: { family: 'Inter, sans-serif', size: 11, weight: '500' as const },
                            color: 'rgb(var(--color-dj-text-primary))',
                            padding: 8,
                        },
                        grid: {
                          display: false, 
                        },
                        border: { 
                          display: true,
                          color: 'rgba(0, 0, 0, 0.25)' // Solid X-axis bottom line
                        }
                    }
                } : undefined, 
                ...chartSpec.options 
            }
        });
    } catch (error) {
        console.error("Error creating chart:", error, "with spec:", chartSpec);
    }

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [chartSpec]);

  if (!chartSpec || !chartSpec.labels || !chartSpec.datasets) {
    return <p className="text-sm text-dj-text-secondary p-4">Chart data is incomplete or unavailable.</p>;
  }

  return (
    <div className="relative w-full h-auto min-h-[250px] max-h-[450px] flex justify-center items-center">
      <canvas ref={canvasRef} aria-label={chartSpec.title || `Chart of type ${chartSpec.type}`} role="img"></canvas>
    </div>
  );
};
