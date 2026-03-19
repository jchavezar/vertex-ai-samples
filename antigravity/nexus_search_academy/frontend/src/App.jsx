import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, RefreshCw, Key, Sparkles, ChevronRight, Terminal, ExternalLink, Play, Code, CheckCircle2, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getWifLoginUrl, exchangeForGoogleToken } from './api/auth';
import { executeStreamAssist } from './api/search';
import ChatOverlay from './components/ChatOverlay';

export default function App() {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isTopologyOpen, setIsTopologyOpen] = useState(false);
  const [idToken, setIdToken] = useState('');
  const [googleToken, setGoogleToken] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamAnswer, setStreamAnswer] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [logs, setLogs] = useState([]);
  const logEndRef = useRef(null);

  const steps = [
    {
      id: 1,
      title: "Identity Provider Login",
      icon: "Shield",
      description: "The cycle begins with the Identity Provider (Microsoft Entra ID). You authenticate to prove who you are, receiving an OIDC ID Token.",
      code: `// api/auth.js\nexport const getWifLoginUrl = () => {\n  const redirect = window.location.origin + '/';\n  const url = \`\${CONFIG.ISSUER}/oauth2/v2.0/authorize?client_id=\${CONFIG.MS_APP_ID}&response_type=id_token&redirect_uri=\${encodeURIComponent(redirect)}&scope=openid%20profile%20email&response_mode=fragment\`;\n  return url;\n};`
    },
    {
      id: 2,
      title: "Hash Fragment Listener",
      icon: "Key",
      description: "Upon successful login, Azure redirects back with the ID Token in the URL hash fragment. The application extracts this token to proceed.",
      code: `// App.jsx\nconst hash = window.location.hash;\nif (hash.includes('id_token=')) {\n  const idToken = new URLSearchParams(hash.substring(1)).get('id_token');\n  setIdToken(idToken);\n}`
    },
    {
      id: 3,
      title: "STS Token Exchange",
      icon: "RefreshCw",
      description: "We exchange the Entra ID Token for a Google Federated Access Token using the Secure Token Service (STS). This is the core of WIF.",
      code: `// api/auth.js\nexport const exchangeForGoogleToken = async (idToken) => {\n  const payload = {\n    audience: \`//iam.googleapis.com/.../providers/...\`,\n    grant_type: 'urn:ietf:params:oauth:grant-type:token-exchange',\n    subject_token: idToken\n  };\n  const resp = await axios.post('/sts/v1/token', payload);\n  return resp.data;\n};`
    },
    {
      id: 4,
      title: "Backend Metadata Broker",
      icon: "Shield",
      description: "The backend uses Elevated Service Account context to securely read Assistant configurations and connected DataStores, avoiding 403 authorization restrictive blockers.",
      code: `// backend/main.py\nadmin_creds, _ = google.auth.default()\nds_resp = requests.get(ds_url, headers={'Authorization': f'Bearer {admin_creds.token}'})\ndataStoreSpecs = [ {'dataStore': r['name']} for r in details ]`
    },
    {
      id: 5,
      title: "Authenticated StreamAssist",
      icon: "Sparkles",
      description: "Armed with the DataStore specs, the backend streams the query using the USER's WIF Token back down into Vertex AI for optimal security trimming compliance.",
      code: `// backend/main.py
payload = {
  "query": query,
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {
          "dataStore": "projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/5817ee80-82a4-49e3-a19c-2cedc73a6300",
          "description": "SharePoint Online Federated Corpus" // Explicitly linking the connector index
        }
      ]
    }
  }
}

response_stream = requests.post(assist_url, headers=headers, json=payload)`
    }
  ];

  const addLog = (type, message, data = null) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      data: data ? JSON.stringify(data, null, 2) : null
    }]);
  };

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Hash Listener for Step 2
  useEffect(() => {
    const hash = window.location.hash;
    if (hash.includes('id_token=')) {
      addLog('info', 'Detected Auth Redirect Hash');
      const params = new URLSearchParams(hash.substring(1));
      const token = params.get('id_token');
      if (token) {
        setIdToken(token);
        addLog('success', 'Extracted Microsoft ID Token', { token: token.substring(0, 30) + '...' });
        setCurrentStepIndex(1); // Move to Step 2 (Listener)
        // Cleanup hash to avoid refresh loops
        window.history.replaceState(null, null, ' ');
      }
    }
  }, []);

  const handleLaunchLogin = () => {
    const url = getWifLoginUrl();
    addLog('call', 'getWifLoginUrl()', { url });
    addLog('info', 'Redirecting to Microsoft Entra ID...');
    setTimeout(() => {
      window.location.href = url;
    }, 1000);
  };

  const handleTriggerExchange = async () => {
    setLoading(true);
    addLog('call', 'exchangeForGoogleToken(idToken)', { idToken: idToken.substring(0, 20) + '...' });
    try {
      const data = await exchangeForGoogleToken(idToken);
      addLog('success', 'STS Exchange Successful', data);
      if (data.access_token) {
        setGoogleToken(data.access_token);
        setCurrentStepIndex(3); // Skip to StreamAssist or move next
      } else {
         addLog('warning', 'Exchange did not return access_token', data);
      }
    } catch (err) {
      addLog('error', 'STS Exchange Failed', err.response?.data || err.message);
      // Fallback simulation trigger for workshop if blocked
      addLog('info', 'Triggering Fallback Simulation Mode due to Auth restriction');
      setGoogleToken('ya29_simulated_fallback_token');
      setCurrentStepIndex(3);
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySubmit = async (e) => {
    if (e) e.preventDefault();
    if (!query) return;

    setLoading(true);
    setStreamAnswer('');
    setSearchResults([]);
    const toolsSpecMock = {
      vertexAiSearchSpec: {
        dataStoreSpecs: [
          {
             dataStore: "projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/5817ee80-82a4-49e3-a19c-2cedc73a6300",
             description: "SharePoint Online Connector Index"
          }
        ]
      }
    };
    addLog('call', 'executeStreamAssist(googleToken, query)', { query, toolsSpec: toolsSpecMock });

    try {
      await executeStreamAssist(
        googleToken, 
        query, 
        (chunk, full, results, cites) => {
          if (chunk) setStreamAnswer(full);
          if (results.length > 0) setSearchResults(results);
        },
        (event, payload, headers) => {
          if (event.includes('POST')) {
            addLog('api_request', event, { headers, payload });
          } else {
            addLog('api_packet', event, payload);
          }
        }
      );
      addLog('success', 'StreamAssist Completed');
    } catch (err) {
      addLog('error', 'StreamAssist Error', err.message);
    } finally {
      setLoading(false);
    }
  };

  const activeStep = steps[currentStepIndex];

  const getIcon = (iconName) => {
    const icons = { Shield, RefreshCw, Key, Sparkles };
    const IconComponent = icons[iconName] || Shield;
    return <IconComponent size={20} />;
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#0a0a10', color: '#e2e8f0', overflow: 'hidden' }}>
      {/* Futuristic Header */}
      <header style={{ padding: '1rem 2rem', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(10, 10, 16, 0.9)', backdropFilter: 'blur(10px)', zIndex: 10, position: 'sticky', top: 0 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '2px' }} className="glow-text">
            NEXUS SEARCH ACADEMY
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.8rem' }}>EPOCH 3050 // REAL-TIME AUTHN INTELLIGENCE</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            onClick={() => setIsTopologyOpen(true)}
            style={{ padding: '0.5rem 0.8rem', background: 'rgba(0, 242, 254, 0.1)', border: '1px solid rgba(0, 242, 254, 0.3)', borderRadius: '6px', fontSize: '0.75rem', color: '#00f2fe', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', fontWeight: 'bold' }}
          >
            View Topology
          </button>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: googleToken ? '#10b981' : '#ef4444', boxShadow: googleToken ? '0 0 10px #10b981' : 'none' }}></div>
          <span style={{ fontSize: '0.8rem', opacity: 0.8 }}>{googleToken ? 'WIF CONNECTED' : 'DISCONNECTED'}</span>
        </div>
      </header>

      {/* Timeline Stepper */}
      <div style={{ padding: '1.5rem 2rem', display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(0,0,0,0.2)' }}>
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div 
              className={`timeline-node ${index <= currentStepIndex ? 'active' : ''}`}
              onClick={() => index <= currentStepIndex && setCurrentStepIndex(index)}
              style={{ cursor: index <= currentStepIndex ? 'pointer' : 'not-allowed' }}
            >
              {getIcon(step.icon)}
            </div>
            {index < steps.length - 1 && (
              <div className={`timeline-line ${index < currentStepIndex ? 'active' : ''}`} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Main Content */}
      <main style={{ flexGrow: 1, padding: '1.5rem 2rem', display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '1.5rem', overflow: 'hidden', minHeight: 0 }}>
        
        {/* Explanation Side */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflowY: 'auto', padding: '1.5rem', minHeight: 0 }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeStep.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem' }}>
                <div style={{ color: '#00f2fe' }}>{getIcon(activeStep.icon)}</div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: '700' }}>Step {activeStep.id}: {activeStep.title}</h2>
              </div>
              
              <p style={{ color: '#94a3b8', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                {activeStep.description}
              </p>

              {/* Step Specific Actions */}
              <div style={{ flexGrow: 1 }}>
                {activeStep.id === 1 && (
                  <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <button onClick={handleLaunchLogin} className="glow-button" style={{ padding: '1rem 2rem', fontSize: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.8rem' }}>
                      <Play size={18} /> Authenticate via Entra ID
                    </button>
                  </div>
                )}

                {activeStep.id === 2 && (
                  <div>
                    <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <h4 style={{ fontSize: '0.9rem', color: '#00f2fe', marginBottom: '0.5rem' }}>Extracted ID Token</h4>
                      <pre className="code-block" style={{ wordBreak: 'break-all', whiteSpace: 'pre-wrap' }}>
                        {idToken || 'Waiting for token from redirect...'}
                      </pre>
                    </div>
                    {idToken && (
                      <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                        <button onClick={() => setCurrentStepIndex(2)} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                          Advance to Exchange <ChevronRight size={16} />
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {activeStep.id === 3 && (
                  <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <button 
                      onClick={handleTriggerExchange} 
                      disabled={!idToken && !googleToken}
                      style={{ padding: '1rem 2rem', display: 'inline-flex', alignItems: 'center', gap: '0.8rem' }}
                    >
                      <RefreshCw size={18} className={loading ? 'spin' : ''} />
                      {loading ? 'Exchanging...' : 'Trigger STS Exchange'}
                    </button>
                  </div>
                )}

                {activeStep.id === 4 && (
                  <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <div style={{ marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: '1.6' }}>
                        To discover connected DataStore Specs without throwing CORS/403 blocks, the Backend automatically triggers a background configuration lookup with elevated Service Account context securely bound.
                      </p>
                    </div>
                    <button 
                      onClick={() => setCurrentStepIndex(4)} 
                      style={{ padding: '0.8rem 1.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                      Advance to StreamAssist <ChevronRight size={16} />
                    </button>
                  </div>
                )}

                {activeStep.id === 5 && (
                  <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <form onSubmit={handleQuerySubmit} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                      <input 
                        type="text" 
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask Vertex AI Assist..."
                        style={{ flexGrow: 1, padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid #33334c', borderRadius: '8px', color: 'white' }}
                      />
                      <button type="submit" disabled={!googleToken || loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {loading ? <RefreshCw size={16} className="spin" /> : <Sparkles size={16} />} Scan
                      </button>
                    </form>

                    {streamAnswer && (() => {
                      const thoughtMatch = streamAnswer.match(/<thought>([\s\S]*?)<\/thought>/);
                      const thoughtText = thoughtMatch ? thoughtMatch[1] : null;
                      const answerText = streamAnswer.replace(/<thought>[\s\S]*?<\/thought>/, '').trim();

                      return (
                        <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                          <h4 style={{ fontSize: '0.8rem', color: '#00f2fe', marginBottom: '0.5rem' }}>ANSWER STREAM</h4>
                          
                          {thoughtText && (
                            <div style={{ marginBottom: '1rem', padding: '0.8rem', background: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.15)', borderRadius: '6px' }}>
                              <div style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 'bold', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                <Sparkles size={12} /> Reasoning & Verification Thought
                              </div>
                              <div style={{ fontSize: '0.8rem', color: '#a7f3d0', opacity: 0.9, fontStyle: 'italic', lineHeight: '1.4' }}>
                                {thoughtText}
                              </div>
                            </div>
                          )}

                          {answerText && (
                            <div style={{ fontSize: '0.9rem', color: '#e2e8f0', lineHeight: '1.6' }}>
                              <ReactMarkdown 
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  table: ({ ...props }) => <table style={{ borderCollapse: 'collapse', width: '100%', margin: '0.8rem 0', background: 'rgba(255,255,255,0.01)', borderRadius: '6px' }} {...props} />,
                                  th: ({ ...props }) => <th style={{ border: '1px solid rgba(255,255,255,0.1)', padding: '0.6rem', background: 'rgba(255,255,255,0.03)', color: '#00f2fe', textAlign: 'left', fontWeight: 'bold' }} {...props} />,
                                  td: ({ ...props }) => <td style={{ border: '1px solid rgba(255,255,255,0.05)', padding: '0.6rem' }} {...props} />,
                                  p: ({ ...props }) => <p style={{ marginBottom: '0.8rem' }} {...props} />,
                                  strong: ({ ...props }) => <strong style={{ color: '#4ade80' }} {...props} />,
                                  h3: ({ ...props }) => <h3 style={{ color: '#00f2fe', margin: '1rem 0 0.5rem 0' }} {...props} />
                                }}
                              >
                                {answerText}
                              </ReactMarkdown>
                            </div>
                          )}
                        </div>
                      );
                    })()}

                    {searchResults.length > 0 && (
                      <div style={{ marginTop: '1rem' }}>
                        <h4 style={{ fontSize: '0.8rem', color: '#d946ef', marginBottom: '0.5rem' }}>GROUNDING SOURCES</h4>
                        <div style={{ maxHeight: '150px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {searchResults.map((res, i) => (
                            <div key={i} style={{ padding: '0.6rem', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', fontSize: '0.8rem' }}>
                              <div style={{ fontWeight: '600', color: '#e2e8f0' }}>{res.document.structData.title}</div>
                              <div style={{ opacity: 0.6, fontSize: '0.7rem' }}>URL: {res.document.structData.url}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Log / Code side */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', maxHeight: '100%', overflow: 'hidden', padding: '1.5rem', minHeight: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Terminal size={16} style={{ color: '#d946ef' }} />
              <h3 style={{ fontSize: '0.9rem', letterSpacing: '1px', fontWeight: '600' }}>LIVE LOG STREAM</h3>
            </div>
            <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>REAL-TIME EXECUTION</div>
          </div>

          {/* Logs container */}
          <div style={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.8rem', marginBottom: '1.5rem' }}>
            {logs.length === 0 && (
              <div style={{ color: '#94a3b8', fontSize: '0.8rem', textAlign: 'center', padding: '2rem' }}>
                System idling. Initiate authentication to stream logs.
              </div>
            )}
            {logs.map((log, i) => (
              <div key={i} style={{ fontSize: '0.8rem', fontFamily: 'monospace', padding: '0.6rem', background: 'rgba(0,0,0,0.2)', borderRadius: '6px', borderLeft: `3px solid ${
                log.type === 'success' ? '#10b981' : 
                log.type === 'error' ? '#ef4444' : 
                log.type === 'call' ? '#00f2fe' : 
                log.type === 'api_request' ? '#d946ef' : '#94a3b8'
              }` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', opacity: 0.6, fontSize: '0.7rem', marginBottom: '0.2rem' }}>
                  <span>[{log.type.toUpperCase()}]</span>
                  <span>{log.timestamp}</span>
                </div>
                <div style={{ color: log.type === 'error' ? '#ef4444' : '#e2e8f0' }}>{log.message}</div>
                {log.data && (
                  <pre style={{ marginTop: '0.4rem', padding: '0.4rem', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflowX: 'auto', fontSize: '0.75rem', color: '#94a3b8' }}>
                    {log.data}
                  </pre>
                )}
              </div>
            ))}
            <div ref={logEndRef} />
          </div>

          {/* Under the hood code */}
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem' }}>
            <h4 style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Code size={14} /> INSPECTOR: Code executing in this layout
            </h4>
            <pre className="code-block" style={{ maxHeight: '150px', overflowY: 'auto' }}>
              <code>{activeStep.code}</code>
            </pre>
          </div>
        </div>

      </main>
      {isTopologyOpen && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}
            onClick={() => setIsTopologyOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              style={{ background: '#111116', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '2rem', maxWidth: '800px', width: '100%', maxHeight: '85vh', overflowY: 'auto' }}
              onClick={e => e.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.8rem' }}>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#00f2fe' }}>Topology & Permission Matrix</h2>
                <button onClick={() => setIsTopologyOpen(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
              </div>

              {/* Topology Map */}
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1rem', color: '#e2e8f0', marginBottom: '0.8rem' }}>Identity Access Chain</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                  <div style={{ padding: '0.5rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '4px', textAlign: 'center' }}>Microsoft Entra Login</div>
                  <ChevronRight size={16} />
                  <div style={{ padding: '0.5rem', background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: '4px', textAlign: 'center' }}>STS Token Exchange</div>
                  <ChevronRight size={16} />
                  <div style={{ padding: '0.5rem', background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.2)', borderRadius: '4px', textAlign: 'center' }}>Backend Elevated Broker</div>
                  <ChevronRight size={16} />
                  <div style={{ padding: '0.5rem', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '4px', textAlign: 'center' }}>Vertex Streams Query</div>
                </div>
              </div>

              {/* Matrix Table */}
              <div>
                <h3 style={{ fontSize: '1rem', color: '#e2e8f0', marginBottom: '0.8rem' }}>Permissions Configuration Matrix</h3>
                <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <th style={{ textAlign: 'left', padding: '0.8rem', color: '#94a3b8' }}>Dimension</th>
                      <th style={{ textAlign: 'left', padding: '0.8rem', color: '#94a3b8' }}>Scope / Service</th>
                      <th style={{ textAlign: 'left', padding: '0.8rem', color: '#94a3b8' }}>Permission / Role</th>
                      <th style={{ textAlign: 'left', padding: '0.8rem', color: '#94a3b8' }}>Purpose</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.8rem', fontWeight: 'bold' }}>Microsoft Entra</td>
                      <td style={{ padding: '0.8rem' }}>Graph API</td>
                      <td style={{ padding: '0.8rem', color: '#4ade80' }}>User.Read</td>
                      <td style={{ padding: '0.8rem', opacity: 0.8 }}>Identity verification</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.8rem', fontWeight: 'bold' }}>Microsoft Entra</td>
                      <td style={{ padding: '0.8rem' }}>SharePoint</td>
                      <td style={{ padding: '0.8rem', color: '#4ade80' }}>Sites.Read.All</td>
                      <td style={{ padding: '0.8rem', opacity: 0.8 }}>Grants reading capability for crawl indices</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.8rem', fontWeight: 'bold' }}>Google Cloud (User)</td>
                      <td style={{ padding: '0.8rem' }}>WIF Pool</td>
                      <td style={{ padding: '0.8rem', color: '#4ade80' }}>Workload Identity User</td>
                      <td style={{ padding: '0.8rem', opacity: 0.8 }}>Allows swapping external credentials</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.8rem', fontWeight: 'bold' }}>Google Cloud (User)</td>
                      <td style={{ padding: '0.8rem' }}>Vertex AI Search</td>
                      <td style={{ padding: '0.8rem', color: '#4ade80' }}>discoveryengine.viewer</td>
                      <td style={{ padding: '0.8rem', opacity: 0.8 }}>View permission over Search indices</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.8rem', fontWeight: 'bold' }}>Google Cloud (SA)</td>
                      <td style={{ padding: '0.8rem' }}>Backend Context</td>
                      <td style={{ padding: '0.8rem', color: '#4ade80' }}>discoveryengine.admin</td>
                      <td style={{ padding: '0.8rem', opacity: 0.8 }}>Elevated background read config bypasses CORS</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      )}
      <ChatOverlay logs={logs} />
    </div>
  );
}
