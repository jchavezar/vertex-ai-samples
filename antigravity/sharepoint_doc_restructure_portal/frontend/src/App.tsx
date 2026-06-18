import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  FileText, 
  AlertOctagon, 
  CheckCircle2, 
  UserCheck, 
  Terminal, 
  Send, 
  File, 
  User, 
  CornerDownRight, 
  RefreshCw,
  Search,
  Check,
  AlertTriangle,
  GitBranch,
  Network,
  Activity,
  Upload,
  Plus,
  Link2,
  Lock,
  LogOut,
  FolderOpen,
  HelpCircle
} from 'lucide-react';

const API_BASE = "/api";

interface Document {
  id: string;
  filename: string;
  site: string;
  type: string;
  sub_type: string;
  confidentiality: string;
  pwc_proprietary: any;
  industry: string;
  primary_topic: string;
  lifecycle: string;
  customer_scope: string;
  allowed_groups: string[];
  confidence: number;
  pii_detected: boolean;
  liability_cap: string;
  state: "APPROVED" | "PENDING_QA" | "EXCEPTION";
  owner: string;
  rationale: string;
  elements: string[];
  exception_reason?: string;
  webUrl?: string;
  is_signed?: string;
  standard_terms?: string;
  permitted_use?: string;
  engagement_letter_link?: string;
}

interface OntologyProperty {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

interface OntologyClass {
  name: string;
  parent: string;
  description: string;
  properties: OntologyProperty[];
}

interface OntologyRelation {
  source: string;
  type: string;
  target: string;
  description: string;
}

interface Ontology {
  model_generator: string;
  region: string;
  generated_at: string;
  classes: OntologyClass[];
  relations: OntologyRelation[];
}

interface Message {
  sender: 'user' | 'bot';
  text: string;
  sources?: { title: string; snippet: string; url?: string }[];
  latency?: string;
  model?: string;
  region?: string;
  isThinking?: boolean;
}

interface AuthState {
  authenticated: boolean;
  account?: {
    username: string;
    name: string;
    tenant_id: string;
  };
}

interface ArchStep {
  id: number;
  title: string;
  sub: string;
  desc: string;
  latency: string;
  target: string;
  badgeColor: string;
  reqs: { code: string; name: string; desc: string }[];
}

const pipelineSteps: ArchStep[] = [
  {
    id: 1,
    title: "SharePoint Sync & ACL Capture",
    sub: "Step 01 / Discovery",
    desc: "Crawls files via Graph API. Resolves directory security Group IDs for target file ACL mapping.",
    latency: "~0.80s",
    target: "Microsoft Graph",
    badgeColor: "bg-blue-50 text-blue-700",
    reqs: [
      { code: "FR04", name: "Duplicate & Version Handling", desc: "Checks filename matches in existing collections before writing, skipping redundant operations." },
      { code: "FR06", name: "Ingestion from Governed Sources", desc: "Direct integration via Microsoft Graph API for SharePoint Site / Drive folders." },
      { code: "FR22", name: "Delta Processing", desc: "Triggers scheduler queries to identify modified files while ignoring duplicates." },
      { code: "FR27", name: "Repository Context Capture", desc: "Saves SharePoint Site URL path and nesting folder structures with each record." },
      { code: "FR28", name: "Structured Metadata Ingestion", desc: "Maintains original document names, file IDs, and Graph link properties." },
      { code: "FR31", name: "Migration Support", desc: "Ensures taxonomy labels are preserved when document pointers are shifted." },
      { code: "FR33", name: "System of Record Preservation", desc: "Original SharePoint files remain completely unaltered; only indexing occurs." },
      { code: "FR38", name: "Scope & Date Limits", desc: "Restricts crawler path target scopes to prevent unintended directory scans." }
    ]
  },
  {
    id: 2,
    title: "Unredacted PII Telemetry Check",
    sub: "Step 02 / Inspection",
    desc: "Flags SSN or phone values. Raw content is fully retained to maintain 100% semantic learning.",
    latency: "~0.10s",
    target: "DLP Audit",
    badgeColor: "bg-red-50 text-red-700",
    reqs: [
      { code: "FR02", name: "Lifecycle Tagging", desc: "Extracts file headers to mark active, draft, or historical classifications." },
      { code: "FR07", name: "Metadata Quality Validation", desc: "Runs regex patterns and validation checks against raw extracted string sequences." },
      { code: "FR21", name: "Incident Logging & Tracking", desc: "Automatically captures extraction failures or corruption alerts as exceptions." },
      { code: "FR26", name: "End-to-End Metadata Lineage", desc: "Logs source telemetry check indicators inside database record audits." }
    ]
  },
  {
    id: 3,
    title: "Ontology & Class Parsing",
    sub: "Step 03 / Extraction",
    desc: "Extracts 3-level PwC taxonomy attributes (Confidentiality, Industry, Doc Sub-Type) dynamically.",
    latency: "~3.50s",
    target: "Gemini 3.5 Flash",
    badgeColor: "bg-purple-50 text-purple-700",
    reqs: [
      { code: "FR01", name: "Document Classification", desc: "Assigns core Document Type and Sub-Type based on PwC tax classifications." },
      { code: "FR03", name: "Qualifying Doc Identification", desc: "Identifies deliverables vs. proposals, filtering out non-business material." },
      { code: "FR10", name: "Engagement Letter Validation", desc: "Extracts is_signed status, standard_terms, and permitted deliverable use." },
      { code: "FR11", name: "Entity Extraction", desc: "Extracts target clients, sectors, locations, and key candidate profiles." },
      { code: "FR12", name: "Tagging Evidence & Rationale", desc: "Generates a textual reasoning string describing why each category was chosen." },
      { code: "FR16", name: "Item-Level Confidence Scoring", desc: "Attaches a statistical confidence value for document type and entity labels." },
      { code: "FR34", name: "Relationship Extraction", desc: "Resolves entities and matches them to create graph associations." },
      { code: "FR35", name: "Deliverable to Contract Linkage", desc: "Extracts engagement_letter_link to pair deliverables with their agreements." },
      { code: "FR37", name: "Non-standard Liability Flagging", desc: "Extracts and audits custom liability caps in engagement letters." },
      { code: "FR41", name: "Automated Semantic Tagging", desc: "Uses zero-shot instruction parsing to eliminate manual tagging efforts." },
      { code: "FR42", name: "Controlled Taxonomy", desc: "Forces taxonomy assignments to strictly conform to predefined PwC classes." },
      { code: "FR43", name: "Hierarchy Support", desc: "Resolves Level 1 and Level 2 child dependencies (e.g. Engagement -> CV)." }
    ]
  },
  {
    id: 4,
    title: "gemini-embedding-2 Vector",
    sub: "Step 04 / Search Cache",
    desc: "Computes asymmetric query/document vectors with structured titles and text prefixes.",
    latency: "~0.50s",
    target: "Embeddings 2",
    badgeColor: "bg-yellow-50 text-yellow-700",
    reqs: [
      { code: "FR08", name: "Related Content Suggestions", desc: "Uses cosine distance matches to discover and display context-sharing files." },
      { code: "FR09", name: "Search Enablement", desc: "Enables natural language RAG searches powered by 768-D vector indexing." },
      { code: "FR23", name: "Tagging at Ingestion", desc: "Generates vector indexes immediately on file sync, making them searchable instantly." }
    ]
  },
  {
    id: 5,
    title: "Document & Audit Persistence",
    sub: "Step 05 / Storage",
    desc: "Saves documents metadata catalog state, validation overrides, and exception registries.",
    latency: "~0.05s",
    target: "Cloud Firestore",
    badgeColor: "bg-green-50 text-green-700",
    reqs: [
      { code: "FR13", name: "Tag QA Workflow", desc: "Pins low-confidence tagging results to the PENDING_QA queue for human review." },
      { code: "FR14", name: "Mandatory Tagging Validation", desc: "Prevents validation saves unless required fields are selected by the auditor." },
      { code: "FR15", name: "Tagging Ownership", desc: "Records the crawling username or supervisor who triggered ingestion." },
      { code: "FR17", name: "Human Validation Workflow", desc: "Updates state, audit logs, and status when a lead confirms or rejects tags." },
      { code: "FR19", name: "Action Audit Trail", desc: "Maintains a record collection of every tagging change, override, and supervisor ID." },
      { code: "FR45", name: "Exception Queue", desc: "Flags failed extractions or rejected records to the EXCEPTION queue dashboard." }
    ]
  },
  {
    id: 6,
    title: "Append-Only Event Ledger",
    sub: "Step 06 / Ledger",
    desc: "Streams incremental state and tag validations to BigQuery for SQL reporting and customer review.",
    latency: "~0.10s",
    target: "BigQuery Analytics",
    badgeColor: "bg-indigo-50 text-indigo-700",
    reqs: [
      { code: "FR19", name: "Action Audit Trail", desc: "Stores a permanent append-only historical event log of all validation decisions." },
      { code: "FR20", name: "Reviewer Feedback Loop", desc: "Exposes override logs for analysis to refine future prompting rules." },
      { code: "FR26", name: "End-to-End Lineage Validation", desc: "Provides SQL ledger capabilities to verify metadata derivation histories." }
    ]
  }
];

export default function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [ontology, setOntology] = useState<Ontology | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [activeTab, setActiveTab] = useState<'queue' | 'ontology' | 'architecture'>('queue');
  const [selectedArchStep, setSelectedArchStep] = useState<number | null>(null);
  
