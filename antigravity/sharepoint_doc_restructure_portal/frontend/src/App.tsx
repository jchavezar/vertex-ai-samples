import { useState, useEffect, useRef } from 'react';
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
  HelpCircle,
  Command,
  Sun,
  Moon,
  X,
  ChevronDown,
  ChevronUp
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
    target: "Gemini 2.5 Flash",
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
  const [panelHeight, setPanelHeight] = useState(384);
  const [isPanelMinimized, setIsPanelMinimized] = useState(false);
  const isResizingRef = useRef(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    isResizingRef.current = true;
    document.body.style.cursor = 'ns-resize';
    document.body.style.userSelect = 'none';
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizingRef.current) return;
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight >= 60 && newHeight <= window.innerHeight - 100) {
        setPanelHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      if (isResizingRef.current) {
        isResizingRef.current = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

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
      text: "Aether Governance Engine Online. Initialized using Gemini 2.5 Flash (Region: global). Ask me a question about documents or relationships."
    }
  ]);
  
  // Simulator logs
  const [simulatorLogs, setSimulatorLogs] = useState<string[]>([]);
  
  // Edit metadata state
  const [editType, setEditType] = useState('');
  const [editCap, setEditCap] = useState('');

  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatTextAreaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow and shrink textarea based on chatInput state
  useEffect(() => {
    const textarea = chatTextAreaRef.current;
    if (textarea) {
      textarea.style.height = '38px';
      if (chatInput.trim()) {
        textarea.style.height = `${textarea.scrollHeight}px`;
      }
    }
  }, [chatInput]);

  // Next-Gen Spotlight / Command Palette State
  const [isSpotlightOpen, setIsSpotlightOpen] = useState(false);
  const [spotlightQuery, setSpotlightQuery] = useState('');
  const [spotlightFilter, setSpotlightFilter] = useState<'all' | 'signed' | 'unsigned' | 'pwc' | 'confidential'>('all');
  const [selectedSpotlightIndex, setSelectedSpotlightIndex] = useState(0);
  const [isSpotlightSearchingRemote, setIsSpotlightSearchingRemote] = useState(false);
  const [spotlightRemoteAnswer, setSpotlightRemoteAnswer] = useState<string | null>(null);
  const [spotlightRemoteSources, setSpotlightRemoteSources] = useState<any[]>([]);

  // Spotlight Light Theme state (persisted)
  const [isSpotlightLightTheme, setIsSpotlightLightTheme] = useState<boolean>(() => {
    return localStorage.getItem('spotlightTheme') === 'light';
  });

  const toggleSpotlightTheme = () => {
    setIsSpotlightLightTheme(prev => {
      const next = !prev;
      localStorage.setItem('spotlightTheme', next ? 'light' : 'dark');
      return next;
    });
  };

  // Toggle Spotlight with Command+K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSpotlightOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsSpotlightOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Compute filtered results
  const filteredSpotlightDocs = documents.filter(doc => {
    // 1. Query filter
    const trimmedQuery = spotlightQuery.trim().toLowerCase();
    if (!trimmedQuery) return true;

    // Check if this document is one of the matched sources from remote semantic search
    const isSemanticMatch = spotlightRemoteSources.some(src => 
      src.title.toLowerCase() === doc.filename.toLowerCase() ||
      doc.filename.toLowerCase().includes(src.title.toLowerCase()) ||
      src.title.toLowerCase().includes(doc.filename.toLowerCase())
    );
    if (isSemanticMatch) return true;

    // Split query into keywords (e.g., words with length > 3) to allow natural language search
    const keywords = trimmedQuery.split(/\s+/).filter(word => word.length > 3);
    if (keywords.length > 0) {
      // If we have keywords, check if any of the keywords match the document's metadata
      const matchesKeywords = keywords.some(keyword => 
        doc.filename.toLowerCase().includes(keyword) ||
        doc.type.toLowerCase().includes(keyword) ||
        doc.sub_type.toLowerCase().includes(keyword) ||
        doc.primary_topic.toLowerCase().includes(keyword) ||
        (doc.content && doc.content.toLowerCase().includes(keyword))
      );
      if (!matchesKeywords) return false;
    } else {
      // Substring matching fallback
      const matchesQuery = 
        doc.filename.toLowerCase().includes(trimmedQuery) ||
        doc.type.toLowerCase().includes(trimmedQuery) ||
        doc.sub_type.toLowerCase().includes(trimmedQuery) ||
        doc.primary_topic.toLowerCase().includes(trimmedQuery) ||
        (doc.content && doc.content.toLowerCase().includes(trimmedQuery));
      if (!matchesQuery) return false;
    }

    // 2. Class/Badge filters
    if (spotlightFilter === 'signed') return doc.is_signed?.toLowerCase() === 'yes';
    if (spotlightFilter === 'unsigned') return doc.is_signed?.toLowerCase() === 'no';
    if (spotlightFilter === 'pwc') return doc.type.toLowerCase().includes('pwc');
    if (spotlightFilter === 'confidential') return doc.confidentiality?.toLowerCase().includes('confidential');

    return true;
  });

  // Handle Spotlight remote deep search
  const handleSpotlightRemoteSearch = async () => {
    if (!spotlightQuery.trim()) return;
    setIsSpotlightSearchingRemote(true);
    setSpotlightRemoteAnswer(null);
    setSpotlightRemoteSources([]);
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: spotlightQuery })
      });
      if (response.ok) {
        const data = await response.json();
        setSpotlightRemoteAnswer(data.answer);
        setSpotlightRemoteSources(data.sources || []);
      } else {
        setSpotlightRemoteAnswer("Semantic search service temporarily unavailable.");
      }
    } catch (e) {
      setSpotlightRemoteAnswer("Connection error. Ensure backend is running on 8085.");
    } finally {
      setIsSpotlightSearchingRemote(false);
    }
  };

  // Reset selected index when query or filter changes
  useEffect(() => {
    setSelectedSpotlightIndex(0);
    setSpotlightRemoteAnswer(null);
    setSpotlightRemoteSources([]);
  }, [spotlightQuery, spotlightFilter]);

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
    if (chatTextAreaRef.current) {
      chatTextAreaRef.current.style.height = '38px';
    }
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
      <header className="border-b border-[#d8d6d0] bg-[#faf9f6] px-8 py-5 rounded-none flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <span className="font-bold text-xl tracking-[0.05em] uppercase">AETHER</span>
          <span className="text-xs text-[#7c7a75] tracking-widest uppercase">/ SharePoint Restructure Console</span>
          
          {/* Spotlight Trigger Pill */}
          <button 
            onClick={() => setIsSpotlightOpen(true)}
            className="hidden md:flex items-center gap-2 px-3 py-1 bg-white border border-[#d8d6d0] hover:border-[#1a1a19] text-[#7c7a75] hover:text-[#1a1a19] text-xs font-medium rounded-none transition-all shadow-sm ml-6 cursor-pointer"
          >
            <Search className="h-3.5 w-3.5 text-blue-700" />
            <span>Semantic Spotlight...</span>
            <kbd className="bg-[#faf9f6] border border-[#d8d6d0] px-1 py-0.2 text-[9px] font-mono text-[#7c7a75] rounded">⌘K</kbd>
          </button>
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
                <div 
                  style={{ height: isPanelMinimized ? '44px' : `${panelHeight}px` }}
                  className="border-t border-[#d8d6d0] bg-[#f4f3ef] shrink-0 flex flex-col relative transition-all duration-150 ease-out"
                >
                  {/* Resize Handle (only active when not minimized) */}
                  {!isPanelMinimized && (
                    <div 
                      onMouseDown={handleMouseDown}
                      className="absolute top-0 left-0 right-0 h-1.5 cursor-ns-resize hover:bg-[#1a1a19]/10 transition-colors z-30"
                      title="Drag to resize panel vertically"
                    />
                  )}

                  {/* Header Bar */}
                  <div className="h-11 border-b border-[#d8d6d0] px-6 flex items-center justify-between select-none bg-[#ecebe5] shrink-0 z-20">
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] uppercase font-bold text-[#7c7a75] tracking-wider">Human-In-The-Loop QA</span>
                      <span className="text-[12px] font-bold text-[#1a1a19] truncate max-w-xl">{selectedDoc.filename}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {isPanelMinimized ? (
                        <button 
                          onClick={() => setIsPanelMinimized(false)}
                          className="p-1 hover:bg-[#1a1a19]/10 text-[#1a1a19] transition-colors"
                          title="Restore Panel"
                        >
                          <ChevronUp className="h-4 w-4" />
                        </button>
                      ) : (
                        <button 
                          onClick={() => setIsPanelMinimized(true)}
                          className="p-1 hover:bg-[#1a1a19]/10 text-[#1a1a19] transition-colors"
                          title="Minimize Panel"
                        >
                          <ChevronDown className="h-4 w-4" />
                        </button>
                      )}
                      <button 
                        onClick={() => setSelectedDoc(null)}
                        className="p-1 hover:bg-red-100 hover:text-red-700 text-[#1a1a19] transition-colors"
                        title="Close Panel"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Scrollable Content (only fully visible when not minimized) */}
                  {!isPanelMinimized && (
                    <div className="flex-1 overflow-y-auto p-6 flex gap-6">
                      
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
                  Below is the interactive visual diagram showing the live data orchestration, from Microsoft Graph crawlers to target analytical storage in Google Cloud. Latencies are benchmarked using <strong>gemini-embedding-2</strong> and <strong>gemini-2.5-flash</strong>.
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
                            <div key={sIdx} className="text-xs text-[#7c7a75] flex items-baseline gap-1.5 group relative">
                              <CornerDownRight className="h-3 w-3 shrink-0 mt-0.5" />
                              <div className="flex-1 min-w-0">
                                <div className="flex flex-wrap items-center gap-2 mb-0.5 relative">
                                  {src.url && src.url !== "#" ? (
                                    <a href={src.url} target="_blank" rel="noreferrer" className="underline font-medium hover:text-[#1a1a19] text-blue-700 flex items-center gap-0.5 shrink-0">
                                      {src.title} <Link2 className="h-3 w-3" />
                                    </a>
                                  ) : (
                                    <span className="font-medium text-[#1a1a19] shrink-0">{src.title}</span>
                                  )}

                                  {/* FLOATING HOVER CARD WINDOW */}
                                  {foundDoc && (
                                    <div className="absolute bottom-full left-0 mb-2 hidden group-hover:flex flex-col w-80 bg-[#faf9f6] border-2 border-[#1a1a19] p-4 shadow-[4px_4px_0px_0px_rgba(26,26,25,0.15)] z-50 pointer-events-none text-[#1a1a19] font-sans rounded-none transition-all">
                                      <div className="border-b border-[#d8d6d0] pb-2 mb-2 flex items-center justify-between">
                                        <span className="text-[9px] uppercase font-mono font-bold text-[#7c7a75]">Document Metadata Card</span>
                                        <span className="text-[9px] font-mono bg-[#1a1a19] text-[#faf9f6] px-1.5 py-0.5 font-bold uppercase truncate">{foundDoc.state || "APPROVED"}</span>
                                      </div>
                                      <h4 className="font-bold text-xs text-[#1a1a19] truncate mb-3">{foundDoc.filename}</h4>
                                      <div className="space-y-2 text-[11px]">
                                        <div className="flex justify-between items-center border-b border-dotted border-[#d8d6d0] pb-1">
                                          <span className="text-[#7c7a75] font-mono text-[9px] uppercase">Lifecycle:</span>
                                          <span className="font-bold text-[#1a1a19]">{foundDoc.lifecycle || 'ACTIVE/PRODUCTION'}</span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-dotted border-[#d8d6d0] pb-1">
                                          <span className="text-[#7c7a75] font-mono text-[9px] uppercase">Confidentiality:</span>
                                          <span className="font-bold text-red-700 uppercase">{foundDoc.confidentiality || 'CONFIDENTIAL'}</span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-dotted border-[#d8d6d0] pb-1">
                                          <span className="text-[#7c7a75] font-mono text-[9px] uppercase">Classification:</span>
                                          <span className="font-bold">{foundDoc.sub_type || 'UNCLASSIFIED'}</span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-dotted border-[#d8d6d0] pb-1">
                                          <span className="text-[#7c7a75] font-mono text-[9px] uppercase">Primary Topic:</span>
                                          <span className="font-semibold truncate max-w-[150px] text-right">{foundDoc.primary_topic || 'GENERAL'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                          <span className="text-[#7c7a75] font-mono text-[9px] uppercase">PII Status:</span>
                                          <span className={`font-bold ${foundDoc.pii_detected ? 'text-red-600' : 'text-green-700'}`}>
                                            {foundDoc.pii_detected ? '⚠️ DETECTED' : '✅ CLEAN'}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
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
            <form onSubmit={handleSearchSubmit} className="flex gap-3 bg-[#faf9f6] border border-[#d8d6d0] focus-within:border-[#1a1a19] p-2 transition-all duration-200 items-center">
              <textarea 
                ref={chatTextAreaRef}
                rows={1}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSearchSubmit(e);
                  }
                }}
                placeholder="Ask a question..."
                className="flex-1 text-xs bg-transparent px-3 py-2 text-[#1a1a19] focus:outline-none resize-none min-h-[38px] max-h-[200px] overflow-y-auto leading-relaxed border-none outline-none"
                style={{ height: '38px' }}
              />
              <button 
                type="submit"
                className="bg-[#1a1a19] text-[#faf9f6] px-5 text-xs font-semibold tracking-wider uppercase rounded-none hover:bg-[#7c7a75] hover:text-[#faf9f6] transition-colors flex items-center justify-center gap-1.5 shrink-0 h-[38px]"
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

      {/* NEXT-GEN SEMANTIC SPOTLIGHT COMMAND PALETTE */}
      {isSpotlightOpen && (() => {
        const activeDoc = filteredSpotlightDocs[selectedSpotlightIndex];
        // Helper to find and extract snippet of matching text in real-time
        const getMatchSnippet = (doc: any, query: string) => {
          if (!query.trim() || !doc || !doc.content) return null;
          const contentStr = doc.content;
          const index = contentStr.toLowerCase().indexOf(query.toLowerCase());
          if (index === -1) {
            // Check individual words if no direct substring
            const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 3);
            for (const word of words) {
              const wordIdx = contentStr.toLowerCase().indexOf(word);
              if (wordIdx !== -1) {
                const start = Math.max(0, wordIdx - 50);
                const end = Math.min(contentStr.length, wordIdx + word.length + 80);
                return {
                  text: (start > 0 ? '...' : '') + contentStr.substring(start, end).replace(/\n+/g, ' ') + (end < contentStr.length ? '...' : ''),
                  matchedWord: word
                };
              }
            }
            return null;
          }
          const start = Math.max(0, index - 50);
          const end = Math.min(contentStr.length, index + query.length + 80);
          return {
            text: (start > 0 ? '...' : '') + contentStr.substring(start, end).replace(/\n+/g, ' ') + (end < contentStr.length ? '...' : ''),
            matchedWord: query
          };
        };

        const snippetInfo = getMatchSnippet(activeDoc, spotlightQuery);

        return (
          <div className={`fixed inset-0 backdrop-blur-xl flex items-start justify-center z-50 p-4 pt-[10vh] transition-all duration-300 ${
            isSpotlightLightTheme ? 'bg-stone-900/50' : 'bg-neutral-950/80'
          }`}>
            <div className={`w-full max-w-4xl rounded-none flex flex-col max-h-[82vh] overflow-hidden transition-all duration-300 transform scale-100 font-sans relative border-2 ${
              isSpotlightLightTheme 
                ? 'bg-white border-cyan-600/40 shadow-[0_0_60px_rgba(8,145,178,0.15)]' 
                : 'bg-neutral-950/95 border-cyan-500/40 shadow-[0_0_60px_rgba(6,182,212,0.25)]'
            }`}>
              
              {/* Cyber Scanner Grid Background Overlay */}
              <div className={`absolute inset-0 pointer-events-none opacity-[0.03] bg-[size:20px_20px] animate-[pulse_8s_infinite] ${
                isSpotlightLightTheme
                  ? 'bg-[linear-gradient(rgba(255,255,255,0)_95%,#0891b2_95%),linear-gradient(90deg,rgba(255,255,255,0)_95%,#0891b2_95%)]'
                  : 'bg-[linear-gradient(rgba(18,18,18,0)_95%,#06b6d4_95%),linear-gradient(90deg,rgba(18,18,18,0)_95%,#06b6d4_95%)]'
              }`}></div>
              
              {/* Top Cyan Glow Line */}
              <div className={`h-[2px] w-full animate-[pulse_2s_infinite] bg-gradient-to-r from-transparent to-transparent ${
                isSpotlightLightTheme ? 'via-cyan-600' : 'via-cyan-400'
              }`}></div>

              {/* Palette Search Input Bar */}
              <div className={`flex items-center gap-4 px-6 py-4 border-b relative z-10 shrink-0 ${
                isSpotlightLightTheme ? 'border-cyan-600/20 bg-stone-50' : 'border-cyan-500/20 bg-neutral-950/90'
              }`}>
                <div className="relative flex items-center justify-center">
                  <Search className={`h-5 w-5 animate-[pulse_1.5s_infinite] ${isSpotlightLightTheme ? 'text-cyan-600' : 'text-cyan-400'}`} />
                  <span className={`absolute h-6 w-6 rounded-full border animate-ping opacity-40 ${
                    isSpotlightLightTheme ? 'border-cyan-600/40' : 'border-cyan-500/40'
                  }`}></span>
                </div>
                <div className="flex-1 flex flex-col">
                  <input 
                    type="text" 
                    placeholder="QUERY MATRIX DATABASE / SHIFT+ENTER FOR SEMANTIC DEEP AI..."
                    className={`bg-transparent text-sm outline-none border-none font-mono tracking-wider w-full select-all font-bold uppercase ${
                      isSpotlightLightTheme ? 'text-cyan-950 placeholder-cyan-800/40' : 'text-cyan-100 placeholder-cyan-800/60'
                    }`}
                    value={spotlightQuery}
                    autoFocus
                    onChange={(e) => setSpotlightQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        if (e.shiftKey) {
                          handleSpotlightRemoteSearch();
                        } else if (filteredSpotlightDocs[selectedSpotlightIndex]) {
                          setSelectedDoc(filteredSpotlightDocs[selectedSpotlightIndex]);
                          setIsSpotlightOpen(false);
                        }
                      } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        setSelectedSpotlightIndex(prev => Math.min(prev + 1, filteredSpotlightDocs.length - 1));
                      } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        setSelectedSpotlightIndex(prev => Math.max(prev - 1, 0));
                      }
                    }}
                  />
                </div>
                
                {/* Simulated Pulse Waveform to look alive */}
                <div className="hidden sm:flex items-center gap-0.5 h-4 px-2 opacity-60">
                  <span className={`w-[2px] h-2 animate-[pulse_0.4s_infinite] ${isSpotlightLightTheme ? 'bg-cyan-600' : 'bg-cyan-500'}`}></span>
                  <span className={`w-[2px] h-3 animate-[pulse_0.6s_infinite] ${isSpotlightLightTheme ? 'bg-cyan-600' : 'bg-cyan-500'}`}></span>
                  <span className={`w-[2px] h-1 animate-[pulse_0.3s_infinite] ${isSpotlightLightTheme ? 'bg-cyan-500' : 'bg-cyan-400'}`}></span>
                  <span className={`w-[2px] h-4 animate-[pulse_0.5s_infinite] ${isSpotlightLightTheme ? 'bg-cyan-600' : 'bg-cyan-500'}`}></span>
                  <span className={`w-[2px] h-2 animate-[pulse_0.7s_infinite] ${isSpotlightLightTheme ? 'bg-cyan-500' : 'bg-cyan-400'}`}></span>
                </div>

                {/* Theme Toggle Button */}
                <button 
                  onClick={toggleSpotlightTheme}
                  title="Toggle Theme"
                  className={`flex items-center gap-1 px-2 py-0.5 text-[9px] uppercase font-mono border rounded-none cursor-pointer transition-all ${
                    isSpotlightLightTheme 
                      ? 'text-cyan-850 bg-cyan-100 border-cyan-400 hover:bg-cyan-200' 
                      : 'text-cyan-400 bg-cyan-950/40 border-cyan-500/30 hover:bg-cyan-950/80 shadow-[0_0_8px_rgba(6,182,212,0.1)]'
                  }`}
                >
                  {isSpotlightLightTheme ? <Sun className="h-3 w-3 animate-[spin_4s_linear_infinite]" /> : <Moon className="h-3 w-3" />}
                  <span>{isSpotlightLightTheme ? 'LIGHT' : 'DARK'}</span>
                </button>

                <div className={`flex items-center gap-1.5 text-[9px] uppercase font-mono px-2 py-0.5 border ${
                  isSpotlightLightTheme 
                    ? 'text-cyan-800 bg-cyan-100 border-cyan-300' 
                    : 'text-cyan-400 bg-cyan-950/40 border-cyan-500/30 shadow-[0_0_8px_rgba(6,182,212,0.1)]'
                }`}>
                  <Command className="h-3 w-3" />
                  <span>ESC</span>
                </div>
              </div>

              {/* Quick Filters Row */}
              <div className={`flex items-center gap-2 px-6 py-3 border-b overflow-x-auto shrink-0 z-10 relative ${
                isSpotlightLightTheme ? 'bg-stone-100/60 border-cyan-600/10' : 'bg-neutral-900/60 border-cyan-500/10'
              }`}>
                <span className={`text-[9px] uppercase font-mono font-bold tracking-wider mr-2 shrink-0 ${
                  isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-600'
                }`}>FILTER_SET //</span>
                <button 
                  onClick={() => setSpotlightFilter('all')}
                  className={`px-3 py-1 text-[10px] font-mono font-bold rounded-none uppercase transition-all tracking-wider border ${
                    spotlightFilter === 'all' 
                      ? isSpotlightLightTheme
                        ? 'bg-cyan-100 text-cyan-800 border-cyan-600 shadow-[0_0_8px_rgba(8,145,178,0.15)]'
                        : 'bg-cyan-500/20 text-cyan-300 border-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.2)]'
                      : isSpotlightLightTheme
                        ? 'bg-transparent text-stone-500 border-stone-200 hover:text-cyan-700 hover:border-cyan-600/30'
                        : 'bg-transparent text-neutral-400 border-neutral-800 hover:text-cyan-400 hover:border-cyan-500/30'
                  }`}
                >
                  ALL [{documents.length}]
                </button>
                <button 
                  onClick={() => setSpotlightFilter('signed')}
                  className={`px-3 py-1 text-[10px] font-mono font-bold rounded-none uppercase transition-all tracking-wider border ${
                    spotlightFilter === 'signed' 
                      ? isSpotlightLightTheme
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-600 shadow-[0_0_8px_rgba(16,185,129,0.15)]'
                        : 'bg-emerald-500/20 text-emerald-300 border-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.2)]'
                      : isSpotlightLightTheme
                        ? 'bg-transparent text-stone-500 border-stone-200 hover:text-emerald-700 hover:border-emerald-500/30'
                        : 'bg-transparent text-neutral-400 border-neutral-800 hover:text-emerald-400 hover:border-emerald-500/30'
                  }`}
                >
                  SIGNED
                </button>
                <button 
                  onClick={() => setSpotlightFilter('unsigned')}
                  className={`px-3 py-1 text-[10px] font-mono font-bold rounded-none uppercase transition-all tracking-wider border ${
                    spotlightFilter === 'unsigned' 
                      ? isSpotlightLightTheme
                        ? 'bg-rose-100 text-rose-800 border-rose-600 shadow-[0_0_8px_rgba(244,63,94,0.15)]'
                        : 'bg-rose-500/20 text-rose-300 border-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.2)]'
                      : isSpotlightLightTheme
                        ? 'bg-transparent text-stone-500 border-stone-200 hover:text-rose-700 hover:border-rose-500/30'
                        : 'bg-transparent text-neutral-400 border-neutral-800 hover:text-rose-400 hover:border-rose-500/30'
                  }`}
                >
                  UNSIGNED
                </button>
                <button 
                  onClick={() => setSpotlightFilter('pwc')}
                  className={`px-3 py-1 text-[10px] font-mono font-bold rounded-none uppercase transition-all tracking-wider border ${
                    spotlightFilter === 'pwc' 
                      ? isSpotlightLightTheme
                        ? 'bg-blue-100 text-blue-800 border-blue-600 shadow-[0_0_8px_rgba(59,130,246,0.15)]'
                        : 'bg-blue-500/20 text-blue-300 border-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.2)]'
                      : isSpotlightLightTheme
                        ? 'bg-transparent text-stone-500 border-stone-200 hover:text-blue-700 hover:border-blue-500/30'
                        : 'bg-transparent text-neutral-400 border-neutral-800 hover:text-blue-400 hover:border-blue-500/30'
                  }`}
                >
                  PwC CORP
                </button>
                <button 
                  onClick={() => setSpotlightFilter('confidential')}
                  className={`px-3 py-1 text-[10px] font-mono font-bold rounded-none uppercase transition-all tracking-wider border ${
                    spotlightFilter === 'confidential' 
                      ? isSpotlightLightTheme
                        ? 'bg-amber-100 text-amber-800 border-amber-600 shadow-[0_0_8px_rgba(245,158,11,0.15)]'
                        : 'bg-amber-500/20 text-amber-300 border-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.2)]'
                      : isSpotlightLightTheme
                        ? 'bg-transparent text-stone-500 border-stone-200 hover:text-amber-700 hover:border-amber-500/30'
                        : 'bg-transparent text-neutral-400 border-neutral-800 hover:text-amber-400 hover:border-amber-500/30'
                  }`}
                >
                  CLASSIFIED
                </button>
              </div>

              {/* Results Grid Container */}
              <div className="flex-1 overflow-y-auto p-4 grid grid-cols-1 md:grid-cols-5 gap-4 min-h-[350px] z-10 relative">
                
                {/* Left Column: List of Results (Reactive to search) */}
                <div className={`md:col-span-3 border-r pr-3 max-h-[52vh] overflow-y-auto space-y-1.5 scrollbar-thin scrollbar-track-transparent ${
                  isSpotlightLightTheme 
                    ? 'border-stone-200 scrollbar-thumb-stone-200' 
                    : 'border-neutral-800/80 scrollbar-thumb-cyan-950'
                }`}>
                  <div className={`text-[10px] font-mono uppercase font-bold tracking-wider mb-2.5 px-2 flex justify-between ${
                    isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-600'
                  }`}>
                    <span>INDEXED_CORES ({filteredSpotlightDocs.length})</span>
                    <span>NAV_KEYS [↑↓] // ENTER [↵]</span>
                  </div>

                  {filteredSpotlightDocs.length === 0 ? (
                    <div className={`p-12 text-center text-xs font-mono border border-dashed ${
                      isSpotlightLightTheme 
                        ? 'text-cyan-800/60 border-cyan-300 bg-cyan-50' 
                        : 'text-cyan-700/60 border-cyan-900/40 bg-cyan-950/5'
                    }`}>
                      NO CORES MATCHING TERM OR CONFIGURATION IN THE DIRECTORY.
                    </div>
                  ) : (
                    filteredSpotlightDocs.map((doc, idx) => {
                      const isSelected = idx === selectedSpotlightIndex;
                      
                      // Calculate simulated relevancy match percentage for futuristic vibe
                      let relevancy = 0;
                      if (!spotlightQuery.trim()) {
                        relevancy = 100 - idx;
                      } else {
                        const scoreSeed = doc.id.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);
                        relevancy = Math.floor(82 + (scoreSeed % 12) + (doc.filename.toLowerCase().includes(spotlightQuery.toLowerCase()) ? 6 : 0));
                      }
                      relevancy = Math.min(100, Math.max(50, relevancy));

                      return (
                        <div 
                          key={doc.id}
                          onClick={() => {
                            setSelectedDoc(doc);
                            setIsSpotlightOpen(false);
                          }}
                          onMouseEnter={() => setSelectedSpotlightIndex(idx)}
                          className={`p-3 rounded-none flex flex-col justify-between transition-all cursor-pointer border ${
                            isSelected 
                              ? isSpotlightLightTheme
                                ? 'bg-cyan-50 border-cyan-500 text-cyan-950 shadow-[0_0_12px_rgba(8,145,178,0.1)]'
                                : 'bg-cyan-500/10 border-cyan-500/80 text-cyan-100 shadow-[0_0_12px_rgba(6,182,212,0.15)]' 
                              : isSpotlightLightTheme
                                ? 'bg-stone-50 border-stone-200 text-stone-600 hover:bg-stone-100 hover:border-stone-300'
                                : 'bg-neutral-900/25 border-neutral-900/60 text-neutral-400 hover:bg-neutral-900/50 hover:border-neutral-800'
                          }`}
                        >
                          <div className="flex items-center gap-2 justify-between">
                            <span className={`font-mono text-xs truncate max-w-[340px] font-bold ${
                              isSelected 
                                ? isSpotlightLightTheme ? 'text-cyan-750' : 'text-cyan-300' 
                                : isSpotlightLightTheme ? 'text-stone-800' : 'text-neutral-200'
                            }`}>
                              {doc.filename}
                            </span>
                            <span className={`text-[8px] px-1.5 py-0.2 font-mono font-bold border ${
                              doc.confidentiality === 'Highly Confidential' 
                                ? isSpotlightLightTheme
                                  ? 'bg-rose-50 text-rose-750 border-rose-300'
                                  : 'bg-rose-950/40 text-rose-400 border-rose-500/30' 
                                : doc.confidentiality === 'Confidential' 
                                  ? isSpotlightLightTheme
                                    ? 'bg-amber-50 text-amber-750 border-amber-300'
                                    : 'bg-amber-950/40 text-amber-400 border-amber-500/30' 
                                  : isSpotlightLightTheme
                                    ? 'bg-stone-100 text-stone-600 border-stone-300'
                                    : 'bg-neutral-950/40 text-neutral-400 border-neutral-800'
                            }`}>{doc.confidentiality}</span>
                          </div>
                          
                          <div className="text-[9px] font-mono mt-2 flex items-center justify-between opacity-80">
                            <span className={`${isSpotlightLightTheme ? 'text-cyan-600 font-bold' : 'text-cyan-700'} font-semibold`}>{doc.sub_type.toUpperCase()}</span>
                            <div className="flex items-center gap-2">
                              <span className={`${isSpotlightLightTheme ? 'text-stone-500' : 'text-neutral-500'} font-bold`}>{doc.site.toUpperCase()}</span>
                              <span className={`px-1 rounded-sm font-bold text-[8px] ${
                                isSelected 
                                  ? isSpotlightLightTheme ? 'text-cyan-750 bg-cyan-100' : 'text-cyan-400 bg-cyan-950/50' 
                                  : isSpotlightLightTheme ? 'text-stone-500 bg-stone-100' : 'text-neutral-500 bg-neutral-950/30'
                              }`}>
                                MATCH_RATIO: {relevancy}%
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Right Column: Interactive Selected Preview / AI Retrieval */}
                <div className="md:col-span-2 flex flex-col justify-between max-h-[52vh] overflow-y-auto pl-2 font-mono">
                  
                  {/* 1. Quick Info Card or Semantic Answer Preview */}
                  <div className="flex-1 flex flex-col justify-between">
                    {isSpotlightSearchingRemote ? (
                      <div className={`flex-1 flex flex-col items-center justify-center p-8 text-center border ${
                        isSpotlightLightTheme 
                          ? 'bg-cyan-50/50 border-cyan-200 text-cyan-900' 
                          : 'bg-cyan-950/5 border-cyan-500/20 text-cyan-300'
                      }`}>
                        <RefreshCw className={`h-8 w-8 animate-spin mb-3 ${isSpotlightLightTheme ? 'text-cyan-600' : 'text-cyan-400'}`} />
                        <span className={`text-xs font-bold uppercase tracking-wider animate-[pulse_1s_infinite] ${
                          isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-300'
                        }`}>Neural Extraction Active</span>
                        <span className={`text-[10px] mt-2 leading-relaxed max-w-[220px] ${
                          isSpotlightLightTheme ? 'text-cyan-800/80' : 'text-cyan-600'
                        }`}>
                          Traversing Firestore records, processing multi-document RAG context and synthesizing answers via Gemini-3-Flash...
                        </span>
                      </div>
                    ) : spotlightRemoteAnswer ? (
                      <div className={`border-2 p-4 flex flex-col justify-between h-full overflow-y-auto relative ${
                        isSpotlightLightTheme 
                          ? 'bg-cyan-50/50 border-cyan-500/30' 
                          : 'bg-cyan-950/15 border-cyan-500/30'
                      }`}>
                        <div className={`absolute top-1 right-2 text-[8px] animate-pulse ${isSpotlightLightTheme ? 'text-cyan-600' : 'text-cyan-700'}`}>MATRIX_LIVE</div>
                        <div>
                          <div className={`flex items-center gap-1.5 border px-2 py-1 mb-3 text-[10px] font-bold ${
                            isSpotlightLightTheme 
                              ? 'bg-cyan-100 text-cyan-800 border-cyan-300' 
                              : 'bg-cyan-950/50 text-cyan-300 border-cyan-500/20'
                          }`}>
                            <Activity className={`h-3.5 w-3.5 animate-pulse ${isSpotlightLightTheme ? 'text-cyan-600' : 'text-cyan-400'}`} />
                            <span>CO-PILOT CONTEXT INTEGRATION</span>
                          </div>
                          
                          {/* Answer Box */}
                          <div className={`text-xs leading-relaxed font-mono p-3 border mb-3 select-all ${
                            isSpotlightLightTheme 
                              ? 'text-cyan-950 bg-white border-cyan-200' 
                              : 'text-cyan-100 bg-neutral-950/50 border-cyan-500/10'
                          }`}>
                            {spotlightRemoteAnswer}
                          </div>
                        </div>
                        
                        {spotlightRemoteSources.length > 0 && (
                          <div className={`border-t pt-3 ${isSpotlightLightTheme ? 'border-cyan-200' : 'border-cyan-500/20'}`}>
                            <span className={`text-[9px] uppercase font-bold block mb-1.5 tracking-wider ${
                              isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-600'
                            }`}>GROUNDED SOURCE CITATIONS //</span>
                            <div className="space-y-1">
                              {spotlightRemoteSources.map((src, sIdx) => (
                                <div key={sIdx} className={`text-[10px] font-bold truncate flex items-center gap-1 ${
                                  isSpotlightLightTheme ? 'text-cyan-700 hover:text-cyan-800' : 'text-cyan-400 hover:text-cyan-300'
                                }`}>
                                  <span className={isSpotlightLightTheme ? 'text-cyan-500' : 'text-cyan-600'}>⚡</span>
                                  <a href={src.url || "#"} className="hover:underline">{src.title}</a>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : activeDoc ? (
                      <div className="flex flex-col h-full justify-between">
                        <div className={`p-4 border ${
                          isSpotlightLightTheme 
                            ? 'bg-stone-50 border-stone-200' 
                            : 'bg-neutral-900/40 border-cyan-500/20'
                        }`}>
                          <span className={`text-[9px] uppercase font-bold block mb-1 tracking-wider ${
                            isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-600'
                          }`}>MATRIX RATIONALE //</span>
                          <p className={`text-xs leading-relaxed font-mono p-2 border mb-4 italic ${
                            isSpotlightLightTheme 
                              ? 'text-stone-800 bg-white border-stone-200' 
                              : 'text-cyan-100 bg-neutral-950/30 border-neutral-900'
                          }`}>
                            "{activeDoc.rationale}"
                          </p>
                          
                          <span className={`text-[9px] uppercase font-bold block mb-1 tracking-wider ${
                            isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-600'
                          }`}>TOPIC SCOPE //</span>
                          <p className={`text-xs font-bold ${
                            isSpotlightLightTheme ? 'text-cyan-800' : 'text-cyan-300'
                          }`}>
                            {activeDoc.primary_topic.toUpperCase()}
                          </p>
                          
                          {/* Live Keyword Match Snippet Highlight Box */}
                          {snippetInfo && (
                            <div className={`mt-4 pt-3 border-t ${isSpotlightLightTheme ? 'border-stone-200' : 'border-cyan-500/10'}`}>
                              <span className="text-[9px] uppercase font-bold text-rose-500 block mb-1 tracking-wider">DIRECT CLAUSE MATCH //</span>
                              <div className={`text-[10px] font-mono leading-relaxed border p-2 ${
                                isSpotlightLightTheme 
                                  ? 'bg-rose-50 border-rose-200 text-rose-900' 
                                  : 'bg-rose-950/15 border-rose-500/20 text-rose-200'
                              }`}>
                                {(() => {
                                  const text = snippetInfo.text;
                                  const term = snippetInfo.matchedWord;
                                  const idx = text.toLowerCase().indexOf(term.toLowerCase());
                                  if (idx === -1) return <span>{text}</span>;
                                  return (
                                    <span>
                                      {text.substring(0, idx)}
                                      <mark className={`px-0.5 font-bold ${
                                        isSpotlightLightTheme ? 'bg-rose-200 text-rose-900' : 'bg-rose-500 text-neutral-950'
                                      }`}>{text.substring(idx, idx + term.length)}</mark>
                                      {text.substring(idx + term.length)}
                                    </span>
                                  );
                                })()}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* FR10 Quick Pill */}
                        {activeDoc.is_signed && activeDoc.is_signed !== "N/A" && (
                          <div className={`mt-3.5 p-3.5 border flex flex-col relative ${
                            isSpotlightLightTheme 
                              ? 'bg-amber-50 border-amber-200' 
                              : 'bg-amber-950/20 border-amber-500/20'
                          }`}>
                            <div className="absolute top-1 right-2 text-[7px] text-amber-500 animate-pulse">FR10 CODE</div>
                            <div className="flex items-center gap-1.5 text-[9px] font-bold text-amber-500 mb-1.5 uppercase tracking-wider">
                              <CheckCircle2 className="h-3.5 w-3.5 text-amber-500 animate-[pulse_1.5s_infinite]" />
                              <span>CONTRACT RECORD ISOLATED</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                              <div><span className={isSpotlightLightTheme ? 'text-stone-500' : 'text-neutral-500'}>SIGNED:</span> <strong className="text-amber-800">{activeDoc.is_signed.toUpperCase()}</strong></div>
                              <div><span className={isSpotlightLightTheme ? 'text-stone-500' : 'text-neutral-500'}>TERMS:</span> <strong className="text-amber-800">{activeDoc.standard_terms.toUpperCase()}</strong></div>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className={`flex-1 flex flex-col items-center justify-center p-8 text-center border border-dashed ${
                        isSpotlightLightTheme 
                          ? 'text-cyan-800/60 border-cyan-200 bg-cyan-50/50' 
                          : 'text-cyan-700/60 border-cyan-900/20 bg-cyan-950/5'
                      }`}>
                        <Command className={`h-8 w-8 mb-3 animate-[bounce_2s_infinite] ${
                          isSpotlightLightTheme ? 'text-cyan-400/60' : 'text-cyan-600/30'
                        }`} />
                        <span className="text-xs uppercase font-mono leading-relaxed">QUERY SYSTEM STANDBY // AWAKEN CO-PILOT WITH KEYWORD SPECTRUMS</span>
                      </div>
                    )}
                  </div>

                  {/* 2. Deep Search Trigger Trigger Box */}
                  {!isSpotlightSearchingRemote && !spotlightRemoteAnswer && spotlightQuery.trim() && (
                    <button 
                      onClick={handleSpotlightRemoteSearch}
                      className={`mt-4 w-full text-xs font-bold py-2.5 px-3 rounded-none uppercase flex items-center justify-center gap-2 transition-all cursor-pointer shrink-0 font-mono tracking-wider ${
                        isSpotlightLightTheme 
                          ? 'bg-cyan-600 hover:bg-cyan-700 text-white shadow-[0_0_15px_rgba(8,145,178,0.2)]' 
                          : 'bg-cyan-500 hover:bg-cyan-600 text-neutral-950 shadow-[0_0_15px_rgba(6,182,212,0.3)]'
                      }`}
                    >
                      <Activity className={`h-4 w-4 animate-[pulse_0.5s_infinite] ${isSpotlightLightTheme ? 'text-white' : 'text-neutral-950'}`} />
                      <span>INITIALIZE NEURAL DEEP SEARCH</span>
                      <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded-sm ml-auto font-bold ${
                        isSpotlightLightTheme ? 'text-cyan-800 bg-cyan-100' : 'text-cyan-950 bg-cyan-300/60'
                      }`}>SHIFT+ENTER</span>
                    </button>
                  )}

                  {spotlightRemoteAnswer && (
                    <button 
                      onClick={() => {
                        setSpotlightRemoteAnswer(null);
                        setSpotlightRemoteSources([]);
                      }}
                      className={`mt-4 w-full border text-xs font-bold py-2.5 px-3 rounded-none uppercase transition-all cursor-pointer shrink-0 font-mono tracking-wider ${
                        isSpotlightLightTheme 
                          ? 'border-cyan-600/30 hover:border-cyan-600/50 hover:bg-cyan-50 text-cyan-800' 
                          : 'border-cyan-500/30 hover:border-cyan-500/50 hover:bg-cyan-500/5 text-cyan-400'
                      }`}
                    >
                      RETURN TO CORPUS PREVIEW
                    </button>
                  )}
                </div>

              </div>

              {/* Command Palette Footer Instructions */}
              <div className={`px-6 py-3 border-t flex items-center justify-between text-[10px] shrink-0 relative z-10 font-mono ${
                isSpotlightLightTheme 
                  ? 'border-stone-200 bg-stone-100 text-stone-600' 
                  : 'border-cyan-500/20 bg-neutral-950 text-cyan-600/80'
              }`}>
                <div className="flex items-center gap-4">
                  <span><kbd className={`px-1.5 py-0.2 rounded font-mono shadow-sm border ${
                    isSpotlightLightTheme 
                      ? 'bg-stone-200 border-stone-300 text-stone-700' 
                      : 'bg-cyan-950 border-cyan-500/30 text-cyan-400'
                  }`}>↑↓</kbd> TRAVERSE</span>
                  <span><kbd className={`px-1.5 py-0.2 rounded font-mono shadow-sm border ${
                    isSpotlightLightTheme 
                      ? 'bg-stone-200 border-stone-300 text-stone-700' 
                      : 'bg-cyan-950 border-cyan-500/30 text-cyan-400'
                  }`}>↵</kbd> LOAD PORTAL</span>
                  <span><kbd className={`px-2 py-0.2 rounded font-mono shadow-sm border ${
                    isSpotlightLightTheme 
                      ? 'bg-stone-200 border-stone-300 text-stone-700' 
                      : 'bg-cyan-950 border-cyan-500/30 text-cyan-400'
                  }`}>SHIFT+↵</kbd> AI CO-PILOT DEEP DEBATE</span>
                </div>
                <span className={`text-[9px] uppercase font-bold tracking-widest animate-pulse ${
                  isSpotlightLightTheme ? 'text-cyan-700' : 'text-cyan-400'
                }`}>AETHER SEMANTIC CO-PILOT v1.2</span>
              </div>

            </div>
          </div>
        );
      })()}

    </div>
  );
}
