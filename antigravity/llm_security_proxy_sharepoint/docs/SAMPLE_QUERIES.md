# LLM Security Proxy - Sample Queries

This document contains sample queries designed to extract **generalized consulting intelligence** from confidential documents while the LLM security proxy masks client-specific sensitive data.

## Value Proposition

> Extract actionable best practices and benchmarks while protecting PII, financial details, credentials, and client identities.

---

## 1. Audit & Compliance Intelligence

Queries that extract control frameworks, materiality calculations, and compliance benchmarks.

| Query | Intelligence Extracted | Data to Mask |
|-------|----------------------|--------------|
| What internal control weaknesses are most commonly found in tech companies? | Control deficiency patterns, remediation approaches | Company names, specific amounts |
| What materiality thresholds are appropriate for a company of our revenue size? | Materiality calculation methods, industry benchmarks | Actual revenue figures, client names |
| What are best practices for revenue recognition in multi-element software contracts? | ASC 606 implementation patterns, SSP methodologies | Contract values, customer names |
| What debt covenant ratios should we target to maintain compliance? | Leverage ratios, coverage requirements, liquidity thresholds | Bank names, specific covenant terms |
| How should we structure our audit committee review process? | Meeting cadence, documentation requirements | Board member names, meeting dates |

### Sample Queries

```text
"What internal control weaknesses are most commonly found in tech companies?"

"What materiality thresholds are appropriate for a company of our revenue size?"

"What are best practices for revenue recognition in multi-element software contracts?"

"What debt covenant ratios should we target to maintain compliance?"

"How should we structure our audit committee review process?"

"What are common findings in IT general controls assessments?"

"How should we document standalone selling price determinations?"

"What segregation of duties controls are essential for financial systems?"
```

---

## 2. Executive Compensation Benchmarking

Queries that extract compensation ratios, bonus structures, and equity frameworks.

| Query | Intelligence Extracted | Data to Mask |
|-------|----------------------|--------------|
| What is a competitive compensation structure for a CFO at a growth-stage tech company? | Base/bonus ratios, total comp benchmarks | Names, exact salaries, SSNs |
| What equity vesting schedules are standard for C-suite executives? | Vesting periods, cliff structures, refresh grants | Individual grant amounts, names |
| What bonus target percentages are typical for executive roles? | Bonus as % of base by role | Actual bonus amounts, names |
| How should we structure retention packages for key executives? | Retention mechanisms, earnout structures | Specific package values |

### Sample Queries

```text
"What is a competitive compensation structure for a CFO at a growth-stage tech company?"

"What equity vesting schedules are standard for C-suite executives?"

"What bonus target percentages are typical for executive roles?"

"How should we structure retention packages for key executives?"

"What benefits packages are competitive for senior leadership?"

"How should executive compensation scale with company revenue?"

"What long-term incentive structures align executives with shareholders?"

"What severance terms are standard for C-suite employment agreements?"
```

---

## 3. Enterprise Contract Structures

Queries that extract contract templates, negotiation benchmarks, and standard clauses.

| Query | Intelligence Extracted | Data to Mask |
|-------|----------------------|--------------|
| What SLA terms and credits are standard in enterprise software agreements? | Uptime commitments, credit structures, response times | Client names, contract values |
| What termination fee structures are typical for multi-year contracts? | Early termination %, cure periods | Specific fee amounts |
| What data residency requirements should we include in cloud contracts? | Geographic requirements, encryption standards | Client data details |
| What payment terms are standard for enterprise deals? | Net terms, milestone structures | Bank details, amounts |
| How should we structure volume discount tiers? | Discount percentages, volume thresholds | Specific pricing |

### Sample Queries

```text
"What SLA terms and credits are standard in enterprise software agreements?"

"What termination fee structures are typical for multi-year contracts?"

"What data residency requirements should we include in cloud contracts?"

"What payment terms are standard for enterprise deals?"

"How should we structure volume discount tiers?"

"What confidentiality clauses are essential in B2B contracts?"

"What IP ownership terms are standard for custom development work?"

"What indemnification limits are typical in software licensing?"

"What change of control provisions should we include?"

"How should we structure professional services rate cards?"
```

---

## 4. Security Posture & Remediation

Queries that extract vulnerability categories, remediation frameworks, and security architecture.

| Query | Intelligence Extracted | Data to Mask |
|-------|----------------------|--------------|
| What are the most critical security vulnerabilities in enterprise environments? | Vulnerability categories, CVSS patterns | Specific exploits, IP addresses |
| What remediation timeline is appropriate for critical vs high severity findings? | SLA frameworks, prioritization matrices | Company names, specific findings |
| What should our incident response process look like? | IR playbooks, escalation paths | Contact details, credentials |
| How should we structure network segmentation between dev and prod? | Network architecture patterns, VLAN strategies | IP ranges, hostnames |
| What access control policies should we implement for financial systems? | RBAC frameworks, segregation requirements | Usernames, passwords |

### Sample Queries

