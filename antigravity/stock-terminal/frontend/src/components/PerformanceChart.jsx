import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const PerformanceChart = ({ ticker, externalData }) => {
  const chartData = externalData?.history?.map(d => ({
    time: d.date,
    price: d.close,
    sp500: d.close * 0.98
  })) || [
      { time: '9:45', price: 288.10, sp500: 287.50 },
      { time: '10:00', price: 289.20, sp500: 288.00 },
      { time: '10:15', price: 288.50, sp500: 288.20 },
      { time: '10:30', price: 287.80, sp500: 288.50 },
      { time: '10:45', price: 286.90, sp500: 287.80 },
      { time: '11:00', price: 287.40, sp500: 288.10 },
      { time: '11:15', price: 288.10, sp500: 288.40 },
      { time: '11:30', price: 289.30, sp500: 289.00 },
      { time: '11:45', price: 290.50, sp500: 289.50 },
      { time: '12:00', price: 291.20, sp500: 290.10 },
      { time: '12:15', price: 290.80, sp500: 290.50 },
      { time: '12:30', price: 289.50, sp500: 290.80 },
      { time: '12:45', price: 288.48, sp500: 290.20 },
    ];

  return (
    <div className="card chart-container">
      <div className="section-title">
        <span>Performance <span style={{ color: '#004b87', cursor: 'pointer' }}>→</span></span>
        <div className="chart-controls">
          <span className="control active">{externalData ? '1M' : '1D'}</span>
          <span className="control">1M</span>
          <span className="control">6M</span>
          <span className="control">YTD</span>
        </div>
      </div>

      <div className="chart-legend">
        <div className="legend-item"><span className="dot" style={{ background: '#004b87' }}></span> {ticker}</div>
        <div className="legend-item"><span className="dot" style={{ background: '#6ab04c' }}></span> S&P 500</div>
      </div>

      <div style={{ height: 240, width: '100%' }}>
        <ResponsiveContainer>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#004b87" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#004b87" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis
              dataKey="time"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#8c959f' }}
            />
            <YAxis
              domain={['dataMin - 1', 'dataMax + 1']}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#8c959f' }}
              orientation="right"
            />
            <Tooltip
              contentStyle={{ fontSize: 11, borderRadius: 4, border: '1px solid #d1d9e0' }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#004b87"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorPrice)"
            />
            <Line
              type="monotone"
              dataKey="sp500"
              stroke="#6ab04c"
              strokeWidth={1}
              dot={false}
              strokeDasharray="5 5"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <table className="compact-performance-table">
        <thead>
          <tr>
            <th></th>
            <th>1M%</th>
            <th>3M%</th>
            <th>6M%</th>
            <th>YTD%</th>
            <th>1Y%</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>FDS-US</td>
            <td className="text-down">-1.36</td>
            <td className="text-up">0.87</td>
            <td className="text-down">-35.35</td>
            <td className="text-down">-0.59</td>
            <td className="text-down">-36.58</td>
          </tr>
          <tr>
            <td>S&P 500</td>
            <td className="text-up">1.95</td>
            <td className="text-up">4.59</td>
            <td className="text-up">11.19</td>
            <td className="text-up">1.68</td>
            <td className="text-up">19.26</td>
          </tr>
        </tbody>
      </table>

      <style jsx="true">{`
        .chart-container {
          min-height: 400px;
        }
        .chart-controls {
          display: flex;
          gap: 8px;
        }
        .control {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 2px;
          cursor: pointer;
          color: var(--text-secondary);
        }
        .control.active {
          background: #e6f0ff;
          color: #004b87;
          font-weight: 700;
        }
        .chart-legend {
          display: flex;
          gap: 16px;
          margin-bottom: 12px;
          font-size: 10px;
          color: var(--text-secondary);
        }
        .legend-item {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        .compact-performance-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 16px;
          font-size: 10px;
        }
        .compact-performance-table th {
          text-align: right;
          color: var(--text-muted);
          padding: 4px;
          border-bottom: 1px solid var(--border-light);
        }
        .compact-performance-table td {
          text-align: right;
          padding: 6px 4px;
          font-weight: 600;
        }
        .compact-performance-table td:first-child {
          text-align: left;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
};

export default PerformanceChart;
