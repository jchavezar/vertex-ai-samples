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

interface PerformanceChartProps {
  ticker: string;
  externalData?: any;
  defaultData?: any;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ ticker, externalData, defaultData }) => {
  const isMultiSeries = externalData?.series && externalData.series.length > 0;

  const formatXAxis = (tickItem: any) => {
    if (!tickItem || typeof tickItem !== 'string') return tickItem;

    const match = tickItem.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (match) {
      const month = match[2];
      const day = match[3];

      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const monthLabel = monthNames[parseInt(month, 10) - 1];

      return `${monthLabel} ${day}`;
    }

    return tickItem;
  };

  const getLabelKey = (data: any[]) => {
    if (!data || data.length === 0) return 'label';
    const first = data[0];
    if ('label' in first) return 'label';
    if ('regionName' in first) return 'regionName';
    if ('countryName' in first) return 'countryName';
    return 'label';
  };

  const getValueKey = (data: any[]) => {
    if (!data || data.length === 0) return 'value';
    const first = data[0];
    if ('value' in first) return 'value';
    if ('regionRevenue' in first) return 'regionRevenue';
    if ('countryRevenue' in first) return 'countryRevenue';
    return 'value';
  };

  let chartData: any[] = [];
  let seriesConfig: any[] = [];

  const COLORS = ['#004b87', '#dc3545', '#28a745', '#ffc107', '#6f42c1'];

  if (isMultiSeries) {
    const allDates = new Set<string>();
    externalData.series.forEach((s: any) => {
      s.history.forEach((d: any) => allDates.add(d.date));
    });

    const sortedDates = Array.from(allDates).sort();

    if (sortedDates.length > 0) {
      chartData = sortedDates.map(date => {
        const row: any = { time: date };
        externalData.series.forEach((s: any, idx: number) => {
          if (s.history && Array.isArray(s.history)) {
            const point = s.history.find((p: any) => p.date === date);
            const key = `series_${idx}`;
            row[key] = point ? point.close : null;
          }
        });
        return row;
      });
    }

    if (externalData.series && Array.isArray(externalData.series)) {
      seriesConfig = externalData.series.map((s: any, idx: number) => ({
        key: `series_${idx}`,
        ticker: s.ticker,
        color: COLORS[idx % COLORS.length],
        history: s.history
      }));
    }
  } else if (!externalData?.chartType || externalData.chartType === 'line') {
    const activeData = (externalData?.history || externalData?.data || (Array.isArray(externalData) ? externalData : null)) || (defaultData?.history);

    if (!activeData && !defaultData) {
      chartData = [
        { time: '9:45', price: 288.10, sp500: 287.50 },
        { time: '10:00', price: 289.20, sp500: 288.00 },
      ];
    } else if (activeData && Array.isArray(activeData)) {
      chartData = activeData.map((d: any) => ({
        time: d.date || d.label || d.time,
        price: d.close || d.value || d.price,
        sp500: (d.close || d.value || d.price) * 0.98
      }));
    } else {
      console.warn("PerformanceChart: activeData is not an array", activeData);
      chartData = [
        { time: 'Data Error', price: 0, sp500: 0 }
      ];
    }
  }

  if (chartData.length === 0) {
    chartData = [
      { time: '9:45', price: 288.10, sp500: 287.50 },
    ];
  }

  return (
    <div className="card min-h-[400px]">
      <div className="flex items-center justify-between mb-3 text-[13px] uppercase tracking-wide text-[var(--text-secondary)]">
        <span>{externalData?.title || "Performance"} <span className="text-[var(--brand)] cursor-pointer">→</span></span>
        <div className="flex gap-2">
          {['1D', '1M', '6M', 'YTD'].map(period => (
            <span
              key={period}
              className={`text-[10px] px-1.5 py-0.5 rounded cursor-pointer transition-colors ${(externalData ? '1M' : '1D') === period
                  ? 'bg-blue-500/15 text-[var(--brand)] font-extrabold border border-blue-500/20'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
            >
              {period}
            </span>
          ))}
        </div>
      </div>

      <div className="flex gap-4 mb-3 text-[10px] text-[var(--text-secondary)]">
        {isMultiSeries && Array.isArray(seriesConfig) ? (
          seriesConfig.map(s => (
            <div key={s.key} className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full" style={{ background: s.color }}></span>
              {s.ticker}
            </div>
          ))
        ) : (
          <>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#3ea6ff]"></span>
              {externalData?.ticker || ticker || "Unknown"}
            </div>
            {!externalData && (
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#6ab04c]"></span>
                S&P 500
              </div>
            )}
          </>
        )}
      </div>

      <div className="h-[240px] w-full">
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
                {Array.isArray(externalData.data) && externalData.data.map((entry: any, index: number) => (
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
                domain={['dataMin', 'dataMax']}
                fontSize={10}
                tickLine={false}
                axisLine={false}
                tick={{ fill: '#8c959f' }}
                orientation="right"
              />
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
        <table className="w-full border-collapse mt-4 text-[10px]">
          <thead>
            <tr>
              <th className="text-left text-[var(--text-secondary)] font-normal p-1 border-b border-[var(--border-light)]"></th>
              {isMultiSeries && chartData.length > 0 && chartData.length <= 8 ? (
                chartData.map(d => <th key={d.time} className="text-right text-[var(--text-muted)] font-normal p-1 border-b border-[var(--border-light)]">{formatXAxis(d.time)}</th>)
              ) : (
                <>
                  {['1M%', '3M%', '6M%', 'YTD%', '1Y%'].map(h => (
                    <th key={h} className="text-right text-[var(--text-muted)] font-normal p-1 border-b border-[var(--border-light)]">{h}</th>
                  ))}
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {isMultiSeries ? (
              seriesConfig.map(s => {
                const first = s.history[0]?.close || 0;
                const last = s.history[s.history.length - 1]?.close || 0;
                const pct = first ? ((last - first) / first * 100).toFixed(2) : '0.00';

                return (
                  <tr key={s.key}>
                    <td className="text-left p-1.5 font-bold" style={{ color: s.color }}>{s.ticker}</td>
                    {isMultiSeries && chartData.length > 0 && chartData.length <= 8 ? (
                      chartData.map(d => {
                        const val = d[s.key];
                        return <td key={d.time} className="text-right p-1.5 font-bold">
                          {val ? (val > 10 ? `$${val.toFixed(2)}` : `${val.toFixed(2)}%`) : '-'}
                        </td>;
                      })
                    ) : (
                      <>
                        <td className={`text-right p-1.5 font-bold ${Number(pct) >= 0 ? "text-[var(--green)]" : "text-[var(--red)]"}`}>{pct}</td>
                        <td className="text-right p-1.5 font-bold">-</td>
                        <td className="text-right p-1.5 font-bold">-</td>
                        <td className="text-right p-1.5 font-bold">-</td>
                        <td className="text-right p-1.5 font-bold">-</td>
                      </>
                    )}
                  </tr>
                );
              })
            ) : (
              <tr>
                <td className="text-left p-1.5 font-bold text-[var(--text-primary)]">{externalData?.ticker || ticker || "Unknown"}</td>
                <td className="text-right p-1.5 font-bold text-[var(--red)]">-</td>
                <td className="text-right p-1.5 font-bold text-[var(--green)]">-</td>
                <td className="text-right p-1.5 font-bold text-[var(--red)]">-</td>
                <td className="text-right p-1.5 font-bold text-[var(--red)]">-</td>
                <td className="text-right p-1.5 font-bold text-[var(--red)]">-</td>
              </tr>
            )}
          </tbody>
        </table>
      ) : null}
    </div>
  );
};
