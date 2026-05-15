"""Generate GA vs Preview model comparison HTML report.

Usage:
    python ga_comparison.py

Reads:
  - judged/rag_md_v2.json (baseline: Gemini 3 flash preview)
  - judged/agent_ga_flash.json (GA: Gemini 2.5 flash)

Writes:
  - ga_comparison.html (styled comparison report)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Load judged results
baseline = json.loads((HERE / "judged" / "rag_md_v2.json").read_text())
ga_flash = json.loads((HERE / "judged" / "agent_ga_flash.json").read_text())

def compute_scores(data):
    """Compute composite score and verdict counts."""
    n = len(data)
    if n == 0:
        return {"composite": 0, "correctness": 0, "completeness": 0, "verdicts": {}}

    correctness = sum(q.get("correctness", 0) for q in data) / n * 100
    completeness = sum(q.get("completeness", 0) for q in data) / n * 100
    composite = (correctness + completeness) / 2

    verdicts = {}
    for v in ["correct", "partial", "wrong", "refused", "error"]:
        verdicts[v] = sum(1 for q in data if q.get("verdict") == v)

    avg_latency = sum(q.get("sa_elapsed_s", 0) for q in data if q.get("sa_ok")) / sum(1 for q in data if q.get("sa_ok")) if any(q.get("sa_ok") for q in data) else 0

    return {
        "composite": round(composite, 1),
        "correctness": round(correctness, 1),
        "completeness": round(completeness, 1),
        "verdicts": verdicts,
        "avg_latency": round(avg_latency, 1),
        "n": n,
    }

def compute_by_category(data):
    """Compute scores by question category."""
    by_cat = {}
    for q in data:
        cat = q.get("category", "unknown")
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(q)

    return {cat: compute_scores(qs) for cat, qs in by_cat.items()}

baseline_scores = compute_scores(baseline)
ga_flash_scores = compute_scores(ga_flash)

baseline_by_cat = compute_by_category(baseline)
ga_flash_by_cat = compute_by_category(ga_flash)

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GA vs Preview Models: docparse Benchmark</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .hero {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        .hero p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .content {{
            padding: 2rem;
        }}
        .section {{
            margin-bottom: 2rem;
        }}
        .section h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 1rem;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f3f4f6;
            font-weight: 600;
            color: #374151;
        }}
        tr:hover {{
            background: #f9fafb;
        }}
        .metric {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        .metric.high {{ background: #d1fae5; color: #065f46; }}
        .metric.medium {{ background: #fef3c7; color: #92400e; }}
        .metric.low {{ background: #fee2e2; color: #991b1b; }}
        .winner {{ background: #ecfdf5; font-weight: 600; }}
        .takeaway {{
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 2rem;
        }}
        .takeaway h3 {{
            color: #1e3a8a;
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
        }}
        .takeaway p {{
            color: #1e40af;
            line-height: 1.6;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }}
        .badge.ga {{ background: #dbeafe; color: #1e40af; }}
        .badge.preview {{ background: #e0e7ff; color: #4338ca; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>GA Models vs Preview Models</h1>
            <p>docparse agent benchmark: Can Gemini 2.5-flash (GA) match Gemini 3-flash-preview performance?</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>Overall Performance</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Model</th>
                            <th>Composite</th>
                            <th>Correctness</th>
                            <th>Completeness</th>
                            <th>Avg Latency</th>
                            <th>Correct</th>
                            <th>Partial</th>
                            <th>Wrong</th>
                            <th>Refused</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="{'winner' if baseline_scores['composite'] >= ga_flash_scores['composite'] else ''}">
                            <td>rag_md_v2 <span class="badge preview">PREVIEW</span></td>
                            <td>gemini-3-flash-preview</td>
                            <td><span class="metric {'high' if baseline_scores['composite'] >= 90 else 'medium' if baseline_scores['composite'] >= 80 else 'low'}">{baseline_scores['composite']}%</span></td>
                            <td>{baseline_scores['correctness']}%</td>
                            <td>{baseline_scores['completeness']}%</td>
                            <td>{baseline_scores['avg_latency']}s</td>
                            <td>{baseline_scores['verdicts'].get('correct', 0)}</td>
                            <td>{baseline_scores['verdicts'].get('partial', 0)}</td>
                            <td>{baseline_scores['verdicts'].get('wrong', 0)}</td>
                            <td>{baseline_scores['verdicts'].get('refused', 0)}</td>
                        </tr>
                        <tr class="{'winner' if ga_flash_scores['composite'] >= baseline_scores['composite'] else ''}">
                            <td>agent_ga_flash <span class="badge ga">GA</span></td>
                            <td>gemini-2.5-flash</td>
                            <td><span class="metric {'high' if ga_flash_scores['composite'] >= 90 else 'medium' if ga_flash_scores['composite'] >= 80 else 'low'}">{ga_flash_scores['composite']}%</span></td>
                            <td>{ga_flash_scores['correctness']}%</td>
                            <td>{ga_flash_scores['completeness']}%</td>
                            <td>{ga_flash_scores['avg_latency']}s</td>
                            <td>{ga_flash_scores['verdicts'].get('correct', 0)}</td>
                            <td>{ga_flash_scores['verdicts'].get('partial', 0)}</td>
                            <td>{ga_flash_scores['verdicts'].get('wrong', 0)}</td>
                            <td>{ga_flash_scores['verdicts'].get('refused', 0)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Performance by Category</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Preview (3-flash-preview)</th>
                            <th>GA (2.5-flash)</th>
                            <th>Delta</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add category rows
all_cats = sorted(set(list(baseline_by_cat.keys()) + list(ga_flash_by_cat.keys())))
for cat in all_cats:
    baseline_cat = baseline_by_cat.get(cat, {"composite": 0, "n": 0})
    ga_cat = ga_flash_by_cat.get(cat, {"composite": 0, "n": 0})
    delta = ga_cat["composite"] - baseline_cat["composite"]
    delta_sign = "+" if delta > 0 else ""
    delta_class = "high" if delta > 0 else "low" if delta < -5 else "medium"

    html += f"""
                        <tr>
                            <td>{cat} (n={baseline_cat['n']})</td>
                            <td>{baseline_cat['composite']}%</td>
                            <td>{ga_cat['composite']}%</td>
                            <td><span class="metric {delta_class}">{delta_sign}{delta:.1f}%</span></td>
                        </tr>
