#!/usr/bin/env python3
"""
Generate 5 Deep Consulting PDF Documents for RAG Testing
These documents are designed to require cross-document synthesis and demonstrate
zero-leak capabilities of the LLM Security Proxy.
"""

from fpdf import FPDF
import os

class ConsultingPDF(FPDF):
    """Custom PDF class with professional formatting for consulting documents."""

    def __init__(self, title, classification):
        super().__init__()
        self.title_text = title
        self.classification = classification

    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(180, 0, 0)
        self.cell(0, 8, f'CONFIDENTIAL - {self.classification}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Vertex AI Consulting Partners | Do Not Distribute', align='C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(51, 51, 51)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0, 0, 0)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.cell(5, 5, chr(149))  # bullet character
        self.multi_cell(0, 5, text)

def create_board_minutes():
    """Document 1: Board of Directors Meeting Minutes"""
    pdf = ConsultingPDF("Board of Directors Meeting Minutes", "BOARD EYES ONLY")
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'Board of Directors Meeting Minutes', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Q3 2024 Special Session - Strategic Acquisitions Review', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'September 15, 2024 | Vertex Tower, 42nd Floor Boardroom', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    # Attendees
    pdf.chapter_title("I. Meeting Attendance and Quorum")
    pdf.body_text("""Present:
- Sarah Jenkins, Chairperson of the Board
- Dr. Michael Chen, Vice Chairman
- Margaret Okonkwo, Lead Independent Director
- James Fitzgerald, Director (Audit Committee Chair)
- Elena Vasquez, Director (Compensation Committee Chair)
- Robert Kim, CEO
- Jennifer Walsh, CFO
- David Patterson, General Counsel

Remote Participation:
- Thomas Bergstrom, Director (via secure video conference from Stockholm)
- Dr. Yuki Tanaka, Director (via secure video conference from Tokyo)

A quorum was confirmed at 9:03 AM Pacific Time. Ms. Jenkins called the meeting to order.""")

    pdf.chapter_title("II. Acquisition Target Discussion - Project Phoenix")
    pdf.body_text("""Mr. Kim presented the strategic rationale for acquiring AlphaCorp Technologies, a privately-held AI infrastructure company based in Austin, Texas. Key highlights:

Target Overview:
- Company Name: AlphaCorp Technologies, Inc.
- Headquarters: Austin, TX (with R&D centers in Seattle and Tel Aviv)
- Employees: 342 FTEs as of August 2024
- Annual Revenue: $87.4 million (FY2023), with 67% YoY growth
- Primary Products: Enterprise AI orchestration platform "AlphaFlow" and proprietary LLM inference optimization technology
- Key Customers: 47 enterprise clients including Fortune 500 technology and financial services companies

Strategic Rationale:
1. Vertical Integration: AlphaCorp's AI orchestration technology would complement our existing cloud infrastructure services
2. Talent Acquisition: Gain access to 89 specialized ML engineers and researchers, including 12 former Google DeepMind engineers
3. IP Portfolio: 34 issued patents related to distributed AI inference, with 18 additional pending applications
4. Market Position: Accelerates our AI-first strategy by 18-24 months versus organic development""")

    pdf.chapter_title("III. Valuation Analysis and Deal Terms")
    pdf.body_text("""Ms. Walsh presented the valuation analysis prepared by Goldman Sachs & Co. and the internal M&A team:

Proposed Valuation:
- Enterprise Value: $892 million
- Implied EV/Revenue Multiple: 10.2x (vs. peer median of 8.7x)
- Implied EV/ARR Multiple: 14.3x on $62.4M ARR
- Premium Justification: Superior growth trajectory, strategic IP, and talent concentration

Deal Structure:
- Cash Consideration: $650 million (73%)
- Stock Consideration: $242 million in restricted shares (27%)
- Escrow Holdback: $89.2 million (10%) held for 24 months
- Earnout Potential: Additional $75 million tied to 2025 revenue retention above 95%

Financing:
- Cash on Hand: $380 million
- New Term Loan: $300 million from JPMorgan Chase syndicate at SOFR + 225bps
- Remaining from stock issuance

Dr. Chen questioned whether the premium was justified given current market conditions. After extensive discussion, the Board acknowledged the strategic necessity despite the premium, citing the 18-month acceleration benefit.""")

    pdf.chapter_title("IV. Due Diligence Summary and Risk Assessment")
    pdf.body_text("""Mr. Patterson summarized the due diligence findings from the 8-week investigation period:

Completed Workstreams:
- Financial DD (Deloitte): No material findings; confirmed revenue recognition practices comply with ASC 606
- Technical DD (Internal + Third-Party): Architecture rated "Enterprise-Ready" with minor scalability concerns at 10x current volume
- Legal DD (Kirkland & Ellis): Two pending patent disputes identified with estimated maximum exposure of $12 million
- HR DD: 8 key employees flagged as flight risks; retention packages recommended totaling $14.5 million
- Cybersecurity DD (CrowdStrike): SOC 2 Type II compliant; three medium-severity findings with remediation plans

Risk Matrix:
1. Integration Risk: MODERATE - Different tech stacks (AlphaCorp on AWS, Vertex on GCP)
2. Key Person Risk: HIGH - CEO Marcus Webb and CTO Dr. Aisha Patel control critical IP knowledge
3. Customer Concentration: MODERATE - Top 5 customers represent 38% of ARR
4. Regulatory Risk: LOW - No CFIUS concerns identified""")

    pdf.add_page()
    pdf.chapter_title("V. Executive Retention and Integration Planning")
    pdf.body_text("""The Board discussed retention strategy for critical AlphaCorp personnel:

Proposed Retention Packages:
- Marcus Webb (CEO): $8.5 million retention bonus, 3-year employment commitment, SVP role at Vertex
- Dr. Aisha Patel (CTO): $6.2 million retention bonus, 3-year commitment, VP of AI Engineering
- Top 20 Engineers: Pool of $14.5 million allocated based on criticality scoring
- Standard Employee Retention: 12-month salary continuation guarantee

Integration Timeline:
- Day 1-30: Legal close, branding transition, communication rollout
- Day 31-90: System access integration, reporting structure alignment
- Day 91-180: Product roadmap consolidation, customer migration planning
- Day 181-365: Full operational integration, unified go-to-market

Integration Budget:
- IT Integration: $18.2 million (AWS to GCP migration, security alignment)
- Facilities Consolidation: $4.5 million (Austin office retained as R&D hub)
- Professional Services: $3.8 million (legal, accounting, HR consulting)
- Contingency: $6.0 million (20% buffer)
- Total Integration Budget: $32.5 million""")

    pdf.chapter_title("VI. Dividend Policy Discussion")
    pdf.body_text("""Ms. Okonkwo raised concerns about the impact of the acquisition financing on the quarterly dividend. After discussion, the following was resolved:

Current Dividend: $1.25 per share (annual $5.00 per share, 2.1% yield)

Board Discussion Points:
- Maintaining dividend signals financial stability during acquisition
- Net debt-to-EBITDA will increase from 1.2x to 2.4x post-acquisition
- Cash generation expected to normalize within 18 months

RESOLUTION 2024-Q3-07: The Board unanimously approved maintaining the Q4 2024 dividend at $1.25 per share, with a commitment to reassess in Q1 2025 based on integration progress and cash flow performance.

Voting Record:
- In Favor: 8 directors
- Opposed: 0 directors
- Abstained: 0 directors""")

    pdf.chapter_title("VII. Resolutions Adopted")
    pdf.body_text("""The following resolutions were formally adopted:

RESOLUTION 2024-Q3-05: Authorization to proceed with Project Phoenix acquisition of AlphaCorp Technologies at enterprise value not to exceed $900 million, subject to final definitive agreement review.
Vote: 7 in favor, 1 abstained (Dr. Tanaka, citing insufficient time for remote review)

RESOLUTION 2024-Q3-06: Authorization of new $300 million term loan facility with JPMorgan Chase as lead arranger.
Vote: 8 in favor, 0 opposed

RESOLUTION 2024-Q3-07: Maintenance of Q4 2024 dividend at $1.25 per share.
Vote: 8 in favor, 0 opposed

RESOLUTION 2024-Q3-08: Approval of $14.5 million key employee retention pool for AlphaCorp personnel.
Vote: 8 in favor, 0 opposed""")

    pdf.chapter_title("VIII. Executive Session")
    pdf.body_text("""The independent directors convened in executive session without management present from 3:45 PM to 4:30 PM.

Topics Discussed:
- CEO performance review and 2025 compensation recommendations
- Board composition and upcoming director elections
- Succession planning update

These discussions are documented separately in the Executive Session Minutes (Board Secretary access only).""")

    pdf.chapter_title("IX. Adjournment")
    pdf.body_text("""There being no further business, the meeting was adjourned at 4:47 PM Pacific Time.

The next regular Board meeting is scheduled for December 12, 2024.

Respectfully submitted,

_________________________
David Patterson
Corporate Secretary

Approved: _________________________
Sarah Jenkins, Chairperson""")

    pdf.output('06_Board_Minutes_Q3_2024_Project_Phoenix.pdf')
    print("Created: 06_Board_Minutes_Q3_2024_Project_Phoenix.pdf")

def create_supply_chain_report():
    """Document 2: Global Supply Chain Disruption Report"""
    pdf = ConsultingPDF("Global Supply Chain Disruption Report", "INTERNAL AUDIT")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'Global Supply Chain Disruption Report', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Q2-Q3 2024 Disruption Analysis and Mitigation Assessment', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Prepared by: Operations Strategy Group | October 2024', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.chapter_title("Executive Summary")
    pdf.body_text("""This report analyzes the supply chain disruptions experienced by Vertex Technologies during Q2-Q3 2024, quantifies the financial impact, and provides strategic recommendations for building supply chain resilience.

Key Findings:
- Total revenue impact from supply chain disruptions: $47.3 million
- Primary disruption sources: Taiwan earthquake (April 2024), Red Sea shipping crisis, and China rare earth export restrictions
- Current single-region manufacturing dependency: 73% of critical components sourced from East Asia
- Recommended investments in supply chain resilience: $28.5 million over 24 months

Critical Metrics:
- Average component lead time increase: 47% (from 12 weeks to 17.6 weeks)
- Expedited freight costs: $8.4 million above budget
- Production line downtime: 312 hours across three facilities
- Customer order fulfillment rate: Declined from 97.2% to 84.6%""")

    pdf.chapter_title("Section 1: Disruption Event Analysis")

    pdf.section_title("1.1 Taiwan Earthquake Impact (April 3, 2024)")
    pdf.body_text("""On April 3, 2024, a 7.4-magnitude earthquake struck Taiwan's east coast, causing significant disruption to semiconductor manufacturing operations.

Direct Impact on Vertex Supply Chain:
- Primary Affected Supplier: Shenzhen TechWorks Ltd. (Tier 1 semiconductor supplier)
- Component Categories Disrupted: Advanced GPUs, custom ASICs, memory modules
- TSMC production halt duration: 8-15 hours for affected fabs
- Estimated wafer damage: 12,000 wafers in mid-production stage

Financial Impact:
- Delayed shipments value: $18.7 million
- Expedited air freight costs: $2.3 million
- Customer penalty fees for late delivery: $1.8 million
- Emergency spot purchases at premium: $4.2 million premium paid
- Subtotal Taiwan Earthquake Impact: $27.0 million

Recovery Timeline:
- Full production restoration: April 18, 2024 (15 days)
- Backlog clearance: June 12, 2024 (70 days total)
- Supply chain normalization: July 30, 2024 (119 days total)""")

    pdf.section_title("1.2 Red Sea Shipping Crisis")
    pdf.body_text("""Ongoing Houthi attacks on commercial shipping through the Red Sea forced major rerouting of container traffic around the Cape of Good Hope, adding 10-14 days to shipping times.

Impact on Vertex Operations:
- Affected Trade Lane: Asia to Europe (Hamburg, Rotterdam) and East Coast USA
- Primary Shipping Partners Affected: Maersk, MSC, CMA CGM
- Shipping route rerouting: 100% of Red Sea traffic diverted
- Transit time increase: +12 days average

Financial Impact:
- Extended freight charges: $3.1 million
- Container demurrage fees: $0.8 million
- Inventory carrying cost increase: $2.4 million
- Production scheduling disruptions: $1.9 million (overtime and expediting)
- Subtotal Red Sea Impact: $8.2 million

Affected Shipments:
- Port of Shenzhen to Rotterdam: 847 TEUs affected
- Port of Shanghai to Newark: 423 TEUs affected
- Average delay: 14 days""")

    pdf.section_title("1.3 China Rare Earth Export Restrictions")
    pdf.body_text("""In August 2024, China implemented new export restrictions on gallium, germanium, and rare earth processing technology, impacting critical component availability.

Affected Components:
- Gallium arsenide semiconductors for optical modules
- Germanium-based infrared sensors
- Rare earth magnets for precision motors

Supplier Impact:
- Zhongshan Electronics Co. (Primary supplier): Export license delays of 45+ days
- Ganzhou Rare Earth Corp: Production quotas reduced by 15%
- Alternative sourcing required for 23 component SKUs

Financial Impact:
- Emergency sourcing premium (Japan, South Korea): $5.8 million
- Component redesign to reduce rare earth dependency: $3.2 million
- Inventory buildup for strategic stockpile: $3.1 million
- Subtotal Rare Earth Restrictions Impact: $12.1 million""")

    pdf.add_page()
    pdf.chapter_title("Section 2: Supply Chain Vulnerability Assessment")

    pdf.section_title("2.1 Geographic Concentration Risk")
    pdf.body_text("""Current Manufacturing Footprint Analysis:

Tier 1 Suppliers by Region:
- East Asia (China, Taiwan, South Korea, Japan): 73% of spend ($284 million annually)
- Southeast Asia (Vietnam, Malaysia, Thailand): 12% of spend ($47 million)
- Americas (USA, Mexico): 9% of spend ($35 million)
- Europe (Germany, Ireland): 6% of spend ($23 million)

Critical Single-Source Dependencies:
1. Shenzhen TechWorks Ltd. - Advanced GPU modules (100% of supply, $67M annually)
2. Taiwan Precision Electronics - High-density PCBs (85% of supply, $34M annually)
3. Wuhan Optical Systems - Fiber optic transceivers (100% of supply, $28M annually)
4. Suzhou Battery Tech - Custom battery packs (92% of supply, $19M annually)

Risk Rating: CRITICAL - 4 components with single-source dependency represent $148M annual spend and 90+ day lead times for qualification of alternatives.""")

    pdf.section_title("2.2 Logistics Network Vulnerabilities")
    pdf.body_text("""Primary Shipping Routes and Chokepoints:

Route A: Shenzhen Port > Suez Canal > Rotterdam > Chicago Distribution Center
- Current Status: DISRUPTED (Red Sea rerouting active)
- Transit Time: Increased from 32 days to 46 days
- Cost Increase: +47%

Route B: Shanghai Port > Pacific > Los Angeles > Austin Manufacturing
- Current Status: OPERATIONAL (minor congestion)
- Transit Time: 18 days (stable)
- Port Congestion: Moderate (2-3 day delays)

Route C: Kaohsiung Port > Pacific > Seattle > Portland Distribution
- Current Status: OPERATIONAL
- Transit Time: 14 days (stable)
- Capacity: Near maximum utilization (92%)

Air Freight Dependencies:
- Primary Carrier: Cathay Pacific Cargo (Hong Kong hub)
- Backup Carriers: Korean Air Cargo (Incheon), EVA Air Cargo (Taipei)
- Monthly Capacity: 1,200 tons (currently at 87% utilization)""")

    pdf.chapter_title("Section 3: Financial Impact Summary")
    pdf.body_text("""Consolidated Q2-Q3 2024 Supply Chain Disruption Costs:

Direct Costs:
- Taiwan Earthquake Impact: $27.0 million
- Red Sea Shipping Crisis: $8.2 million
- China Export Restrictions: $12.1 million
- Total Direct Disruption Costs: $47.3 million

Lost Revenue Opportunity:
- Delayed product launches: $22.4 million estimated revenue delay
- Customer order cancellations: $8.7 million
- Market share erosion (estimated): 1.2 percentage points

Cost Absorption by Business Unit:
- Hardware Division: $31.2 million (66%)
- Cloud Infrastructure: $11.4 million (24%)
- Enterprise Solutions: $4.7 million (10%)

Impact on Key Financial Metrics:
- Gross Margin Impact: -180 basis points (from 54.2% to 52.4%)
- Operating Margin Impact: -120 basis points
- Q3 EPS Impact: -$0.23 per share""")

    pdf.add_page()
    pdf.chapter_title("Section 4: Mitigation Strategies and Recommendations")

    pdf.section_title("4.1 Dual-Sourcing Initiative")
    pdf.body_text("""Recommendation: Establish qualified secondary suppliers for all Tier 1 critical components within 18 months.

Priority Actions:
1. GPU Modules: Qualify Samsung Electronics as secondary supplier (est. 12-month qualification cycle)
   - Investment Required: $4.5 million (qualification, tooling, process validation)
   - Target: 35% of volume to secondary supplier by Q4 2025

2. High-Density PCBs: Qualify TTM Technologies (USA) as nearshore alternative
   - Investment Required: $2.8 million
   - Target: 40% of volume to nearshore by Q2 2025

3. Fiber Optic Transceivers: Qualify Lumentum (USA) and II-VI (USA)
   - Investment Required: $3.2 million
   - Target: Eliminate single-source dependency by Q3 2025

4. Battery Packs: Qualify LG Energy Solution (South Korea) and Panasonic (Japan)
   - Investment Required: $2.1 million
   - Target: 50% diversification by Q4 2025""")

    pdf.section_title("4.2 Strategic Inventory Buffer")
    pdf.body_text("""Recommendation: Increase safety stock levels for critical components from 4 weeks to 12 weeks.

Implementation:
- Immediate: Build 8-week buffer for top 50 critical components
- Phase 2: Extend to 12-week buffer for top 100 components
- Strategic Stockpile: 6-month supply of rare earth-dependent components

Investment Required:
- Additional Inventory Carrying Cost: $8.2 million annually
- Warehouse Expansion (Austin facility): $3.5 million capital
- Inventory Management System Upgrade: $1.8 million

Expected ROI: Avoid $15-20 million in future disruption costs annually""")

    pdf.section_title("4.3 Nearshoring and Reshoring Initiatives")
    pdf.body_text("""Recommendation: Establish Mexico manufacturing partnership for 25% of production volume.

Proposed Partner: Foxconn Guadalajara Complex
- Facility: 450,000 sq ft manufacturing campus
- Capabilities: PCB assembly, final product integration, testing
- Timeline: Facility qualification by Q2 2025, production start Q3 2025
- Volume Target: 25% of hardware volume by end of 2026

Investment Required:
- Tooling and Equipment: $12.5 million
- Process Transfer and Qualification: $4.2 million
- Engineering Staff Relocation: $2.3 million
- Total Nearshoring Investment: $19.0 million

Benefits:
- Reduced transit time to US customers: 3 days vs. 18-46 days
- USMCA tariff advantages
- Time zone alignment for operations management
- Reduced geopolitical risk exposure""")

    pdf.chapter_title("Section 5: Action Items and Timeline")
    pdf.body_text("""Approved by Supply Chain Steering Committee - October 15, 2024:

Immediate (Q4 2024):
- Initiate Samsung GPU qualification process - Owner: VP Procurement, Patricia Hernandez
- Contract Red Sea alternative routing with Evergreen Line - Owner: Dir. Logistics, Kevin O'Brien
- Accelerate rare earth strategic stockpile purchases - Owner: Commodity Manager, Lisa Chang

Near-Term (H1 2025):
- Complete TTM Technologies PCB qualification
- Begin Foxconn Guadalajara facility preparation
- Implement upgraded demand sensing analytics platform

Medium-Term (H2 2025 - 2026):
- Achieve 35% secondary sourcing for all critical components
- Complete nearshoring facility ramp-up
- Conduct annual supply chain stress testing exercises

Total Recommended Investment: $28.5 million over 24 months
Expected Annual Risk Reduction: $35-45 million in avoided disruption costs""")

    pdf.output('07_Supply_Chain_Disruption_Report_Q3_2024.pdf')
    print("Created: 07_Supply_Chain_Disruption_Report_Q3_2024.pdf")

def create_hr_compensation_analysis():
    """Document 3: Employee Engagement & Compensation Analysis"""
    pdf = ConsultingPDF("Employee Engagement & Compensation Analysis", "HR CONFIDENTIAL")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'Employee Engagement & Compensation Analysis', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Annual Human Capital Review - FY2024', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Prepared by: HR Analytics & Total Rewards | November 2024', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.chapter_title("Executive Summary")
    pdf.body_text("""This report presents a comprehensive analysis of employee engagement, compensation competitiveness, and turnover dynamics at Vertex Technologies. Key findings reveal concerning trends in mid-management turnover and engagement levels that require immediate attention.

Headline Metrics:
- Overall Employee Engagement Score: 67% (down from 74% in FY2023)
- Voluntary Turnover Rate: 18.4% (industry benchmark: 13.2%)
- Mid-Management Turnover: 24.7% (critical concern)
- Regrettable Turnover Rate: 11.2% (high performers leaving)
- Average Time to Fill Open Positions: 62 days (up from 48 days)
- Total Compensation Competitiveness: 94th percentile (target: 75th)

Key Actions Required:
1. Address mid-management engagement crisis
2. Implement targeted retention programs for high performers
3. Resolve compensation compression issues in engineering
4. Accelerate hiring for AlphaCorp integration""")

    pdf.chapter_title("Section 1: Employee Engagement Analysis")

    pdf.section_title("1.1 Overall Engagement Trends")
    pdf.body_text("""Annual Engagement Survey Results (Conducted September 2024):
- Response Rate: 84% (7,234 of 8,612 employees)
- Overall Engagement Index: 67% (target: 75%)
- YoY Change: -7 percentage points

Engagement Dimension Scores:
- Career Development: 58% (-11% YoY) - CRITICAL
- Manager Effectiveness: 61% (-8% YoY) - CONCERN
- Compensation & Benefits: 72% (-3% YoY)
- Work-Life Balance: 69% (-5% YoY)
- Company Direction: 74% (+2% YoY)
- Team Collaboration: 78% (+1% YoY)

Demographic Analysis:
- Engagement by Tenure: Highest in 0-2 years (74%), lowest in 5-10 years (59%)
- Engagement by Level: Directors 63%, Managers 54%, Individual Contributors 71%
- Engagement by Generation: Gen Z 76%, Millennials 68%, Gen X 62%, Boomers 58%""")

    pdf.section_title("1.2 Critical Issue: Mid-Management Crisis")
    pdf.body_text("""Detailed analysis reveals a severe engagement and retention crisis at the manager and senior manager levels.

Manager-Level Engagement Scores by Department:
- Sales Management (Dir. Mark Volton's org): 47% engagement, 45% turnover - CRITICAL
- Engineering Management: 58% engagement, 28% turnover - CONCERN
- Operations Management: 62% engagement, 19% turnover
- Finance Management: 71% engagement, 12% turnover
- Marketing Management: 65% engagement, 22% turnover

Root Cause Analysis (Exit Interview Themes from 127 departed managers):
1. "Insufficient decision-making authority" - 68% cited
2. "Excessive meeting load reduces productive time" - 61% cited
3. "Unclear path to director-level promotion" - 54% cited
4. "Compensation not aligned with expanded responsibilities" - 52% cited
5. "Burnout from pandemic-era workload expectations" - 49% cited

Employee Verbatim Quotes (Selected from Engagement Survey):
- "My manager Mark V. has no idea what I do day-to-day. 1:1s are always cancelled." - Sales IC
- "Been a senior manager for 4 years with no promotion path. Director roles filled externally." - Engineering
- "The reorg in July made everything worse. Nobody knows who reports to whom." - Operations""")

    pdf.add_page()
    pdf.chapter_title("Section 2: Compensation Competitiveness Analysis")

    pdf.section_title("2.1 Market Positioning Summary")
    pdf.body_text("""Compensation data benchmarked against Radford Global Technology Survey (n=2,847 companies).

Total Compensation by Level (Base + Bonus + Equity):
- Executive (VP+): $485,000-$1,250,000 (positioned at 85th percentile)
- Director: $285,000-$425,000 (positioned at 80th percentile)
- Senior Manager: $195,000-$275,000 (positioned at 65th percentile) - BELOW TARGET
- Manager: $145,000-$195,000 (positioned at 62nd percentile) - BELOW TARGET
- Senior IC: $165,000-$245,000 (positioned at 78th percentile)
- IC: $95,000-$155,000 (positioned at 72nd percentile)

Key Finding: Manager and Senior Manager levels are below our 75th percentile target, contributing to elevated turnover.""")

    pdf.section_title("2.2 Compensation Band Details")
    pdf.body_text("""Detailed Salary Bands by Role Family (Base Salary Only):

Engineering:
- Staff Engineer (L6): $195,000 - $245,000
- Senior Software Engineer (L5): $165,000 - $195,000
- Software Engineer (L4): $140,000 - $165,000
- Associate Engineer (L3): $115,000 - $140,000

Sales:
- Enterprise Account Executive: $125,000 base + $125,000 OTE commission ($250,000 total)
- Senior Account Executive: $95,000 base + $95,000 OTE ($190,000 total)
- Account Executive: $75,000 base + $75,000 OTE ($150,000 total)
- Sales Development Rep: $55,000 base + $25,000 OTE ($80,000 total)

Management:
- VP: $275,000 - $375,000 base
- Senior Director: $225,000 - $285,000 base
- Director: $185,000 - $245,000 base
- Senior Manager: $145,000 - $185,000 base
- Manager: $115,000 - $155,000 base""")

    pdf.section_title("2.3 Equity Compensation Structure")
    pdf.body_text("""Current Equity Grant Guidelines (Annual Refresh):

By Level:
- VP: $200,000-$400,000 annual grant value (4-year vest)
- Director: $100,000-$175,000 annual grant value
- Senior Manager: $50,000-$100,000 annual grant value
- Manager: $25,000-$60,000 annual grant value
- Senior IC (Tech): $75,000-$150,000 annual grant value
- IC: $15,000-$40,000 annual grant value

New Hire Grants:
- VP: $500,000-$1,000,000 (4-year cliff 25%, monthly thereafter)
- Director: $250,000-$500,000
- Senior Manager: $100,000-$200,000
- Manager: $50,000-$100,000

Issue Identified: Engineering IC equity is competitive, but engineering management equity is 15% below market, creating perverse incentive to remain IC.""")

    pdf.chapter_title("Section 3: Turnover Analysis")

    pdf.section_title("3.1 Turnover by Department")
    pdf.body_text("""Voluntary Turnover Rates (TTM as of October 2024):

Department Performance:
- Sales: 28.4% (vs. 18% benchmark) - CRITICAL
  - Under Sales Dir. Mark Volton: 45% turnover (18 of 40 FTEs departed)
  - Under Sales Dir. Jennifer Martinez: 14% turnover (acceptable)
- Engineering: 15.2% (vs. 12% benchmark) - MODERATE CONCERN
  - Platform Team: 22% turnover
  - Cloud Infrastructure: 11% turnover
  - AI/ML Team: 8% turnover (strong retention)
- Customer Success: 21.3% (vs. 15% benchmark) - CONCERN
- Operations: 12.1% (vs. 11% benchmark) - ACCEPTABLE
- Finance: 8.4% (vs. 10% benchmark) - STRONG
- Marketing: 17.8% (vs. 14% benchmark) - MODERATE CONCERN

Regrettable Turnover (High Performers Leaving):
- Overall: 11.2% of high performers left (vs. 7% target)
- Engineering High Performers: 14.1% departed - CRITICAL
- Sales High Performers: 19.2% departed - CRITICAL""")

    pdf.add_page()
    pdf.section_title("3.2 Exit Interview Analysis")
    pdf.body_text("""Exit Interview Data from 892 Voluntary Departures (FY2024):

Top Reasons for Departure:
1. Better compensation elsewhere: 34%
2. Limited career growth opportunities: 28%
3. Poor relationship with direct manager: 22%
4. Burnout/work-life balance: 19%
5. Lack of interesting work: 15%
6. Company direction concerns: 12%
7. Relocation/personal reasons: 11%
8. Better equity/upside at startup: 9%

Destination Analysis:
- Competitors (Google, Microsoft, AWS): 31%
- Venture-backed startups: 24%
- Private equity portfolio companies: 18%
- Other enterprise tech: 15%
- Career change/break: 12%

Cost of Turnover (Calculated):
- Average cost per departure: $87,400 (recruiting, training, productivity loss)
- Total FY2024 turnover cost: $77.9 million (892 departures)
- Regrettable turnover cost: $45.2 million (high performers cost 2x)""")

    pdf.chapter_title("Section 4: Recommended Actions")

    pdf.section_title("4.1 Immediate Actions (Q4 2024)")
    pdf.body_text("""1. Management Compensation Adjustment:
   - Increase manager/senior manager base salary bands by 8%
   - Increase manager equity refresh grants by 25%
   - Investment Required: $4.2 million annually

2. Sales Organization Intervention:
   - Performance review of Sales Dir. Mark Volton
   - Implement skip-level meetings in Sales
   - Deploy pulse surveys in Sales (bi-weekly)
   - Investment Required: $150,000 (consulting support)

3. High Performer Retention Program:
   - Identify top 200 flight-risk employees
   - Deploy retention bonuses ($25,000-$100,000 range)
   - Accelerate promotion decisions
   - Investment Required: $8.5 million (retention pool)""")

    pdf.section_title("4.2 Strategic Initiatives (FY2025)")
    pdf.body_text("""1. Career Framework Redesign:
   - Create dual-track (IC and Management) leveling
   - Publish transparent promotion criteria
   - Implement quarterly career conversations
   - Timeline: Q1 2025 design, Q2 2025 rollout
   - Investment: $1.2 million (consulting, systems)

2. Manager Development Program:
   - Mandatory leadership training for all people managers
   - 360-degree feedback implementation
   - Executive coaching for directors+
   - Investment: $2.8 million annually

3. AlphaCorp Integration People Strategy:
   - Retain 100% of AlphaCorp key technical talent
   - Integrate compensation and equity programs
   - Align engineering levels and career frameworks
   - Investment: $14.5 million (retention packages - per Board approval)

Total Recommended HR Investment: $31.35 million""")

    pdf.chapter_title("Section 5: Key Personnel Concerns")
    pdf.body_text("""Flight Risk Assessment - Critical Individuals:

HIGH RISK (Likely to depart within 6 months):
- Dr. Sarah Kim, VP of AI Research - Approached by OpenAI, Anthropic
- James Morrison, Sr. Dir. Cloud Architecture - Offered CTO role at Series B startup
- Maria Santos, Dir. Customer Success - Engagement score 42%, considering offers

MEDIUM RISK (Retention intervention recommended):
- Kevin O'Brien, Dir. Supply Chain - Key to integration success
- Dr. Chen Wei, Principal Engineer - Critical IP knowledge from AlphaCorp acquisition
- Patricia Hernandez, VP Procurement - Succession planning gap

SUCCESSION GAPS (Critical roles with no ready successor):
- CFO (Jennifer Walsh) - No internal candidate, 18-month development needed
- CTO (Position open post-reorg) - External search underway
- VP Engineering, Platform - Candidate departed Q3, search restarting""")

    pdf.output('08_HR_Compensation_Analysis_FY2024.pdf')
    print("Created: 08_HR_Compensation_Analysis_FY2024.pdf")

def create_rd_roadmap():
    """Document 4: Internal R&D Strategy (Product Roadmap)"""
    pdf = ConsultingPDF("R&D Strategy and Product Roadmap", "RESTRICTED - EXEC TEAM ONLY")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'R&D Strategy and Product Roadmap', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Project Quantum: AI-Powered Enterprise Platform', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, '3-Year Strategic Roadmap (2025-2027)', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Prepared by: Office of the CTO | October 2024', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.chapter_title("Executive Summary")
    pdf.body_text("""Project Quantum represents Vertex Technologies' most ambitious product initiative: a comprehensive AI-powered enterprise platform that will redefine how organizations leverage artificial intelligence for business operations.

Strategic Objectives:
- Position Vertex as a leader in enterprise AI orchestration
- Achieve $500M ARR from AI products by 2027
- Integrate AlphaCorp's AI inference technology into unified platform
- Create competitive moat through proprietary AI capabilities

Investment Summary (2025-2027):
- Total R&D Investment: $147.5 million
- Engineering Headcount Growth: 89 to 245 FTEs
- Patent Filing Target: 50+ new patents
- Expected Revenue Impact: $1.2 billion incremental revenue by 2027

Key Milestones:
- Q2 2025: Project Quantum Beta Launch
- Q4 2025: General Availability with core features
- Q2 2026: Advanced agent capabilities release
- Q4 2027: Full autonomous enterprise AI platform""")

    pdf.chapter_title("Section 1: Market Opportunity and Competitive Analysis")

    pdf.section_title("1.1 Market Size and Growth")
    pdf.body_text("""Enterprise AI Platform Market:
- 2024 Market Size: $28.4 billion
- 2027 Projected Size: $87.6 billion
- CAGR: 45.2%

Addressable Market Segments:
- AI Orchestration & MLOps: $12.3B (2027 projected)
- Conversational AI Platforms: $18.7B (2027 projected)
- AI-Powered Process Automation: $24.8B (2027 projected)
- Enterprise Knowledge Management: $15.4B (2027 projected)

Vertex Target Market Share: 8% of total ($7.0B revenue opportunity)""")

    pdf.section_title("1.2 Competitive Landscape")
    pdf.body_text("""Direct Competitors:
1. Microsoft (Copilot Suite) - Market Leader
   - Strengths: Distribution, Office integration, Azure infrastructure
   - Weaknesses: Expensive, lock-in concerns, limited customization

2. Google (Vertex AI + Workspace AI) - Strong Challenger
   - Strengths: Model quality, data capabilities, cloud integration
   - Weaknesses: Enterprise sales maturity, support reputation

3. AWS (Bedrock + Q) - Infrastructure Leader
   - Strengths: Cloud dominance, breadth of services
   - Weaknesses: Complexity, less turnkey solutions

4. Salesforce (Einstein AI) - CRM Native
   - Strengths: CRM integration, customer data access
   - Weaknesses: Narrow use cases, high cost

5. OpenAI (Enterprise) - Model Leader
   - Strengths: Model capabilities, brand recognition
   - Weaknesses: Platform immaturity, enterprise features

Vertex Differentiation Strategy:
- Open architecture (multi-model, multi-cloud)
- Industry-specific AI agents and workflows
- Superior data governance and security (zero-leak architecture)
- AlphaCorp's proprietary inference optimization (40% cost reduction)""")

    pdf.add_page()
    pdf.chapter_title("Section 2: Product Vision - Project Quantum")

    pdf.section_title("2.1 Platform Architecture")
    pdf.body_text("""Project Quantum Architecture Layers:

Layer 1: AI Foundation (Codename: "Quantum Core")
- Multi-model orchestration engine
- Unified model gateway (GPT-4, Claude, Gemini, Llama, custom models)
- AlphaFlow inference optimization (from AlphaCorp acquisition)
- Proprietary prompt engineering framework

Layer 2: Enterprise Data Layer (Codename: "DataMesh")
- RAG (Retrieval Augmented Generation) infrastructure
- Enterprise knowledge graph with 100B+ entity support
- Real-time data connectors (150+ enterprise systems)
- PII detection and automatic redaction engine
- Zero-leak response architecture (patent pending)

Layer 3: Agent Framework (Codename: "AgentSmith")
- Autonomous AI agent runtime
- Multi-agent collaboration protocols
- Human-in-the-loop workflow engine
- Tool use and API integration framework
- Sandboxed code execution environment

Layer 4: Application Layer (Codename: "QuantumApps")
- Pre-built industry solutions
- Low-code agent builder
- Conversational interface designer
- Analytics and monitoring dashboard""")

    pdf.section_title("2.2 Key Features and Capabilities")
    pdf.body_text("""Planned Feature Set:

Phase 1 Features (GA - Q4 2025):
- Universal AI Gateway with model switching
- Enterprise RAG with SharePoint, Confluence, Salesforce connectors
- Conversation summarization and action extraction
- Basic workflow automation (trigger-action patterns)
- Security: SOC 2 Type II, GDPR compliance

Phase 2 Features (Q2 2026):
- Autonomous AI agents with goal-oriented behavior
- Multi-agent collaboration (Project "Swarm Intelligence")
- Code generation with sandboxed execution
- Advanced analytics with predictive insights
- Industry solutions: Legal, Finance, Healthcare

Phase 3 Features (Q4 2027):
- Fully autonomous enterprise AI operating system
- Self-improving agent capabilities
- Real-time model fine-tuning on enterprise data
- Quantum-ready encryption integration
- Industry solutions: Manufacturing, Retail, Government""")

    pdf.chapter_title("Section 3: Technical Development Roadmap")

    pdf.section_title("3.1 Release Schedule")
    pdf.body_text("""Detailed Release Timeline:

Alpha Releases (Internal Only):
- Alpha 0.1: December 15, 2024 - Core orchestration engine
- Alpha 0.2: February 1, 2025 - RAG infrastructure
- Alpha 0.3: March 15, 2025 - Basic agent framework

Beta Releases (Limited Customer Preview):
- Beta 1.0: April 15, 2025 - Feature-complete beta
- Beta 1.1: June 1, 2025 - Performance optimization
- Beta 1.2: August 1, 2025 - Security hardening

General Availability:
- v1.0 GA: October 15, 2025 - Enterprise launch
- v1.1: January 2026 - Feature expansion
- v2.0: April 2026 - Agent capabilities GA
- v2.5: October 2026 - Industry solutions
- v3.0: April 2027 - Autonomous AI platform

Deprecation Schedule:
- Legacy AI Assistant v2.x: End-of-life December 2025
- Classic Analytics Platform: Migration required by March 2026""")

    pdf.add_page()
    pdf.section_title("3.2 Engineering Resource Allocation")
    pdf.body_text("""R&D Team Structure and Growth Plan:

Current State (Q4 2024): 89 FTEs
- Core Platform: 28 engineers
- AI/ML: 24 engineers (including 12 from AlphaCorp)
- Data Infrastructure: 18 engineers
- Security: 12 engineers
- DevOps/SRE: 7 engineers

Planned State (Q4 2025): 156 FTEs (+67)
- Core Platform: 42 engineers (+14)
- AI/ML: 48 engineers (+24)
- Data Infrastructure: 28 engineers (+10)
- Security: 22 engineers (+10)
- DevOps/SRE: 16 engineers (+9)

Planned State (Q4 2027): 245 FTEs (+89 from 2025)
- Core Platform: 58 engineers
- AI/ML: 78 engineers
- Data Infrastructure: 42 engineers
- Security: 38 engineers
- DevOps/SRE: 29 engineers

Key Hires Required:
- Distinguished Engineer, AI Systems (L8) - $650K+ TC
- VP Engineering, Quantum Platform - Search underway
- Director, AI Security - Critical for enterprise sales
- 15 Senior ML Engineers - AlphaCorp backfill and growth""")

    pdf.chapter_title("Section 4: R&D Investment and Budget")

    pdf.section_title("4.1 Three-Year Investment Plan")
    pdf.body_text("""R&D Budget Allocation (2025-2027):

FY2025 R&D Budget: $42.5 million
- Personnel Costs: $28.2 million
- Cloud Infrastructure: $6.8 million
- ML Training Compute: $4.5 million
- Tools and Software: $1.8 million
- Contractor/Consulting: $1.2 million

FY2026 R&D Budget: $52.0 million (+22% YoY)
- Personnel Costs: $36.4 million
- Cloud Infrastructure: $8.2 million
- ML Training Compute: $4.8 million
- Tools and Software: $1.9 million
- Contractor/Consulting: $0.7 million

FY2027 R&D Budget: $53.0 million (+2% YoY)
- Personnel Costs: $38.5 million
- Cloud Infrastructure: $7.5 million
- ML Training Compute: $4.2 million
- Tools and Software: $2.0 million
- Contractor/Consulting: $0.8 million

Total 3-Year R&D Investment: $147.5 million""")

    pdf.section_title("4.2 Revenue Projections")
    pdf.body_text("""Project Quantum Revenue Forecast:

FY2025:
- Beta Customer Revenue: $8.2 million
- GA Launch Revenue (Q4): $12.5 million
- Total FY2025: $20.7 million

FY2026:
- Platform Subscription: $85.4 million
- Professional Services: $18.2 million
- Training and Certification: $4.8 million
- Total FY2026: $108.4 million

FY2027:
- Platform Subscription: $245.8 million
- Professional Services: $42.5 million
- Industry Solutions: $68.2 million
- Training and Certification: $12.8 million
- Total FY2027: $369.3 million

Cumulative Revenue (2025-2027): $498.4 million
R&D ROI: 3.4x investment over 3 years""")

    pdf.chapter_title("Section 5: Intellectual Property Strategy")
    pdf.body_text("""Patent Portfolio Development:

Current Patent Holdings:
- Existing Vertex Patents: 127 (45 AI-related)
- AlphaCorp Patents (acquired): 34 issued, 18 pending
- Total Portfolio: 161 issued patents

New Patent Filing Targets:
- FY2025: 18 new filings
- FY2026: 20 new filings
- FY2027: 15 new filings

Priority Patent Areas:
1. Zero-Leak Response Architecture (3 filings - Q1 2025)
2. Multi-Agent Collaboration Protocol (2 filings - Q2 2025)
3. Proprietary Inference Optimization (AlphaCorp continuation - 4 filings)
4. Enterprise Knowledge Graph Construction (2 filings - Q3 2025)
5. Autonomous Agent Safety Controls (3 filings - Q4 2025)

Trade Secret Protection:
- AlphaFlow inference optimization algorithms
- Training data curation methodologies
- Customer-specific fine-tuning processes
- Security testing frameworks""")

    pdf.output('09_RD_Roadmap_Project_Quantum_2025_2027.pdf')
    print("Created: 09_RD_Roadmap_Project_Quantum_2025_2027.pdf")

def create_ma_postmortem():
    """Document 5: M&A Post-Mortem Integration Report"""
    pdf = ConsultingPDF("M&A Integration Post-Mortem", "LESSONS LEARNED - RESTRICTED")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'M&A Integration Post-Mortem Report', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Project Nebula: DataStream Systems Acquisition', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Integration Lessons Learned Review', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Prepared by: M&A Integration Office | September 2024', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.chapter_title("Executive Summary")
    pdf.body_text("""This post-mortem documents the integration challenges and lessons learned from the DataStream Systems acquisition (Project Nebula), completed in March 2023. While the acquisition achieved its strategic objectives, the integration process exceeded budget by $8.7 million and timeline by 7 months.

Acquisition Summary:
- Target: DataStream Systems, Inc. (Enterprise data pipeline provider)
- Close Date: March 15, 2023
- Deal Value: $245 million (all cash)
- Employees Acquired: 187
- Expected Integration Duration: 12 months
- Actual Integration Duration: 19 months

Integration Outcomes:
- Revenue Synergies Achieved: 78% of plan ($18.2M vs. $23.4M target)
- Cost Synergies Achieved: 65% of plan ($4.2M vs. $6.5M target)
- Employee Retention: 71% (vs. 85% target) - CRITICAL MISS
- Customer Retention: 94% (vs. 95% target) - ACCEPTABLE
- Technology Integration: Partial completion (ERP migration abandoned)

Total Integration Cost:
- Original Budget: $12.8 million
- Actual Spend: $21.5 million
- Variance: +$8.7 million (68% over budget)

This report provides candid analysis of what went wrong and actionable recommendations for future integrations, including the upcoming AlphaCorp acquisition.""")

    pdf.chapter_title("Section 1: Integration Failures - Root Cause Analysis")

    pdf.section_title("1.1 ERP System Integration Failure")
    pdf.body_text("""The most significant failure was the attempted migration of DataStream's legacy Oracle ERP system to Vertex's SAP S/4HANA platform.

Background:
- DataStream operated Oracle E-Business Suite 12.2 (installed 2009)
- Vertex operates SAP S/4HANA Cloud (migrated 2021)
- Original plan: Full migration within 6 months of close

What Went Wrong:
1. Underestimated Customization Complexity
   - DataStream had 847 custom ABAP equivalents in Oracle
   - Discovery revealed 312 integrations with downstream systems
   - Original estimate: 150 customizations, 80 integrations

2. Data Quality Issues
   - Customer master data: 34% duplicate records
   - Chart of accounts: Incompatible structures requiring manual mapping
   - Historical data: 7 years of data with inconsistent formats

3. Resource Constraints
   - SAP implementation team already at 120% capacity
   - DataStream IT team (12 FTEs) reduced to 8 during integration
   - Key Oracle expert (Sandra Chen) departed month 4

Financial Impact:
- Original ERP Migration Budget: $3.2 million
- Actual Spend Before Abandonment: $5.8 million
- Write-off and Parallel System Costs: $2.9 million
- Total ERP-Related Loss: $8.7 million

Decision: Migration abandoned in month 14. DataStream continues operating on Oracle ERP as isolated subsidiary with manual reconciliation to Vertex financials.""")

    pdf.section_title("1.2 Cultural Integration Challenges")
    pdf.body_text("""Significant cultural clashes emerged between Vertex's structured enterprise culture and DataStream's startup-oriented environment.

Key Cultural Conflicts:
1. Decision-Making Speed
   - DataStream: Decisions made in 24-48 hours by small teams
   - Vertex: Formal approval process requiring 2-4 weeks
   - Impact: DataStream engineers frustrated by bureaucracy

2. Work Flexibility
   - DataStream: Fully remote since 2020, flexible hours
   - Vertex: Hybrid 3 days in-office mandate
   - Impact: 23 DataStream employees cited this in exit interviews

3. Compensation Philosophy
   - DataStream: Higher base, smaller equity (startup had limited upside)
   - Vertex: Lower base, significant equity
   - Impact: Total comp decrease for 45% of transferred employees

Executive Relationship Breakdown:
- DataStream CEO Michael Torres: Departed month 6 (vs. planned 24-month commitment)
- DataStream CTO Dr. Rachel Kim: Departed month 9
- DataStream VP Engineering James Liu: Departed month 8

Exit Reasons Cited:
- "Loss of autonomy in product decisions" - Michael Torres
- "Integration roadmap ignored our technical recommendations" - Dr. Rachel Kim
- "My team is being micromanaged by people who don't understand our product" - James Liu

Retention Package Performance:
- Total retention packages: $8.5 million
- Packages forfeited due to early departure: $4.2 million (49%)
- Lessons: Packages were back-loaded, should have included stay-bonus milestones""")

    pdf.add_page()
    pdf.section_title("1.3 Customer Experience Disruption")
    pdf.body_text("""Despite 94% customer retention (exceeding 93% floor), several customers experienced service disruptions during integration.

Major Customer Incidents:
1. GlobalBank Corp (Top 5 customer - $2.4M ARR)
   - Incident: 4-hour production outage during system cutover
   - Root Cause: Miscommunicated maintenance window
   - Impact: $180,000 SLA credits, executive apology required
   - Status: Retained but reduced contract scope by 15%

2. Meridian Healthcare ($1.8M ARR)
   - Incident: Data pipeline latency increased 340% post-integration
   - Root Cause: Network routing changes not tested end-to-end
   - Impact: 3-month remediation effort, $95,000 credits
   - Status: Retained with additional concessions

3. TechRetail Inc. ($1.2M ARR)
   - Incident: Lost to competitor (Snowflake) month 8
   - Root Cause: Account team transition gap, no coverage for 6 weeks
   - Impact: $1.2M ARR loss
   - Status: Lost - cited "lack of attention during transition"

Customer Feedback Themes (Integration Survey):
- "Communication was poor - didn't know who our contact was" - 45% of respondents
- "Product roadmap seemed uncertain during integration" - 38%
- "Support response times increased significantly" - 52%
- "We felt like an afterthought" - 41%""")

    pdf.chapter_title("Section 2: What Worked Well")

    pdf.section_title("2.1 Product Integration Success")
    pdf.body_text("""Despite operational challenges, the core product integration was successful.

Technical Achievements:
- DataStream Pipeline merged into Vertex Data Platform
- API compatibility maintained for all customer integrations
- Performance improved 23% through infrastructure consolidation
- Security posture enhanced (achieved FedRAMP Moderate)

Product Roadmap Alignment:
- Combined product team established by month 3
- Unified roadmap published by month 5
- First integrated feature released month 8

Engineering Team Integration:
- 67 of 78 DataStream engineers retained through month 12
- Code quality maintained (no increase in production incidents)
- Knowledge transfer 85% complete by month 9""")

    pdf.section_title("2.2 Go-to-Market Integration")
    pdf.body_text("""Sales and marketing integration exceeded expectations in several areas.

Successes:
- Combined sales team trained by month 4
- Cross-sell pipeline: $12.4M identified (exceeded $8M target)
- Marketing rebrand completed month 3 (under budget)
- Partner channel integration smooth (all 23 partners retained)

Revenue Achievement:
- Year 1 Combined Revenue: $287M (101% of plan)
- Cross-sell Revenue Recognized: $8.7M
- New Logo Wins citing combined offering: 14 accounts, $6.2M ARR

Brand Transition:
- "DataStream by Vertex" branding maintained customer familiarity
- Customer confusion minimal based on survey data
- Website consolidation completed month 2""")

    pdf.chapter_title("Section 3: Financial Analysis")
    pdf.body_text("""Integration Budget vs. Actual:

Integration Cost Categories:

1. Technology Integration:
   - Budget: $5.2M | Actual: $9.4M | Variance: +$4.2M (81% over)
   - Driver: ERP migration failure and parallel system costs

2. Personnel & Retention:
   - Budget: $4.5M | Actual: $5.8M | Variance: +$1.3M (29% over)
   - Driver: Additional retention packages, severance for departed execs

3. Professional Services:
   - Budget: $1.8M | Actual: $3.2M | Variance: +$1.4M (78% over)
   - Driver: Extended consulting engagement, legal fees for exec departures

4. Facilities & Operations:
   - Budget: $0.8M | Actual: $1.2M | Variance: +$0.4M (50% over)
   - Driver: Delayed office consolidation, dual facility costs

5. Customer Success & Transition:
   - Budget: $0.5M | Actual: $1.9M | Variance: +$1.4M (280% over)
   - Driver: SLA credits, dedicated customer success resources

Total: Budget $12.8M | Actual $21.5M | Variance +$8.7M (68% over)

Synergy Achievement:

Revenue Synergies:
- Target: $23.4M by end of Year 2
- Achieved: $18.2M (78% of target)
- Gap Driver: Cross-sell ramp slower than expected, 1 major customer lost

Cost Synergies:
- Target: $6.5M annual run-rate
- Achieved: $4.2M (65% of target)
- Gap Driver: ERP consolidation not achieved, parallel systems remain""")

    pdf.add_page()
    pdf.chapter_title("Section 4: Lessons Learned and Recommendations")

    pdf.section_title("4.1 Pre-Close Planning")
    pdf.body_text("""Lesson 1: Technical Due Diligence Must Include Integration Assessment
- DataStream DD focused on product quality, not system complexity
- Recommendation: Require IT integration assessment as DD workstream
- Owner: CIO should participate in all tech acquisitions

Lesson 2: Cultural Assessment is Not Optional
- Cultural differences dismissed as "manageable"
- Recommendation: Formal cultural assessment using standardized tools
- Implement culture integration workstream with executive sponsor

Lesson 3: Retention Package Design
- Back-loaded packages ineffective when executives depart
- Recommendation: 40% paid at close, 30% at 12 months, 30% at 24 months
- Include stay-bonus milestones tied to integration deliverables""")

    pdf.section_title("4.2 Integration Execution")
    pdf.body_text("""Lesson 4: Integration Management Office Authority
- IMO lacked authority to make binding decisions
- Business unit leaders overrode IMO recommendations
- Recommendation: IMO lead must have CEO-delegated authority
- Escalation path: IMO > CEO, not IMO > Business Unit > CEO

Lesson 5: Customer Communication Plan
- No dedicated customer communication owner
- Messages inconsistent across account teams
- Recommendation: Assign dedicated Customer Integration Lead
- Develop standardized communication templates and cadence

Lesson 6: Realistic System Integration Planning
- 6-month ERP migration was unrealistic
- No fallback plan when migration struggled
- Recommendation: Assume 2x timeline for legacy system migrations
- Define clear go/no-go criteria and abandonment triggers

Lesson 7: Resource Allocation
- Integration competed with ongoing operations
- Key personnel stretched across too many initiatives
- Recommendation: Dedicated integration team (not borrowed)
- Budget for backfill of key roles during integration""")

    pdf.section_title("4.3 Specific Recommendations for AlphaCorp Integration")
    pdf.body_text("""Based on Project Nebula lessons, the following are critical for Project Phoenix (AlphaCorp):

1. ERP Strategy: DO NOT attempt full migration
   - Keep AlphaCorp on existing systems for 18-24 months minimum
   - Implement financial consolidation at reporting level only
   - Defer full integration until Quantum platform stabilizes

2. Executive Retention: Front-load packages
   - Marcus Webb and Dr. Aisha Patel packages: 50% at close
   - Milestone bonuses tied to integration deliverables
   - Clear role definitions and decision-making authority documented

3. Technical Team Autonomy
   - Allow AlphaCorp engineering team to maintain existing practices for Year 1
   - Gradual process alignment, not immediate conformity
   - Preserve Austin R&D hub identity

4. Customer Integration
   - Assign dedicated Customer Success lead for top 20 AlphaCorp accounts
   - No system changes for customers in first 6 months
   - Proactive communication campaign starting Day 1

5. Integration Budget
   - Apply 1.5x multiplier to initial estimates based on Nebula experience
   - Current AlphaCorp budget: $32.5M
   - Recommended revised budget: $48.75M (50% contingency)

6. IMO Structure
   - IMO Lead reports directly to CEO (not COO)
   - Weekly CEO integration review meetings
   - Clear escalation authority documented in integration charter""")

    pdf.chapter_title("Section 5: Post-Mortem Participants")
    pdf.body_text("""This post-mortem was conducted September 5-12, 2024 with participation from:

Integration Team:
- Patricia Hernandez, VP Procurement (IMO Co-Lead)
- James Morrison, Sr. Dir. Cloud Architecture (Technical Integration Lead)
- Lisa Martinez, Dir. HR Business Partner
- Kevin O'Brien, Dir. Supply Chain (IT Integration)

Executive Sponsors:
- Jennifer Walsh, CFO
- Robert Kim, CEO (exit interview review only)

External Advisors:
- McKinsey & Company, Integration Practice (facilitation)
- Deloitte M&A Integration Services (benchmarking)

Former DataStream Executives Interviewed:
- Michael Torres (former CEO) - Via external consultant
- Dr. Rachel Kim (former CTO) - Declined interview request
- James Liu (former VP Engineering) - Written response provided

Survey Respondents:
- 67 retained DataStream employees
- 34 departed DataStream employees
- 42 Vertex employees involved in integration
- 18 customer contacts

Document Classification: This report contains candid assessments of named individuals and should not be distributed beyond the Integration Steering Committee without CEO approval.

Prepared by: M&A Integration Office
Approved by: Jennifer Walsh, CFO
Date: September 20, 2024""")

    pdf.output('10_MA_PostMortem_Project_Nebula_DataStream.pdf')
    print("Created: 10_MA_PostMortem_Project_Nebula_DataStream.pdf")

def main():
    """Generate all 5 deep consulting PDF documents."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Generating Deep Consulting PDF Documents...")
    print("=" * 50)

    create_board_minutes()
    create_supply_chain_report()
    create_hr_compensation_analysis()
    create_rd_roadmap()
    create_ma_postmortem()

    print("=" * 50)
    print("All 5 PDF documents generated successfully!")
    print("\nDocuments created:")
    print("1. 06_Board_Minutes_Q3_2024_Project_Phoenix.pdf")
    print("2. 07_Supply_Chain_Disruption_Report_Q3_2024.pdf")
    print("3. 08_HR_Compensation_Analysis_FY2024.pdf")
    print("4. 09_RD_Roadmap_Project_Quantum_2025_2027.pdf")
    print("5. 10_MA_PostMortem_Project_Nebula_DataStream.pdf")
    print("\nThese documents are designed for RAG testing with cross-document synthesis queries.")

if __name__ == "__main__":
    main()
