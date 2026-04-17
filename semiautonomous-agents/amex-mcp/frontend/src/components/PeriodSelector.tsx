import type { StatementSummary } from '../types';

interface Props {
  periods: StatementSummary[];
  selected: string;
  onChange: (period: string) => void;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export function PeriodSelector({ periods, selected, onChange }: Props) {
  const formatPeriod = (p: string) => {
    const [y, m] = p.split('-');
    return `${MONTHS[parseInt(m) - 1]} ${y}`;
  };

  return (
    <div className="period-selector">
      <select value={selected} onChange={(e) => onChange(e.target.value)}>
        {periods.map((p) => (
          <option key={p.period} value={p.period}>
            {formatPeriod(p.period)}
          </option>
        ))}
      </select>
    </div>
  );
}