"""

html += """
                    </tbody>
                </table>
            </div>
"""

# Calculate delta and takeaway
composite_delta = ga_flash_scores['composite'] - baseline_scores['composite']
can_use_ga = ga_flash_scores['composite'] >= 90

takeaway_text = f"""
The GA model (gemini-2.5-flash) achieved {ga_flash_scores['composite']}% composite score vs {baseline_scores['composite']}%
for the preview model (gemini-3-flash-preview), a delta of {composite_delta:+.1f} percentage points.

<strong>{'✓ YES' if can_use_ga else '✗ NO'}</strong> — The customer {'CAN' if can_use_ga else 'CANNOT'} use GA models and still hit 90% composite.

Key differences:
• GA model {'does not support' if True else 'supports'} thinking_level (extended reasoning)
• Latency: {ga_flash_scores['avg_latency']}s (GA) vs {baseline_scores['avg_latency']}s (preview)
• Correct answers: {ga_flash_scores['verdicts'].get('correct', 0)} (GA) vs {baseline_scores['verdicts'].get('correct', 0)} (preview)

Both strategies use the same RAG Engine corpus and retrieval settings (top_k=20, vector_distance_threshold=0.5).
The primary difference is the model: GA 2.5-flash vs Preview 3-flash-preview.
"""

html += f"""
            <div class="takeaway">
                <h3>Can the customer use GA models and still hit 90%?</h3>
                <p>{takeaway_text}</p>
            </div>

            <div class="section">
                <h2>Methodology</h2>
                <p><strong>Dataset:</strong> 216 questions across 5 categories (lookup, comparison, inference, math, visual)</p>
                <p><strong>Corpus:</strong> Same RAG Engine corpus (projects/254356041555/locations/us-central1/ragCorpora/8818611020344852480)</p>
                <p><strong>Retrieval:</strong> top_k=20, vector_distance_threshold=0.5, text-embedding-005</p>
                <p><strong>Judge:</strong> Claude Opus 4.5 on Vertex AI (us-east5)</p>
                <p><strong>Date:</strong> {HERE.name} generated on 2026-04-30</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Write HTML
out_path = HERE / "ga_comparison.html"
out_path.write_text(html)
print(f"Report written to {out_path}")
print(f"\nSummary:")
print(f"  Preview (3-flash-preview): {baseline_scores['composite']}%")
print(f"  GA (2.5-flash):            {ga_flash_scores['composite']}%")
print(f"  Delta:                     {composite_delta:+.1f}%")
print(f"  Can use GA and hit 90%?    {'YES' if can_use_ga else 'NO'}")