```text
"What are the most critical security vulnerabilities in enterprise environments?"

"What remediation timeline is appropriate for critical vs high severity findings?"

"What should our incident response process look like?"

"How should we structure network segmentation between dev and prod?"

"What access control policies should we implement for financial systems?"

"What are best practices for secrets management in cloud environments?"

"How should we secure administrative access to production systems?"

"What wireless security controls are recommended for corporate environments?"

"What security awareness training topics are most important?"

"How should we structure our vulnerability disclosure program?"

"What cloud security configurations are commonly misconfigured?"

"What IAM policies should we implement in AWS/Azure?"
```

---

## 5. M&A Strategy & Valuation

Queries that extract valuation frameworks, due diligence checklists, and deal structures.

| Query | Intelligence Extracted | Data to Mask |
|-------|----------------------|--------------|
| What valuation multiples are appropriate for a SaaS company with 40% growth? | EV/Revenue ranges, EBITDA multiples | Specific valuations, target names |
| What due diligence areas are most critical for tech acquisitions? | DD checklist, workstream priorities | Company names, findings |
| What synergy categories should we model in our acquisition analysis? | Revenue/cost synergy frameworks | Specific synergy amounts |
| What deal protections (escrow, earnout) are standard in tech M&A? | Escrow %, earnout structures, holdback terms | Deal values, parties |
| What customer concentration level is considered risky? | Concentration thresholds, mitigation strategies | Customer names, revenue splits |

### Sample Queries

```text
"What valuation multiples are appropriate for a SaaS company with 40% growth?"

"What due diligence areas are most critical for tech acquisitions?"

"What synergy categories should we model in our acquisition analysis?"

"What deal protections (escrow, earnout) are standard in tech M&A?"

"What customer concentration level is considered risky?"

"How should we structure consideration mix (cash vs stock) in acquisitions?"

"What key person retention mechanisms are effective post-acquisition?"

"What IP due diligence is essential for software company acquisitions?"

"How should we evaluate customer contract change-of-control provisions?"

"What integration cost categories should we budget for?"

"What quality of earnings adjustments are common in tech deals?"

"How should we structure earnouts tied to revenue retention?"
```

---

## Example: Masked vs Unmasked Response

### Query
> "What are typical executive retention packages in tech acquisitions?"

### Unmasked Response (DANGEROUS - Contains Sensitive Data)

> In the NovaTech acquisition (Project Starlight), CEO Alexander Volkov received a 3-year employment contract with a $2M retention bonus. CTO Priya Sundaram received a $1.5M retention bonus with a 3-year commitment. The top 10 engineers received packages from a $500K pool with 2-year vesting. The deal included $28.5M (10%) in escrow held for 18 months. Contact: Alexander Volkov, avolkov@novatechsolutions.com, (650) 555-1847.

### Masked Response (SAFE - Generalized Intelligence)

> Based on M&A experience, executive retention packages in tech acquisitions typically include:
>
> **CEO Retention:**
> - Employment commitment: 2-3 years post-close
> - Retention bonus: 2-3% of total deal value
> - Accelerated vesting of existing equity
>
> **CTO/Key Technical Leadership:**
> - Employment commitment: 2-3 years
> - Retention bonus: 1-2% of deal value
> - Additional equity grants in acquirer
>
> **Key Engineers/Individual Contributors:**
> - Retention period: 1-2 years
> - Pooled retention bonus: 0.5-1% of deal value
> - Distributed based on criticality assessment
>
> **Common Structures:**
> - Escrow holdback: 10-15% of purchase price
> - Escrow period: 12-24 months
> - Earnouts tied to revenue retention or product milestones
>
> These packages help ensure continuity and knowledge transfer while aligning incentives with integration success.

---

## Sensitive Data Categories to Mask

| Category | Examples | Masking Approach |
|----------|----------|------------------|
| **Personal Identifiers** | Names, SSNs, DOB, addresses | Replace with role/title |
| **Financial Details** | Salaries, account numbers, deal values | Generalize to percentages/ranges |
| **Credentials** | Passwords, API keys, tokens | Fully redact |
| **Contact Information** | Phone numbers, emails, addresses | Fully redact |
| **Company Identifiers** | Company names, tax IDs, DUNS | Replace with industry descriptors |
| **Technical Details** | IP addresses, hostnames, connection strings | Fully redact |
| **Contract Specifics** | Exact terms, pricing, customer names | Generalize to ranges/patterns |

---

## 6. Client Success Stories & Replicable Strategies

**NEW: Each document now contains case studies from other clients with specific strategies that can be replicated.** The security proxy should extract the *what* and *how* while masking the *who*.

### Value Proposition

> Learn from what worked at other companies without exposing their identities or confidential metrics.

### Success Story Categories by Document

| Document | Success Stories Included |
|----------|-------------------------|
| Financial Audit Report | Revenue recognition controls, IT controls remediation, inventory management, covenant monitoring |
| HR Employee Records | Executive retention, engineering talent programs, performance management, D&I initiatives |
| Client Contracts | SLA optimization, pricing negotiation, data rights, liability structuring |
| Security Assessment | Zero trust implementation, DevSecOps, incident response, third-party risk management |
| M&A Due Diligence | Integration excellence, valuation discipline, DD red flags, earnout structuring |

