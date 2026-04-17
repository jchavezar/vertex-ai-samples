import { useState, useCallback, useEffect, useRef } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';

interface Source {
  title: string;
  url: string;
  file_type: string;
  entity_type: string;
}

interface SearchResult {
  answer: string;
  sources: Source[];
  session_token?: string;
  skipped_reasons?: string[];
  raw_response?: string;
  request_payload?: any;
  error?: string;
  _trace?: any[];
}

function ResultPanel({ label, color, result, loading }: {
  label: string; color: string; result: SearchResult | null; loading: boolean;
}) {
  const [showRequest, setShowRequest] = useState(false);
  const [showResponse, setShowResponse] = useState(false);
  const [showTrace, setShowTrace] = useState(false);

  if (loading) {
    return (
      <div className={`result-panel panel-${color}`}>
        <div className="panel-header"><h3>{label}</h3></div>
        <div className="loading-indicator"><div className="dot-pulse" /><span>Calling {label}...</span></div>
      </div>
    );
  }

  if (!result) return null;

  const apiTrace = result._trace?.find((t: any) => t.stage === 'streamAssist' || t.stage === 'streamAnswer');

  return (
    <div className={`result-panel panel-${color}`}>
      <div className="panel-header">
        <h3>{label}</h3>
        <span className={`badge ${result.error ? 'badge-red' : result.skipped_reasons?.length ? 'badge-yellow' : 'badge-green'}`}>
          {result.error ? 'ERROR' : result.skipped_reasons?.length ? 'SKIPPED' : 'OK'}
        </span>
        {apiTrace?.duration_ms != null && <span className="trace-duration">{apiTrace.duration_ms}ms</span>}
      </div>

      {result.skipped_reasons && result.skipped_reasons.length > 0 && (
        <div className="skipped-reasons">
          {result.skipped_reasons.map((r, i) => (
            <span key={i} className="badge badge-yellow">{r}</span>
          ))}
        </div>
      )}

      <div className="answer-text">
        {result.error || result.answer || 'No answer generated.'}
      </div>

      {result.sources && result.sources.length > 0 && (
        <div className="sources">
          <h4>Sources ({result.sources.length})</h4>
          {result.sources.map((src, i) => (
            <a key={i} href={src.url} target="_blank" rel="noopener noreferrer" className="source-link">
              {src.title} {src.file_type && <span className="source-type">{src.file_type}</span>}
            </a>
          ))}
        </div>
      )}

      <div className="panel-inspector">
        <div className="inspector-toggle" onClick={() => setShowRequest(!showRequest)}>
          {showRequest ? '\u25BC' : '\u25B6'} Request
        </div>
        {showRequest && result.request_payload && (
          <pre className="json-block">{JSON.stringify(result.request_payload, null, 2)}</pre>
        )}

        <div className="inspector-toggle" onClick={() => setShowResponse(!showResponse)}>
          {showResponse ? '\u25BC' : '\u25B6'} Response
        </div>
        {showResponse && result.raw_response && (
          <pre className="json-block">{(() => {
            try { return JSON.stringify(JSON.parse(result.raw_response), null, 2); }
            catch { return result.raw_response; }
          })()}</pre>
        )}

        <div className="inspector-toggle" onClick={() => setShowTrace(!showTrace)}>
          {showTrace ? '\u25BC' : '\u25B6'} Trace
        </div>
        {showTrace && result._trace && (
          <div className="trace-list">
            {result._trace.map((t: any, i: number) => (
              <div key={i} className={`trace-entry ${t.status < 300 ? 'trace-ok' : 'trace-err'}`}>
                <span className="trace-stage">{t.stage}</span>
                <span className="trace-status">{t.status}</span>
                {t.duration_ms != null && <span className="trace-duration">{t.duration_ms}ms</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';
  const spKey = `sp_connected_${username}`;

  const [spConnected, setSpConnected] = useState(false);
  const [connectionChecked, setConnectionChecked] = useState(false);
  const [authInProgress, setAuthInProgress] = useState(false);
  const [authStatus, setAuthStatus] = useState('');

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionTokenAssist, setSessionTokenAssist] = useState<string | null>(null);
  const [sessionTokenAnswer, setSessionTokenAnswer] = useState<string | null>(null);
  const [resultAssist, setResultAssist] = useState<SearchResult | null>(null);
  const [resultAnswer, setResultAnswer] = useState<SearchResult | null>(null);

  const [enableAssist, setEnableAssist] = useState(true);
  const [enableAnswer, setEnableAnswer] = useState(true);
  const [includeDataStoreSpecs, setIncludeDataStoreSpecs] = useState(true);
  const [ignoreNonAnswerSeeking, setIgnoreNonAnswerSeeking] = useState(true);
  const [ignoreAdversarial, setIgnoreAdversarial] = useState(true);
  const [ignoreLowRelevant, setIgnoreLowRelevant] = useState(true);

  const consentPopupRef = useRef<Window | null>(null);

  const getToken = useCallback(async (silent = true): Promise<string | null> => {
    if (!accounts[0]) return null;
    try {
      const resp = await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
      return resp.idToken;
    } catch {
      if (silent) return null;
      try {
        return (await instance.acquireTokenPopup(loginRequest)).idToken;
      } catch {
        return null;
      }
    }
  }, [instance, accounts]);

  const handleLogin = async () => {
    try { await instance.loginPopup(loginRequest); }
    catch (err: any) { console.error('Login failed:', err.message); }
  };

  useEffect(() => {
    const handler = async (event: MessageEvent) => {
      if (event.data?.fullRedirectUrl) {
        try {
          const token = await getToken();
          const resp = await fetch('/api/oauth/exchange', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(token ? { 'X-Entra-Id-Token': token } : {}) },
            body: JSON.stringify({ fullRedirectUrl: event.data.fullRedirectUrl }),
          });
          const data = await resp.json();
          if (data.success) { setSpConnected(true); localStorage.setItem(spKey, '1'); }
          else setAuthStatus(`Authorization failed: ${data.error || 'Unknown'}`);
        } catch (err: any) { setAuthStatus(`Exchange failed: ${err.message}`); }
        setAuthInProgress(false);
        return;
      }
      if (event.data?.type === 'sharepoint-oauth-callback') {
        if (event.data.success) { setSpConnected(true); localStorage.setItem(spKey, '1'); }
        else setAuthStatus(`Authorization failed: ${event.data.error || 'Unknown'}`);
        setAuthInProgress(false);
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [spKey, getToken]);

  useEffect(() => {
    if (!isAuthenticated) return;
    (async () => {
      const token = await getToken();
      if (!token) { setConnectionChecked(true); return; }
      try {
        const resp = await fetch('/api/sharepoint/check-connection', { headers: { 'X-Entra-Id-Token': token } });
        const data = await resp.json();
        setSpConnected(data.connected);
        data.connected ? localStorage.setItem(spKey, '1') : localStorage.removeItem(spKey);
      } catch { setSpConnected(false); localStorage.removeItem(spKey); }
      finally { setConnectionChecked(true); }
    })();
  }, [isAuthenticated, getToken, spKey]);

  useEffect(() => {
    if (!authInProgress || !consentPopupRef.current) return;
    const interval = setInterval(async () => {
      const popup = consentPopupRef.current;
      if (!popup || popup.closed) {
        clearInterval(interval);
        consentPopupRef.current = null;
        await new Promise(r => setTimeout(r, 1500));
        const token = await getToken();
        if (token) {
          const resp = await fetch('/api/sharepoint/check-connection', { headers: { 'X-Entra-Id-Token': token } });
          const data = await resp.json();
          if (data.connected) { setSpConnected(true); localStorage.setItem(spKey, '1'); }
        }
        setAuthInProgress(false);
        setAuthStatus('');
      }
    }, 500);
    return () => clearInterval(interval);
  }, [authInProgress, getToken, spKey]);

  const handleConsent = async () => {
    setAuthInProgress(true);
    setAuthStatus('Opening consent...');
    const popup = window.open('about:blank', 'sp_consent', 'width=600,height=700,left=200,top=100');
    consentPopupRef.current = popup;
    if (!popup) { setAuthStatus('Popup blocked.'); setAuthInProgress(false); return; }
    try {
      const token = await getToken();
      const hint = username ? `?login_hint=${encodeURIComponent(username)}` : '';
      const resp = await fetch(`/api/sharepoint/auth-url${hint}`, { headers: token ? { 'X-Entra-Id-Token': token } : {} });
      const data = await resp.json();
      popup.location.href = data.auth_url;
      setAuthStatus('Complete consent in the popup...');
    } catch (err: any) { popup.close(); setAuthStatus(`Failed: ${err.message}`); setAuthInProgress(false); }
  };

  const fireSearch = async (token: string, mode: string, sessionToken: string | null): Promise<SearchResult> => {
    const resp = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': token },
      body: JSON.stringify({
        query: query.trim(), mode,
        include_data_store_specs: includeDataStoreSpecs,
        ignore_non_answer_seeking: ignoreNonAnswerSeeking,
        ignore_adversarial: ignoreAdversarial,
        ignore_low_relevant: ignoreLowRelevant,
        session_token: sessionToken,
      }),
    });
    return resp.json();
  };

  const handleSearch = async () => {
    const q = query.trim();
    if (!q || loading || (!enableAssist && !enableAnswer)) return;
    const token = await getToken();
    if (!token) return;

    setLoading(true);
    if (enableAssist) setResultAssist(null);
    if (enableAnswer) setResultAnswer(null);

    try {
      const promises: Promise<void>[] = [];
      if (enableAssist) {
        promises.push(
          fireSearch(token, 'stream_assist', sessionTokenAssist).then(data => {
            setResultAssist(data);
            if (data.session_token) setSessionTokenAssist(data.session_token);
          }).catch(err => setResultAssist({ answer: '', sources: [], error: err.message }))
        );
      }
      if (enableAnswer) {
        promises.push(
          fireSearch(token, 'stream_answer', sessionTokenAnswer).then(data => {
            setResultAnswer(data);
            if (data.session_token) setSessionTokenAnswer(data.session_token);
          }).catch(err => setResultAnswer({ answer: '', sources: [], error: err.message }))
        );
      }
      await Promise.all(promises);
    } finally { setLoading(false); }
  };

  return (
    <div className="lab">
      <header>
        <div className="header-left">
          <h1>StreamAnswer Lab</h1>
          <span className="subtitle">streamAnswer vs streamAssist — side-by-side troubleshooting</span>
        </div>
        <div className="header-right">
          {isAuthenticated ? (
            <>
              <span className="user-email">{username}</span>
              {spConnected && <span className="badge badge-green">SP Connected</span>}
              <button className="btn-small" onClick={() => instance.logoutPopup()}>Logout</button>
            </>
          ) : (
            <button className="btn-primary" onClick={handleLogin}>Sign in with Microsoft</button>
          )}
        </div>
      </header>

      {!isAuthenticated && (
        <section className="card center-card">
          <h2>Sign in to get started</h2>
          <p>Sign in with your Microsoft account to test StreamAnswer and StreamAssist APIs.</p>
          <button className="btn-primary" onClick={handleLogin}>Sign in with Microsoft</button>
        </section>
      )}

      {isAuthenticated && !connectionChecked && (
        <div className="center-card"><div className="dot-pulse" /><p>Checking SharePoint connection...</p></div>
      )}

      {isAuthenticated && connectionChecked && (
        <>
          {!spConnected && (
            <div className="banner banner-warning">
              <span>SharePoint requires authorization to access your documents.</span>
              <button className="btn-primary" onClick={handleConsent} disabled={authInProgress}>
                {authInProgress ? 'Authorizing...' : 'Connect SharePoint'}
              </button>
              {authStatus && <div className="banner-status">{authStatus}</div>}
            </div>
          )}

          <div className="config-panel">
            <div className="config-row">
              <label className="config-label">APIs</label>
              <div className="checkbox-group">
                <label className={`checkbox-api ${enableAssist ? 'checked-blue' : ''}`}>
                  <input type="checkbox" checked={enableAssist} onChange={e => setEnableAssist(e.target.checked)} />
                  <span>streamAssist</span>
                </label>
                <label className={`checkbox-api ${enableAnswer ? 'checked-purple' : ''}`}>
                  <input type="checkbox" checked={enableAnswer} onChange={e => setEnableAnswer(e.target.checked)} />
                  <span>streamAnswer</span>
                </label>
              </div>
            </div>
            <div className="config-row">
              <label className="config-label">Options</label>
              <div className="checkbox-group">
                <label className="checkbox">
                  <input type="checkbox" checked={includeDataStoreSpecs} onChange={e => setIncludeDataStoreSpecs(e.target.checked)} />
                  <span>dataStoreSpecs</span>
                </label>
                <label className="checkbox" style={{ opacity: enableAnswer ? 1 : 0.4 }}>
                  <input type="checkbox" checked={ignoreNonAnswerSeeking} onChange={e => setIgnoreNonAnswerSeeking(e.target.checked)} disabled={!enableAnswer} />
                  <span>ignoreNonAnswerSeeking</span>
                </label>
                <label className="checkbox" style={{ opacity: enableAnswer ? 1 : 0.4 }}>
                  <input type="checkbox" checked={ignoreAdversarial} onChange={e => setIgnoreAdversarial(e.target.checked)} disabled={!enableAnswer} />
                  <span>ignoreAdversarial</span>
                </label>
                <label className="checkbox" style={{ opacity: enableAnswer ? 1 : 0.4 }}>
                  <input type="checkbox" checked={ignoreLowRelevant} onChange={e => setIgnoreLowRelevant(e.target.checked)} disabled={!enableAnswer} />
                  <span>ignoreLowRelevant</span>
                </label>
              </div>
            </div>
            <div className="config-row config-endpoints">
              {enableAssist && <span className="endpoint-display endpoint-blue">POST .../assistants/default_assistant:streamAssist</span>}
              {enableAnswer && <span className="endpoint-display endpoint-purple">POST .../servingConfigs/default_search:streamAnswer</span>}
            </div>
          </div>

          <form className="search-bar" onSubmit={e => { e.preventDefault(); handleSearch(); }}>
            <input
              type="text" value={query} onChange={e => setQuery(e.target.value)}
              placeholder="Ask about your SharePoint documents..."
              disabled={loading || !spConnected}
            />
            <button type="submit" className="btn-primary" disabled={loading || !query.trim() || !spConnected || (!enableAssist && !enableAnswer)}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>

          <div className={`results-grid ${enableAssist && enableAnswer ? 'dual' : 'single'}`}>
            {enableAssist && (
              <ResultPanel label="streamAssist" color="blue" result={resultAssist} loading={loading && !resultAssist} />
            )}
            {enableAnswer && (
              <ResultPanel label="streamAnswer" color="purple" result={resultAnswer} loading={loading && !resultAnswer} />
            )}
          </div>
        </>
      )}
    </div>
  );
}
