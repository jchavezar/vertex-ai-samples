import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, RefreshCw, Key, Sparkles, ChevronRight, Terminal, ExternalLink, Play, Code, CheckCircle2, AlertTriangle } from 'lucide-react';
import { getWifLoginUrl, exchangeForGoogleToken } from './api/auth';
import { executeStreamAssist } from './api/search';
import ChatOverlay from './components/ChatOverlay';

export default function App() {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
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
      title: "Authenticated StreamAssist",
      icon: "Sparkles",
      description: "Armed with the Google Token, you can now safely query StreamAssist. The token authorizes access to the Discovery Engine datastores.",
      code: `// api/search.js\nexport const executeStreamAssist = async (token, query) => {\n  const headers = { Authorization: \`Bearer \${token}\` };\n  const resp = await fetch('/google-api/...:streamAssist', {\n    method: 'POST', headers, body: JSON.stringify(payload)\n  });\n  // Parse SSE stream...\n};`
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
    addLog('call', 'executeStreamAssist(googleToken, query)', { query });

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

                    {streamAnswer && (
                      <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <h4 style={{ fontSize: '0.8rem', color: '#00f2fe', marginBottom: '0.5rem' }}>ANSWER STREAM</h4>
                        <p style={{ lineHeight: '1.6', color: '#e2e8f0' }}>{streamAnswer}</p>
                      </div>
                    )}

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
      <ChatOverlay logs={logs} />
    </div>
  );
}