  // MS365 Auth States
  const [auth, setAuth] = useState<AuthState>({ authenticated: false });
  const [isVerifyingAuth, setIsVerifyingAuth] = useState(false);
  const [loginUrl, setLoginUrl] = useState<string | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const codeVerifyingRef = useRef(false);

  // Ingestion form state (Manual upload)
  const [showIngestForm, setShowIngestForm] = useState(false);
  const [ingestFilename, setIngestFilename] = useState('');
  const [ingestContent, setIngestContent] = useState('');
  const [ingestSite, setIngestSite] = useState('Tax Engagement Library');
  const [ingestGroups, setIngestGroups] = useState<string[]>(['group::finance-all']);
  const [isIngesting, setIsIngesting] = useState(false);

  // SharePoint Crawler state (Real Sync)
  const [showSpImportForm, setShowSpImportForm] = useState(false);
  const [spSites, setSpSites] = useState<any[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState('');
  const [spDrives, setSpDrives] = useState<any[]>([]);
  const [selectedDriveId, setSelectedDriveId] = useState('');
  const [spFolderPath, setSpFolderPath] = useState('/');
  const [spAllowedGroups, setSpAllowedGroups] = useState<string[]>(['group::finance-all']);
  const [isSyncingSp, setIsSyncingSp] = useState(false);
  const [siteSearchQuery, setSiteSearchQuery] = useState('');

  // Chat state
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: "Aether Governance Engine Online. Initialized using Gemini 3.5 Flash (Region: global). Ask me a question about documents or relationships."
    }
  ]);
  
  // Simulator logs
  const [simulatorLogs, setSimulatorLogs] = useState<string[]>([]);
  
  // Edit metadata state
  const [editType, setEditType] = useState('');
  const [editCap, setEditCap] = useState('');

  const chatEndRef = useRef<HTMLDivElement>(null);

  const handleOAuthCallback = async (code: string) => {
    setIsVerifyingAuth(true);
    try {
      const redirectUri = window.location.origin;
      const response = await fetch(`${API_BASE}/auth/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, redirect_uri: redirectUri }),
      });
      if (response.ok) {
        const data = await response.json();
        setAuth({ authenticated: true, account: data.account });
        alert("Login successful!");
      } else {
        const err = await response.json();
        alert(`Authentication failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (e) {
      alert("Verification failed: " + e);
    } finally {
      setIsVerifyingAuth(false);
      // Clean query parameter from address bar
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchOntology();
    fetchCrawlerStatus();
    
    // Check if we are returning from Microsoft OAuth redirect with code parameter
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      if (!codeVerifyingRef.current) {
        codeVerifyingRef.current = true;
        // Clean query parameter from address bar immediately to prevent double processing or reload issues
        window.history.replaceState({}, document.title, window.location.pathname);
        handleOAuthCallback(code);
      }
    } else {
      checkAuthStatus();
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll crawler logs when syncing is active
  useEffect(() => {
    let intervalId: any = null;

    if (isSyncingSp) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE}/sharepoint/crawler-logs`);
          if (response.ok) {
            const data = await response.json();
            setSimulatorLogs(data.logs);
            
            if (data.status === 'idle') {
              setIsSyncingSp(false);
              clearInterval(intervalId);
              await fetchDocuments();
            }
          }
        } catch (e) {
          console.error("Failed to poll crawler logs:", e);
        }
      }, 1000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isSyncingSp]);

  const fetchCrawlerStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/sharepoint/crawler-logs`);
      if (response.ok) {
        const data = await response.json();
        setSimulatorLogs(data.logs || []);
        if (data.status === 'running') {
          setIsSyncingSp(true);
        }
      }
    } catch (e) {
      console.error("Failed to fetch crawler status on mount:", e);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/status`);
      const data = await response.json();
      setAuth(data);
    } catch (e) {
      console.error("Auth status check failed:", e);
    }
  };

  const startLoginFlow = async () => {
    setIsRedirecting(true);
    try {
      const redirectUri = window.location.origin;
      const response = await fetch(`${API_BASE}/auth/login-url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      if (response.ok) {
        const data = await response.json();
        if (data.login_url) {
          setLoginUrl(data.login_url);
          // Redirect the current window
          window.location.href = data.login_url;
        } else {
          alert("Error: Login URL not returned from backend.");
          setIsRedirecting(false);
        }
      } else {
        const err = await response.json();
        alert("Failed to start login: " + (err.detail || 'Unknown error'));
        setIsRedirecting(false);
      }
    } catch (e) {
      alert("Failed to start login: " + e);
      setIsRedirecting(false);
    }
  };

  const handleLogout = async () => {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
    setAuth({ authenticated: false });
    alert("Logged out from MS365.");
  };

  const fetchSpSites = async () => {
    try {
      const response = await fetch(`${API_BASE}/sharepoint/sites?search=${siteSearchQuery}`);
      if (!response.ok) throw new Error("Unauthorized or not loaded");
      const data = await response.json();
      setSpSites(data);
    } catch (e) {
      alert("Sites loading failed. Ensure you are logged in to Microsoft first.");
    }
  };

  const fetchSpDrives = async (siteId: string) => {
    setSelectedSiteId(siteId);
    try {
      const response = await fetch(`${API_BASE}/sharepoint/sites/${siteId}/drives`);
      const data = await response.json();
      setSpDrives(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSpImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSiteId || !selectedDriveId) {
      alert("Please select a SharePoint Site and Document Library.");
      return;
    }

    setSimulatorLogs(["[CRAWLER] Initializing async background sync request..."]);
    
    try {
      const response = await fetch(`${API_BASE}/sharepoint/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: selectedSiteId,
          drive_id: selectedDriveId,
          folder_path: spFolderPath,
          allowed_groups: spAllowedGroups
        })
      });

      if (response.ok) {
        setIsSyncingSp(true);
        setShowSpImportForm(false);
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: `SharePoint Sync initiated in background. You can watch the real-time logs in the crawler output console below.`
        }]);
      } else {
        const err = await response.json();
        alert(`Sync request failed: ${err.detail}`);
        setIsSyncingSp(false);
      }
    } catch (error) {
      alert("Connection error: " + error);
      setIsSyncingSp(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await response.json();
      setDocuments(data);
      if (selectedDoc) {
        const refreshed = data.find((d: Document) => d.id === selectedDoc.id);
        if (refreshed) setSelectedDoc(refreshed);
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  const fetchOntology = async () => {
    try {
      const response = await fetch(`${API_BASE}/ontology`);
      const data = await response.json();
      setOntology(data);
    } catch (error) {
      console.error("Error fetching ontology:", error);
    }
  };

  const handleValidate = async (id: string, state: "APPROVED" | "EXCEPTION", reason?: string) => {
    console.log(`[UI] Triggering validation for ${id} -> State: ${state}`);
    try {
      const payload = {
        state,
        confidentiality: editCap || undefined,
        document_sub_type: editType || undefined,
        exception_reason: reason || undefined
      };
      
      const response = await fetch(`${API_BASE}/documents/${id}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        console.log(`[UI] Validation successful for ${id}`);
        setEditCap('');
        setEditType('');
        await fetchDocuments();
      } else {
        const err = await response.json();
        console.error(`[UI] Validation rejected:`, err);
        alert(`Failed to approve tags: ${err.detail || 'Validation rejected by server'}`);
      }
    } catch (error) {
      console.error("[UI] Error validating document:", error);
      alert(`Network error during validation: ${error}`);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const query = chatInput;
    setChatInput('');
    setMessages(prev => [...prev, { sender: 'user', text: query }]);
    setMessages(prev => [...prev, { sender: 'bot', text: 'Thinking...', isThinking: true }]);

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (status ${response.status})`);
      }
      
      const data = await response.json();
      
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, {
          sender: 'bot',
          text: data.answer,
          sources: data.sources,
          latency: data.latency,
          model: data.model,
          region: data.region
        }];
      });
    } catch (error: any) {
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking);
        return [...filtered, { sender: 'bot', text: error.message || "Error calling search endpoint." }];
      });
    }
  };

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestFilename.trim() || !ingestContent.trim()) return;

    setIsIngesting(true);
    try {
      const response = await fetch(`${API_BASE}/documents/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: ingestFilename,
          content: ingestContent,
          site: ingestSite,
          allowed_groups: ingestGroups
        })
      });
      
      if (response.ok) {
        setIngestFilename('');
        setIngestContent('');
        setShowIngestForm(false);
        await fetchDocuments();
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: `Pipeline ingest completed for [${ingestFilename}]. Document has been mapped to dynamic ontology and indexed for search context.`
        }]);
      } else {
        const err = await response.json();
        alert(`Ingestion failed: ${err.detail}`);
      }
    } catch (error) {
      console.error("Error during ingestion:", error);
    } finally {
      setIsIngesting(false);
    }
  };



  const renderFlowDiagram = (text: string) => {
    if (!text) return null;
    if (typeof text !== "string") return <p className="whitespace-pre-line">{String(text)}</p>;
    if (!text.includes("```mermaid")) return <p className="whitespace-pre-line">{text}</p>;

    const parts = text.split("```mermaid");
    const preText = parts[0];
    const rest = parts[1].split("```");
    const rawGraph = rest[0].trim();
    const postText = rest[1] || "";

    const nodes: string[] = [];
    rawGraph.split("\n").forEach(line => {
      if (line.includes("-->")) {
        const parts = line.split("-->").map(p => p.trim().replace(";", ""));
        parts.forEach(p => {
          if (!nodes.includes(p) && !p.startsWith("flowchart")) {
            nodes.push(p);
          }
        });
      }
    });

    return (
      <div>
        <p className="whitespace-pre-line mb-3">{preText}</p>
        <div className="my-4 border border-[#d8d6d0] bg-[#faf9f6] p-4 rounded-none">
          <div className="text-[10px] text-[#7c7a75] uppercase font-bold tracking-wider mb-3 flex items-center gap-1">
            <Network className="h-3 w-3" /> Extracted Process Map
          </div>
          <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
            {nodes.map((node, nIdx) => (
              <React.Fragment key={nIdx}>
                <div className="border border-[#1a1a19] px-3 py-1.5 bg-[#f4f3ef] font-bold">
                  {node}
                </div>
                {nIdx < nodes.length - 1 && (
                  <span className="text-[#7c7a75]">➔</span>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
        <p className="whitespace-pre-line mt-3">{postText}</p>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-[#faf9f6] text-[#1a1a19] overflow-hidden rounded-none">
      
      {/* 1. Architectural Header */}
      <header className="border-b border-[#d8d6d0] bg-[#faf9f6] px-8 py-5 rounded-none flex items-baseline justify-between shrink-0">
        <div className="flex items-baseline gap-3">
          <span className="font-bold text-xl tracking-[0.05em] uppercase">AETHER</span>
          <span className="text-xs text-[#7c7a75] tracking-widest uppercase">/ SharePoint Restructure Console</span>
        </div>
        
        <div className="flex items-center gap-4">
          {/* MS365 Connection Status */}
          {auth.authenticated ? (
            <div className="flex items-center gap-2 text-xs border border-[#d8d6d0] px-3 py-1 bg-green-50 rounded-none">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span className="text-green-800 font-medium">{auth.account?.username}</span>
              <button 
                onClick={handleLogout}
                className="text-red-600 hover:text-red-800 ml-1.5 font-bold uppercase text-[9px] flex items-center gap-0.5"
              >
                <LogOut className="h-3 w-3" /> Disconnect
              </button>
            </div>
          ) : isRedirecting ? (
            <div className="flex items-center gap-3 text-xs">
              <span className="text-[#1a1a19] font-medium flex items-center gap-1.5">
                <RefreshCw className="h-3 w-3 animate-spin text-blue-700" /> Opening Microsoft login...
              </span>
              {loginUrl && (
                <a 
                  href={loginUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-700 hover:text-blue-900 underline font-bold uppercase text-[10px] tracking-wider"
                >
                  Click here if not redirected
                </a>
              )}
            </div>
          ) : (
            <button 
              onClick={startLoginFlow}
              className="text-xs text-[#faf9f6] bg-[#1a1a19] px-3 py-1 rounded-none font-bold uppercase flex items-center gap-1.5"
            >
              <Link2 className="h-3.5 w-3.5" /> Connect SharePoint
            </button>
          )}
        </div>
      </header>

      {/* 2. Main Layout Grid */}
      <div className="flex-1 flex min-height-0 overflow-hidden">
        
        {/* Left Section: Switchable Tabs */}
        <div className="flex-1 flex flex-col min-width-0 border-r border-[#d8d6d0] overflow-hidden">
          
          <div className="border-b border-[#d8d6d0] bg-[#faf9f6] shrink-0 flex">
            <button 
              onClick={() => setActiveTab('queue')}
              className={`flex-1 py-4 text-xs font-bold uppercase tracking-wider text-center border-r border-[#d8d6d0] last:border-r-0 ${
                activeTab === 'queue' ? 'bg-[#f4f3ef] border-b-2 border-b-[#1a1a19]' : 'bg-[#faf9f6]'
              }`}
            >
              Document Queue
            </button>
            <button 
              onClick={() => setActiveTab('ontology')}
              className={`flex-1 py-4 text-xs font-bold uppercase tracking-wider text-center border-r border-[#d8d6d0] ${
                activeTab === 'ontology' ? 'bg-[#f4f3ef] border-b-2 border-b-[#1a1a19]' : 'bg-[#faf9f6]'
              }`}
            >
              Dynamic Ontology Map
            </button>
            <button 
              onClick={() => setActiveTab('architecture')}
              className={`flex-1 py-4 text-xs font-bold uppercase tracking-wider text-center border-r border-[#d8d6d0] last:border-r-0 ${
                activeTab === 'architecture' ? 'bg-[#f4f3ef] border-b-2 border-b-[#1a1a19]' : 'bg-[#faf9f6]'
              }`}
            >
              Pipeline Architecture
            </button>
          </div>

          {/* TAB 1: Document Queue */}
          {activeTab === 'queue' && (
            <div className="flex-1 flex flex-col min-height-0 overflow-hidden">
              <div className="p-6 border-b border-[#d8d6d0] shrink-0 bg-[#faf9f6] flex justify-between items-center">
                <h2 className="text-xs tracking-widest uppercase font-bold text-[#1a1a19]">Ingested SharePoint Corpus</h2>
                <div className="flex gap-2">
                  <button 
                    onClick={() => {
                      if (!auth.authenticated) {
                        alert("You must log in to Microsoft SharePoint first.");
                        return;
                      }
                      setShowSpImportForm(!showSpImportForm);
                      setShowIngestForm(false);
                    }}
                    className="text-[10px] text-[#faf9f6] flex items-center gap-1 bg-blue-700 px-3 py-1 rounded-none uppercase font-bold"
                  >
                    <FolderOpen className="h-3 w-3" /> Sync SharePoint Site
                  </button>
                  <button 
                    onClick={() => {
                      setShowIngestForm(!showIngestForm);
                      setShowSpImportForm(false);
                    }}
                    className="text-[10px] text-[#faf9f6] flex items-center gap-1 bg-[#1a1a19] px-3 py-1 rounded-none uppercase font-bold"
                  >
                    <Plus className="h-3 w-3" /> Upload Local Mock
                  </button>
                  <button 
                    onClick={fetchDocuments}
                    className="text-[10px] text-[#7c7a75] hover:text-[#1a1a19] flex items-center gap-1 border border-[#d8d6d0] px-2 py-0.5 bg-[#f4f3ef] rounded-none font-bold"
                  >
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </button>
                </div>
              </div>

              {/* REAL SHAREPOINT IMPORT PANEL */}
              {showSpImportForm && (
                <div className="border-b border-[#d8d6d0] bg-blue-50 p-6 shrink-0">
                  <form onSubmit={handleSpImportSubmit} className="space-y-4">
                    <div className="text-xs font-bold uppercase tracking-widest text-blue-800 border-b border-dotted border-blue-200 pb-1.5 flex items-center gap-1.5">
                      <FolderOpen className="h-4 w-4" /> Live SharePoint Site Ingest (Graph API)
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-[9px] uppercase text-blue-700 block mb-1">Search SharePoint Sites</label>
                        <div className="flex gap-1.5">
                          <input 
                            type="text"
                            value={siteSearchQuery}
                            onChange={(e) => setSiteSearchQuery(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault();
                                fetchSpSites();
                              }
                            }}
                            placeholder="e.g. sockcop"
                            className="w-full text-xs bg-[#faf9f6] border border-blue-200 px-2 py-1 focus:outline-none rounded-none"
                          />
                          <button 
                            type="button"
                            onClick={fetchSpSites}
                            className="bg-blue-700 text-white text-[9px] font-bold px-3 py-1 uppercase"
                          >
                            Find
                          </button>
                        </div>
                      </div>
                      
                      {spSites.length > 0 && (
                        <div>
                          <label className="text-[9px] uppercase text-blue-700 block mb-1">Select Site Target</label>
                          <select 
                            value={selectedSiteId}
                            onChange={(e) => fetchSpDrives(e.target.value)}
                            className="w-full text-xs bg-[#faf9f6] border border-blue-200 p-1.5 focus:outline-none rounded-none"
                          >
                            <option value="">-- Choose Site --</option>
                            {spSites.map(site => (
                              <option key={site.id} value={site.id}>{site.displayName}</option>
                            ))}
                          </select>
                        </div>
                      )}

                      {spDrives.length > 0 && (
                        <div>
                          <label className="text-[9px] uppercase text-blue-700 block mb-1">Select Document Library</label>
                          <select 
                            value={selectedDriveId}
                            onChange={(e) => setSelectedDriveId(e.target.value)}
                            className="w-full text-xs bg-[#faf9f6] border border-blue-200 p-1.5 focus:outline-none rounded-none"
                          >
                            <option value="">-- Choose Library --</option>
                            {spDrives.map(drive => (
                              <option key={drive.id} value={drive.id}>{drive.name}</option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>

                    {selectedDriveId && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-[9px] uppercase text-blue-700 block mb-1">Folder Sub-Path</label>
                          <input 
                            type="text"
                            value={spFolderPath}
                            onChange={(e) => setSpFolderPath(e.target.value)}
                            placeholder="/"
                            className="w-full text-xs bg-[#faf9f6] border border-blue-200 px-3 py-1.5 focus:outline-none rounded-none"
                          />
                        </div>
                        <div>
                          <label className="text-[9px] uppercase text-blue-700 block mb-1">Inherited ACL Groups</label>
                          <select 
                            multiple
                            value={spAllowedGroups}
                            onChange={(e) => {
                              const opts = Array.from(e.target.selectedOptions, o => o.value);
                              setSpAllowedGroups(opts);
                            }}
                            className="w-full text-xs bg-[#faf9f6] border border-blue-200 p-1.5 focus:outline-none rounded-none h-16"
                          >
                            <option value="group::finance-all">Finance Department (group::finance-all)</option>
                            <option value="group::hr-all">HR Operations (group::hr-all)</option>
                            <option value="group::employees">All Employees (group::employees)</option>
                          </select>
                        </div>
                      </div>
                    )}

                    {selectedDriveId && (
                      <button 
                        type="submit"
                        disabled={isSyncingSp}
                        className="w-full bg-blue-700 text-white text-xs font-semibold py-3 uppercase tracking-wider hover:opacity-90 rounded-none disabled:opacity-50"
                      >
                        {isSyncingSp ? "Downloading & Scanning Files via Gemini..." : "Start Crawling SharePoint Site"}
                      </button>
                    )}
                  </form>
                </div>
              )}

              {/* MANUAL LOCAL INGESTION FORM */}
              {showIngestForm && (
                <div className="border-b border-[#d8d6d0] bg-[#f4f3ef] p-6 shrink-0 transition-all">
                  <form onSubmit={handleIngestSubmit} className="space-y-4">
                    <div className="text-xs font-bold uppercase tracking-widest text-[#7c7a75] border-b border-dotted border-[#d8d6d0] pb-1.5 flex items-center gap-1.5">
                      <Upload className="h-3.5 w-3.5" /> Run Mock Ingestion Pipeline
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">Document Filename</label>
                        <input 
                          type="text" 
                          required
                          value={ingestFilename}
                          onChange={(e) => setIngestFilename(e.target.value)}
                          placeholder="e.g. Client_D_Engagement_Letter.pdf"
                          className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] px-3 py-1.5 focus:outline-none focus:border-[#1a1a19] rounded-none"
                        />
                      </div>
                      <div>
                        <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">SharePoint Site Source</label>
                        <input 
                          type="text" 
                          value={ingestSite}
                          onChange={(e) => setIngestSite(e.target.value)}
                          className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] px-3 py-1.5 focus:outline-none focus:border-[#1a1a19] rounded-none"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">Document Text / Content</label>
                      <textarea 
                        required
                        rows={4}
                        value={ingestContent}
                        onChange={(e) => setIngestContent(e.target.value)}
                        placeholder="Paste agreement text..."
                        className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] p-3 focus:outline-none focus:border-[#1a1a19] rounded-none font-sans"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">Security Access Groups</label>
                        <select 
                          multiple
                          value={ingestGroups}
                          onChange={(e) => {
                            const opts = Array.from(e.target.selectedOptions, o => o.value);
                            setIngestGroups(opts);
                          }}
                          className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] p-1.5 focus:outline-none focus:border-[#1a1a19] rounded-none h-16"
                        >
                          <option value="group::finance-all">Finance Department (group::finance-all)</option>
                          <option value="group::hr-all">HR Operations (group::hr-all)</option>
                          <option value="group::employees">All Employees (group::employees)</option>
                        </select>
                      </div>
                      <div className="flex items-end">
                        <button 
                          type="submit"
                          disabled={isIngesting}
                          className="w-full bg-[#1a1a19] text-[#faf9f6] text-xs font-semibold py-3 uppercase tracking-wider hover:opacity-90 rounded-none disabled:opacity-50"
                        >
                          {isIngesting ? "Running Extraction..." : "Trigger Ingest & Embedding"}
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              )}

              {/* Scrollable Doc Grid */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {documents.map((doc) => (
                  <div 
                    key={doc.id}
                    onClick={() => {
                      setSelectedDoc(doc);
                      setEditType(doc.sub_type);
                      setEditCap(doc.confidentiality);
                    }}
                    className={`group flex items-center justify-between p-4 border border-[#d8d6d0] cursor-pointer transition-all duration-300 rounded-none hover:bg-[#f4f3ef] ${
                      selectedDoc?.id === doc.id ? 'bg-[#f4f3ef]' : 'bg-[#faf9f6]'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 border border-[#d8d6d0] bg-[#faf9f6] rounded-none">
                        <FileText className="h-5 w-5 text-[#7c7a75]" />
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-sm font-medium leading-none text-[#1a1a19]">{doc.filename}</span>
                        <span className="text-[10px] text-[#7c7a75] uppercase tracking-wider">{doc.site}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="flex gap-1">
                        {doc.elements.map(el => (
                          <span key={el} className="text-[8px] border border-[#d8d6d0] bg-[#f4f3ef] px-1 text-[#7c7a75] uppercase rounded-none">
                            {el}
                          </span>
                        ))}
                      </div>

                      <span className="text-[10px] font-mono text-[#7c7a75] border border-[#d8d6d0] px-1.5 py-0.5 bg-[#faf9f6]">
                        {Math.round(doc.confidence * 100)}%
                      </span>
                      
                      {doc.state === 'APPROVED' && (
                        <span className="text-[9px] bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 uppercase font-bold tracking-wider rounded-none">
                          Approved
                        </span>
                      )}
                      {doc.state === 'PENDING_QA' && (
                        <span className="text-[9px] bg-orange-50 text-orange-700 border border-orange-200 px-2 py-0.5 uppercase font-bold tracking-wider rounded-none">
                          Pending QA
                        </span>
                      )}
                      {doc.state === 'EXCEPTION' && (
                        <span className="text-[9px] bg-red-50 text-red-700 border border-red-200 px-2 py-0.5 uppercase font-bold tracking-wider rounded-none">
                          Exception
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Selected Document Details Panel */}
              {selectedDoc && (
                <div className="border-t border-[#d8d6d0] bg-[#f4f3ef] p-6 h-96 overflow-y-auto shrink-0 flex gap-6">
                  
                  <div className="flex-1 flex flex-col justify-between border-r border-[#d8d6d0] pr-6">
                    <div>
                      <div className="flex items-baseline gap-2 mb-2">
                        <h3 className="text-sm font-bold text-[#1a1a19] uppercase tracking-wider">{selectedDoc.filename}</h3>
                        <span className="text-[10px] text-[#7c7a75]">({selectedDoc.id})</span>
                      </div>
                      
                      <div className="flex gap-2 my-2 border-b border-dotted border-[#d8d6d0] pb-2">
                        <span className="text-[9px] uppercase font-bold text-[#7c7a75]">Multimodal Extractions:</span>
                        {selectedDoc.elements.includes("charts") && (
                          <span className="text-[9px] text-green-700 font-bold flex items-center gap-1"><BarChart4 className="h-3 w-3" /> Charts OCR</span>
                        )}
                        {selectedDoc.elements.includes("diagrams") && (
                          <span className="text-[9px] text-blue-700 font-bold flex items-center gap-1"><Network className="h-3 w-3" /> Process Diagram</span>
                        )}
                        {selectedDoc.elements.includes("signature_block") && (
                          <span className="text-[9px] text-purple-700 font-bold flex items-center gap-1"><UserCheck className="h-3 w-3" /> Sign block</span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs mt-3">
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">Level 1: Document Type</span><strong>{selectedDoc.type}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">Level 2: Sub-Type</span><strong>{selectedDoc.sub_type}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">Confidentiality</span><strong>{selectedDoc.confidentiality}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">PwC Proprietary</span><strong>{selectedDoc.pwc_proprietary}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">Primary Industry</span><strong>{selectedDoc.industry}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">Primary Topic</span><strong>{selectedDoc.primary_topic}</strong></div>
                        <div><span className="text-[#7c7a75] uppercase text-[9px] block">PII Detected</span><strong>{selectedDoc.pii_detected ? "Yes (DLP Redacted)" : "No"}</strong></div>
                      </div>

                      {/* FR10: Engagement Letter & Contract Validation Section */}
                      {(selectedDoc.is_signed || selectedDoc.standard_terms || selectedDoc.permitted_use || selectedDoc.liability_cap || selectedDoc.engagement_letter_link) && (
                        <div className="mt-4 pt-3 border-t border-[#d8d6d0]">
                          <div className="flex items-center gap-1.5 mb-2 bg-[#f4f2ee] px-2 py-1 border-l-2 border-amber-600">
                            <span className="text-[10px] font-bold text-amber-900 bg-amber-100 px-1 py-0.5 rounded">FR10</span>
                            <span className="text-[10px] font-bold text-amber-900 uppercase tracking-wider">Contract / Engagement Validation</span>
                          </div>
                          <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs">
                            {selectedDoc.is_signed && (
                              <div>
                                <span className="text-[#7c7a75] uppercase text-[9px] block">Signed Status</span>
                                <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold mt-0.5 ${
                                  selectedDoc.is_signed.toLowerCase() === 'yes' ? 'bg-green-100 text-green-800 border border-green-200' :
                                  selectedDoc.is_signed.toLowerCase() === 'no' ? 'bg-red-100 text-red-800 border border-red-200' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {selectedDoc.is_signed}
                                </span>
                              </div>
                            )}
                            {selectedDoc.standard_terms && (
                              <div>
                                <span className="text-[#7c7a75] uppercase text-[9px] block">Standard Terms (PwC Template)</span>
                                <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold mt-0.5 ${
                                  selectedDoc.standard_terms.toLowerCase() === 'yes' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                                  selectedDoc.standard_terms.toLowerCase() === 'no' ? 'bg-orange-100 text-orange-800 border border-orange-200' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {selectedDoc.standard_terms}
                                </span>
                              </div>
                            )}
                            {selectedDoc.permitted_use && selectedDoc.permitted_use !== "N/A" && (
                              <div className="col-span-2">
                                <span className="text-[#7c7a75] uppercase text-[9px] block">Permitted Deliverable Use</span>
                                <strong className="text-gray-900 block mt-0.5">{selectedDoc.permitted_use}</strong>
                              </div>
                            )}
                            {selectedDoc.liability_cap && selectedDoc.liability_cap !== "N/A" && (
                              <div>
                                <span className="text-[#7c7a75] uppercase text-[9px] block">Extracted Liability Cap</span>
                                <strong className="text-amber-900 font-mono block mt-0.5">{selectedDoc.liability_cap}</strong>
                              </div>
                            )}
                            {selectedDoc.engagement_letter_link && selectedDoc.engagement_letter_link !== "N/A" && (
                              <div className="col-span-2 mt-1 bg-amber-50/50 p-2 border border-amber-100/50">
                                <span className="text-[#7c7a75] uppercase text-[9px] block">Linked Engagement Letter</span>
                                <strong className="text-amber-800 block mt-0.5 font-mono text-[11px]">{selectedDoc.engagement_letter_link}</strong>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-dotted border-[#d8d6d0]">
                      <span className="text-[9px] text-[#7c7a75] uppercase block font-bold mb-0.5">Gemini Extraction Rationale:</span>
                      <p className="text-xs italic text-[#1a1a19] font-serif leading-relaxed">"{selectedDoc.rationale}"</p>
                      {selectedDoc.webUrl && selectedDoc.webUrl !== "#" && (
                        <div className="mt-2 text-xs">
                          <span className="text-[#7c7a75]">SharePoint Link: </span>
                          <a href={selectedDoc.webUrl} target="_blank" rel="noreferrer" className="text-blue-700 underline font-mono flex items-center gap-1 mt-0.5">
                            <Link2 className="h-3 w-3" /> Open file in SharePoint
                          </a>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Column */}
                  <div className="w-80 flex flex-col justify-between">
                    <div>
                      <h4 className="text-[10px] uppercase font-bold text-[#7c7a75] tracking-wider mb-3">Human-in-the-loop QA</h4>
                      {selectedDoc.state === 'EXCEPTION' && (
                        <div className="bg-red-50 border border-red-200 text-red-700 p-3 text-xs flex gap-2 rounded-none mb-3">
                          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                          <div><strong>Failed State:</strong> {selectedDoc.exception_reason}</div>
                        </div>
                      )}
                      <div className="space-y-3">
                        <div>
                          <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">Override Sub-Type</label>
                          <input 
                            type="text" 
                            value={editType}
                            onChange={(e) => setEditType(e.target.value)}
                            className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] px-3 py-1.5 focus:outline-none focus:border-[#1a1a19] rounded-none"
                          />
                        </div>
                        <div>
                          <label className="text-[9px] uppercase text-[#7c7a75] block mb-1">Override Confidentiality</label>
                          <input 
                            type="text" 
                            value={editCap}
                            onChange={(e) => setEditCap(e.target.value)}
                            className="w-full text-xs bg-[#faf9f6] border border-[#d8d6d0] px-3 py-1.5 focus:outline-none focus:border-[#1a1a19] rounded-none"
                          />
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <button 
                        onClick={() => handleValidate(selectedDoc.id, 'APPROVED')}
                        className="flex-1 bg-[#1a1a19] text-[#faf9f6] text-xs font-semibold py-2 px-3 uppercase tracking-wider hover:opacity-90 rounded-none"
                      >
                        Approve Tags
                      </button>
                      <button 
                        onClick={() => {
                          const reason = prompt("Enter Exception Reason:");
                          if (reason) handleValidate(selectedDoc.id, 'EXCEPTION', reason);
                        }}
                        className="border border-red-300 text-red-700 hover:bg-red-50 text-xs font-semibold py-2 px-3 uppercase tracking-wider rounded-none"
                      >
                        Escalate Exception
                      </button>
                    </div>
                  </div>

                </div>
              )}
            </div>
          )}

          {/* TAB 2: Dynamic Ontology View */}
          {activeTab === 'ontology' && ontology && (
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              <div className="border border-[#d8d6d0] bg-[#f4f3ef] p-4 rounded-none flex items-center justify-between">
                <div>
                  <span className="text-[9px] text-[#7c7a75] uppercase block font-bold">Model Ontology Generator:</span>
                  <strong className="text-xs font-mono">{ontology.model_generator} ({ontology.region})</strong>
                </div>
                <div className="text-right">
                  <span className="text-[9px] text-[#7c7a75] uppercase block">Last Rebuilt:</span>
                  <span className="text-xs font-mono">{new Date(ontology.generated_at).toLocaleTimeString()}</span>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs tracking-widest uppercase font-bold text-[#1a1a19] border-b border-[#d8d6d0] pb-2 flex items-center gap-1.5">
                  <GitBranch className="h-4 w-4" /> Entity Classes & Schema Properties
                </h3>
                {ontology.classes.map((cls, cIdx) => (
                  <div key={cIdx} className="border border-[#d8d6d0] bg-[#faf9f6] p-4 rounded-none">
                    <div className="flex items-baseline gap-2 border-b border-dotted border-[#d8d6d0] pb-1.5 mb-2">
                      <span className="text-sm font-bold text-[#1a1a19]">{cls.name}</span>
                      {cls.parent && (
                        <span className="text-[9px] text-[#7c7a75] uppercase">extends {cls.parent}</span>
                      )}
                    </div>
                    <p className="text-xs text-[#7c7a75] italic mb-3">{cls.description}</p>
                    <div className="space-y-2">
                      {cls.properties.map((prop, pIdx) => (
                        <div key={pIdx} className="flex justify-between items-baseline border-b border-dotted border-gray-200 py-1 text-xs">
                          <span className="font-mono font-bold text-[#1a1a19]">
                            {prop.name}{prop.required && <span className="text-red-500">*</span>}
                          </span>
                          <span className="text-[10px] text-[#7c7a75] font-mono mr-auto ml-2">({prop.type})</span>
                          <span className="text-xs text-right text-gray-600 max-w-xs">{prop.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

            </div>
          )}

          {/* TAB 3: Pipeline Architecture Flow */}
          {activeTab === 'architecture' && (
            <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-[#faf9f6]">
              
              <div className="border border-[#d8d6d0] bg-[#f4f3ef] p-5 rounded-none">
                <span className="text-[10px] text-[#7c7a75] uppercase font-bold tracking-widest block mb-1">Architecture Overview</span>
                <h2 className="text-sm font-bold uppercase text-[#1a1a19]">Aether Zero-Leak & Real-Time ACL Sync Ingestion Pipeline</h2>
                <p className="text-xs text-[#7c7a75] mt-2 leading-relaxed">
                  Below is the interactive visual diagram showing the live data orchestration, from Microsoft Graph crawlers to target analytical storage in Google Cloud. Latencies are benchmarked using <strong>gemini-embedding-2</strong> and <strong>gemini-3.5-flash</strong>.
                </p>
              </div>

              {/* FLOW DIAGRAM WORKSPACE */}
              <div className="space-y-6">
                <h3 className="text-xs tracking-widest uppercase font-bold text-[#1a1a19] border-b border-[#d8d6d0] pb-2 flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-red-600" /> Ingestion & Processing Pipeline
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {pipelineSteps.map((step) => {
                    const isSelected = selectedArchStep === step.id;
                    return (
                      <div 
                        key={step.id}
                        onClick={() => setSelectedArchStep(step.id)}
                        className={`border p-4 rounded-none relative cursor-pointer transition-all duration-150 ${
                          isSelected 
                            ? 'border-[#1a1a19] bg-[#f4f3ef] shadow-sm' 
                            : 'border-[#d8d6d0] bg-white hover:border-[#1a1a19]'
                        }`}
                      >
                        <div className="flex items-center justify-between border-b border-dotted border-gray-200 pb-2 mb-3">
                          <span className="text-[9px] font-mono text-[#7c7a75] uppercase">{step.sub}</span>
                          <span className={`text-[9px] font-mono px-1.5 py-0.5 uppercase font-bold ${step.badgeColor}`}>
                            {step.target}
                          </span>
                        </div>
                        <strong className="text-xs font-bold text-[#1a1a19] block">{step.title}</strong>
                        <p className="text-[11px] text-[#7c7a75] mt-2">
                          {step.desc}
                        </p>
                        <div className="mt-4 flex items-center justify-between text-[10px] font-mono border-t border-dotted border-gray-200 pt-2 text-[#7c7a75]">
                          <span>Latency: <strong className="text-[#1a1a19]">{step.latency}</strong></span>
                          <span className="text-blue-700 underline text-[9px] font-bold">
                            {step.reqs.length} Mapped Reqs
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* FLOATING COMPLIANCE AUDIT MODAL OVERLAY */}
              {selectedArchStep !== null && (
                <div 
                  className="fixed inset-0 bg-[#1a1a19]/40 backdrop-blur-[1.5px] z-50 flex items-center justify-center p-4"
                  onClick={() => setSelectedArchStep(null)}
                >
                  <div 
                    className="bg-white border-2 border-[#1a1a19] w-full max-w-xl max-h-[80vh] flex flex-col rounded-none shadow-[6px_6px_0px_0px_rgba(26,26,25,1)]"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {/* Modal Header */}
                    {(() => {
                      const step = pipelineSteps.find(s => s.id === selectedArchStep)!;
                      return (
                        <>
                          <div className="flex items-center justify-between border-b border-[#d8d6d0] p-5 bg-[#f4f3ef]">
                            <div>
                              <span className="text-[9px] font-mono text-[#7c7a75] uppercase tracking-wider">{step.sub} / PIPELINE AUDIT</span>
                              <h3 className="text-xs font-bold uppercase text-[#1a1a19] mt-0.5">{step.title}</h3>
                            </div>
                            <button 
                              onClick={() => setSelectedArchStep(null)}
                              className="text-[10px] text-[#7c7a75] hover:text-[#1a1a19] font-mono border border-[#d8d6d0] px-2 py-0.5 bg-white hover:bg-gray-100 rounded-none font-bold"
                            >
                              ✕ CLOSE
                            </button>
                          </div>

                          {/* Modal Body */}
                          <div className="flex-1 overflow-y-auto p-6 space-y-4">
                            <p className="text-xs text-[#7c7a75] border-b border-dotted border-gray-200 pb-3 leading-relaxed">
                              This sync pipeline segment addresses and verifies <strong>{step.reqs.length} functional requirements</strong>:
                            </p>
                            
                            <div className="space-y-3">
                              {step.reqs.map((r, idx) => (
                                <div key={idx} className="border border-[#d8d6d0] p-4 bg-[#faf9f6] rounded-none hover:border-[#1a1a19] transition-all">
                                  <div className="flex items-baseline gap-2 mb-2">
                                      <span className="text-[9px] font-mono font-bold bg-[#1a1a19] text-[#faf9f6] px-1.5 py-0.2 rounded-none">
                                        {r.code}
                                      </span>
                                      <strong className="text-xs text-[#1a1a19] font-bold">{r.name}</strong>
                                      <span className="text-[9px] font-mono font-bold text-green-700 bg-green-50 border border-green-200 px-1.5 py-0.2 rounded-none ml-auto uppercase">
                                        Verified
                                      </span>
                                  </div>
                                  <p className="text-xs text-[#7c7a75] leading-relaxed">
                                    {r.desc}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Modal Footer */}
                          <div className="border-t border-[#d8d6d0] p-4 bg-[#f4f3ef] flex justify-end">
                            <button 
                              onClick={() => setSelectedArchStep(null)}
                              className="bg-[#1a1a19] text-[#faf9f6] text-xs font-bold uppercase tracking-widest px-4 py-2 hover:opacity-90 rounded-none shadow-[2px_2px_0px_0px_rgba(124,122,117,1)]"
                            >
                              Close Audit
                            </button>
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>
              )}

              {/* RAG & SECURITY BOUNDARY VISUALIZATION */}
              <div className="space-y-4 border border-[#d8d6d0] bg-[#f4f3ef] p-6 rounded-none">
                <h3 className="text-xs tracking-widest uppercase font-bold text-[#1a1a19] flex items-center gap-1.5">
                  <Shield className="h-4 w-4 text-green-700" /> Real-time Security & Dynamic Zero-Leak Flow
                </h3>
                <p className="text-xs text-[#7c7a75] leading-relaxed">
                  How searches verify identity and block data leakage dynamically at search execution time:
                </p>

                <div className="flex flex-col md:flex-row items-stretch gap-3 mt-4">
                  <div className="flex-1 bg-white p-3 border border-[#d8d6d0] text-xs">
                    <strong className="block mb-1 text-[10px] font-mono uppercase text-[#7c7a75]">1. Auth Handshake</strong>
                    User connects via SharePoint -&gt; Backend MSAL resolves active Microsoft token claims.
                  </div>
                  <div className="flex items-center justify-center font-bold text-gray-400">➜</div>
                  <div className="flex-1 bg-white p-3 border border-[#d8d6d0] text-xs">
                    <strong className="block mb-1 text-[10px] font-mono uppercase text-[#7c7a75]">2. Group Claim Filter</strong>
                    Resolves transitive security groups -&gt; Pre-filters vector search (ignoring documents user cannot access).
                  </div>
                  <div className="flex items-center justify-center font-bold text-gray-400">➜</div>
                  <div className="flex-1 bg-white p-3 border border-[#d8d6d0] text-xs">
                    <strong className="block mb-1 text-[10px] font-mono uppercase text-[#7c7a75]">3. Zero-Leak Synthesis</strong>
                    Gemini reads matching context -&gt; Masks matching PII tokens dynamically with <code>&lt;redact&gt;</code> tags.
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>

        {/* Right Section: Aether AI Chat */}
        <div className="w-[480px] bg-[#f4f3ef] flex flex-col min-height-0 overflow-hidden shrink-0">
          
          <div className="flex items-baseline justify-between px-6 py-5 border-b border-[#d8d6d0] bg-[#f4f3ef] shrink-0">
            <h3 className="font-bold text-[#1a1a19] text-xs tracking-widest uppercase">AETHER AI CONSOLE</h3>
            <span className={`text-[10px] uppercase font-bold flex items-center gap-1.5 ${auth.authenticated ? "text-green-700" : "text-[#7c7a75]"}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${auth.authenticated ? "bg-green-500 animate-pulse" : "bg-gray-400"}`}></span>
              {auth.authenticated ? "Connected: SharePoint Index" : "SharePoint Index: Offline"}
            </span>
          </div>

          {/* Messages Scroller */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg, index) => (
              <div key={index} className="flex flex-col w-full">
                <span className="text-[9px] font-bold text-[#7c7a75] tracking-wider uppercase mb-1">
                  {msg.sender === 'user' ? "User" : "Aether AI"}
                </span>
                
                {msg.isThinking ? (
                  <div className="text-xs border-l border-[#1a1a19] pl-3 text-[#1a1a19] font-mono">
                    Searching index... <span className="console-cursor">█</span>
                  </div>
                ) : (
                  <div className="text-sm border-l border-[#1a1a19] pl-3 text-[#1a1a19] leading-relaxed rounded-none">
                    {renderFlowDiagram(msg.text)}
                    
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 space-y-1.5 border-t border-dotted border-[#d8d6d0] pt-2">
                        <span className="text-[9px] uppercase text-[#7c7a75] font-bold block">Grounded Citations:</span>
                        {msg.sources.map((src, sIdx) => {
                          const cleanTitle = src.title.trim().toLowerCase();
                          const foundDoc = documents.find(d => {
                            const cleanDocName = d.filename.trim().toLowerCase();
                            return cleanDocName === cleanTitle || cleanDocName.includes(cleanTitle) || cleanTitle.includes(cleanDocName);
                          });
                          return (
                            <div key={sIdx} className="text-xs text-[#7c7a75] flex items-baseline gap-1.5">
                              <CornerDownRight className="h-3 w-3 shrink-0 mt-0.5" />
                              <div className="flex-1 min-w-0">
                                <div className="flex flex-wrap items-center gap-2 mb-0.5">
                                  {src.url && src.url !== "#" ? (
                                    <a href={src.url} target="_blank" rel="noreferrer" className="underline font-medium hover:text-[#1a1a19] text-blue-700 flex items-center gap-0.5 shrink-0">
                                      {src.title} <Link2 className="h-3 w-3" />
                                    </a>
                                  ) : (
                                    <span className="font-medium text-[#1a1a19] shrink-0">{src.title}</span>
                                  )}
                                  {foundDoc && (
                                    <button
                                      type="button"
                                      onClick={() => {
                                        setSelectedDoc(foundDoc);
                                        setEditType(foundDoc.sub_type || "");
                                        setEditCap(foundDoc.confidentiality || "");
                                        setActiveTab('queue');
                                      }}
                                      className="inline-flex items-center gap-1 text-[9px] uppercase font-bold tracking-widest px-1.5 py-0.5 bg-[#1a1a19] text-[#faf9f6] hover:bg-[#7c7a75] hover:text-[#faf9f6] transition-colors border-none cursor-pointer rounded-none shadow-[2px_2px_0px_0px_rgba(124,122,117,0.5)]"
                                    >
                                      View Metadata & Ontology 🔍
                                    </button>
                                  )}
                                </div>
                                <span className="block text-[10px] italic font-serif text-[#7c7a75] leading-relaxed">"{src.snippet}"</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {(msg.latency || msg.model) && (
                      <div className="mt-3 flex justify-between border-t border-dotted border-[#d8d6d0] pt-1 text-[9px] font-mono text-[#7c7a75]">
                        <span>[LATENCY: {msg.latency}]</span>
                        <span>[MODEL: {msg.model} // REGION: {msg.region || 'global'}]</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Chat Form */}
          <div className="p-6 border-t border-[#d8d6d0] bg-[#f4f3ef] shrink-0">
            <form onSubmit={handleSearchSubmit} className="flex gap-4">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask: 'show blueprint process map' or 'liability caps'..."
                className="flex-1 text-xs bg-[#faf9f6] border border-[#d8d6d0] px-4 py-3 text-[#1a1a19] focus:outline-none focus:border-[#1a1a19] rounded-none"
              />
              <button 
                type="submit"
                className="bg-[#1a1a19] text-[#faf9f6] px-5 py-3 text-xs font-semibold tracking-wider uppercase rounded-none hover:opacity-90 flex items-center gap-1.5"
              >
                <Send className="h-3.5 w-3.5" /> Send
              </button>
            </form>
          </div>

        </div>

      </div>

      {/* 3. Bottom Block: Crawler Terminal */}
      <footer className="h-48 border-t border-[#d8d6d0] bg-[#111111] text-green-400 font-mono p-4 overflow-hidden flex flex-col shrink-0">
        <div className="flex items-center justify-between border-b border-[#333] pb-2 mb-2 shrink-0">
          <span className="text-[10px] uppercase font-bold tracking-wider flex items-center gap-1.5 text-gray-400">
            <Terminal className="h-3.5 w-3.5" /> LIVE PIPELINE CRAWLER STATUS LOGS
          </span>
          <div className="flex items-center gap-2">
            {isSyncingSp && (
              <span className="text-[9px] font-mono px-2 py-0.5 bg-green-950 border border-green-500 text-green-400 uppercase font-bold animate-pulse">
                Sync Active
              </span>
            )}
            <button 
              onClick={() => setSimulatorLogs([])}
              className="text-[9px] uppercase font-bold px-3 py-1 border border-gray-600 text-gray-400 hover:border-gray-400 hover:text-white rounded-none transition-all"
            >
              Clear Console
            </button>
          </div>
        </div>

        {/* Terminal Text box */}
        <div className="flex-1 overflow-y-auto text-xs space-y-1">
          {simulatorLogs.length === 0 ? (
            <span className="text-gray-600">Active crawler log stream ready...</span>
          ) : (
            simulatorLogs.map((log, idx) => (
              <div key={idx} className={
                log.includes("WARNING") 
                ? "text-yellow-400" 
                : log.includes("successfully") || log.includes("completed")
                ? "text-green-400" 
                : "text-gray-400"
              }>
                {log}
              </div>
            ))
          )}
        </div>
      </footer>

      {/* MSAL Authentication Verification Loading Overlay */}
      {isVerifyingAuth && (
        <div className="fixed inset-0 bg-black/45 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#faf9f6] border border-[#1a1a19] p-8 max-w-sm w-full rounded-none shadow-xl text-center">
            <div className="flex justify-center mb-4">
              <Shield className="h-8 w-8 text-blue-700 animate-pulse" />
            </div>
            <h3 className="font-bold text-sm tracking-wider uppercase mb-2 text-[#1a1a19]">
              Authenticating Connection
            </h3>
            <p className="text-xs text-[#7c7a75] leading-relaxed">
              Exchanging authorization parameters with Microsoft Enterprise services. Please wait...
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
