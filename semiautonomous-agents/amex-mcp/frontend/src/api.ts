import type {
  StatementSummary,
  Transaction,
  CategoryBreakdown,
  SankeyData,
  TrendsData,
  Subscription,
  InsightsData,
} from './types';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchStatements(): Promise<StatementSummary[]> {
  return get('/api/statements');
}

export async function fetchStatement(period: string): Promise<Record<string, unknown>> {
  return get(`/api/statements/${period}`);
}

export async function fetchTransactions(params: {
  period?: string;
  category?: string;
  card_member?: string;
  search?: string;
}): Promise<Transaction[]> {
  const qs = new URLSearchParams();
  if (params.period) qs.set('period', params.period);
  if (params.category) qs.set('category', params.category);
  if (params.card_member) qs.set('card_member', params.card_member);
  if (params.search) qs.set('search', params.search);
  return get(`/api/transactions?${qs}`);
}

export async function fetchCategories(period: string): Promise<{
  period: string;
  total_spend: number;
  categories: CategoryBreakdown[];
}> {
  return get(`/api/categories/${period}`);
}

export async function fetchSankey(period: string): Promise<SankeyData> {
  return get(`/api/sankey/${period}`);
}

export async function fetchTrends(months?: number): Promise<TrendsData> {
  const qs = months ? `?months=${months}` : '';
  return get(`/api/trends${qs}`);
}

export async function fetchSubscriptions(): Promise<{
  subscriptions: Subscription[];
  audit: Record<string, unknown>[];
}> {
  return get('/api/subscriptions');
}

export async function fetchInsights(period: string): Promise<InsightsData> {
  return get(`/api/insights/${period}`);
}
