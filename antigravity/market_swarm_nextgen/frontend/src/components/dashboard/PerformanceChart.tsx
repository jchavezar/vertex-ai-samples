import React from 'react';
import {
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
    if (typeof tickItem === 'number') {
      if (Math.abs(tickItem) >= 1.0e+12) return (tickItem / 1.0e+12).toFixed(1) + "T";
      if (Math.abs(tickItem) >= 1.0e+9) return (tickItem / 1.0e+9).toFixed(1) + "B";
      if (Math.abs(tickItem) >= 1.0e+6) return (tickItem / 1.0e+6).toFixed(1) + "M";
      if (Math.abs(tickItem) >= 1.0e+3) return (tickItem / 1.0e+3).toFixed(1) + "K";
      return tickItem;
    }

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

  const getValueKeys = (data: any[]) => {
    if (!data || data.length === 0) return ['value'];
    const first = data[0];
    const keys = Object.keys(first);

    // Filter for numeric keys that aren't common metadata or ID keys
    const numericKeys = keys.filter(k =>
      typeof first[k] === 'number' &&
      !['fiscalYear', 'fiscalPeriod', 'relativePeriod', 'estimateCount', 'up', 'down', 'isNormalized'].includes(k)
    );

    if (numericKeys.length > 0) return numericKeys;
    return ['value'];
  };

  const getValueKey = (data: any[]) => {
    return getValueKeys(data)[0];
  };

  const getLabelKey = (data: any[]) => {
    if (!data || data.length === 0) return 'label';
    const first = data[0];

    // Priority keys
    if ('category' in first) return 'category';
    if ('label' in first) return 'label';
    if ('ticker' in first) return 'ticker';
    if ('company' in first) return 'company';
    if ('name' in first) return 'name';
    if ('regionName' in first) return 'regionName';
    if ('countryName' in first) return 'countryName';

    // Fallback: first string key
    const keys = Object.keys(first);
    const stringKey = keys.find(k => typeof first[k] === 'string');
    return stringKey || keys[0] || 'label';
  };

  /**
   * Smart Pivot: If the data is "flat" (e.g. multiple rows for the same entity with different metrics),
   * this groups them so Recharts can render grouped bars.
   */
  const pivotData = (data: any[]) => {
    if (!data || data.length === 0) return data;

    // If it already has multiple numeric keys, it's likely already pivoted
    if (getValueKeys(data).length > 1) return data;

    const labelKey = getLabelKey(data);
    const valueKey = getValueKeys(data)[0];

    // Check if labels follow a "Category - Metric" or "Metric - Category" pattern
    // This is a heuristic to group items like "GOOGL Rev", "GOOGL NI" into a "GOOGL" category.
    const groups: { [key: string]: any } = {};

    data.forEach(item => {
      const fullLabel = String(item[labelKey]);
      // Search for common delimiters or split points
      // Tickers are usually uppercase 1-5 chars
      const tickerMatch = fullLabel.match(/^([A-Z]{1,5})\b/);
      const category = tickerMatch ? tickerMatch[1] : fullLabel;
      const metric = tickerMatch ? fullLabel.replace(category, "").trim() : valueKey;

      if (!groups[category]) {
        groups[category] = { [labelKey]: category, category };
      }

      const cleanMetric = metric || valueKey;
      groups[category][cleanMetric] = item[valueKey];
    });

    return Object.values(groups);
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
      // Normalize to % change if S&P 500 data is present (Real Data Mode)
      // Check if we have real S&P 500 data
      const hasRealSp500 = activeData.some((d: any) => d.sp500_close !== undefined);

      let basePrice = activeData[0]?.close || activeData[0]?.value || activeData[0]?.price || 1;
      let baseSp500 = activeData[0]?.sp500_close || 1;

      // If we are showing real comparison, we normalize to 0% start
      // If just price, we show price.
      // But user requested "Performance" which usually implies comparison.
      // Let's assume if we have sp500 data, we do % comparison.

      chartData = activeData.map((d: any) => {
        const rawPrice = d.close || d.value || d.price;
        const rawSp500 = d.sp500_close;

        let priceVal = rawPrice;
        let sp500Val = null;

        if (hasRealSp500 && rawSp500) {
          // Normalized
          priceVal = ((rawPrice - basePrice) / basePrice) * 100;
          sp500Val = ((rawSp500 - baseSp500) / baseSp500) * 100;
        }

        return {
          time: d.date || d.label || d.time,
          price: priceVal,
          sp500: sp500Val,
          isNormalized: hasRealSp500,
          originalPrice: rawPrice
        };
      });
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

  const isNormalized = chartData.length > 0 && chartData[0].isNormalized;

  return (
    <div className="h-full flex flex-col">
      <div className="flex gap-6 mb-0 text-[11px] font-mono tracking-tight border-b border-[var(--border)] pb-4 px-6 pt-6">
        {isMultiSeries && Array.isArray(seriesConfig) ? (
          seriesConfig.map(s => (
            <div key={s.key} className="flex items-center gap-2">
              <span className="w-2 h-0.5" style={{ background: s.color }}></span>
              <span className="text-[var(--text-secondary)] uppercase">{s.ticker}</span>
            </div>
          ))
        ) : (
          <>
              <div className="flex items-center gap-2">
                <div className="flex flex-col">
                  <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold">Asset</span>
                  <span className="text-[var(--text-primary)] font-bold text-lg tracking-tight">{externalData?.ticker || ticker}</span>
                </div>
              </div>
              {isNormalized && (
                <div className="flex items-center gap-2 ml-4">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[var(--text-muted)] uppercase">Benchmark</span>
                    <span className="text-[#22c55e] font-bold">S&P 500</span>
                  </div>
                </div>
            )}
          </>
        )}
      </div>

      <div className="flex-1 w-full min-h-[200px] mt-4 px-2">
        <ResponsiveContainer>
          {externalData?.chartType === 'bar' && Array.isArray(externalData.data) ? (
            (() => {
              const transformData = pivotData(externalData.data);
              const labelKey = getLabelKey(transformData);
              const valueKeys = getValueKeys(transformData);

              return (
                <BarChart
                  layout="vertical"
                  data={transformData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" />
                  <XAxis
                    type="number"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    axisLine={{ stroke: '#475569' }}
                    tickFormatter={formatXAxis}
                  />
                  <YAxis
                    type="category"
                    dataKey={labelKey}
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }}
                    axisLine={{ stroke: '#475569' }}
                    width={100}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' }}
                    itemStyle={{ color: '#f8fafc', fontSize: '11px' }}
                    labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontWeight: 'bold' }}
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  />
                  <Legend verticalAlign="top" align="right" height={36} wrapperStyle={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }} />
                  {valueKeys.map((key, index) => (
                    <Bar
                      key={key}
                      dataKey={key}
                      fill={COLORS[index % COLORS.length]}
                      radius={[0, 4, 4, 0]}
                      barSize={valueKeys.length > 2 ? 15 : 25}
                      name={key === 'value' && externalData.title ? externalData.title : (key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1'))}
                    />
                  ))}
                </BarChart>
              );
            })()
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
                  {Array.isArray(externalData.data) && externalData.data.map((_: any, index: number) => (
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
                    tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatXAxis}
              />
              <YAxis
                yAxisId="price"
                    domain={['auto', 'auto']}
                fontSize={10}
                tickLine={false}
                axisLine={false}
                    tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 500 }}
                orientation="right"
                    tickFormatter={(val) => isNormalized ? `${val.toFixed(1)}%` : val}
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
                    formatter={(val: number, name: string) => {
                      if (name === 'price' || name === 'sp500') {
                        return isNormalized ? `${val.toFixed(2)}%` : val;
                      }
                      return val;
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
                        <defs>
                          <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                          </linearGradient>
                          <linearGradient id="colorPriceStroke" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="#3b82f6" />
                            <stop offset="100%" stopColor="#60a5fa" />
                          </linearGradient>
                        </defs>
                  <Area
                    yAxisId="price"
                    type="monotone"
                    dataKey="price"
                          name={externalData?.ticker || ticker}
                          stroke="url(#colorPriceStroke)" /* Use gradient stroke if possible, or var(--brand) */
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                          activeDot={{ r: 6, strokeWidth: 2, stroke: 'var(--bg-app)', fill: 'var(--brand)' }}
                  />
                        {isNormalized && (
                          <Line
                            yAxisId="price"
                            type="monotone"
                            dataKey="sp500"
                            name="S&P 500"
                            stroke="#22c55e"
                            strokeWidth={2}
                            dot={false}
                            strokeDasharray="3 3"
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
