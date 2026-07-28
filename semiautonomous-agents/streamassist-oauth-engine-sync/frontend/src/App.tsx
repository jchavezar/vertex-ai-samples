import { useState, useCallback, useEffect, useRef } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';

interface Source {
  title: string;
  url: string;
  description: string;
  file_type: string;
  author: string;
  entity_type: string;
}

interface Message {
  role: 'user' | 'assistant';
  text: string;
  sources?: Source[];
  duration_ms?: number;
  thought?: string;
  suggestions?: string[];
}

interface HttpTrace {
  stage: string;
  method: string;
  url: string;
  request_headers: Record<string, string>;
  request_body: any;
  response_headers: Record<string, string>;
  response_body: any;
  status_code: number;
  duration_ms: number;
  curl?: string;
}

interface BackendConfig {
  PROJECT_NUMBER: string;
  ENGINE_ID: string;
  CONNECTOR_ID: string;
  WIF_POOL_ID: string;
  WIF_PROVIDER_ID: string;
  CONNECTOR_CLIENT_ID: string;
  TENANT_ID: string;
  SHAREPOINT_DOMAIN: string;
  BACKEND_PORT: number;
  SCOPES: string;
}

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';

  // State Management
  const [activeTab, setActiveTab] = useState<'wizard' | 'search'>('wizard');
  const [backendConfig, setBackendConfig] = useState<BackendConfig | null>(null);
  const [spConnected, setSpConnected] = useState(false);
  const [authStatus, setAuthStatus] = useState('');
  const [disconnecting, setDisconnecting] = useState(false);
  
  // Search State
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [lastSuggestions, setLastSuggestions] = useState<string[]>([]);
  const [activeStep, setActiveStep] = useState<number | null>(null);

  // Diagnostic Wizard State
  const [wizardStep, setWizardStep] = useState<number>(1);
  const [entraToken, setEntraToken] = useState<string>('');
  const [gcpToken, setGcpToken] = useState<string>('');
  const [resolvedAuthUrl, setResolvedAuthUrl] = useState<string>('');
  const [capturedRedirectUrl, setCapturedRedirectUrl] = useState<string>('');
  const [stepTraces, setStepTraces] = useState<Record<number, HttpTrace[]>>({});
  const [stepLoading, setStepLoading] = useState<Record<number, boolean>>({});
  const [stepStatus, setStepStatus] = useState<Record<number, 'idle' | 'success' | 'error'>>({});

  const consentPopupRef = useRef<Window | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const searchStartRef = useRef<number>(0);

  // Fetch backend configuration on load
  useEffect(() => {
    fetch('/api/diagnostic/configuration')
      .then(r => r.json())
      .then(data => setBackendConfig(data))
      .catch(err => console.error("Failed to load backend config:", err));
  }, []);

  // Update check connection state
  const checkConnection = useCallback(async (token: string) => {
    try {
      const resp = await fetch('/api/sharepoint/check-connection', {
        headers: { 'X-Entra-Id-Token': token }
      });
      const data = await resp.json();
      setSpConnected(data.connected);
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 8: data._trace }));
      }
    } catch {
      // Clean pass-through
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      getToken().then(t => {
        if (t) {
          setEntraToken(t);
          checkConnection(t);
        }
      });
    }
  }, [isAuthenticated, checkConnection]);

  // Handle auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    const id = setInterval(() => setElapsedMs(Date.now() - searchStartRef.current), 50);
    return () => clearInterval(id);
  }, [loading]);

  // MSAL token getter
  const getToken = useCallback(async (): Promise<string> => {
    if (!accounts[0]) return '';
    try {
      const resp = await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
      return resp.accessToken;
    } catch {
      return '';
    }
  }, [instance, accounts]);

  // Step 1: MSAL Login
  const executeStep1 = async () => {
    setStepLoading(prev => ({ ...prev, 1: true }));
    setStepStatus(prev => ({ ...prev, 1: 'idle' }));
    try {
      const resp = await instance.loginPopup(loginRequest);
      setEntraToken(resp.accessToken);
      setStepStatus(prev => ({ ...prev, 1: 'success' }));
      setWizardStep(2);
    } catch (err: any) {
      setStepStatus(prev => ({ ...prev, 1: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 1: false }));
    }
  };

  // Step 2: WIF STS Token Exchange
  const executeStep2 = async () => {
    setStepLoading(prev => ({ ...prev, 2: true }));
    try {
      const resp = await fetch('/api/diagnostic/sts-exchange', {
        method: 'POST',
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      if (data.success && data.gcp_token) {
        setGcpToken(data.gcp_token);
        setStepStatus(prev => ({ ...prev, 2: 'success' }));
        setWizardStep(3);
      } else {
        setStepStatus(prev => ({ ...prev, 2: 'error' }));
      }
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 2: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 2: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 2: false }));
    }
  };

  // Step 3: Proactive Allowlist Custom Domain
  const executeStep3 = async () => {
    setStepLoading(prev => ({ ...prev, 3: true }));
    try {
      const resp = await fetch('/api/diagnostic/allowlist-domain', {
        method: 'POST',
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      if (data.success) {
        setStepStatus(prev => ({ ...prev, 3: 'success' }));
        setWizardStep(4);
      } else {
        setStepStatus(prev => ({ ...prev, 3: 'error' }));
      }
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 3: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 3: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 3: false }));
    }
  };

  // Step 4: Retrieve WidgetConfig & Resolve OAuth Uri
  const executeStep4 = async () => {
    setStepLoading(prev => ({ ...prev, 4: true }));
    try {
      const resp = await fetch('/api/sharepoint/auth-url', {
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      if (data.auth_url) {
        setResolvedAuthUrl(data.auth_url);
        setStepStatus(prev => ({ ...prev, 4: 'success' }));
        setWizardStep(5);
      } else {
        setStepStatus(prev => ({ ...prev, 4: 'error' }));
      }
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 4: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 4: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 4: false }));
    }
  };

  // Step 5: Open Consent Popup & Monitor
  const executeStep5 = () => {
    if (!resolvedAuthUrl) return;
    setStepLoading(prev => ({ ...prev, 5: true }));
    setStepStatus(prev => ({ ...prev, 5: 'idle' }));
    
    const popup = window.open('about:blank', 'sp_diag_consent', 'width=650,height=750,left=150,top=100');
    consentPopupRef.current = popup;
    
    if (!popup) {
      alert("Popup blocked! Please allow popups for this site.");
      setStepLoading(prev => ({ ...prev, 5: false }));
      return;
    }
    
    popup.location.href = resolvedAuthUrl;
    setAuthStatus('Waiting for consent popup window to close or post code back...');
  };

  // Listen for callback redirection posted from redirect page
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (event.data?.fullRedirectUrl) {
        setCapturedRedirectUrl(event.data.fullRedirectUrl);
        setStepStatus(prev => ({ ...prev, 5: 'success' }));
        setStepLoading(prev => ({ ...prev, 5: false }));
        setWizardStep(6);
        setAuthStatus('Redirect URL intercepted!');
        if (consentPopupRef.current) {
          consentPopupRef.current.close();
          consentPopupRef.current = null;
        }
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, []);

  // Polling fallback to check if user closed consent popup
  useEffect(() => {
    if (!stepLoading[5] || !consentPopupRef.current) return;
    const interval = setInterval(async () => {
      const popup = consentPopupRef.current;
      if (!popup || popup.closed) {
        clearInterval(interval);
        consentPopupRef.current = null;
        setAuthStatus('Popup closed. Attempting connection health check...');
        await new Promise(r => setTimeout(r, 1500));
        
        // Check if token was successfully stored in the background
        const resp = await fetch('/api/sharepoint/check-connection', {
          headers: { 'X-Entra-Id-Token': entraToken }
        });
        const data = await resp.json();
        if (data.connected) {
          setSpConnected(true);
          setStepStatus(prev => ({ ...prev, 5: 'success' }));
          setWizardStep(8); // Jump straight to check connection
        } else {
          setStepStatus(prev => ({ ...prev, 5: 'error' }));
          setAuthStatus('No stored credentials verified. Consent may have failed.');
        }
        setStepLoading(prev => ({ ...prev, 5: false }));
      }
    }, 500);
    return () => clearInterval(interval);
  }, [stepLoading, entraToken]);

  // Step 6: acquireAndStoreRefreshToken (Step 4 of design)
  const executeStep6 = async () => {
    if (!capturedRedirectUrl) return;
    setStepLoading(prev => ({ ...prev, 6: true }));
    try {
      const resp = await fetch('/api/oauth/exchange', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': entraToken
        },
        body: JSON.stringify({ fullRedirectUrl: capturedRedirectUrl })
      });
      const data = await resp.json();
      if (data.success) {
        setSpConnected(true);
        setStepStatus(prev => ({ ...prev, 6: 'success' }));
        setWizardStep(7);
      } else {
        setStepStatus(prev => ({ ...prev, 6: 'error' }));
      }
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 6: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 6: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 6: false }));
    }
  };

  // Step 7: updateEngineUserData (AUTHORIZED)
  const executeStep7 = async () => {
    setStepLoading(prev => ({ ...prev, 7: true }));
    try {
      // Step 7 is already run during /api/oauth/exchange on the backend, 
      // but we fetch check connection to verify that everything synchronized.
      const resp = await fetch('/api/sharepoint/check-connection', {
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      if (data.connected) {
        setStepStatus(prev => ({ ...prev, 7: 'success' }));
        setWizardStep(8);
      } else {
        setStepStatus(prev => ({ ...prev, 7: 'error' }));
      }
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 7: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 7: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 7: false }));
    }
  };

  // Step 8: Active Connection health check
  const executeStep8 = async () => {
    setStepLoading(prev => ({ ...prev, 8: true }));
    try {
      const resp = await fetch('/api/sharepoint/check-connection', {
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      setSpConnected(data.connected);
      setStepStatus(prev => ({ ...prev, 8: data.connected ? 'success' : 'error' }));
      if (data._trace) {
        setStepTraces(prev => ({ ...prev, 8: data._trace }));
      }
    } catch {
      setStepStatus(prev => ({ ...prev, 8: 'error' }));
    } finally {
      setStepLoading(prev => ({ ...prev, 8: false }));
    }
  };

  // Disconnect / Revoke State to EXPIRED (Step 6 of design)
  const executeDisconnect = async () => {
    setDisconnecting(true);
    try {
      const resp = await fetch('/api/sharepoint/disconnect', {
        method: 'POST',
        headers: { 'X-Entra-Id-Token': entraToken }
      });
      const data = await resp.json();
      if (data.success) {
        setSpConnected(false);
        setWizardStep(1);
        setStepStatus({});
        setStepTraces({});
        setCapturedRedirectUrl('');
        setResolvedAuthUrl('');
        setGcpToken('');
      } else {
        alert("Server rejected disconnection patch.");
      }
    } catch {
      alert("Failed to connect to server during disconnect request.");
    } finally {
      setDisconnecting(false);
    }
  };

  // Search Engine Queries
  const executeSearch = async (forcedQuery?: string) => {
    const q = (forcedQuery || query).trim();
    if (!q || loading) return;

    // Add user message AND assistant placeholder immediately to history
    setMessages(prev => [
      ...prev, 
      { role: 'user', text: q },
      { 
        role: 'assistant', 
        text: '', 
        sources: [], 
        thought: '', 
        suggestions: [],
        duration_ms: 0
      }
    ]);
    setQuery('');
    setLastSuggestions([]);
    setElapsedMs(0);
    searchStartRef.current = Date.now();
    setLoading(true);
    setActiveStep(1); // Timeline starts at Step 1

    try {
      const resp = await fetch('/api/search/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': entraToken },
        body: JSON.stringify({ query: q, session_token: sessionToken })
      });

      if (!resp.body) {
        throw new Error("Streaming is not supported by your browser.");
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // Retain any unfinished line chunk
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;

          try {
            const data = JSON.parse(trimmed.substring(5).trim());

            if (data.type === 'token_exchange') {
              if (data._trace) {
                setStepTraces(prev => ({ ...prev, 10: data._trace }));
              }
            } else if (data.type === 'status') {
              setActiveStep(data.step);
            } else if (data.type === 'text') {
              setMessages(prev => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last && last.role === 'assistant') {
                  last.text += data.delta;
                  last.duration_ms = Date.now() - searchStartRef.current;
                }
                return next;
              });
            } else if (data.type === 'thought') {
              setMessages(prev => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last && last.role === 'assistant') {
                  last.thought = (last.thought || '') + data.delta;
                }
                return next;
              });
            } else if (data.type === 'citation') {
              setMessages(prev => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last && last.role === 'assistant') {
                  const currentSources = last.sources || [];
                  if (!currentSources.some(s => s.url === data.citation.url)) {
                    last.sources = [...currentSources, data.citation];
                  }
                }
                return next;
              });
            } else if (data.type === 'suggestions') {
              setMessages(prev => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last && last.role === 'assistant') {
                  last.suggestions = [...(last.suggestions || []), ...data.suggestions];
                }
                return next;
              });
              setLastSuggestions(prev => {
                const uniq = new Set([...prev, ...data.suggestions]);
                return Array.from(uniq);
              });
            } else if (data.type === 'session') {
              if (data.token) setSessionToken(data.token);
            } else if (data.type === 'search_trace') {
              if (data.trace) {
                setStepTraces(prev => ({ ...prev, 10: data.trace }));
              }
            } else if (data.type === 'done') {
              setActiveStep(null); // Clear active highlights when done
            } else if (data.type === 'error') {
              setMessages(prev => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last && last.role === 'assistant') {
                  last.text = `Error: ${data.message}`;
                }
                return next;
              });
            }
          } catch (jsonErr) {
            console.error("Failed to parse SSE line JSON:", jsonErr, line);
          }
        }
      }

    } catch (err: any) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `Network streaming error: ${err.message}`, 
        duration_ms: Date.now() - searchStartRef.current 
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Helper: Decode JWT Claims
  const decodeJwt = (token: string) => {
    if (!token) return null;
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      return JSON.parse(atob(parts[1]));
    } catch {
      return null;
    }
  };

  const claims = decodeJwt(entraToken);

  return (
    <div className="app-layout with-sidebar">
      <div className="app">
        <header>
          <div className="title-group">
            <h1>Sync Portal Diagnostic Studio</h1>
            <span className="subtitle">Real-time Step-by-Step API & Header Inspection</span>
          </div>
          
          <div className="user-info">
            {isAuthenticated ? (
              <>
                <span className="user-badge">{username}</span>
                {spConnected && (
                  <button className="btn-secondary btn-disconnect" onClick={executeDisconnect} disabled={disconnecting}>
                    {disconnecting ? 'Revoking...' : 'Deregister Connector'}
                  </button>
                )}
                <button className="btn-secondary" onClick={() => instance.logoutPopup()}>Logout</button>
              </>
            ) : (
              <button className="btn-primary" onClick={executeStep1}>Login</button>
            )}
          </div>
        </header>

        {/* Tab Selection */}
        <div className="tab-bar">
          <button className={`tab-btn ${activeTab === 'wizard' ? 'active' : ''}`} onClick={() => setActiveTab('wizard')}>
            🛠 Diagnostic Step-by-Step Wizard
          </button>
          <button className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`} onClick={() => setActiveTab('search')}>
            🔍 Search Grounding Sandbox {spConnected ? '🟢' : '🔒'}
          </button>
        </div>

        <div className="main-scrollable-content">
          {activeTab === 'wizard' && (
            <div className="wizard-workspace">
              
              {/* Step 1: MSAL Login */}
              <div className={`wizard-card ${wizardStep === 1 ? 'active' : ''} step-${stepStatus[1]}`}>
                <div className="step-badge">Step 1</div>
                <h3>Microsoft Entra Authentication (MSAL Portal App)</h3>
                <p>Authenticates client-side against your Azure Directory, producing an identity JWT mapping your claims.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Mechanism:</strong> Local OAuth 2.0 Implicit Grant / Authorization Code Flow via Microsoft <code>@azure/msal-browser</code>.</p>
                    <p><strong>Endpoint:</strong> <code>https://login.microsoftonline.com/{backendConfig?.TENANT_ID || '{TENANT_ID}'}/oauth2/v2.0/authorize</code></p>
                    <p><strong>Requested Scopes:</strong></p>
                    <pre className="jwt-string">
                      {`openid\noffline_access\nhttps://${backendConfig?.SHAREPOINT_DOMAIN || 'contoso.sharepoint.com'}/AllSites.Read\nhttps://${backendConfig?.SHAREPOINT_DOMAIN || 'contoso.sharepoint.com'}/Sites.Search.All`}
                    </pre>
                  </div>
                </details>

                {entraToken ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ ID Token Acquired</span>
                    <pre className="jwt-string">{entraToken.substring(0, 80)}...</pre>
                    {claims && (
                      <table className="claims-table">
                        <thead>
                          <tr><th>Claim</th><th>Value</th></tr>
                        </thead>
                        <tbody>
                          <tr><td>aud (Audience)</td><td><code>{claims.aud}</code></td></tr>
                          <tr><td>sub (Subject)</td><td><code>{claims.sub}</code></td></tr>
                          <tr><td>name (User Name)</td><td>{claims.name}</td></tr>
                          <tr><td>email (User Email)</td><td>{claims.email}</td></tr>
                        </tbody>
                      </table>
                    )}
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep1} disabled={stepLoading[1]}>
                    {stepLoading[1] ? 'Authenticating...' : 'Run MSAL Login'}
                  </button>
                )}
              </div>

              {/* Step 2: WIF STS Exchange */}
              <div className={`wizard-card ${wizardStep === 2 ? 'active' : ''} ${!entraToken ? 'disabled' : ''} step-${stepStatus[2]}`}>
                <div className="step-badge">Step 2</div>
                <h3>Workforce Identity Federation (WIF) Exchange</h3>
                <p>Posts the Entra JWT token to Google STS to retrieve a temporary GCP workforce principal token.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>POST</code></p>
                    <p><strong>Endpoint:</strong> <code>https://sts.googleapis.com/v1/token</code></p>
                    <p><strong>Exchange Request Payload:</strong></p>
                    <pre className="jwt-string">
{`{
  "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
  "audience": "//iam.googleapis.com/projects/${backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/workloadIdentityPools/${backendConfig?.WIF_POOL_ID || 'POOL_ID'}/providers/${backendConfig?.WIF_PROVIDER_ID || 'PROVIDER_ID'}",
  "scope": "https://www.googleapis.com/auth/cloud-platform",
  "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
  "subjectToken": "Microsoft_Entra_Id_Token_JWT",
  "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
}`}
                    </pre>
                  </div>
                </details>

                {gcpToken ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ GCP STS Token Exchanged</span>
                    <pre className="jwt-string">{gcpToken.substring(0, 80)}...</pre>
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep2} disabled={!entraToken || stepLoading[2]}>
                    {stepLoading[2] ? 'Exchanging...' : 'Execute STS Exchange'}
                  </button>
                )}
                {stepTraces[2] && <RenderTraceList traces={stepTraces[2]} />}
              </div>

              {/* Step 3: Domain Allowlist */}
              <div className={`wizard-card ${wizardStep === 3 ? 'active' : ''} ${!gcpToken ? 'disabled' : ''} step-${stepStatus[3]}`}>
                <div className="step-badge">Step 3</div>
                <h3>Proactive Custom Domain Allowlist (Widget Config)</h3>
                <p>Invokes a programmatic PATCH to <code>default_search_widget_config</code> allowlisting your browser origin.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>PATCH</code></p>
                    <p><strong>Endpoint:</strong> <code>https://discoveryengine.googleapis.com/v1alpha/projects/{backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/collections/default_collection/engines/{backendConfig?.ENGINE_ID || 'ENGINE_ID'}/searchWidgetConfig</code></p>
                    <p><strong>Query Parameters:</strong> <code>updateMask=allowed_domains</code></p>
                    <p><strong>Authorization Header:</strong> <code>Authorization: Bearer GCP_Federated_STS_Token</code></p>
                    <p><strong>Request Body:</strong></p>
                    <pre className="jwt-string">
{`{
  "allowedDomains": [
    "localhost",
    "127.0.0.1",
    "your-custom-app-domain.com"
  ]
}`}
                    </pre>
                  </div>
                </details>

                {stepStatus[3] === 'success' ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ Origin Allowlisted</span>
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep3} disabled={!gcpToken || stepLoading[3]}>
                    {stepLoading[3] ? 'Allowlisting...' : 'PATCH Widget Config Domain'}
                  </button>
                )}
                {stepTraces[3] && <RenderTraceList traces={stepTraces[3]} />}
              </div>

              {/* Step 4: Resolve Auth URL */}
              <div className={`wizard-card ${wizardStep === 4 ? 'active' : ''} ${stepStatus[3] !== 'success' ? 'disabled' : ''} step-${stepStatus[4]}`}>
                <div className="step-badge">Step 4</div>
                <h3>Fetch Widget Config & Resolve Authorization URI</h3>
                <p>Queries Google with customDomain parameters to securely generate signed authorization paths.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>GET</code></p>
                    <p><strong>Endpoint:</strong> <code>https://discoveryengine.googleapis.com/v1alpha/projects/{backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/collections/default_collection/engines/{backendConfig?.ENGINE_ID || 'ENGINE_ID'}/searchWidgetConfig</code></p>
                    <p><strong>Query Parameters:</strong> <code>customDomain=your_current_origin</code></p>
                    <p><strong>Authorization Header:</strong> <code>Authorization: Bearer GCP_Federated_STS_Token</code></p>
                    <p><strong>GCP Output Field Extracted:</strong> <code>searchWidgetConfig.jsonSetting.sharePointConfig.authorizationUri</code></p>
                  </div>
                </details>

                {resolvedAuthUrl ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ Authorization URI Resolved</span>
                    <pre className="jwt-string">{resolvedAuthUrl.substring(0, 100)}...</pre>
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep4} disabled={stepStatus[3] !== 'success' || stepLoading[4]}>
                    {stepLoading[4] ? 'Resolving...' : 'Fetch Authorized Path'}
                  </button>
                )}
                {stepTraces[4] && <RenderTraceList traces={stepTraces[4]} />}
              </div>

              {/* Step 5: Popup & Poll */}
              <div className={`wizard-card ${wizardStep === 5 ? 'active' : ''} ${!resolvedAuthUrl ? 'disabled' : ''} step-${stepStatus[5]}`}>
                <div className="step-badge">Step 5</div>
                <h3>Consent Popup & Redirect Callback Interceptor</h3>
                <p>Launches MS Consent Popup, intercepts authentication codes, or polls closure as backup.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Action:</strong> Redirects the browser user to Microsoft OAuth 2.0 Consent Portal.</p>
                    <p><strong>Redirect Destination URI:</strong> <code>https://login.microsoftonline.com/{backendConfig?.TENANT_ID || 'common'}/oauth2/v2.0/authorize</code></p>
                    <p><strong>Intercept Strategy:</strong> Listens to <code>window.postMessage</code> communication dispatched from Google's redirect target (<code>https://vertexaisearch.cloud.google.com/oauth-redirect</code>) once authorization is approved.</p>
                  </div>
                </details>

                {capturedRedirectUrl ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ Consent Callback Capture Intercepted</span>
                    <pre className="jwt-string">{capturedRedirectUrl.substring(0, 100)}...</pre>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '0.75rem' }}>
                    <button className="btn-primary btn-step" onClick={executeStep5} disabled={!resolvedAuthUrl || stepLoading[5]}>
                      {stepLoading[5] ? 'Consenting Window Open...' : 'Launch Consent Popup'}
                    </button>
                    
                    <div style={{ marginTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '12px' }}>
                      <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', display: 'block', marginBottom: '6px' }}>
                        💡 <strong>Manual Fallback:</strong> Since Google's OOTB redirect handler resides on a different domain (`vertexaisearch.cloud.google.com`), cross-origin policies can block automatic closure. Simply copy the <strong>entire address bar URL</strong> from the stuck popup and paste it here:
                      </label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input 
                           type="text" 
                           placeholder="Paste https://vertexaisearch.cloud.google.com/oauth-redirect?code=..." 
                           className="chat-input"
                           style={{ flex: 1, height: '38px', fontSize: '12px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.15)' }}
                           onChange={(e) => {
                             const val = e.target.value.trim();
                             if (val.startsWith('http') && val.includes('code=')) {
                               setCapturedRedirectUrl(val);
                               setStepStatus(prev => ({ ...prev, 5: 'success' }));
                               setWizardStep(6);
                               setAuthStatus('Redirect URL manually captured!');
                               if (consentPopupRef.current) {
                                 consentPopupRef.current.close();
                                 consentPopupRef.current = null;
                               }
                             }
                           }}
                        />
                      </div>
                    </div>
                  </div>
                )}
                {authStatus && <div className="auth-status-bar">{authStatus}</div>}
              </div>

              {/* Step 6: acquireAndStoreRefreshToken */}
              <div className={`wizard-card ${wizardStep === 6 ? 'active' : ''} ${!capturedRedirectUrl ? 'disabled' : ''} step-${stepStatus[6]}`}>
                <div className="step-badge">Step 6</div>
                <h3>Store Refresh Token (acquireAndStoreRefreshToken)</h3>
                <p>Submits callback redirect URI to Discovery Engine, exchanging it for per-user refresh tokens.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>POST</code></p>
                    <p><strong>Endpoint:</strong> <code>https://discoveryengine.googleapis.com/v1alpha/projects/{backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/collections/default_collection/dataConnectors/{backendConfig?.CONNECTOR_ID || 'CONNECTOR_ID'}:acquireAndStoreRefreshToken</code></p>
                    <p><strong>Authorization Header:</strong> <code>Authorization: Bearer GCP_Federated_STS_Token</code></p>
                    <p><strong>Request Body:</strong></p>
                    <pre className="jwt-string">
{`{
  "clientId": "${backendConfig?.CONNECTOR_CLIENT_ID || 'CLIENT_ID'}",
  "callbackUri": "Intercepted_Redirect_Callback_URI"
}`}
                    </pre>
                  </div>
                </details>

                {stepStatus[6] === 'success' ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ Refresh Token Stored Successfully</span>
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep6} disabled={!capturedRedirectUrl || stepLoading[6]}>
                    {stepLoading[6] ? 'Storing...' : 'Acquire & Store Refresh Token'}
                  </button>
                )}
                {stepTraces[6] && <RenderTraceList traces={stepTraces[6]} />}
              </div>

              {/* Step 7: updateEngineUserData */}
              <div className={`wizard-card ${wizardStep === 7 ? 'active' : ''} ${stepStatus[6] !== 'success' ? 'disabled' : ''} step-${stepStatus[7]}`}>
                <div className="step-badge">Step 7</div>
                <h3>Engine State Synchronization (AUTHORIZED)</h3>
                <p>Calls <code>updateEngineUserData</code> to permanently sync authorized state across all OOTB interfaces.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>POST</code></p>
                    <p><strong>Endpoint:</strong> <code>https://discoveryengine.googleapis.com/v1alpha/projects/{backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/collections/default_collection/engines/{backendConfig?.ENGINE_ID || 'ENGINE_ID'}:updateEngineUserData</code></p>
                    <p><strong>Authorization Header:</strong> <code>Authorization: Bearer GCP_Federated_STS_Token</code></p>
                    <p><strong>Request Body:</strong></p>
                    <pre className="jwt-string">
{`{
  "userConsentStatus": "AUTHORIZED"
}`}
                    </pre>
                  </div>
                </details>

                {stepStatus[7] === 'success' ? (
                  <div className="token-success-box" style={{ marginTop: '0.75rem' }}>
                    <span className="success-check">✓ Engine Metadata State Synchronized (AUTHORIZED)</span>
                  </div>
                ) : (
                  <button className="btn-primary btn-step" style={{ marginTop: '0.75rem' }} onClick={executeStep7} disabled={stepStatus[6] !== 'success' || stepLoading[7]}>
                    {stepLoading[7] ? 'Syncing...' : 'Sync Engine State'}
                  </button>
                )}
                {stepTraces[7] && <RenderTraceList traces={stepTraces[7]} />}
              </div>

              {/* Step 8: check connection */}
              <div className={`wizard-card ${wizardStep === 8 ? 'active' : ''} step-${stepStatus[8]}`}>
                <div className="step-badge">Step 8</div>
                <h3>Active Connection Health Check (acquireAccessToken)</h3>
                <p>Calls <code>acquireAccessToken</code> via WIF to verify refresh tokens exist on the backend.</p>
                
                <details className="api-details-expander">
                  <summary>💻 Under the Hood: API Specification</summary>
                  <div className="api-details-content">
                    <p><strong>Method:</strong> <code>POST</code></p>
                    <p><strong>Endpoint:</strong> <code>https://discoveryengine.googleapis.com/v1alpha/projects/{backendConfig?.PROJECT_NUMBER || 'PROJECT_NUM'}/locations/global/collections/default_collection/dataConnectors/{backendConfig?.CONNECTOR_ID || 'CONNECTOR_ID'}:acquireAccessToken</code></p>
                    <p><strong>Authorization Header:</strong> <code>Authorization: Bearer GCP_Federated_STS_Token</code></p>
                    <p><strong>Action:</strong> Checks if Google can programmatically generate an active Microsoft access token from the stored user credentials. If yes, connection is healthy.</p>
                  </div>
                </details>

                <div className="connection-report-card" style={{ marginTop: '0.75rem' }}>
                  <span className={`status-pill ${spConnected ? 'healthy' : 'unhealthy'}`}>
                    {spConnected ? 'Connected 🟢' : 'Not Connected 🔒'}
                  </span>
                  <button className="btn-secondary" onClick={executeStep8} disabled={stepLoading[8]}>
                    {stepLoading[8] ? 'Verifying...' : 'Query Connection Status'}
                  </button>
                </div>
                {stepTraces[8] && <RenderTraceList traces={stepTraces[8]} />}
              </div>

            </div>
          )}

          {activeTab === 'search' && (
            <div className="search-workspace">
              {/* Premium Auth Control Bar */}
              <div className="chat-auth-control-bar">
                <div className="auth-status-indicator">
                  <div className={`status-dot ${isAuthenticated ? 'active' : 'inactive'}`} />
                  <div className="status-label-group">
                    <span className="control-label">Microsoft Identity</span>
                    <span className="control-val">
                      {isAuthenticated ? `${username}` : 'Not Authenticated 🔒'}
                    </span>
                  </div>
                </div>

                <div className="auth-action-buttons">
                  {!isAuthenticated ? (
                    <button className="btn-primary btn-sm" onClick={executeStep1}>
                      Login with Microsoft
                    </button>
                  ) : (
                    <button className="btn-secondary btn-sm" onClick={() => instance.logoutPopup()}>
                      Disconnect Microsoft
                    </button>
                  )}
                </div>

                <div className="separator" />

                <div className="gemini-toggle-container">
                  <div className="status-label-group">
                    <span className="control-label">Gemini Enterprise Integration</span>
                    <span className="control-val">
                      {spConnected ? 'AUTHORIZED 🟢' : 'DEAUTHORIZED 🔴'}
                    </span>
                  </div>
                  <label className="switch-toggle">
                    <input 
                      type="checkbox" 
                      checked={spConnected}
                      disabled={disconnecting}
                      onChange={async (e) => {
                        const nextVal = e.target.checked;
                        if (!nextVal) {
                          // Deauthorize
                          await executeDisconnect();
                        } else {
                          // Authorize - check connection or run STS + sync
                          if (!entraToken) {
                            alert("Please log in with Microsoft first!");
                            return;
                          }
                          setLoading(true);
                          try {
                            const resp = await fetch('/api/sharepoint/check-connection', {
                              headers: { 'X-Entra-Id-Token': entraToken }
                            });
                            const data = await resp.json();
                            if (data.connected) {
                              setSpConnected(true);
                              alert("SharePoint Connector synchronized and AUTHORIZED successfully!");
                            } else {
                              alert("No stored refresh token found on the backend for this account. Please run the Step-by-Step Diagnostic Wizard once to register the connector.");
                            }
                          } catch {
                            alert("Connection verification failed.");
                          } finally {
                            setLoading(false);
                          }
                        }
                      }}
                    />
                    <span className="slider-round" />
                  </label>
                </div>
              </div>

              <div className="search-container">
                <div className="messages-area">
                  {messages.length === 0 && !loading && (
                    <div className="empty-state">
                      <div className="empty-icon">📂</div>
                      <h3>Search Connected SharePoint</h3>
                      <p>Query SharePoint documents with active per-user security mappings.</p>
                      {!spConnected && (
                        <p style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                          ⚠️ Note: The Gemini Enterprise integration is currently deauthorized. You must toggle it ON above to query.
                        </p>
                      )}
                    </div>
                  )}

                  {messages.map((msg, i) => (
                    <div key={i} className={`message message-${msg.role}`}>
                      <div className="message-bubble">
                        {msg.role === 'assistant' && msg.duration_ms !== undefined && msg.duration_ms > 0 && (!loading || i < messages.length - 1) && (
                          <div className="timer-badge">⏱ Query processing time: {(msg.duration_ms / 1000).toFixed(2)}s</div>
                        )}
                        
                        {msg.role === 'assistant' && (
                          <ThoughtToggle 
                            thought={msg.thought || ''} 
                            activeStep={i === messages.length - 1 ? activeStep : null} 
                          />
                        )}

                        <div className="message-text">
                          {msg.role === 'assistant' ? (
                            msg.text ? (
                              <RenderFormattedText text={msg.text} />
                            ) : (
                              loading && i === messages.length - 1 && (
                                <div className="loading-bubble" style={{ marginTop: '0.5rem' }}>
                                  <div className="spinner" />
                                  <span>Searching SharePoint...</span>
                                  <span className="timer-badge">{(elapsedMs / 1000).toFixed(2)}s</span>
                                </div>
                              )
                            )
                          ) : (
                            msg.text
                          )}
                        </div>

                        {msg.sources && msg.sources.length > 0 && (
                          <div className="sources">
                            <h4>Grounded Citations ({msg.sources.length})</h4>
                            <div className="source-cards">
                              {msg.sources.map((src, j) => (
                                <a key={j} href={src.url} target="_blank" rel="noopener noreferrer" className="source-card">
                                  <div className="source-info">
                                    <span className="source-title">{src.title}</span>
                                    <span className="source-meta">
                                      {src.entity_type || 'Document'} {src.file_type && ` \u00B7 ${src.file_type.split('/').pop()?.toUpperCase()}`}
                                    </span>
                                  </div>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* dynamic clickable suggestion chips derived from streamAssist replies */}
                {lastSuggestions.length > 0 && !loading && (
                  <div className="suggestions-panel">
                    <div className="suggestions-title">🧠 Suggested follow-up questions:</div>
                    <div className="suggestions-chips">
                      {lastSuggestions.map((sug, chipIdx) => (
                        <button 
                          key={chipIdx} 
                          type="button" 
                          className="suggestion-chip" 
                          onClick={() => executeSearch(sug)}
                        >
                          {sug}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <form className="search-input-form" onSubmit={(e) => { e.preventDefault(); executeSearch(); }}>
                  <input
                    type="text" value={query} onChange={(e) => setQuery(e.target.value)}
                    placeholder={spConnected ? "Ask a question about documents in your connected SharePoint..." : "Please authorize Gemini Enterprise Integration above to start querying..."} 
                    disabled={loading || !spConnected}
                  />
                  <button type="submit" className="btn-primary" disabled={loading || !query.trim() || !spConnected}>
                    Search
                  </button>
                </form>
              </div>
              {stepTraces[10] && (
                <div className="search-traces">
                  <h3>Search Outbound Call Trace</h3>
                  <RenderTraceList traces={stepTraces[10]} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Configuration & Environment Sidebar */}
      <aside className="debug-sidebar">
        <div className="sidebar-header">
          <h3>Environment Setup</h3>
        </div>
        
        {backendConfig ? (
          <div className="config-inspector">
            <div className="config-section">
              <h4>GCP Environment</h4>
              <div className="config-item"><label>PROJECT_NUMBER</label><code>{backendConfig.PROJECT_NUMBER}</code></div>
              <div className="config-item"><label>ENGINE_ID</label><code>{backendConfig.ENGINE_ID}</code></div>
              <div className="config-item"><label>CONNECTOR_ID</label><code>{backendConfig.CONNECTOR_ID}</code></div>
            </div>

            <div className="config-section">
              <h4>Workforce Pool (WIF)</h4>
              <div className="config-item"><label>POOL_ID</label><code>{backendConfig.WIF_POOL_ID}</code></div>
              <div className="config-item"><label>PROVIDER_ID</label><code>{backendConfig.WIF_PROVIDER_ID}</code></div>
            </div>

            <div className="config-section">
              <h4>Microsoft App Management</h4>
              <div className="config-item"><label>TENANT_ID</label><code>{backendConfig.TENANT_ID}</code></div>
              <div className="config-item"><label>CLIENT_ID</label><code>{backendConfig.CONNECTOR_CLIENT_ID}</code></div>
              <div className="config-item"><label>SHAREPOINT_DOMAIN</label><code>{backendConfig.SHAREPOINT_DOMAIN}</code></div>
            </div>
            
            <div className="config-section">
              <h4>Entra ID Configuration Guide</h4>
              <p className="guide-text">
                1. <strong>Redirect URI:</strong> In App Registration, set Web redirect to: <code className="block">https://vertexaisearch.cloud.google.com/oauth-redirect</code>
              </p>
              <p className="guide-text">
                2. <strong>Permissions:</strong> Add delegated: <code className="block">AllSites.Read</code>, <code className="block">Sites.Search.All</code>, <code className="block">offline_access</code>. Ensure admin consent is granted.
              </p>
              <p className="guide-text">
                3. <strong>Implicit Grant:</strong> Ensure ID Tokens are checked in Authentication panel.
              </p>
            </div>
          </div>
        ) : (
          <div className="sidebar-empty">
            <div className="spinner" />
            <p>Loading server configuration...</p>
          </div>
        )}
      </aside>
    </div>
  );
}

// Sub-component to render HTTP transactions
function RenderTraceList({ traces }: { traces: HttpTrace[] }) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  return (
    <div className="http-traces-container">
      {traces.map((trace, i) => (
        <div key={i} className={`http-trace-card status-${trace.status_code < 300 ? 'ok' : 'fail'}`}>
          <div className="http-trace-header" onClick={() => setExpanded(prev => ({ ...prev, [i]: !prev[i] }))}>
            <span className="trace-badge-method">{trace.method}</span>
            <span className="trace-badge-status">{trace.status_code}</span>
            <span className="trace-url">{trace.url.substring(0, 60)}...</span>
            <span className="trace-duration">{trace.duration_ms}ms</span>
            <span className="trace-chevron">{expanded[i] ? '▼' : '▶'}</span>
          </div>
          
          {expanded[i] && (
            <div className="http-trace-details">
              {trace.curl && (
                <div className="code-section">
                  <h5>Equivalent cURL Command</h5>
                  <pre className="curl-block">{trace.curl}</pre>
                </div>
              )}
              
              <div className="trace-grid-split">
                <div className="code-section">
                  <h5>Request Headers</h5>
                  <pre className="headers-block">{JSON.stringify(trace.request_headers, null, 2)}</pre>
                  {trace.request_body && (
                    <>
                      <h5>Request Body</h5>
                      <pre className="body-block">{JSON.stringify(trace.request_body, null, 2)}</pre>
                    </>
                  )}
                </div>

                <div className="code-section">
                  <h5>Response Headers</h5>
                  <pre className="headers-block">{JSON.stringify(trace.response_headers, null, 2)}</pre>
                  <h5>Response Body</h5>
                  <pre className="body-block">{JSON.stringify(trace.response_body, null, 2)}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Animated indicator showing sub-steps of the backend operations while waiting
function DynamicStepDesc({ stepNum, defaultDesc, activeStep }: { stepNum: number; defaultDesc: string; activeStep?: number | null }) {
  const [subStep, setSubStep] = useState(0);

  useEffect(() => {
    if (activeStep !== 4 || stepNum !== 4) {
      setSubStep(0);
      return;
    }

    const interval = setInterval(() => {
      setSubStep(prev => (prev < 4 ? prev + 1 : prev));
    }, 2000);

    return () => clearInterval(interval);
  }, [activeStep, stepNum]);

  if (stepNum === 4 && activeStep === 4) {
    const subSteps = [
      "🔑 Exchanging WIF security descriptors and verifying OIDC claims...",
      "🌐 Establishing secure TLS connection to sockcop.sharepoint.com...",
      "🔍 Dispatching ACL-scoped semantic query to SharePoint Site collection...",
      "📄 Extracting relevant document snippets and validating permissions...",
      "🧠 Bundling context blocks and initiating grounded reasoning synthesis..."
    ];
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '4px' }}>
        <div style={{ fontSize: '0.7rem', color: '#60a5fa', fontWeight: 600 }}>
          {subSteps[subStep]}
        </div>
        <div style={{ display: 'flex', gap: '3px', alignItems: 'center', marginTop: '2px' }}>
          {[0, 1, 2, 3, 4].map(idx => (
            <div 
              key={idx} 
              style={{ 
                height: '3px', 
                width: '16px', 
                borderRadius: '2px', 
                background: idx <= subStep ? '#3b82f6' : 'rgba(255,255,255,0.08)',
                opacity: idx === subStep ? 0.8 : 1,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }} 
            />
          ))}
        </div>
      </div>
    );
  }

  return <>{defaultDesc}</>;
}

// Collapsible thought process toggle element
function ThoughtToggle({ thought, activeStep }: { thought: string; activeStep?: number | null }) {
  const [open, setOpen] = useState(false);

  // Auto-expand the internal pipeline drawer when search launches (step 1 is active)
  useEffect(() => {
    if (activeStep === 1) {
      setOpen(true);
    }
  }, [activeStep]);

  const getStepStyle = (stepNum: number) => {
    if (activeStep === undefined || activeStep === null) {
      // Resting / Completed state: Show default brand colors
      const defaultColors = ['#3b82f6', '#3b82f6', '#10b981', '#f59e0b', 'purple'];
      return {
        opacity: 1,
        circleBg: defaultColors[stepNum - 1],
        circleColor: '#fff',
        textWeight: '600',
        pulse: false,
        check: false
      };
    }
    if (activeStep === stepNum) {
      // Active step: Bright blue pulsing highlight
      return { 
        opacity: 1, 
        circleBg: '#2563eb', 
        circleColor: '#fff', 
        textWeight: '700', 
        pulse: true,
        check: false
      };
    }
    if (activeStep > stepNum) {
      // Finished step: Solid green indicator
      return { 
        opacity: 0.9, 
        circleBg: '#059669', 
        circleColor: '#fff', 
        textWeight: '600',
        pulse: false,
        check: true
      };
    }
    // Pending step: Muted and semi-transparent
    return { 
      opacity: 0.35, 
      circleBg: 'rgba(255, 255, 255, 0.05)', 
      circleColor: 'var(--text-muted)', 
      textWeight: '500',
      pulse: false,
      check: false
    };
  };

  const steps = [
    {
      num: 1,
      title: "Exchange Microsoft Identity Token (OAuth Client-Side)",
      desc: "Verified claims locally and established active security parameters via MSAL."
    },
    {
      num: 2,
      title: "Federate to GCP Workforce Pool (STS Token Exchange)",
      desc: "Converted Microsoft JWT token into a Federated GCP Principal under the workforce provider."
    },
    {
      num: 3,
      title: "Resolve Authorized SharePoint Access (Aquire Access Token)",
      desc: "Resolved Microsoft refresh token mappings on the backend, ensuring direct read credentials exist."
    },
    {
      num: 4,
      title: "Semantic SharePoint Search & ACL Match (Search Tool)",
      desc: "Dispatched user-authenticated query to SharePoint index matching Microsoft user ACL access boundaries."
    },
    {
      num: 5,
      title: "Grounded Synthesis (Synthesis Tool)",
      desc: "Reconstructed the raw response, formatted search citations, extracted thoughts, and decoded Base64 follow-up suggestions."
    }
  ];

  return (
    <div className="thought-toggle-container">
      <div className="thought-header" onClick={() => setOpen(!open)}>
        <span>
          <span className="thought-icon">🧠</span> 
          Internal Reasoning & Tool Execution Pipeline
          {activeStep && (
            <span style={{ marginLeft: '0.75rem', background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', fontSize: '0.65rem', padding: '0.15rem 0.45rem', borderRadius: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700, animation: 'pulse 1.5s infinite' }}>
              Executing Step {activeStep}/5
            </span>
          )}
        </span>
        <span className="thought-arrow">{open ? '▼' : '▶'}</span>
      </div>
      {open && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Visual Grounding Pipeline flow */}
          <div className="pipeline-flow-wrapper" style={{ padding: '0.85rem 0.85rem 0.45rem 0.85rem', background: 'rgba(0,0,0,0.15)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
              🛠 Execution Sequence Log:
            </div>
            
            <div className="pipeline-steps" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {steps.map((step) => {
                const style = getStepStyle(step.num);
                return (
                  <div key={step.num} className="pipeline-step" style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', opacity: style.opacity, transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }}>
                    <span 
                      className={`step-number ${style.pulse ? 'pulse-glow-blue' : ''}`} 
                      style={{ 
                        background: style.circleBg, 
                        color: style.circleColor, 
                        fontSize: '9px', 
                        fontWeight: 'bold', 
                        borderRadius: '50%', 
                        width: '16px', 
                        height: '16px', 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        flexShrink: 0, 
                        marginTop: '2px',
                        border: style.pulse ? '1px solid #60a5fa' : '1px solid transparent',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                      }}
                    >
                      {style.check ? '✓' : step.num}
                    </span>
                    <div>
                      <div style={{ fontSize: '0.78rem', fontWeight: style.textWeight as any, color: style.pulse ? '#60a5fa' : 'var(--text-primary)', transition: 'color 0.3s' }}>
                        {step.title}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: style.pulse ? '#93c5fd' : 'var(--text-secondary)' }}>
                        <DynamicStepDesc stepNum={step.num} defaultDesc={step.desc} activeStep={activeStep} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {thought && thought.trim() && (
            <div style={{ padding: '0 0.85rem 0.85rem 0.85rem' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
                💭 Model Internal Thoughts:
              </div>
              <div className="thought-content" style={{ border: 'none', padding: 0 }}>
                {thought}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Natively render formatted text containing markdown headers, bullet lists, bold highlights, and markdown tables.
function RenderFormattedText({ text }: { text: string }) {
  if (!text) return null;

  const lines = text.split('\n');
  const renderedElements: JSX.Element[] = [];

  let listItems: string[] = [];
  let inList = false;
  let listType: 'ul' | 'ol' = 'ul';

  let inTable = false;
  let tableHeaders: string[] = [];
  let tableRows: string[][] = [];

  const flushList = (key: number) => {
    if (listItems.length > 0) {
      if (listType === 'ul') {
        renderedElements.push(
          <ul key={`list-${key}`}>
            {listItems.map((item, idx) => (
              <li key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkups(item) }} />
            ))}
          </ul>
        );
      } else {
        renderedElements.push(
          <ol key={`list-${key}`}>
            {listItems.map((item, idx) => (
              <li key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkups(item) }} />
            ))}
          </ol>
        );
      }
      listItems = [];
    }
    inList = false;
  };

  const flushTable = (key: number) => {
    if (tableRows.length > 0 || tableHeaders.length > 0) {
      renderedElements.push(
        <div className="markdown-table-wrapper" key={`table-wrap-${key}`}>
          <table className="markdown-table">
            {tableHeaders.length > 0 && (
              <thead>
                <tr>
                  {tableHeaders.map((th, idx) => (
                    <th key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkups(th) }} />
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {tableRows.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} dangerouslySetInnerHTML={{ __html: formatInlineMarkups(cell) }} />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableHeaders = [];
      tableRows = [];
    }
    inTable = false;
  };

  const formatInlineMarkups = (str: string) => {
    // Bold highlight replacement
    let formatted = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
  };

  lines.forEach((line, lineIdx) => {
    const trimmed = line.trim();

    // Check if we are starting or continuing a table
    if (trimmed.startsWith('|')) {
      if (inList) flushList(lineIdx);
      inTable = true;
      
      const cells = line.split('|').map(c => c.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      
      // Ignore horizontal separators
      if (trimmed.includes('---')) {
        return;
      }

      if (tableHeaders.length === 0 && tableRows.length === 0) {
        tableHeaders = cells;
      } else {
        tableRows.push(cells);
      }
      return;
    } else {
      if (inTable) flushTable(lineIdx);
    }

    // Check headings
    if (trimmed.startsWith('###')) {
      if (inList) flushList(lineIdx);
      renderedElements.push(
        <h3 key={lineIdx} dangerouslySetInnerHTML={{ __html: formatInlineMarkups(trimmed.substring(3).trim()) }} />
      );
      return;
    }

    // Check bullet lists
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      if (inList && listType !== 'ul') {
        flushList(lineIdx);
      }
      inList = true;
      listType = 'ul';
      listItems.push(trimmed.substring(2));
      return;
    }

    // Check ordered lists
    if (/^\d+\.\s/.test(trimmed)) {
      if (inList && listType !== 'ol') {
        flushList(lineIdx);
      }
      inList = true;
      listType = 'ol';
      listItems.push(trimmed.replace(/^\d+\.\s/, ''));
      return;
    }

    // Blank line
    if (!trimmed) {
      if (inList) flushList(lineIdx);
      return;
    }

    // Standard paragraph line
    if (inList) {
      // Append multi-line content to the last list item
      listItems[listItems.length - 1] += ' ' + trimmed;
    } else {
      renderedElements.push(
        <p key={lineIdx} className="message-text-formatted" dangerouslySetInnerHTML={{ __html: formatInlineMarkups(line) }} />
      );
    }
  });

  // Final flush of active structures
  if (inList) flushList(9999);
  if (inTable) flushTable(9999);

  return <div className="formatted-text-container">{renderedElements}</div>;
}

