export interface StatementSummary {
  period: string;
  total_debits: number;
  total_credits: number;
  transaction_count: number;
}

export interface Transaction {
  date: string;
  description: string;
  amount: number;
  card_member: string;
  enriched_category: string;
  subcategory: string;
  merchant_clean: string;
  tags: string[];
  merchant_type: string;
  purchase_channel: string;
  purpose: string;
  categorization_confidence: number;
  receipt_found?: boolean;
  receipt_details?: Record<string, unknown>;
}

export interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
  count: number;
}

export interface SankeyNode {
  name: string;
  amount?: number;
  percentage?: number;
  side?: 'left' | 'right';
}

export interface SankeyLink {
  source: number;
  target: number;
  value: number;
  sourceCategory?: string;
}

export interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

export interface PeriodTotal {
  period: string;
  total: number;
}

export interface TrendsData {
  period_totals: PeriodTotal[];
  category_trends: Record<string, { period: string; amount: number }[]>;
  member_totals: Record<string, Record<string, number>>;
}

export interface Subscription {
  merchant: string;
  amount: number;
  frequency: string;
  category: string;
  first_seen: string;
  last_seen: string;
  status: string;
  annual_cost: number;
}

export interface InsightsData {
  highlights: string[];
  anomalies: { description: string; severity: string }[];
  ai_trends: string[];
  recommendations: {
    title: string;
    description: string;
    potential_savings: number;
    priority: string;
  }[];
  spending_score: number;
  score_explanation: string;
}

export type Page = 'dashboard' | 'transactions' | 'reports' | 'subscriptions' | 'insights';

export const CATEGORY_COLORS: Record<string, string> = {
  'Dining': '#f97316',
  'Groceries': '#22c55e',
  'Transportation': '#3b82f6',
  'Travel': '#8b5cf6',
  'Shopping': '#ec4899',
  'Entertainment': '#eab308',
  'Health': '#14b8a6',
  'Utilities': '#6366f1',
  'Subscriptions': '#f43f5e',
  'Insurance': '#0ea5e9',
  'Education': '#a855f7',
  'Personal Care': '#d946ef',
  'Home': '#84cc16',
  'Gifts': '#fb923c',
  'Fees': '#64748b',
  'Other': '#94a3b8',
};
