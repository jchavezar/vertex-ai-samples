from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GcpErrorItem(BaseModel):
    id: str = Field(..., description="Unique error identifier")
    timestamp: str = Field(..., description="ISO timestamp of error occurrence")
    severity: str = Field("ERROR", description="Log severity e.g. ERROR, CRITICAL, ALERT")
    serviceName: str = Field(..., description="GCP service name e.g. Cloud Run, Cloud SQL, GKE")
    resourceType: str = Field(..., description="GCP resource type e.g. cloud_run_revision, cloudsql_database")
    summary: str = Field(..., description="Short error title or headline")
    fullText: str = Field(..., description="Full text payload or detailed error message")
    logPayload: Dict[str, Any] = Field(default_factory=dict, description="Structured log payload")
    labels: Dict[str, str] = Field(default_factory=dict, description="Resource labels e.g. region, instance")

class HypothesisItem(BaseModel):
    id: str
    title: str
    relevanceScore: Optional[float] = None
    overviewText: str
    rootCauseText: str
    remediationCommands: List[str] = Field(default_factory=list)
    recommendationText: str
    relevantResources: List[str] = Field(default_factory=list)

class EvidenceItem(BaseModel):
    id: str
    title: str
    checkType: str
    commandExecuted: Optional[str] = None
    text: str
    normalOperation: Optional[bool] = None

class CloudAssistDiagnostic(BaseModel):
    investigationName: str
    title: str
    executionState: str
    recapText: str
    hypotheses: List[HypothesisItem] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    rawObservationsCount: int = 0

class DiagnoseRequest(BaseModel):
    errorItem: GcpErrorItem
    customQuery: Optional[str] = None

class ChatMessageRequest(BaseModel):
    message: str
    contextError: Optional[GcpErrorItem] = None
    contextDiagnostic: Optional[CloudAssistDiagnostic] = None
    conversationHistory: List[Dict[str, str]] = Field(default_factory=list)

class ChatMessageResponse(BaseModel):
    reply: str
    sourcesCited: List[str] = Field(default_factory=list)
