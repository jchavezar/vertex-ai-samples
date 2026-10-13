export type ArchitecturalTierId = 'TIER_1' | 'TIER_2' | 'TIER_3' | 'TIER_4';

export type BlockerFlagId =
  | 'License Compliance Blocker'
  | 'Missing ML Model in DB'
  | 'Counterfactual What-If Simulator'
  | 'Hidden Unstructured Notes'
  | 'External 3P Market API'
  | 'Incomplete Spec';

export interface ArchitecturalTier {
  id: ArchitecturalTierId;
  code: string;
  title: string;
  subtitle: string;
  coveragePct: number;
  cumulativeCeilingPct: number;
  avgConfidencePct: number;
  engineStack: string[];
  description: string;
  whyRawMcpFails: string;
}

export interface BlockerFlag {
  id: BlockerFlagId;
  label: string;
  shortCode: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  count: number;
  description: string;
  remediationPattern: string;
}

export interface KPIFormula {
  id: string;
  metricName: string;
  domain: string;
  daxExpression: string;
  canonicalSqlExpression: string;
  dataplexGlossaryTerm: string;
  sourceSystems: string[];
  grain: string;
}

export interface ExecutionStep {
  stepOrder: number;
  pillar:
    | 'PRE_FLIGHT_GOVERNANCE'
    | 'GENAI_TOOLBOX_MCP'
    | 'DATAPLEX_KC_BQCA'
    | 'PYTHON_WHAT_IF_SANDBOX'
    | 'VERTEX_UNSTRUCTURED_RAG'
    | 'EXTERNAL_MARKET_MCP'
    | 'WORKSPACE_ACTION_MESH';
  title: string;
  status: 'PASSED' | 'BLOCKED' | 'EXECUTED' | 'SYNTHESIZED';
  latencyMs: number;
  detail: string;
  artifactSnippet?: string;
}

export interface SimulationResult {
  questionId: string;
  questionText: string;
  tier: ArchitecturalTierId;
  complianceStatus: 'APPROVED' | 'BLOCKED_UNLICENSED_3P_FEED' | 'RESTRICTED_RBAC_MASKED';
  rawSqlMcpOutcome:
    | 'SUCCESS'
    | 'FAILED_HALLUCINATED_METRIC'
    | 'FAILED_MISSING_UNSTRUCTURED'
    | 'BLOCKED_LICENSE';
  federatedMeshOutcome: 'VERIFIED_SYNTHESIS' | 'GOVERNANCE_SAFE_FALLBACK';
  totalLatencyMs: number;
  traceSteps: ExecutionStep[];
  synthesizedAnswer: string;
  sqlExecuted?: string;
  dataPreview?: Array<Record<string, string | number>>;
}

export interface CopilotMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  modelUsed?: string;
  citations?: string[];
}

export interface BenchmarkQuestion {
  id: string;
  code: string;
  priority?: string;
  persona: string;
  domain: string;
  question: string;
  tier: ArchitecturalTierId;
  tierLabel: string;
  systemsInvolved: string[];
  blockerFlags: BlockerFlagId[];
  confidence_pct: number;
  missing_artifacts: string[];
  rawDbMcpSufficient: boolean;
  dataplexKcCeilingSufficient: boolean;
  requiresMultiToolFederation: boolean;
  architecturalDiagnosis: string;
  recommendedArchitecture?: string;
  daxOrMetricFormula: KPIFormula;
  genaiToolboxYaml: string;
  bigqueryGoldViewDdl: string;
  defaultSimulation: SimulationResult;
}
