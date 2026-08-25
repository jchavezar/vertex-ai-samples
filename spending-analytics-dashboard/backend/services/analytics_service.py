import json
import pandas as pd
from typing import Dict, Any, List

class AnalyticsService:
    def __init__(self, data_filepath: str):
        self.data_filepath = data_filepath
        self.records = self._load_data()
        self.df = pd.DataFrame(self.records)

    def _load_data(self) -> List[Dict[str, Any]]:
        with open(self.data_filepath, 'r') as f:
            return json.load(f)

    def get_summary_kpis(self) -> Dict[str, Any]:
        df = self.df
        positive_df = df[df['amount'] > 0]
        negative_df = df[df['amount'] < 0]

        total_gross = float(positive_df['amount'].sum())
        
        # Categorize negative transactions into Statement Payments vs Real Merchant Returns
        payment_mask = negative_df['raw_description'].str.upper().str.contains('PAYMENT|AUTOPAY|AUTO-PAY|ACH|THANK YOU|ONLINE PAYMENT|MOBILE PAYMENT|DIRECT DEBIT|EPAY', na=False)
        payments_df = negative_df[payment_mask]
        returns_df = negative_df[~payment_mask]

        total_statement_payments = float(payments_df['amount'].sum())
        total_merchant_returns = float(returns_df['amount'].sum())
        
        # Real Net Spend = Gross Purchases - Real Merchandise Returns
        total_real_net = total_gross + total_merchant_returns
        total_count = len(df)
        avg_transaction = total_gross / len(positive_df) if len(positive_df) > 0 else 0

        top_merchant = positive_df.groupby('clean_merchant')['amount'].sum().idxmax() if len(positive_df) > 0 else "N/A"
        top_merchant_amount = float(positive_df.groupby('clean_merchant')['amount'].sum().max()) if len(positive_df) > 0 else 0

        top_category = positive_df.groupby('primary_category')['amount'].sum().idxmax() if len(positive_df) > 0 else "N/A"
        top_category_amount = float(positive_df.groupby('primary_category')['amount'].sum().max()) if len(positive_df) > 0 else 0

        return {
            "total_gross": round(total_gross, 2),
            "total_refunds": round(abs(total_merchant_returns), 2),
            "total_merchant_returns": round(abs(total_merchant_returns), 2),
            "total_statement_payments": round(abs(total_statement_payments), 2),
            "total_net": round(total_real_net, 2),
            "total_count": total_count,
            "purchases_count": len(positive_df),
            "returns_count": len(returns_df),
            "payments_count": len(payments_df),
            "avg_transaction": round(avg_transaction, 2),
            "top_merchant": top_merchant,
            "top_merchant_amount": round(top_merchant_amount, 2),
            "top_category": top_category,
            "top_category_amount": round(top_category_amount, 2),
            "date_range": {
                "start": df['date'].min(),
                "end": df['date'].max()
            }
        }

    def get_category_breakdown(self) -> List[Dict[str, Any]]:
        positive_df = self.df[self.df['amount'] > 0]
        grouped = positive_df.groupby('primary_category').agg(
            total_amount=('amount', 'sum'),
            count=('amount', 'count'),
            avg_amount=('amount', 'mean')
        ).reset_index()

        total_spent = positive_df['amount'].sum()
        grouped['percentage'] = (grouped['total_amount'] / total_spent * 100).round(1)
        grouped['total_amount'] = grouped['total_amount'].round(2)
        grouped['avg_amount'] = grouped['avg_amount'].round(2)
        
        return grouped.sort_values(by='total_amount', ascending=False).to_dict(orient='records')

    def get_expense_type_breakdown(self) -> List[Dict[str, Any]]:
        positive_df = self.df[self.df['amount'] > 0]
        grouped = positive_df.groupby('expense_type').agg(
            total_amount=('amount', 'sum'),
            count=('amount', 'count')
        ).reset_index()
        total_spent = positive_df['amount'].sum()
        grouped['percentage'] = (grouped['total_amount'] / total_spent * 100).round(1)
        grouped['total_amount'] = grouped['total_amount'].round(2)
        return grouped.sort_values(by='total_amount', ascending=False).to_dict(orient='records')

    def get_cardholder_comparison(self) -> Dict[str, Any]:
        df = self.df
        positive_df = df[df['amount'] > 0]
        
        result = {}
        for member in df['card_member'].unique():
            m_pos = positive_df[positive_df['card_member'] == member]
            m_neg = df[(df['card_member'] == member) & (df['amount'] < 0)]
            
            top_cat = m_pos.groupby('primary_category')['amount'].sum().idxmax() if len(m_pos) > 0 else "N/A"
            top_merchant = m_pos.groupby('clean_merchant')['amount'].sum().idxmax() if len(m_pos) > 0 else "N/A"
            
            cat_split = m_pos.groupby('primary_category')['amount'].sum().round(2).to_dict()
            
            result[member] = {
                "total_gross": round(float(m_pos['amount'].sum()), 2),
                "total_refunds": round(abs(float(m_neg['amount'].sum())), 2),
                "net_spent": round(float(m_pos['amount'].sum() + m_neg['amount'].sum()), 2),
                "transaction_count": len(df[df['card_member'] == member]),
                "avg_transaction": round(float(m_pos['amount'].mean()), 2) if len(m_pos) > 0 else 0,
                "top_category": top_cat,
                "top_merchant": top_merchant,
                "category_breakdown": cat_split
            }
        return result

    def get_merchant_leaderboard(self, top_n: int = 15) -> List[Dict[str, Any]]:
        positive_df = self.df[self.df['amount'] > 0]
        grouped = positive_df.groupby(['clean_merchant', 'primary_category']).agg(
            total_spent=('amount', 'sum'),
            transaction_count=('amount', 'count'),
            avg_spent=('amount', 'mean')
        ).reset_index()

        grouped['total_spent'] = grouped['total_spent'].round(2)
        grouped['avg_spent'] = grouped['avg_spent'].round(2)
        return grouped.sort_values(by='total_spent', ascending=False).head(top_n).to_dict(orient='records')

    def get_daily_timeline(self) -> List[Dict[str, Any]]:
        df = self.df.copy()
        df['date_parsed'] = pd.to_datetime(df['date'])
        
        # Exclude statement autopay payments from the daily shopping/spending refund curve
        payment_mask = df['raw_description'].str.upper().str.contains('PAYMENT|AUTOPAY|AUTO-PAY|ACH|THANK YOU|ONLINE PAYMENT|MOBILE PAYMENT|DIRECT DEBIT|EPAY', na=False)
        spend_df = df[~payment_mask]

        daily = spend_df.groupby('date').agg(
            gross_spent=('amount', lambda x: x[x > 0].sum()),
            refunds=('amount', lambda x: abs(x[x < 0].sum())),
            net_spent=('amount', lambda x: x.sum()),
            count=('id', 'count')
        ).reset_index()
        
        daily['gross_spent'] = daily['gross_spent'].round(2)
        daily['refunds'] = daily['refunds'].round(2)
        daily['net_spent'] = daily['net_spent'].round(2)
        daily['date_parsed'] = pd.to_datetime(daily['date'])
        
        return daily.sort_values(by='date_parsed').drop(columns=['date_parsed']).to_dict(orient='records')

    def get_spend_timeline(self, freq: str = 'W') -> List[Dict[str, Any]]:
        return self.get_daily_timeline()

    def get_tags_distribution(self) -> List[Dict[str, Any]]:
        tag_counts = {}
        tag_spend = {}
        for _, row in self.df[self.df['amount'] > 0].iterrows():
            tags = row.get('tags', [])
            amt = row['amount']
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                tag_spend[tag] = tag_spend.get(tag, 0) + amt

        res = []
        for tag in tag_counts:
            res.append({
                "tag": tag,
                "count": tag_counts[tag],
                "total_spent": round(tag_spend[tag], 2)
            })
        return sorted(res, key=lambda x: x['total_spent'], reverse=True)

    def get_tag_cloud(self) -> List[Dict[str, Any]]:
        return self.get_tags_distribution()

    def get_subscriptions_analysis(self) -> Dict[str, Any]:
        from services.subscription_service import detect_subscriptions
        return detect_subscriptions(self.records)

