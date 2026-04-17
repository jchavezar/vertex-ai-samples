import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

interface Props {
  data: Record<string, Record<string, number>>;
}

const MEMBER_COLORS = ['#f97316', '#3b82f6', '#22c55e', '#8b5cf6', '#ec4899'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatPeriod(p: string) {
  const [, m] = p.split('-');
  return MONTHS[parseInt(m) - 1];
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <div className="label">{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
          <span style={{ fontSize: 13 }}>{p.name}: ${p.value?.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
        </div>
      ))}
    </div>
  );
}

export function MemberComparison({ data }: Props) {
  const members = new Set<string>();
  Object.values(data).forEach(m => Object.keys(m).forEach(k => members.add(k)));
  const memberList = Array.from(members);

  const chartData = Object.entries(data)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([period, memberTotals]) => ({
      name: formatPeriod(period),
      ...memberTotals,
    }));

  if (!chartData.length) return <div className="empty-state"><p>No member data</p></div>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
        <Tooltip content={<CustomTooltip />} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
        {memberList.map((member, i) => (
          <Bar key={member} dataKey={member} fill={MEMBER_COLORS[i % MEMBER_COLORS.length]} radius={[4, 4, 0, 0]} maxBarSize={32} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
