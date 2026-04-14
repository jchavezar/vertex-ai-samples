"""
Generate 3 complex interrelated PDF documents for testing hierarchical RAG.

Documents model a distributed payment processing system with:
1. System Architecture - Component overview and connections
2. Operations Manual - Procedures referencing architecture
3. Troubleshooting Guide - Diagnostic flows referencing both

This creates lateral peer relationships between agents for testing expansion retrieval.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def create_architecture_pdf():
    """Document 1: System Architecture - Overview of all components."""
    doc = SimpleDocTemplate(
        "system_architecture.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkblue,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=12,
        leading=16,
    )

    content = []

    # Page 1: Overview
    content.append(Paragraph("NexaPay Distributed Payment System Architecture", title_style))
    content.append(Paragraph("Version 3.2.1 | Classification: Internal", body_style))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Executive Summary", heading_style))
    content.append(
        Paragraph(
            """The NexaPay platform processes over 2.4 billion transactions annually across 47 countries.
            This document describes the distributed architecture comprising 7 core subsystems that work
            in concert to provide sub-100ms transaction latency with 99.997% uptime. The system uses
            event-driven microservices communicating via Apache Kafka with PostgreSQL for persistence
            and Redis for distributed caching. Each subsystem is owned by a dedicated engineering team
            and operates as an independent agent within the orchestration framework.""",
            body_style,
        )
    )

    content.append(Paragraph("Orchestrator Agent", heading_style))
    content.append(
        Paragraph(
            """The Orchestrator Agent is the central coordination layer that routes incoming payment
            requests to the appropriate downstream agents. It maintains a real-time view of system
            health via heartbeat monitoring and implements circuit breakers to isolate failing
            components. Key responsibilities include:

            <b>Request Routing:</b> All payment requests enter through the Orchestrator which examines
            the payment type, currency, and merchant configuration to determine the processing path.
            Standard card payments route to the Payment Gateway Agent, while alternative payment
            methods (APMs) like bank transfers route to the APM Handler Agent.

            <b>State Management:</b> The Orchestrator maintains distributed transaction state using
            Redis Cluster with a 15-minute TTL. This allows any node to resume processing if the
            original handler fails. State transitions are logged to Kafka for audit compliance.

            <b>Dependencies:</b> The Orchestrator directly depends on the Auth Agent for session
            validation, the Payment Gateway Agent for card processing, the Risk Engine Agent for
            fraud scoring, and the Notification Agent for customer communications.""",
            body_style,
        )
    )

    # Page 2: Auth and Payment Gateway
    content.append(Paragraph("Auth Agent", heading_style))
    content.append(
        Paragraph(
            """The Auth Agent handles all authentication and authorization for the platform.
            It implements OAuth 2.0 with PKCE for mobile clients and mutual TLS for server-to-server
            communication. Session tokens are JWTs with a 30-minute expiry, stored in Redis with
            automatic refresh for active sessions.

            <b>Token Validation:</b> Every API request includes a bearer token that the Auth Agent
            validates against the session store. Invalid or expired tokens trigger a 401 response
            with a refresh token flow hint. The Auth Agent caches validation results for 60 seconds
            to reduce Redis load during burst traffic.

            <b>Permission Model:</b> The Auth Agent enforces role-based access control (RBAC) with
            merchant-specific permission sets. A payment can only proceed if the authenticated user
            has the 'payments:write' permission for the target merchant account.

            <b>Dependencies:</b> Auth Agent depends on the Session Store (Redis Cluster) and the
            Identity Provider integration. It is consumed by all other agents for request validation.
            Critical dependency for the Billing Agent which requires valid sessions for all operations.""",
            body_style,
        )
    )

    content.append(Paragraph("Payment Gateway Agent", heading_style))
    content.append(
        Paragraph(
            """The Payment Gateway Agent interfaces with external card networks (Visa, Mastercard,
            Amex, Discover) and acquiring banks. It handles card tokenization, authorization requests,
            capture, and settlement batch processing.

            <b>Authorization Flow:</b> Card details are tokenized using PCI-compliant vault storage.
            The token is sent to the acquiring bank with transaction amount, currency, and merchant
            credentials. Authorization responses include approval codes, decline reasons, or soft
            decline indicators that trigger 3DS authentication.

            <b>Settlement Processing:</b> Daily batch settlement runs at 23:00 UTC. The Payment
            Gateway aggregates approved transactions by acquiring bank and submits settlement files
            via SFTP. Settlement confirmations update the Billing Agent with final amounts including
            interchange fees and currency conversion adjustments.

            <b>Dependencies:</b> Requires the Auth Agent for merchant authentication, the Risk Engine
            Agent for pre-authorization fraud checks, and the Billing Agent for settlement accounting.
            Also depends on the Refund Handler Agent for reversal processing.""",
            body_style,
        )
    )

    # Page 3: Risk Engine and Billing
    content.append(Paragraph("Risk Engine Agent", heading_style))
    content.append(
        Paragraph(
            """The Risk Engine Agent performs real-time fraud detection using a combination of
            rule-based filters and machine learning models. Every transaction receives a risk score
            from 0-1000, with transactions above the merchant-configured threshold triggering
            additional verification or automatic decline.

            <b>Scoring Pipeline:</b> The Risk Engine evaluates 47 signals including device fingerprint,
            IP geolocation, velocity patterns, and behavioral biometrics. The ML model is a gradient
            boosting ensemble trained on 18 months of chargeback data, achieving 94.3% precision at
            2.1% false positive rate.

            <b>Velocity Rules:</b> Configurable velocity limits prevent card testing attacks. Default
            limits: 5 transactions per card per hour, $2,000 daily per card, 10 transactions per
            device fingerprint per day. Merchants can customize these thresholds via the API.

            <b>Dependencies:</b> The Risk Engine consumes data from the Auth Agent (user behavior
            history), the Payment Gateway Agent (transaction patterns), and the Data Pipeline Agent
            (feature engineering). It feeds scores to both the Orchestrator and the Monitoring Agent
            for alerting on anomalous patterns.""",
            body_style,
        )
    )

    content.append(Paragraph("Billing Agent", heading_style))
    content.append(
        Paragraph(
            """The Billing Agent manages merchant accounts, fee calculation, payouts, and financial
            reconciliation. It maintains the source of truth for all monetary balances and generates
            compliance reports for regulatory audits.

            <b>Fee Calculation:</b> Transaction fees are calculated based on merchant pricing tiers:
            interchange-plus, flat rate, or tiered pricing. The Billing Agent applies the correct
            fee structure based on card type, transaction amount, and merchant volume tier. Complex
            blended rates for international transactions factor in currency conversion margins.

            <b>Payout Processing:</b> Daily payouts to merchant bank accounts are scheduled based on
            the merchant's configured payout delay (T+1, T+2, or T+7). The Billing Agent generates
            payout batches, submits to partner banks via API, and reconciles confirmations. Failed
            payouts trigger the Notification Agent to alert merchant operations.

            <b>Dependencies:</b> Critical dependency on Auth Agent for all operations. Receives
            settlement data from Payment Gateway Agent. Consumes refund events from Refund Handler
            Agent. Sends balance alerts to Notification Agent. Reports to Monitoring Agent for
            financial anomaly detection.""",
            body_style,
        )
    )

    # Page 4: Supporting Agents
    content.append(Paragraph("Refund Handler Agent", heading_style))
    content.append(
        Paragraph(
            """The Refund Handler Agent processes all return transactions including full refunds,
            partial refunds, and chargeback responses. It coordinates with the Payment Gateway Agent
            for network-level reversals and the Billing Agent for balance adjustments.

            <b>Refund Types:</b> Customer-initiated refunds go through the standard flow: validate
            original transaction, check refund eligibility (within 180 days, not already refunded),
            submit reversal to network, update Billing Agent. Chargebacks follow the dispute flow:
            receive notification from network, gather evidence from Data Pipeline, submit response,
            track arbitration outcome.

            <b>Partial Refunds:</b> Multiple partial refunds are allowed up to the original transaction
            amount. Each partial refund creates a linked transaction record. The Refund Handler
            calculates prorated fee adjustments for interchange-plus merchants.

            <b>Dependencies:</b> Requires Payment Gateway Agent for network reversals. Updates Billing
            Agent for all balance changes. Queries Data Pipeline Agent for chargeback evidence.
            Triggers Notification Agent for customer refund confirmations.""",
            body_style,
        )
    )

    content.append(Paragraph("Notification Agent", heading_style))
    content.append(
        Paragraph(
            """The Notification Agent handles all outbound communications including transaction
            receipts, payment confirmations, payout notifications, and system alerts. It supports
            multiple channels: email, SMS, push notifications, and webhooks.

            <b>Template System:</b> Notifications use Handlebars templates with merchant-specific
            branding. Templates are versioned and support A/B testing. Multi-language support covers
            47 locales with automatic language detection based on customer preferences.

            <b>Webhook Delivery:</b> Critical events are delivered to merchant webhook endpoints with
            exponential backoff retry (1s, 5s, 30s, 5m, 30m). Failed deliveries after 5 attempts
            trigger an alert to the Monitoring Agent and email to merchant technical contacts.

            <b>Dependencies:</b> Receives events from Orchestrator, Payment Gateway Agent, Billing
            Agent, and Refund Handler Agent. Consumes customer preferences from Data Pipeline Agent.
            Reports delivery metrics to Monitoring Agent.""",
            body_style,
        )
    )

    content.append(Paragraph("Data Pipeline Agent", heading_style))
    content.append(
        Paragraph(
            """The Data Pipeline Agent manages the data warehouse, feature engineering for ML models,
            and analytics queries. It ingests events from all other agents via Kafka and maintains
            both real-time and historical views.

            <b>Event Streaming:</b> All agent events are published to Kafka topics with schema
            registry enforcement. The Data Pipeline consumes these events, transforms them into
            analytical schemas, and loads into BigQuery for reporting. Real-time aggregations feed
            the Risk Engine Agent's feature store.

            <b>Feature Engineering:</b> Daily batch jobs compute customer behavior features: average
            transaction amount, preferred payment times, device patterns, geographic distribution.
            These features power the Risk Engine's ML models and merchant analytics dashboards.

            <b>Dependencies:</b> Consumes events from all agents via Kafka. Provides feature data to
            Risk Engine Agent. Supplies evidence data to Refund Handler Agent for chargebacks.
            Feeds Monitoring Agent with aggregated metrics for alerting.""",
            body_style,
        )
    )

    content.append(Paragraph("Monitoring Agent", heading_style))
    content.append(
        Paragraph(
            """The Monitoring Agent provides observability across the platform through metrics
            collection, log aggregation, distributed tracing, and alerting. It ensures SLA compliance
            and enables rapid incident response.

            <b>Metrics Pipeline:</b> All agents emit Prometheus metrics which are scraped every 15
            seconds. Key SLIs include: p99 latency, error rate, throughput, and queue depth. SLOs
            are defined per-agent with automatic alerting on breach.

            <b>Distributed Tracing:</b> OpenTelemetry spans trace requests across all agents. The
            Monitoring Agent aggregates traces in Jaeger and provides transaction-level debugging.
            Slow transaction analysis identifies bottlenecks in the processing pipeline.

            <b>Dependencies:</b> Receives metrics and logs from all agents. Consumes health status
            from Orchestrator. Triggers Notification Agent for on-call alerts. Queries Data Pipeline
            Agent for historical trend analysis.""",
            body_style,
        )
    )

    doc.build(content)
    print("Created: system_architecture.pdf")


def create_operations_manual_pdf():
    """Document 2: Operations Manual - Procedures referencing architecture."""
    doc = SimpleDocTemplate(
        "operations_manual.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkgreen,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkgreen,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=12,
        leading=16,
    )

    content = []

    # Page 1: Overview and Daily Procedures
    content.append(Paragraph("NexaPay Operations Manual", title_style))
    content.append(Paragraph("For Platform Operations Team | Version 2.8", body_style))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Daily Operations Checklist", heading_style))
    content.append(
        Paragraph(
            """This section covers the daily operational procedures that must be completed by the
            platform operations team. All procedures reference the system architecture components
            documented in the System Architecture guide.

            <b>Morning Health Check (08:00 UTC):</b>
            1. Verify Orchestrator Agent heartbeat dashboard shows all green
            2. Confirm overnight settlement batch from Payment Gateway Agent completed successfully
            3. Check Billing Agent payout queue for any stuck transactions
            4. Review Monitoring Agent alert history for overnight incidents
            5. Validate Risk Engine Agent model scores are within normal distribution

            <b>Midday Verification (14:00 UTC):</b>
            1. Confirm Auth Agent session counts are within capacity limits
            2. Verify Notification Agent webhook delivery rate exceeds 99.5%
            3. Check Data Pipeline Agent Kafka lag is under 1000 messages
            4. Review Payment Gateway Agent authorization approval rate

            <b>Evening Preparation (20:00 UTC):</b>
            1. Verify all Billing Agent daily reconciliation reports generated
            2. Confirm Refund Handler Agent queue is empty before settlement cutoff
            3. Check Data Pipeline Agent BigQuery load jobs are on schedule""",
            body_style,
        )
    )

    content.append(Paragraph("Settlement Processing Procedures", heading_style))
    content.append(
        Paragraph(
            """Settlement is the critical daily process where authorized transactions are finalized
            with acquiring banks. This procedure involves coordination between the Payment Gateway
            Agent, Billing Agent, and Monitoring Agent.

            <b>Pre-Settlement Checklist (22:00 UTC):</b>
            The Payment Gateway Agent begins aggregating the day's authorized transactions at 22:00
            UTC. Before the 23:00 UTC batch submission, operations must verify:

            1. No active incidents on Payment Gateway Agent or Billing Agent
            2. All partner bank API endpoints responding (check Monitoring Agent status page)
            3. Acquiring bank maintenance windows do not overlap with settlement window
            4. Currency conversion rates have been updated in Billing Agent (feeds from Risk Engine)

            <b>Settlement Execution (23:00-23:30 UTC):</b>
            The Payment Gateway Agent submits settlement files to each acquiring bank via SFTP.
            Monitor the following in real-time via Monitoring Agent dashboards:

            1. File generation progress: expect ~500,000 transactions per file
            2. SFTP upload status: timeout alerts if transfer exceeds 5 minutes
            3. Acquiring bank acknowledgment: expect ACK within 10 minutes of upload
            4. Any NACK responses require immediate escalation to banking ops team

            <b>Post-Settlement Reconciliation (23:30-00:30 UTC):</b>
            After acquiring bank acknowledgments, the Billing Agent reconciles settlement amounts:

            1. Compare submitted transaction totals to acknowledged amounts
            2. Flag any interchange fee variances exceeding 0.5%
            3. Update merchant account balances with settlement confirmations
            4. Generate settlement summary report for finance team
            5. Notify Notification Agent to send merchant settlement confirmations""",
            body_style,
        )
    )

    # Page 2: Authentication and Session Management
    content.append(Paragraph("Authentication Operations", heading_style))
    content.append(
        Paragraph(
            """The Auth Agent is a critical dependency for all platform operations. Session
            management issues cascade to all downstream agents, making authentication operations
            a priority for the platform team.

            <b>Session Capacity Monitoring:</b>
            The Auth Agent Redis cluster stores active sessions with a 30-minute TTL. Normal
            operation maintains 2-5 million concurrent sessions. When approaching the 10 million
            session soft limit:

            1. Enable Auth Agent session compression (reduces memory 40%)
            2. Reduce session TTL to 15 minutes for non-premium merchants
            3. Alert Orchestrator Agent to enable traffic shedding for lowest-tier merchants
            4. Prepare to scale Redis cluster if sessions exceed 8 million for 15 minutes

            <b>Token Refresh Storm Prevention:</b>
            If many sessions expire simultaneously (e.g., after maintenance), a token refresh
            storm can overwhelm the Auth Agent. Mitigation steps:

            1. Enable Auth Agent token refresh jitter (spreads renewals over 5-minute window)
            2. Increase Auth Agent replica count temporarily
            3. Have Orchestrator Agent queue non-critical requests during refresh peak
            4. Monitor Redis CPU via Monitoring Agent - scale if exceeding 70%

            <b>Emergency Session Invalidation:</b>
            In case of security incident requiring mass session invalidation:

            1. Trigger Auth Agent emergency flush via admin API (requires VP Security approval)
            2. Notify all agents via Orchestrator to expect authentication failures
            3. Enable Notification Agent customer communication for re-authentication prompt
            4. Monitor Data Pipeline Agent for unusual access patterns post-flush
            5. Conduct post-incident review with Risk Engine Agent team""",
            body_style,
        )
    )

    content.append(Paragraph("Payment Processing Operations", heading_style))
    content.append(
        Paragraph(
            """Standard payment processing flows through multiple agents. Operations must understand
            the full flow to diagnose issues effectively.

            <b>Transaction Flow Overview:</b>
            1. Request arrives at Orchestrator Agent which validates basic parameters
            2. Orchestrator routes to Auth Agent for session and permission validation
            3. Auth Agent confirms, Orchestrator forwards to Risk Engine Agent
            4. Risk Engine returns fraud score, if below threshold proceed to Payment Gateway
            5. Payment Gateway Agent tokenizes card and sends to acquiring bank
            6. Authorization response returns through Payment Gateway to Orchestrator
            7. Orchestrator instructs Billing Agent to record pending transaction
            8. Orchestrator triggers Notification Agent to send customer receipt

            <b>Latency Monitoring:</b>
            End-to-end P99 latency target is 100ms. If Monitoring Agent alerts on latency breach:

            1. Check individual agent latencies in distributed trace (Orchestrator dashboard)
            2. Most common culprits: Risk Engine Agent model inference, Payment Gateway bank calls
            3. If Risk Engine slow: check feature store connection to Data Pipeline Agent
            4. If Payment Gateway slow: check acquiring bank endpoint health

            <b>Authorization Decline Handling:</b>
            When Payment Gateway Agent returns a decline, operations may need to intervene:

            1. Soft declines (3DS required): Let flow continue to authentication
            2. Hard declines (insufficient funds): No action, customer notified via Notification Agent
            3. Network declines (bank unavailable): Check Payment Gateway Agent network status
            4. Risk declines (fraud score too high): Review in Risk Engine Agent dashboard
            5. Repeated declines from same merchant: Escalate to Billing Agent team for account review""",
            body_style,
        )
    )

    # Page 3: Refund and Chargeback Operations
    content.append(Paragraph("Refund Operations", heading_style))
    content.append(
        Paragraph(
            """Refund processing is handled by the Refund Handler Agent in coordination with
            Payment Gateway Agent and Billing Agent. Operations oversight ensures refunds process
            correctly and merchant balances remain accurate.

            <b>Standard Refund Processing:</b>
            Refunds initiated via merchant API or customer service portal flow through:

            1. Refund Handler Agent validates original transaction exists and is refundable
            2. For card transactions, Refund Handler requests reversal from Payment Gateway Agent
            3. Payment Gateway Agent submits reversal to card network (same-day for Visa/MC)
            4. On network confirmation, Refund Handler Agent notifies Billing Agent
            5. Billing Agent deducts refund amount from merchant balance plus fee adjustment
            6. Notification Agent sends refund confirmation to customer

            <b>Refund Stuck in Processing:</b>
            If refunds remain in PROCESSING state for more than 4 hours:

            1. Check Refund Handler Agent queue depth via Monitoring Agent
            2. Verify Payment Gateway Agent network connectivity to card networks
            3. Check for any acquiring bank outages affecting reversal processing
            4. If network ACK received but Billing Agent not updated, check Kafka lag
            5. Manual intervention: Use Refund Handler Agent admin API to force state transition

            <b>Negative Balance Prevention:</b>
            The Billing Agent blocks refunds that would create negative merchant balance. When
            merchants complain about blocked refunds:

            1. Review merchant balance in Billing Agent dashboard
            2. Check if pending payouts are consuming available balance
            3. If legitimate, use Billing Agent admin API to increase credit limit temporarily
            4. Notify Risk Engine Agent team of merchants frequently hitting limits""",
            body_style,
        )
    )

    content.append(Paragraph("Chargeback Response Procedures", heading_style))
    content.append(
        Paragraph(
            """Chargebacks require rapid response to meet network deadlines. The Refund Handler
            Agent manages the dispute lifecycle with evidence from Data Pipeline Agent.

            <b>Chargeback Notification Receipt:</b>
            When card networks notify of a chargeback (via Payment Gateway Agent feed):

            1. Refund Handler Agent creates dispute record with 7-day response deadline
            2. Data Pipeline Agent is queried for transaction evidence package
            3. Evidence includes: IP address, device fingerprint, delivery confirmation, 3DS result
            4. Monitoring Agent alert fires for chargebacks exceeding $10,000 or high-risk merchants

            <b>Evidence Package Assembly:</b>
            The Refund Handler Agent auto-generates evidence packages using Data Pipeline Agent data:

            1. Transaction details: timestamp, amount, currency, merchant descriptor
            2. Customer verification: Auth Agent session data, 3DS authentication result
            3. Delivery proof: shipping tracking if available in merchant webhook data
            4. Risk assessment: Risk Engine Agent score at time of authorization
            5. Velocity context: customer's transaction history from Data Pipeline Agent

            <b>Response Submission:</b>
            Evidence packages are submitted via Payment Gateway Agent to the card network:

            1. Refund Handler Agent formats evidence per network requirements (Visa vs MC differ)
            2. Payment Gateway Agent uploads to network dispute portal
            3. Confirmation stored in Data Pipeline Agent for audit trail
            4. Notification Agent sends dispute status update to merchant

            <b>Arbitration Escalation:</b>
            If initial response is rejected and merchant wants to pursue arbitration:

            1. Refund Handler Agent escalates to arbitration queue (requires merchant approval)
            2. Additional evidence may be requested from Data Pipeline Agent
            3. Billing Agent places chargeback amount in escrow during arbitration
            4. Final ruling updates Billing Agent balance accordingly""",
            body_style,
        )
    )

    # Page 4: Payout and Reconciliation
    content.append(Paragraph("Merchant Payout Operations", heading_style))
    content.append(
        Paragraph(
            """Payouts transfer settled funds from platform accounts to merchant bank accounts.
            The Billing Agent manages payout scheduling with support from Notification Agent
            for merchant communications.

            <b>Daily Payout Processing:</b>
            Payouts run based on merchant-configured schedule (T+1, T+2, or T+7):

            1. Billing Agent calculates available balance minus reserve and pending refunds
            2. Payout batches grouped by destination bank for efficiency
            3. Billing Agent submits payout API calls to partner banks
            4. Bank confirmations update merchant balance and trigger Notification Agent

            <b>Failed Payout Investigation:</b>
            When bank rejects a payout (invalid account, closed account, etc.):

            1. Billing Agent marks payout as FAILED and retains funds in merchant balance
            2. Notification Agent sends failure notice with reason code to merchant
            3. Operations reviews pattern: single merchant vs. systematic bank issue
            4. If bank API issue, escalate to Payment Gateway Agent team (shared bank connections)

            <b>Reserve Management:</b>
            High-risk merchants have rolling reserves (10-30% of volume held for 90 days):

            1. Billing Agent automatically withholds reserve from each payout
            2. Reserve releases are scheduled 90 days after original transaction
            3. Risk Engine Agent can recommend reserve increase based on chargeback patterns
            4. Reserve disputes require Risk Engine Agent and Billing Agent joint review

            <b>Balance Reconciliation:</b>
            Daily reconciliation ensures platform accounting integrity:

            1. Billing Agent generates reconciliation report comparing transactions to payouts
            2. Data Pipeline Agent provides independent transaction totals for verification
            3. Any discrepancies flag for investigation (usually timing differences)
            4. Monthly reconciliation certified by finance team using Billing Agent reports""",
            body_style,
        )
    )

    content.append(Paragraph("Notification System Operations", heading_style))
    content.append(
        Paragraph(
            """The Notification Agent handles all customer and merchant communications. Operations
            ensures delivery reliability and manages communication preferences.

            <b>Webhook Delivery Monitoring:</b>
            Merchant webhooks are critical for order fulfillment systems. Monitor via Monitoring Agent:

            1. Webhook delivery success rate target: 99.5% first-attempt, 99.95% with retries
            2. Failing endpoints trigger escalation after 5 retry attempts over 30 minutes
            3. Repeated failures cause endpoint suspension (merchant notified via email)
            4. Reactivation requires merchant to confirm endpoint health

            <b>Email Deliverability:</b>
            Transaction receipts and notifications via email require monitoring:

            1. Check Notification Agent email provider dashboard for bounce rates
            2. Bounce rate exceeding 2% triggers investigation (Auth Agent customer data quality)
            3. Spam complaints trigger immediate review of email templates
            4. Work with Data Pipeline Agent to identify customer email validation issues

            <b>Push Notification Issues:</b>
            Mobile push notifications depend on device token validity:

            1. Invalid token errors indicate customer app uninstall or token refresh
            2. Notification Agent should mark token invalid after 3 consecutive failures
            3. Auth Agent provides updated tokens on customer's next app login
            4. High invalid token rates may indicate mobile SDK issues (escalate to eng team)""",
            body_style,
        )
    )

    doc.build(content)
    print("Created: operations_manual.pdf")


def create_troubleshooting_guide_pdf():
    """Document 3: Troubleshooting Guide - Diagnostic flows referencing both docs."""
    doc = SimpleDocTemplate(
        "troubleshooting_guide.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkred,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkred,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=12,
        leading=16,
    )

    content = []

    # Page 1: Authentication Failures
    content.append(Paragraph("NexaPay Troubleshooting Guide", title_style))
    content.append(Paragraph("Platform Support Runbook | Version 4.1", body_style))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Authentication Failure Diagnosis", heading_style))
    content.append(
        Paragraph(
            """Authentication issues originate in the Auth Agent but cascade through all downstream
            agents. This section provides diagnostic trees for common authentication failures.

            <b>Symptom: 401 Unauthorized on all endpoints</b>

            Step 1: Check Auth Agent health
            - Verify Auth Agent pods are running (kubectl get pods -l app=auth-agent)
            - Check Auth Agent logs for Redis connection errors
            - Verify Redis Cluster health via Monitoring Agent dashboard

            Step 2: If Auth Agent healthy, check session state
            - Query Auth Agent admin API for session count
            - Compare to normal baseline (2-5 million concurrent)
            - If sessions near zero, investigate recent cache flush or Redis failover

            Step 3: If sessions exist, check token validation
            - Use Auth Agent debug endpoint to validate a known-good token
            - If validation fails despite valid token, check for clock skew
            - JWT tokens require server clocks synchronized within 30 seconds

            Step 4: Cross-agent verification
            - Confirm Orchestrator Agent can reach Auth Agent (network partition check)
            - Verify Auth Agent is not rate-limiting the calling agent
            - Check if specific merchant's tokens failing (permission issue vs. system issue)

            <b>Resolution paths:</b>
            - Redis connection: Restart Auth Agent pods to reconnect
            - Clock skew: Trigger NTP sync on affected nodes
            - Network partition: Engage network operations team
            - Token format: Check for recent Auth Agent deployment that changed token format""",
            body_style,
        )
    )

    content.append(Paragraph("Session Expiration Storm", heading_style))
    content.append(
        Paragraph(
            """A session expiration storm occurs when many sessions expire simultaneously,
            causing a surge in token refresh requests that overwhelm the Auth Agent.

            <b>Symptom: Auth Agent latency spike with 429 errors</b>

            Identification:
            - Monitoring Agent shows Auth Agent p99 latency > 500ms
            - Auth Agent logs show Redis connection pool exhaustion
            - Token refresh endpoint returning 429 Too Many Requests
            - Orchestrator Agent queuing requests waiting for auth validation

            Immediate Mitigation:
            1. Enable Auth Agent emergency mode via admin API (increases connection pool)
            2. Temporarily reduce session validation cache TTL to 120 seconds
            3. Have Orchestrator Agent enable graceful degradation (allow cached validations)
            4. Scale Auth Agent replicas (kubectl scale deployment auth-agent --replicas=10)

            Root Cause Investigation:
            1. Check for recent maintenance that caused mass session invalidation
            2. Review if session TTL was recently changed (should have staggered rollout)
            3. Verify Redis cluster didn't experience failover causing session loss
            4. Check Data Pipeline Agent for unusual login patterns indicating attack

            Prevention:
            - Auth Agent sessions should use jittered expiration (random offset up to 5 min)
            - Major changes to session handling require coordinated rollout with Orchestrator
            - Monitoring Agent should alert at 70% of Auth Agent capacity before critical""",
            body_style,
        )
    )

    # Page 2: Payment Processing Failures
    content.append(Paragraph("Payment Authorization Failures", heading_style))
    content.append(
        Paragraph(
            """Payment failures can originate from multiple agents in the processing chain.
            This diagnostic tree identifies the failure point.

            <b>Symptom: High authorization decline rate (> 5% above baseline)</b>

            Step 1: Identify failure source
            - Check Monitoring Agent for which agent is returning errors
            - Payment Gateway Agent errors indicate network/bank issues
            - Risk Engine Agent blocks indicate fraud scoring issues
            - Auth Agent errors indicate session/permission issues

            Step 2: If Risk Engine Agent blocks elevated
            - Review Risk Engine Agent dashboard for score distribution
            - Check if ML model was recently updated (score drift)
            - Verify Data Pipeline Agent feature store is providing correct signals
            - If velocity rules triggering falsely, check clock synchronization

            Step 3: If Payment Gateway Agent errors
            - Check acquiring bank status pages for reported outages
            - Review Payment Gateway Agent logs for specific bank error codes
            - Verify network connectivity to bank endpoints (may need VPN check)
            - Check if specific card types failing (BIN-level issue)

            Step 4: If intermittent across agents
            - Check Orchestrator Agent request queuing (timeout-related declines)
            - Verify Kafka cluster health (event delivery delays)
            - Review Monitoring Agent for infrastructure issues (CPU, memory, network)

            <b>Specific Error Codes:</b>
            - Error 05 (Do Not Honor): Bank-side decline, no action possible
            - Error 51 (Insufficient Funds): Customer issue, no action possible
            - Error 14 (Invalid Card): Check if tokenization working in Payment Gateway
            - Error 91 (Issuer Unavailable): Bank timeout, retry may succeed
            - Risk Score 850+: Likely fraud, review in Risk Engine dashboard""",
            body_style,
        )
    )

    content.append(Paragraph("Settlement Batch Failures", heading_style))
    content.append(
        Paragraph(
            """Settlement failures require immediate attention as they affect merchant cash flow.
            The Payment Gateway Agent and Billing Agent must be investigated together.

            <b>Symptom: Settlement batch did not complete by 00:30 UTC</b>

            Step 1: Check batch generation status
            - Review Payment Gateway Agent logs for batch generation start (22:00 UTC)
            - Verify transaction aggregation completed (should show count)
            - Check for any malformed transactions blocking batch generation

            Step 2: Check SFTP upload status
            - Payment Gateway Agent logs show SFTP connection attempts
            - Verify bank SFTP endpoints are reachable (network team check)
            - Check file size - unusually large files may timeout
            - Verify SFTP credentials haven't expired (quarterly rotation)

            Step 3: Check bank acknowledgment
            - If upload successful, check for bank ACK/NACK
            - NACK with validation error: Review file format (Payment Gateway team)
            - NACK with duplicate batch: Previous batch may have succeeded
            - No response: Escalate to banking operations team

            Step 4: Post-settlement reconciliation
            - If ACK received but Billing Agent not updated, check Kafka consumer lag
            - Verify Billing Agent settlement processor is running
            - Check for any database locks in Billing Agent (transaction table)

            <b>Recovery Procedures:</b>
            - Partial batch failure: Regenerate failed portion only
            - Complete failure: Wait for bank confirmation before retry
            - Billing Agent sync issue: Trigger manual reconciliation job
            - Always notify affected merchants via Notification Agent if delay > 1 hour""",
            body_style,
        )
    )

    # Page 3: Refund and Chargeback Issues
    content.append(Paragraph("Refund Processing Failures", heading_style))
    content.append(
        Paragraph(
            """Refund failures frustrate customers and merchants. The Refund Handler Agent
            coordinates with multiple agents, so failures can have various root causes.

            <b>Symptom: Refunds stuck in PROCESSING state</b>

            Step 1: Identify the stuck stage
            - INITIATED: Refund Handler hasn't started processing (queue backed up)
            - VALIDATING: Original transaction lookup failing (Data Pipeline issue)
            - REVERSING: Payment Gateway network reversal pending
            - ACCOUNTING: Billing Agent balance update pending

            Step 2: Queue backup (INITIATED)
            - Check Refund Handler Agent queue depth via Monitoring Agent
            - Verify Refund Handler pods are healthy and not restarting
            - Check for deadlock with Billing Agent (mutual resource lock)
            - Scale Refund Handler replicas if queue growing faster than processing

            Step 3: Validation failures (VALIDATING)
            - Check Data Pipeline Agent BigQuery for original transaction
            - Verify transaction wasn't already refunded (duplicate request)
            - Check if transaction is outside refund window (180 days)
            - Review if merchant has refund permission in Auth Agent

            Step 4: Network reversal delays (REVERSING)
            - Check Payment Gateway Agent connection to card networks
            - Verify reversal was submitted (Payment Gateway logs)
            - Some networks batch reversals (Amex = up to 24h delay)
            - If network confirmed but state not updated, check Kafka lag

            Step 5: Accounting failures (ACCOUNTING)
            - Check Billing Agent for sufficient merchant balance
            - Verify no database deadlocks in Billing Agent transaction table
            - Check if fee adjustment calculation is failing (complex interchange)

            <b>Manual Intervention:</b>
            - Use Refund Handler admin API to force state transition (requires approval)
            - For Billing Agent stuck, may need to manually credit merchant account
            - Always log manual interventions in Data Pipeline for audit trail""",
            body_style,
        )
    )

    content.append(Paragraph("Chargeback Evidence Issues", heading_style))
    content.append(
        Paragraph(
            """Missing or incomplete chargeback evidence leads to lost disputes and merchant losses.
            Evidence flows from Data Pipeline Agent through Refund Handler Agent.

            <b>Symptom: Evidence package missing key data</b>

            Step 1: Check Data Pipeline availability
            - Verify BigQuery dataset contains transaction timeframe
            - Check if data retention policy purged needed records (90 days for some tables)
            - Confirm Kafka events were captured at transaction time

            Step 2: Specific missing evidence types
            - Missing 3DS result: Check Auth Agent logs for authentication flow
            - Missing device fingerprint: Check if customer used fingerprint-exempt flow
            - Missing delivery proof: Verify merchant webhook included tracking data
            - Missing risk score: Check if Risk Engine Agent scored transaction

            Step 3: Cross-reference with original transaction
            - Use Monitoring Agent distributed trace to find full transaction flow
            - Each agent should have logged their contribution to the transaction
            - Missing spans indicate agent didn't process request (Auth failure?)

            Step 4: Evidence reconstruction
            - Some evidence can be reconstructed from Monitoring Agent logs
            - IP geolocation can be re-derived from logged IP address
            - Device fingerprint may be in Auth Agent session metadata
            - Contact merchant for supplemental evidence (shipping receipts, etc.)

            <b>Escalation Path:</b>
            - If evidence truly unavailable, document gap in dispute response
            - Notify Risk Engine Agent team to improve scoring for similar transactions
            - Review Data Pipeline retention policies with compliance team
            - Consider requiring additional merchant data for high-risk categories""",
            body_style,
        )
    )

    # Page 4: Infrastructure and Integration Issues
    content.append(Paragraph("Kafka Event Delivery Failures", heading_style))
    content.append(
        Paragraph(
            """Kafka is the event backbone connecting all agents. Delivery failures cause
            data inconsistency between agents and eventual system-wide issues.

            <b>Symptom: Agent states out of sync (e.g., Payment Gateway shows success, Billing not updated)</b>

            Step 1: Check consumer lag
            - Monitoring Agent Kafka dashboard shows lag per topic per consumer
            - Lag > 10,000 messages indicates consumer falling behind
            - Lag growing steadily means consumer throughput insufficient
            - Lag spiking then recovering indicates transient processing issue

            Step 2: Identify affected consumers
            - Each agent consumes specific topics (documented in System Architecture)
            - Billing Agent consumes: payment.authorized, payment.captured, refund.completed
            - Data Pipeline Agent consumes: all topics (analytics catch-all)
            - Notification Agent consumes: all customer-facing events

            Step 3: Consumer health check
            - Verify consumer pods are running and not in crash loop
            - Check consumer logs for deserialization errors (schema mismatch)
            - Verify consumer group hasn't been reset (offset corruption)
            - Check if consumer is paused (manual intervention in past incident?)

            Step 4: Producer health check
            - Verify producing agent is publishing to correct topic
            - Check for producer acknowledgment failures in logs
            - Verify Kafka cluster has quorum and is accepting writes
            - Check if topic configuration was changed (partition count, retention)

            <b>Recovery Procedures:</b>
            - If lag is temporary, monitor until caught up
            - If consumer broken, fix and restart (messages are retained in Kafka)
            - If messages lost (rare), trigger full reconciliation between agents
            - Data Pipeline Agent can replay events to downstream consumers""",
            body_style,
        )
    )

    content.append(Paragraph("Cross-Agent Latency Issues", heading_style))
    content.append(
        Paragraph(
            """When end-to-end latency degrades, identifying the slow agent is critical.
            The Monitoring Agent provides distributed tracing to pinpoint bottlenecks.

            <b>Symptom: P99 transaction latency exceeds 100ms SLA</b>

            Step 1: Examine distributed traces
            - Use Monitoring Agent Jaeger UI to find slow transactions
            - Each agent span shows its contribution to total latency
            - Identify which agent span is longest

            Step 2: Common latency culprits
            - Auth Agent: Redis connection pool exhausted (scale Redis)
            - Risk Engine Agent: ML model inference slow (check GPU availability)
            - Payment Gateway Agent: Bank API timeout (check bank status)
            - Billing Agent: Database lock contention (check transaction volume)
            - Data Pipeline Agent: Feature store query slow (check BigQuery slots)

            Step 3: Inter-agent latency
            - If gap between agent spans, check network latency
            - Orchestrator to downstream agent calls should be < 5ms
            - If Kafka-based communication, check consumer lag
            - If HTTP-based, check connection pool sizing

            Step 4: Resource saturation check
            - CPU saturation causes processing delays
            - Memory pressure causes GC pauses
            - Network bandwidth saturation causes queuing
            - Disk I/O saturation affects logging and persistence

            <b>Remediation Playbook:</b>
            - Identify bottleneck agent from traces
            - Check that agent's resource metrics in Monitoring Agent
            - Scale horizontally if CPU-bound, vertically if memory-bound
            - If external dependency (bank, Redis), enable circuit breaker
            - Document incident and latency profile for future reference""",
            body_style,
        )
    )

    content.append(Paragraph("Complete System Outage Recovery", heading_style))
    content.append(
        Paragraph(
            """In a complete system outage, agents must be recovered in a specific order
            to ensure data consistency and proper event flow.

            <b>Recovery Order:</b>

            Phase 1 - Data Infrastructure (Target: 5 minutes)
            1. Verify Kafka cluster quorum restored
            2. Verify Redis Cluster majority available
            3. Verify PostgreSQL primary accepting connections
            4. Verify BigQuery accessible (Data Pipeline Agent dependency)

            Phase 2 - Foundation Agents (Target: +5 minutes)
            1. Start Monitoring Agent first (observability for rest of recovery)
            2. Start Data Pipeline Agent (event capture must be running)
            3. Start Auth Agent (all other agents depend on authentication)
            4. Verify Auth Agent can connect to Redis and validate tokens

            Phase 3 - Core Processing (Target: +5 minutes)
            1. Start Orchestrator Agent (central routing must be up)
            2. Start Risk Engine Agent (required for payment processing)
            3. Start Payment Gateway Agent (payment authorization path)
            4. Verify end-to-end payment flow via test transaction

            Phase 4 - Supporting Agents (Target: +5 minutes)
            1. Start Billing Agent (will catch up on Kafka events)
            2. Start Refund Handler Agent (can process queued refunds)
            3. Start Notification Agent (will send queued notifications)
            4. Verify all agents show healthy in Monitoring Agent

            Phase 5 - Reconciliation (Target: +30 minutes)
            1. Data Pipeline Agent validates event continuity
            2. Billing Agent reconciles transaction state with Payment Gateway
            3. Notification Agent clears any queued messages
            4. Run system-wide health check script

            <b>Post-Recovery:</b>
            - Enable traffic gradually (10%, 25%, 50%, 100%)
            - Monitor all agents for increased latency or errors
            - Schedule post-incident review within 48 hours
            - Update this runbook with any lessons learned""",
            body_style,
        )
    )

    doc.build(content)
    print("Created: troubleshooting_guide.pdf")


if __name__ == "__main__":
    create_architecture_pdf()
    create_operations_manual_pdf()
    create_troubleshooting_guide_pdf()
    print("\nAll PDFs generated successfully!")
