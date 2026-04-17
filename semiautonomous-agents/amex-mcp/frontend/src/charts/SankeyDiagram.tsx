import { Sankey, Tooltip, ResponsiveContainer, Layer } from 'recharts';
import type { SankeyData } from '../types';
import { CATEGORY_COLORS } from '../types';

interface Props {
  data: SankeyData;
}

const fmt = (n: number) => '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });

function SankeyNode({ x, y, width, height, payload }: any) {
  const name = payload?.name || '';
  const color = CATEGORY_COLORS[name] || '#94a3b8';
  const isLeft = payload?.sourceLinks?.length > 0;
  const amount = payload?.amount ?? payload?.value ?? 0;
  const pct = payload?.percentage;

  // Build label
  let label = name.length > 24 ? name.slice(0, 22) + '...' : name;
  const amountLabel = amount > 0 ? fmt(amount) : '';

  return (
    <Layer>
      <rect
        x={x}
        y={y}
        width={width}
        height={Math.max(height, 2)}
        fill={color}
        fillOpacity={0.95}
        rx={4}
      />
      {isLeft ? (
        <>
          <text
            x={x - 8}
            y={y + height / 2 - (amountLabel ? 7 : 0)}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize={12}
            fontWeight={600}
            fill="#1a1a2e"
          >
            {label}
          </text>
          {amountLabel && (
            <text
              x={x - 8}
              y={y + height / 2 + 9}
              textAnchor="end"
              dominantBaseline="middle"
              fontSize={11}
              fill="#64748b"
            >
              {amountLabel}{pct !== undefined ? ` (${pct}%)` : ''}
            </text>
          )}
        </>
      ) : (
        <>
          <text
            x={x + width + 8}
            y={y + height / 2 - (amountLabel ? 7 : 0)}
            textAnchor="start"
            dominantBaseline="middle"
            fontSize={12}
            fontWeight={500}
            fill="#1a1a2e"
          >
            {label}
          </text>
          {amountLabel && (
            <text
              x={x + width + 8}
              y={y + height / 2 + 9}
              textAnchor="start"
              dominantBaseline="middle"
              fontSize={11}
              fill="#64748b"
            >
              {amountLabel}
            </text>
          )}
        </>
      )}
    </Layer>
  );
}

function SankeyLink({ sourceX, sourceY, sourceControlX, targetX, targetY, targetControlX, linkWidth, payload }: any) {
  // Color the link based on source category
  const sourceName = payload?.source?.name || '';
  const color = CATEGORY_COLORS[sourceName] || '#94a3b8';

  const halfWidth = Math.max(linkWidth / 2, 1);

  return (
    <Layer>
      <path
        d={`
          M${sourceX},${sourceY + halfWidth}
          C${sourceControlX},${sourceY + halfWidth} ${targetControlX},${targetY + halfWidth} ${targetX},${targetY + halfWidth}
          L${targetX},${targetY - halfWidth}
          C${targetControlX},${targetY - halfWidth} ${sourceControlX},${sourceY - halfWidth} ${sourceX},${sourceY - halfWidth}
          Z
        `}
        fill={color}
        fillOpacity={0.35}
        stroke={color}
        strokeOpacity={0.5}
        strokeWidth={0.5}
        style={{ cursor: 'pointer' }}
      />
    </Layer>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  if (d.source && d.target) {
    const color = CATEGORY_COLORS[d.source.name] || '#94a3b8';
    return (
      <div className="custom-tooltip">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <div style={{ width: 10, height: 10, borderRadius: 3, background: color }} />
          <span className="label" style={{ margin: 0 }}>{d.source.name}</span>
        </div>
        <div style={{ fontWeight: 600, fontSize: 14 }}>
          {d.target.name}: ${d.value?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </div>
      </div>
    );
  }
  return null;
}

export function SankeyDiagram({ data }: Props) {
  if (!data.nodes.length || !data.links.length) {
    return <div className="empty-state"><p>No data for Sankey diagram</p></div>;
  }

  // Compute dynamic height based on node count
  const nodeCount = Math.max(data.nodes.length, 10);
  const chartHeight = Math.max(nodeCount * 32, 500);

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <Sankey
        data={data}
        nodeWidth={18}
        nodePadding={14}
        linkCurvature={0.5}
        margin={{ top: 16, right: 200, bottom: 16, left: 200 }}
        node={<SankeyNode />}
        link={<SankeyLink />}
      >
        <Tooltip content={<CustomTooltip />} />
      </Sankey>
    </ResponsiveContainer>
  );
}
