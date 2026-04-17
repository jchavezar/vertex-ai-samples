import { TrendingUp, TrendingDown } from 'lucide-react';

interface Props {
  label: string;
  value: string;
  change?: number;
  prefix?: string;
}

export function SummaryCard({ label, value, change, prefix }: Props) {
  return (
    <div className="summary-card">
      <div className="label">{label}</div>
      <div className="value">{prefix}{value}</div>
      {change !== undefined && (
        <div className={`change ${change >= 0 ? 'negative' : 'positive'}`}>
          {change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {Math.abs(change).toFixed(1)}% vs last month
        </div>
      )}
    </div>
  );
}
