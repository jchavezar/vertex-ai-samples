import json
import os
import sys

def main():
    in_file = "multi_model_llm_judged_suite.json"
    out_file = "/Users/jesusarguelles/.gemini/jetski/brain/0603c274-f3c2-4d01-b948-9cd747b6dba2/llm_eval_report.md"
    
    if not os.path.exists(in_file):
        print(f"Error: {in_file} does not exist.")
        return

    with open(in_file, "r") as f:
        data = json.load(f)

    summary = data.get("summary", {})
    results = data.get("results", [])

    mcp_sum = summary.get("gemini_36_flash", {})
    sa_sum = summary.get("streamassist_federated", {})

    report = []
    report.append("# 📊 Unbiased Multi-Model LLM Evaluation Report")
    report.append(f"\n*Generated At: {summary.get('llm_judge_timestamp', 'Unknown')}*")
    report.append("\nThis report provides an unbiased, semantic evaluation of both the **Google ADK Gemini 3.6 Flash (MCP)** agent and the **Discovery Engine StreamAssist API** against the 100-query golden test suite.")
    
    # Summary Table
    report.append("\n## 📈 Executive Summary")
    report.append("\n| Metric | Gemini 3.6 Flash (MCP) | StreamAssist (Federated) |")
    report.append("| :--- | :--- | :--- |")
    report.append(f"| **Rigid Substring Precision** | {mcp_sum.get('avg_precision')}% | {sa_sum.get('avg_precision')}% |")
    report.append(f"| **LLM Unbiased Precision** | {mcp_sum.get('llm_precision')}% | {sa_sum.get('llm_precision')}% |")
    report.append(f"| **Average Latency** | {mcp_sum.get('avg_latency_s')}s | {sa_sum.get('avg_latency_s')}s |")
    report.append(f"| **Architecture** | Agent Platform + MCP | Broadcast Federated Search |")
    
    # Failure Reason Breakdown
    report.append("\n## 🔍 Failure Category Breakdown")
    report.append("\nFailure reasons classified by the LLM Judge:")
    
    mcp_reasons = {}
    sa_reasons = {}
    
    for r in results:
        m_r = r["app_judgment"]["failure_reason"]
        s_r = r["streamassist_judgment"]["failure_reason"]
        mcp_reasons[m_r] = mcp_reasons.get(m_r, 0) + 1
        sa_reasons[s_r] = sa_reasons.get(s_r, 0) + 1

    report.append("\n| Failure Reason | Gemini 3.6 Flash (MCP) | StreamAssist (Federated) |")
    report.append("| :--- | :--- | :--- |")
    all_reasons = sorted(list(set(list(mcp_reasons.keys()) + list(sa_reasons.keys()))))
    for reason in all_reasons:
        if reason == "none": continue
        report.append(f"| `{reason}` | {mcp_reasons.get(reason, 0)} | {sa_reasons.get(reason, 0)} |")

    # Detailed Actual Failures
    report.append("\n## ❌ Detailed Factual Errors & Data Gaps")
    report.append("\nThis section highlights cases where the models committed genuine factual errors or had missing data (excluding rigid matching false negatives).")

    report.append("\n### 🤖 Gemini 3.6 Flash (MCP) Actual Failures")
    mcp_fail_list = []
    for r in results:
        j = r["app_judgment"]
        if not j["factual_correctness"] and j["failure_reason"] != "rigid_matching_false_negative":
            mcp_fail_list.append(r)

    if not mcp_fail_list:
        report.append("\n*No actual factual failures or missing data detected!*")
    else:
        for r in mcp_fail_list:
            report.append(f"\n#### [{r['id']}] {r['query']}")
            report.append(f"* **Expected Tool**: `{r['expected_tool']}` | **Actual Tools Called**: `{r['tools_called']}`")
            report.append(f"* **Ground Truth Answer**: {r['ground_truth_answer']}")
            report.append(f"* **Agent Answer**: {r['app_answer']}")
            report.append(f"* **Failure Reason**: `{r['app_judgment']['failure_reason']}`")
            report.append(f"* **Judge Analysis**: *{r['app_judgment']['analysis']}*")

    report.append("\n### 🌐 StreamAssist (Federated) Actual Failures")
    sa_fail_list = []
    for r in results:
        j = r["streamassist_judgment"]
        if not j["factual_correctness"] and j["failure_reason"] != "rigid_matching_false_negative":
            sa_fail_list.append(r)

    if not sa_fail_list:
        report.append("\n*No actual factual failures or missing data detected!*")
    else:
        for r in sa_fail_list:
            report.append(f"\n#### [{r['id']}] {r['query']}")
            report.append(f"* **Ground Truth Answer**: {r['ground_truth_answer']}")
            report.append(f"* **StreamAssist Answer**: {r['streamassist_answer']}")
            report.append(f"* **Failure Reason**: `{r['streamassist_judgment']['failure_reason']}`")
            report.append(f"* **Judge Analysis**: *{r['streamassist_judgment']['analysis']}*")

    with open(out_file, "w") as f:
        f.write("\n".join(report))
    print(f"Markdown report written to: {out_file}")

if __name__ == "__main__":
    main()
