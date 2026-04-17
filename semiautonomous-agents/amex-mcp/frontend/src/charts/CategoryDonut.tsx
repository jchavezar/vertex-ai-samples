import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import type { CategoryBreakdown } from '../types';
import { CATEGORY_COLORS } from '../types';

interface Props {
  categories: CategoryBreakdown[];
  totalSpend: number;
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <div className="label">{d.category}</div>
      <div className="value">${d.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
      <div className="label">{d.percentage}% &middot; {d.count} txns</div>
    </div>
  );
}

export function CategoryDonut({ categories, totalSpend }: Props) {
  return (
    <div style={{ position: 'relative' }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={categories}
            dataKey="amount"
            nameKey="category"
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={120}
            paddingAngle={2}
            strokeWidth={0}
          >
            {categories.map((c) => (
              <Cell key={c.category} fill={CATEGORY_COLORS[c.category] || '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
        pointerEvents: 'none',
      }}>
        <div style={{ fontSize: 12, color: '#64748b' }}>Total Spend</div>
        <div style={{ fontSize: 24, fontWeight: 700 }}>
          ${totalSpend.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </div>
      </div>
    </div>
  );
}
