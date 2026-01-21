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
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const PerformanceChart = ({ ticker, externalData, defaultData }) => {
  const isMultiSeries = externalData?.series && externalData.series.length > 0;

  const formatXAxis = (tickItem) => {
    if (!tickItem || typeof tickItem !== 'string') return tickItem;

    // If it's a full ISO date YYYY-MM-DD
    const match = tickItem.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (match) {
      const year = match[1];
      const month = match[2];
      const day = match[3];

      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const monthLabel = monthNames[parseInt(month, 10) - 1];

      // Just show "Month Day" for most cases, add 'YY if it's a multi-year view
      // Since we don't know the range here, we'll stick to a clean "Month DD"
      return `${monthLabel} ${day}`;
    }

    // If it's already a short string like "Jan 16", pass it through
    return tickItem;
  };

  const getLabelKey = (data) => {
    if (!data || data.length === 0) return 'label';
    const first = data[0];
    if ('label' in first) return 'label';
    if ('regionName' in first) return 'regionName';
    if ('countryName' in first) return 'countryName';
    return 'label';
  };

  const getValueKey = (data) => {
    if (!data || data.length === 0) return 'value';
    const first = data[0];
    if ('value' in first) return 'value';
    if ('regionRevenue' in first) return 'regionRevenue';
    if ('countryRevenue' in first) return 'countryRevenue';
    return 'value';
  };

  let chartData = [];
  let seriesConfig = [];

  const COLORS = ['#004b87', '#dc3545', '#28a745', '#ffc107', '#6f42c1'];

  if (isMultiSeries) {
    // 1. Collect all unique dates
    const allDates = new Set();
    externalData.series.forEach(s => {
      s.history.forEach(d => allDates.add(d.date));
    });

    // 2. Sort dates
    const sortedDates = Array.from(allDates).sort();

    // 3. Build data rows
    if (sortedDates.length > 0) {
      chartData = sortedDates.map(date => {
        const row = { time: date };
        externalData.series.forEach((s, idx) => {
          if (s.history && Array.isArray(s.history)) {
            const point = s.history.find(p => p.date === date);
            const key = `series_${idx}`;
            row[key] = point ? point.close : null;
          }
        });
        return row;
      });
    }

    // 4. Build series config once
    if (externalData.series && Array.isArray(externalData.series)) {
      seriesConfig = externalData.series.map((s, idx) => ({
        key: `series_${idx}`,
        ticker: s.ticker,
        color: COLORS[idx % COLORS.length],
        history: s.history
      }));
    }
  } else if (!externalData?.chartType || externalData.chartType === 'line') {
    // Legacy Single Mode - ONLY for Line Charts
    // Normalize data: support .history (Standard) or .data (Simplified from LLM)
    const activeData = (externalData?.history || externalData?.data || (Array.isArray(externalData) ? externalData : null)) || (defaultData?.history);

    if (!activeData && !defaultData) {
      // Fallback dummy
      chartData = [
        { time: '9:45', price: 288.10, sp500: 287.50 },
        { time: '10:00', price: 289.20, sp500: 288.00 },
      ];
    } else if (activeData && Array.isArray(activeData)) {
      chartData = activeData.map(d => ({
        time: d.date || d.label || d.time,
        price: d.close || d.value || d.price,
        sp500: (d.close || d.value || d.price) * 0.98  // Fake S&P relative for demo
      }));
    } else {
      // If it's not an array, it might be an error or malformed data
      console.warn("PerformanceChart: activeData is not an array", activeData);
      chartData = [
        { time: 'Data Error', price: 0, sp500: 0 }
      ];
    }
  }

  // If we defaulted (no data), use the original fallback logic (omitted here for space, assuming it's acceptable)
  if (chartData.length === 0) {
    chartData = [
      { time: '9:45', price: 288.10, sp500: 287.50 },
    ];
  }
  return (
    <div className="card chart-container">
      <div className="section-title">

        <span>{externalData?.title || "Performance"} <span style={{ color: 'var(--brand)', cursor: 'pointer' }}>→</span></span>
        <div className="chart-controls">
          <span className="control active">{externalData ? '1M' : '1D'}</span>
          <span className="control">1M</span>
          <span className="control">6M</span>
          <span className="control">YTD</span>
        </div>
      </div>

      <div className="chart-legend">
        {isMultiSeries && Array.isArray(seriesConfig) ? (
          seriesConfig.map(s => (
            <div key={s.key} className="legend-item"><span className="dot" style={{ background: s.color }}></span> {s.ticker}</div>
          ))
        ) : (
          <>
              <div className="legend-item"><span className="dot" style={{ background: '#3ea6ff' }}></span> {externalData?.ticker || ticker || "Unknown"}</div>
            {!externalData && <div className="legend-item"><span className="dot" style={{ background: '#6ab04c' }}></span> S&P 500</div>}
          </>
        )}
      </div>

      <div style={{ height: 240, width: '100%' }}>
        <ResponsiveContainer>
          {externalData?.chartType === 'bar' && Array.isArray(externalData.data) ? (
            <BarChart
              layout="vertical"
              data={externalData.data}
              margin={{ top: 10, right: 30, left: 10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
              <XAxis type="number" fontSize={10} tick={{ fill: '#8c959f' }} />
              <YAxis
                type="category"
                dataKey={getLabelKey(externalData.data)}
                fontSize={10}
                tick={{ fill: '#8c959f' }}
                width={120}
              />
              <Tooltip
                cursor={{ fill: 'transparent' }}
                contentStyle={{
                  fontSize: 11,
                  borderRadius: 12,
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  backdropFilter: 'var(--card-blur)',
                  color: 'var(--text-primary)'
                }}
              />
              <Bar dataKey={getValueKey(externalData.data)} fill="var(--brand)" radius={[0, 999, 999, 0]} barSize={20} />
            </BarChart>
          ) : externalData?.chartType === 'pie' && Array.isArray(externalData.data) ? (
            <PieChart margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <Pie
                data={externalData.data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                  dataKey={getValueKey(externalData.data)}
              >
                  {Array.isArray(externalData.data) && externalData.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
                <Tooltip contentStyle={{
                  fontSize: 11,
                  borderRadius: 12,
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  backdropFilter: 'var(--card-blur)',
                  color: 'var(--text-primary)'
                }} />
                <Legend verticalAlign="middle" align="right" layout="vertical" iconType="circle" wrapperStyle={{ fontSize: '10px', color: 'var(--text-secondary)' }} />
            </PieChart>
          ) : (
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--brand)" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="var(--brand)" stopOpacity={0} />
              </linearGradient>
            </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
            <XAxis
              dataKey="time"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#8c959f' }}
                    tickFormatter={formatXAxis}
            />
            <YAxis
                    yAxisId="price"
                    domain={['auto', 'auto']}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#8c959f' }}
              orientation="right"
            />
                  {/* Secondary Axis for Volume */}
                  <YAxis
                    yAxisId="volume"
                    domain={['auto', 'auto']}
                    orientation="left"
                    hide={true}
                  />
            <Tooltip
                    contentStyle={{
                      fontSize: 11,
                      borderRadius: 12,
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border)',
                      backdropFilter: 'var(--card-blur)',
                      color: 'var(--text-primary)'
                    }}
            />

                  {isMultiSeries && Array.isArray(seriesConfig) ? (
                    seriesConfig.map(s => {
                      const isVolume = s.ticker.toLowerCase().includes('volume');
                      return (
                        <Line
                          key={s.key}
                    yAxisId={isVolume ? "volume" : "price"}
                    name={s.ticker}
                    type="monotone"
                    dataKey={s.key}
                    stroke={s.color}
                    strokeWidth={isVolume ? 1 : 2}
                    dot={false}
                    strokeDasharray={isVolume ? "3 3" : undefined}
                  />
                );
              })
                  ) : (
                    <>
                      <Area
                          yAxisId="price"
                          type="monotone"
                          dataKey="price"
                          stroke="var(--brand)"
                          strokeWidth={3}
                          fillOpacity={1}
                          fill="url(#colorPrice)"
                        />
                        {!externalData && (
                          <Line
                            yAxisId="price"
                          type="monotone"
                          dataKey="sp500"
                          stroke="#6ab04c"
                          strokeWidth={1}
                          dot={false}
                          strokeDasharray="5 5"
                        />
                      )}
                    </>
                  )}
          </AreaChart>
          )}
        </ResponsiveContainer>
      </div>

      {!externalData?.chartType || externalData.chartType === 'line' ? (
      <table className="compact-performance-table">
        <thead>
          <tr>
            <th></th>
              {isMultiSeries && chartData.length > 0 && chartData.length <= 8 ? (
                chartData.map(d => <th key={d.time}>{formatXAxis(d.time)}</th>)
              ) : (
                <>
                    <th>1M%</th>
                    <th>3M%</th>
                    <th>6M%</th>
                    <th>YTD%</th>
                    <th>1Y%</th>
                </>
              )}
          </tr>
        </thead>
        <tbody>
            {isMultiSeries ? (
              seriesConfig.map(s => {
                const closes = s.history.map(p => p.close);
                const first = s.history[0]?.close || 0;
                const last = s.history[s.history.length - 1]?.close || 0;
                const pct = first ? ((last - first) / first * 100).toFixed(2) : '0.00';

                return (
                  <tr key={s.key}>
                    <td style={{ color: s.color, fontWeight: 'bold' }}>{s.ticker}</td>
                    {isMultiSeries && chartData.length > 0 && chartData.length <= 8 ? (
                      chartData.map(d => {
                        const val = d[s.key];
                        return <td key={d.time} style={{ fontSize: '10px' }}>
                          {val ? (val > 10 ? `$${val.toFixed(2)}` : `${val.toFixed(2)}%`) : '-'}
                        </td>;
                      })
                    ) : (
                      <>
                          <td className={Number(pct) >= 0 ? "text-up" : "text-down"}>{pct}</td>
                          <td>-</td>
                          <td>-</td>
                          <td>-</td>
                          <td>-</td>
                      </>
                    )}
                  </tr>
                );
              })
            ) : (
                <tr>
                  <td>{externalData?.ticker || ticker || "Unknown"}</td>
                  <td className="text-down">-</td>
                  <td className="text-up">-</td>
                  <td className="text-down">-</td>
                  <td className="text-down">-</td>
                  <td className="text-down">-</td>
                </tr>
            )}
        </tbody>
      </table>
      ) : null}

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
          background: rgba(62, 166, 255, 0.15);
          color: var(--brand);
          font-weight: 800;
          border: 1px solid rgba(62, 166, 255, 0.2);
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
