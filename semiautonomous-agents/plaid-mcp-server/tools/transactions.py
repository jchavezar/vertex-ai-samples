"""
Transaction Tools for Plaid MCP Server
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger("plaid-mcp.transactions")


def register_transaction_tools(mcp, plaid_manager):
    """Register transaction tools with the MCP server."""

    @mcp.tool()
    def plaid_list_transactions(days: int = 90) -> str:
        """
        List recent transactions.

        Args:
            days: Number of days to look back (default 90, max 730)
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=min(days, 730))).strftime("%Y-%m-%d")

            transactions = plaid_manager.get_transactions(start_date, end_date)

            if not transactions:
                return "No transactions found."

            results = []
            results.append(f"## Transactions ({len(transactions)} found, last {days} days)\n")
            results.append("| Date | Description | Amount | Category |")
            results.append("|------|-------------|--------|----------|")

            for txn in transactions[:100]:  # Cap display at 100
                name = txn["merchant_name"] or txn["name"]
                amount = txn["amount"]
                sign = "" if amount >= 0 else "-"
                category = " > ".join(txn["category"]) if txn["category"] else "N/A"
                results.append(
                    f"| {txn['date']} | {name} | {sign}${abs(amount):.2f} | {category} |"
                )

            if len(transactions) > 100:
                results.append(f"\n*Showing 100 of {len(transactions)} transactions.*")

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Transaction list error: {e}")
            return f"Error listing transactions: {str(e)}"

    @mcp.tool()
    def plaid_find_subscriptions(months: int = 6) -> str:
        """
        Analyze transactions to find recurring subscriptions and charges.

        Args:
            months: Number of months to analyze (default 6)
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")

            transactions = plaid_manager.get_transactions(start_date, end_date)

            if not transactions:
                return "No transactions found."

            # Group by normalized merchant name
            merchant_charges = defaultdict(list)
            for txn in transactions:
                if txn["pending"]:
                    continue
                # Only look at charges (positive amounts in Plaid = money out)
                if txn["amount"] <= 0:
                    continue

                name = (txn["merchant_name"] or txn["name"]).strip()
                # Normalize: lowercase, remove extra whitespace
                normalized = " ".join(name.lower().split())
                merchant_charges[normalized].append({
                    "date": txn["date"],
                    "amount": txn["amount"],
                    "original_name": name,
                    "category": txn["category"],
                })

            # Find recurring charges (2+ charges from same merchant with similar amounts)
            subscriptions = []
            for merchant, charges in merchant_charges.items():
                if len(charges) < 2:
                    continue

                # Check if amounts are similar (within 20% of median)
                amounts = [c["amount"] for c in charges]
                amounts.sort()
                median = amounts[len(amounts) // 2]

                consistent = [a for a in amounts if abs(a - median) / median < 0.2]
                if len(consistent) < 2:
                    continue

                # Calculate frequency
                dates = sorted([c["date"] for c in charges])
                if len(dates) >= 2:
                    date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
                    gaps = [(date_objs[i + 1] - date_objs[i]).days for i in range(len(date_objs) - 1)]
                    avg_gap = sum(gaps) / len(gaps)

                    if avg_gap < 10:
                        frequency = "Weekly"
                    elif avg_gap < 45:
                        frequency = "Monthly"
                    elif avg_gap < 100:
                        frequency = "Quarterly"
                    elif avg_gap < 200:
                        frequency = "Semi-annual"
                    else:
                        frequency = "Annual"
                else:
                    frequency = "Unknown"

                avg_amount = sum(consistent) / len(consistent)
                last_charge = max(dates)
                display_name = charges[0]["original_name"]
                category = " > ".join(charges[0]["category"]) if charges[0]["category"] else "N/A"

                # Estimate monthly cost
                if frequency == "Weekly":
                    monthly_cost = avg_amount * 4.33
                elif frequency == "Monthly":
                    monthly_cost = avg_amount
                elif frequency == "Quarterly":
                    monthly_cost = avg_amount / 3
                elif frequency == "Semi-annual":
                    monthly_cost = avg_amount / 6
                elif frequency == "Annual":
                    monthly_cost = avg_amount / 12
                else:
                    monthly_cost = avg_amount

                subscriptions.append({
                    "name": display_name,
                    "monthly_cost": monthly_cost,
                    "charge_amount": avg_amount,
                    "frequency": frequency,
                    "last_charge": last_charge,
                    "count": len(charges),
                    "category": category,
                })

            # Sort by monthly cost descending
            subscriptions.sort(key=lambda x: x["monthly_cost"], reverse=True)

            if not subscriptions:
                return "No recurring subscriptions detected."

            results = []
            results.append(f"## Recurring Subscriptions ({len(subscriptions)} found)\n")
            results.append("| Service | Monthly Cost | Charge Amount | Frequency | Last Charge | Category |")
            results.append("|---------|-------------|---------------|-----------|-------------|----------|")

            total_monthly = 0
            for sub in subscriptions:
                results.append(
                    f"| {sub['name']} | ${sub['monthly_cost']:.2f}/mo | "
                    f"${sub['charge_amount']:.2f} | {sub['frequency']} | "
                    f"{sub['last_charge']} | {sub['category']} |"
                )
                total_monthly += sub["monthly_cost"]

            results.append(f"\n**Total estimated monthly subscriptions: ${total_monthly:.2f}/mo**")
            results.append(f"**Estimated annual cost: ${total_monthly * 12:.2f}/yr**")

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Subscription analysis error: {e}")
            return f"Error analyzing subscriptions: {str(e)}"

    @mcp.tool()
    def plaid_search_transactions(query: str, days: int = 90) -> str:
        """
        Search transactions by merchant name or description.

        Args:
            query: Search term (case-insensitive)
            days: Number of days to look back (default 90)
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            transactions = plaid_manager.get_transactions(start_date, end_date)
            query_lower = query.lower()

            matches = [
                txn for txn in transactions
                if query_lower in (txn["merchant_name"] or "").lower()
                or query_lower in txn["name"].lower()
            ]

            if not matches:
                return f"No transactions matching '{query}' found."

            results = []
            results.append(f"## Transactions matching '{query}' ({len(matches)} found)\n")
            results.append("| Date | Description | Amount | Category |")
            results.append("|------|-------------|--------|----------|")

            total = 0
            for txn in matches:
                name = txn["merchant_name"] or txn["name"]
                amount = txn["amount"]
                total += amount
                category = " > ".join(txn["category"]) if txn["category"] else "N/A"
                sign = "" if amount >= 0 else "-"
                results.append(
                    f"| {txn['date']} | {name} | {sign}${abs(amount):.2f} | {category} |"
                )

            results.append(f"\n**Total: ${total:.2f}**")
            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Transaction search error: {e}")
            return f"Error searching transactions: {str(e)}"

    @mcp.tool()
    def plaid_spending_summary(days: int = 30) -> str:
        """
        Get spending summary by category.

        Args:
            days: Period to summarize (default 30)
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            transactions = plaid_manager.get_transactions(start_date, end_date)

            if not transactions:
                return "No transactions found."

            # Group by top-level category
            categories = defaultdict(lambda: {"total": 0, "count": 0})
            total_spend = 0
            total_income = 0

            for txn in transactions:
                if txn["pending"]:
                    continue
                amount = txn["amount"]
                cat = txn["category"][0] if txn["category"] else "Uncategorized"

                if amount > 0:  # Spending
                    categories[cat]["total"] += amount
                    categories[cat]["count"] += 1
                    total_spend += amount
                else:  # Income/credits
                    total_income += abs(amount)

            # Sort by total spending
            sorted_cats = sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True)

            results = []
            results.append(f"## Spending Summary (last {days} days)\n")
            results.append("| Category | Total | # Transactions | % of Spend |")
            results.append("|----------|-------|----------------|------------|")

            for cat, data in sorted_cats:
                pct = (data["total"] / total_spend * 100) if total_spend > 0 else 0
                results.append(
                    f"| {cat} | ${data['total']:.2f} | {data['count']} | {pct:.1f}% |"
                )

            results.append(f"\n**Total spending: ${total_spend:.2f}**")
            results.append(f"**Total income/credits: ${total_income:.2f}**")
            results.append(f"**Net: ${total_income - total_spend:.2f}**")

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Spending summary error: {e}")
            return f"Error generating summary: {str(e)}"
