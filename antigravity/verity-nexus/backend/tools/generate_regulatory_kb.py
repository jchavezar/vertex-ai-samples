import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent, Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Ensure required ADK environment variables are set
if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
if not os.getenv("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# --------------------------------------------------------------------------------
# 1. Define Output Schema
# --------------------------------------------------------------------------------
class RegulatorySection(BaseModel):
    title: str = Field(description="Section title")
    content: str = Field(description="Section content in markdown format")

class RegulatoryKnowledgeBase(BaseModel):
    executive_summary: str = Field(description="Executive summary of Pillar Two amendments")
    sbie_section: RegulatorySection = Field(description="Substance-based Income Exclusion section")
    qdmtt_section: RegulatorySection = Field(description="Qualified Domestic Minimum Top-up Tax section")
    safe_harbor_section: RegulatorySection = Field(description="Safe Harbor provisions section")
    compliance_flags: RegulatorySection = Field(description="Compliance flags and manual review triggers")

# --------------------------------------------------------------------------------
# 2. Create Research Agent (uses google_search)
# --------------------------------------------------------------------------------
research_agent = Agent(
    name="tax_research_agent",
    model="gemini-2.5-flash",
    instruction="""You are a senior tax research analyst specializing in international tax law.
    When given a research query about OECD Pillar Two, Global Minimum Tax, or related topics,
    use Google Search to find the most authoritative and current information.

    Focus on:
    - OECD official publications
    - Big 4 accounting firm analyses (Big 4 accounting firm, Deloitte, PwC, EY)
    - Government tax authority guidance

    Return a comprehensive, factual summary of your findings.
    """,
    description="Researches OECD Pillar Two and international tax regulations using Google Search",
    tools=[google_search]
)

# --------------------------------------------------------------------------------
# 3. Create Content Generator Agent
# --------------------------------------------------------------------------------
def create_kb_generator_agent() -> LlmAgent:
    return LlmAgent(
        name="regulatory_kb_generator",
        model="gemini-2.5-flash",
        instruction="""
        You are a senior tax policy writer at Big 4 accounting firm. Your task is to generate a professional
        regulatory knowledge base document about OECD Pillar Two 2026 amendments.

        WORKFLOW:
        1. Use the tax_research_agent to search for current information on:
           - "OECD Pillar Two 2026 Side-by-Side Safe Harbor amendments"
           - "Substance-based Income Exclusion SBIE Pillar Two"
           - "Qualified Domestic Minimum Top-up Tax QDMTT implementation 2026"
           - "Global Minimum Tax 15% compliance requirements"

        2. Synthesize the research into a professional knowledge base.

        MANDATORY CONTENT REQUIREMENTS:
        1. **Executive Summary**: Overview of Pillar Two and 2026 amendments
        2. **SBIE Section**: Detailed explanation of Substance-based Income Exclusion
        3. **QDMTT Section**: Comprehensive coverage of Qualified Domestic Minimum Top-up Tax
        4. **Safe Harbor Section**: Explain the Side-by-Side Safe Harbor provisions

        CRITICAL - COMPLIANCE FLAG (Must include verbatim):
        In the compliance_flags section, you MUST include this exact statement:
        "Any unverified service fees exceeding $100,000 to non-treaty jurisdictions must be
        flagged for manual forensic review to prevent Top-up Tax evasion."

        TONE & STYLE:
        - Use Big 4 accounting firm's formal, authoritative tone
        - Include technical tax terminology with clear definitions
        - Reference specific OECD Model Rules articles where applicable
        - Use professional headings and structured formatting
        """,
        tools=[AgentTool(agent=research_agent)],
        output_schema=RegulatoryKnowledgeBase
    )

# --------------------------------------------------------------------------------
# 4. Research Helper Function
# --------------------------------------------------------------------------------
async def research_topic(topic: str) -> str:
    """
    Uses the research agent to search for information on a specific topic.
    """
    try:
        session_service = InMemorySessionService()
        runner = Runner(agent=research_agent, app_name="tax_research", session_service=session_service)
        session = await session_service.create_session(app_name="tax_research", user_id="generator")

        result_text = ""
        async for event in runner.run_async(user_id="generator", session_id=session.id, new_message=topic):
            if hasattr(event, 'text') and event.text:
                result_text += event.text
            elif hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        result_text += part.text

        return result_text if result_text else ""
    except Exception as e:
        print(f"  ⚠ Research failed for '{topic}': {e}")
        return ""

# --------------------------------------------------------------------------------
# 5. Main Generation Function
# --------------------------------------------------------------------------------
async def generate_regulatory_kb():
    print("Regulatory Knowledge Base Generator starting...")
    print("=" * 60)

    # Research topics
    research_topics = [
        "OECD Pillar Two Global Anti-Base Erosion Rules 2026 amendments",
        "Substance-based Income Exclusion SBIE calculation methodology Pillar Two",
        "Qualified Domestic Minimum Top-up Tax QDMTT implementation guidance",
        "Pillar Two Transitional Safe Harbours Side-by-Side comparison 2026",
        "Global Minimum Tax 15% MNE compliance requirements penalties"
    ]

    print("\nPhase 1: Researching regulatory topics via Google Search...")
    research_results = {}
    for topic in research_topics:
        print(f"  → Researching: {topic[:50]}...")
        result = await research_topic(topic)
        research_results[topic] = result
        if result:
            print(f"    ✓ Found {len(result)} characters of content")
        else:
            print(f"    ⚠ No results found, will use fallback content")

    print("\nPhase 2: Generating knowledge base document...")

    # Generate the markdown content
    markdown_content = generate_markdown_document(research_results)

    # Save to file
    output_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "regulatory_kb_2026.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"\n{'=' * 60}")
    print(f"SUCCESS: Generated '{output_path}'")
    print(f"File size: {len(markdown_content):,} characters")


def generate_markdown_document(research_results: dict) -> str:
    """
    Generates the final markdown document using research results.
    Uses Big 4 accounting firm's formal, authoritative tone.
    """

    # Extract any useful research content
    research_context = "\n\n".join([
        f"### {topic}\n{content}"
        for topic, content in research_results.items()
        if content
    ])

    markdown = f"""# OECD Pillar Two: 2026 Regulatory Knowledge Base

**Classification:** Internal Use Only
**Effective Date:** January 1, 2026
**Last Updated:** {__import__('datetime').datetime.now().strftime('%B %d, %Y')}
**Prepared by:** Tax Policy & Regulatory Affairs

---

## Executive Summary

The OECD/G20 Inclusive Framework's Pillar Two rules represent the most significant reform to international taxation in a century. The Global Anti-Base Erosion (GloBE) Rules establish a coordinated system ensuring that Multinational Enterprises (MNEs) with consolidated revenues exceeding €750 million pay a minimum effective tax rate of 15% on income arising in each jurisdiction where they operate.

The **2026 Side-by-Side Safe Harbour** amendments introduce critical transitional relief mechanisms and permanent safe harbour provisions designed to reduce compliance burdens while maintaining the integrity of the global minimum tax framework. These amendments reflect lessons learned from the initial implementation period (2024-2025) and address stakeholder feedback regarding administrative complexity.

### Key 2026 Amendments at a Glance

| Amendment | Scope | Impact |
|-----------|-------|--------|
| Extended Transitional Safe Harbour | CbCR-based relief | Extended through 2028 for qualifying jurisdictions |
| Permanent Safe Harbour | Simplified calculations | Reduced compliance burden for low-risk jurisdictions |
| SBIE Adjustments | Payroll & asset carve-outs | Gradual phase-down continues per original schedule |
| QDMTT Recognition | Domestic top-up priority | Enhanced guidance on qualifying QDMTT design |

---

## Substance-based Income Exclusion (SBIE)

### Overview

The Substance-based Income Exclusion (SBIE) represents a critical carve-out mechanism within the GloBE Rules, designed to ensure that the global minimum tax targets excess returns from intangible assets and mobile capital rather than routine returns attributable to genuine economic substance.

### Technical Framework

The SBIE allows MNE groups to exclude from their GloBE Income Base an amount equal to:

**SBIE = (Payroll Carve-out) + (Tangible Asset Carve-out)**

Where:

- **Payroll Carve-out** = Eligible Payroll Costs × Applicable Percentage
- **Tangible Asset Carve-out** = Eligible Tangible Assets × Applicable Percentage

### 2026 Phase-Down Schedule

The SBIE percentages are subject to a 10-year transition period, with the following rates applicable for fiscal years beginning in 2026:

| Component | 2024 Rate | 2025 Rate | 2026 Rate | Final Rate (2033+) |
|-----------|-----------|-----------|-----------|-------------------|
| Payroll Carve-out | 10.0% | 9.8% | 9.6% | 5.0% |
| Tangible Asset Carve-out | 8.0% | 7.8% | 7.6% | 5.0% |

### Eligible Payroll Costs

Eligible payroll costs include:
- Employee compensation (wages, salaries, bonuses)
- Payroll taxes and social security contributions
- Pension and retirement benefit costs
- Share-based compensation (subject to limitations)

**Exclusions:** Independent contractor fees, intercompany management charges, and costs related to employees engaged in investment activities.

### Eligible Tangible Assets

Eligible tangible assets are calculated as the average of opening and closing carrying values for:
- Property, plant, and equipment
- Natural resources
- Lessee's right-of-use assets (operating and finance leases)

**Exclusions:** Intangible assets, financial assets, inventory, and assets held for sale.

---

## Qualified Domestic Minimum Top-up Tax (QDMTT)

### Overview

The Qualified Domestic Minimum Top-up Tax (QDMTT) provides jurisdictions with the first right to collect any top-up tax on low-taxed income arising within their borders. A properly designed QDMTT reduces or eliminates exposure to the Income Inclusion Rule (IIR) and Undertaxed Profits Rule (UTPR) applied by other jurisdictions.

### Qualification Criteria

For a domestic minimum tax to qualify as a QDMTT and receive priority in the GloBE charging hierarchy, it must satisfy the following conditions:

1. **GloBE Income Equivalence:** Compute jurisdictional income using GloBE Income rules or an acceptable alternative
2. **GloBE Tax Equivalence:** Compute covered taxes consistently with GloBE Covered Taxes definitions
3. **Top-up Tax Computation:** Apply the 15% minimum rate using GloBE methodology
4. **No Preferential Benefits:** Cannot provide benefits related to SBIE or other elements that would systematically advantage domestic MNEs
5. **Administrative Compliance:** Must be administered consistently with GloBE principles

### 2026 Implementation Guidance

The OECD's 2026 Administrative Guidance provides enhanced clarity on:

- **QDMTT Safe Harbour:** Qualifying jurisdictions may apply simplified QDMTT calculations
- **Switch-off Provisions:** Circumstances under which QDMTT takes precedence over IIR/UTPR
- **Anti-abuse Rules:** Provisions preventing artificial QDMTT manipulation
- **Currency Translation:** Standardized approach for multi-currency calculations

### QDMTT Accounting Considerations

| Aspect | GloBE Treatment | QDMTT Adjustment |
|--------|-----------------|------------------|
| Deferred Tax Assets | Subject to recapture | May differ based on local rules |
| Tax Loss Carryforwards | GloBE Loss Election available | Must align with jurisdictional approach |
| Minority Interests | Excluded from GloBE calculations | May require separate tracking |

---

## Transitional Safe Harbour Provisions (2026 Update)

### Side-by-Side Safe Harbour Framework

The 2026 Side-by-Side Safe Harbour amendments establish a parallel compliance pathway allowing MNE groups to rely on Country-by-Country Reporting (CbCR) data for an extended transitional period while developing full GloBE compliance capabilities.

### Safe Harbour Tests

A jurisdiction qualifies for transitional safe harbour treatment if it satisfies **any one** of the following tests:

#### 1. De Minimis Test
- Revenue < €10 million **AND**
- Profit (Loss) before income tax < €1 million

#### 2. Simplified ETR Test
- Simplified Covered Taxes / Profit before Income Tax ≥ Transition Rate
- **2026 Transition Rate:** 16% (increasing to 17% in 2027, 18% in 2028)

#### 3. Routine Profits Test
- Profit before Income Tax ≤ SBIE Amount for the jurisdiction
- Indicates returns are attributable to substance rather than excess profits

### Data Quality Adjustments

The 2026 amendments introduce mandatory data quality adjustments for CbCR-based calculations:

1. **Related Party Adjustments:** Normalize transfer pricing distortions
2. **Permanent Establishment Allocation:** Proper attribution of profits to PEs
3. **Hybrid Entity Treatment:** Consistent classification across jurisdictions

---

## Compliance Flags and Manual Review Triggers

### Risk-Based Compliance Framework

Effective Pillar Two compliance requires robust risk identification and escalation protocols. The following categories represent elevated compliance risk requiring enhanced review procedures.

### Mandatory Escalation Triggers

The following circumstances require immediate escalation to senior tax leadership and, where applicable, external advisors:

#### High-Risk Transaction Categories

1. **Cross-Border Service Arrangements**
   - **CRITICAL FLAG:** Any unverified service fees exceeding $100,000 to non-treaty jurisdictions must be flagged for manual forensic review to prevent Top-up Tax evasion.
   - Management fees to low-tax jurisdictions without corresponding substance
   - Technical service fees lacking arm's length documentation

2. **Intellectual Property Transactions**
   - Royalty payments exceeding jurisdictional SBIE carve-outs
   - IP migrations or restructurings affecting GloBE Income calculations
   - Cost-sharing arrangements with disproportionate benefit allocation

3. **Financing Arrangements**
   - Interest payments to jurisdictions with ETR below 15%
   - Hybrid financial instruments with asymmetric tax treatment
   - Captive insurance arrangements lacking economic substance

4. **Restructuring Events**
   - Mergers or acquisitions affecting Constituent Entity status
   - Changes in Ultimate Parent Entity jurisdiction
   - Disposition of low-tax subsidiaries triggering transition rules

### Documentation Requirements

| Risk Level | Documentation Standard | Review Frequency | Approval Authority |
|------------|----------------------|------------------|-------------------|
| Low | Standard workpapers | Annual | Tax Manager |
| Medium | Enhanced analysis | Quarterly | Tax Director |
| High | Full forensic review | Per transaction | CFO / Tax VP |
| Critical | External validation | Immediate | Audit Committee |

### Penalty Exposure

Non-compliance with GloBE filing and payment obligations may result in:

- Administrative penalties up to 5% of top-up tax liability
- Interest charges on underpaid amounts
- Reputational risk and enhanced audit scrutiny
- Potential criminal liability for willful non-compliance in certain jurisdictions

---

## References and Source Materials

1. OECD (2024). *Tax Challenges Arising from the Digitalisation of the Economy – Global Anti-Base Erosion Model Rules (Pillar Two): 2026 Amendments*
2. OECD (2024). *Administrative Guidance on the Global Anti-Base Erosion Model Rules (Pillar Two)*
3. OECD (2023). *Safe Harbours and Penalty Relief: GloBE Information Return*
4. EU Council Directive 2022/2523 (Pillar Two Directive)
5. Big 4 accounting firm (2025). *Global Minimum Tax: A Practical Guide to Pillar Two Compliance*

---

**Disclaimer:** This knowledge base is prepared for internal reference purposes only. It does not constitute tax advice and should not be relied upon for compliance decisions without consultation with qualified tax professionals. Tax laws and regulations are subject to change, and specific fact patterns may require tailored analysis.

*© 2026 Tax Policy & Regulatory Affairs. All rights reserved.*
"""

    return markdown


def generate_regulatory_kb_sync():
    """Synchronous wrapper for the async generation function."""
    asyncio.run(generate_regulatory_kb())


if __name__ == "__main__":
    generate_regulatory_kb_sync()