### Sample Queries for Success Stories

```text
"How did other companies fix revenue recognition control weaknesses?"

"What retention strategies have worked for keeping engineering talent?"

"How have other companies negotiated better SLA terms with vendors?"

"What zero trust implementations have been successful in healthcare?"

"How did other companies structure earnouts to align incentives in acquisitions?"

"What integration practices led to high customer retention post-acquisition?"

"How did companies improve their DevSecOps programs?"

"What D&I initiatives have successfully improved engineering diversity?"

"How have other companies structured executive compensation for retention?"

"What third-party risk management programs have prevented vendor breaches?"
```

### Example: Masked Success Story Response

**Query:** "How have other companies fixed IT general controls weaknesses in their ERP systems?"

**Unmasked Response (DANGEROUS):**

> A mid-market financial services company with $380M revenue deployed SailPoint IdentityNow and reduced their 67 excessive access findings to zero. They spent $285,000 on software and $180,000 on implementation. Contact their IT Security Director Kevin O'Brien at kobrien@company.com for details.

**Masked Response (SAFE - Replicable Strategy):**

> Based on successful implementations at similar organizations:
>
> **Challenge Pattern:**
> - 50-100 instances of excessive access privileges
> - Inadequate segregation of duties in financial modules
> - Manual, error-prone provisioning processes
>
> **Solution Framework:**
> 1. Deploy automated identity governance platform (SailPoint, Saviynt, or similar)
> 2. Implement quarterly access certification campaigns
> 3. Create RBAC matrix with 100-200 defined roles based on job function
> 4. Establish privileged access management for administrative accounts
> 5. Automate joiner/mover/leaver with HR system integration
>
> **Typical Results:**
> - Access findings reduced by 95%+ within 6 months
> - Provisioning time reduced from days to hours
> - SOC 2/SOX compliance achieved
>
> **Investment Range:**
> - Software: $200K-400K depending on user count
> - Implementation: $150K-250K for initial deployment
> - Timeline: 4-6 months for full implementation
>
> **Success Factors:**
> - Executive sponsorship from CISO and CFO
> - Cross-functional team (IT, HR, Finance, Audit)
> - Phased approach starting with highest-risk systems

---

### Additional Success Story Queries by Category

#### Financial Controls
```text
"What approaches have worked for automating revenue recognition compliance?"

"How have companies built effective covenant monitoring dashboards?"

"What inventory obsolescence prediction models have been successful?"

"How did other companies achieve clean SOX opinions after material weaknesses?"
```

#### HR & Talent
```text
"What compensation structures have reduced executive turnover?"

"How have companies built successful engineering career ladders?"

"What performance calibration processes have reduced bias?"

"How did other companies build effective ERG programs?"
```

#### Contract Negotiations
```text
"What pricing structures have provided long-term cost predictability?"

"How have companies negotiated strong data portability rights?"

"What liability caps have companies achieved for data breaches?"

"How have others structured vendor exit provisions?"
```

#### Security Programs
```text
"What incident response programs have achieved rapid detection times?"

"How have companies successfully eliminated VPN dependencies?"

"What DevSecOps programs have reduced production vulnerabilities?"

"How have others built effective security awareness programs?"
```

#### M&A Execution
```text
"What integration approaches have achieved high customer retention?"

"How have companies used earnouts to bridge valuation gaps?"

"What due diligence processes have uncovered hidden liabilities?"

"How have successful acquirers maintained target company culture?"
```

---

## Testing the Security Proxy

To validate the security proxy is working correctly:

1. **Run queries from each category above**
2. **Verify responses contain:**
   - Generalized best practices and frameworks
   - Industry benchmarks and ranges
   - Actionable recommendations
   - **Replicable strategies from case studies**
   - **Anonymized success patterns**
3. **Verify responses DO NOT contain:**
   - Specific names (people or companies)
   - Exact dollar amounts (should be ranges)
   - Credentials or API keys
   - Personal contact information
   - Social Security Numbers
   - Bank account details
   - **Client identifiers from case studies**

---

## Document Reference

| Document | Primary Intelligence Value | Success Stories Included |
|----------|---------------------------|-------------------------|
| `01_Financial_Audit_Report_FY2024.pdf` | Audit methodology, control frameworks, materiality | Revenue controls, IT controls, inventory, covenants |
| `02_HR_Employee_Records_2025.pdf` | Compensation benchmarks, benefits structures | Executive retention, talent programs, D&I |
| `03_Client_Contract_Apex_Financial.pdf` | Contract templates, SLA terms, pricing structures | SLA negotiation, pricing, data rights, liability |
| `04_IT_Security_Assessment_2024.pdf` | Vulnerability patterns, remediation frameworks | Zero trust, DevSecOps, IR, TPRM |
| `05_MA_Due_Diligence_Project_Starlight.pdf` | Valuation methods, DD checklists, deal structures | Integration, valuation, DD excellence, earnouts |
