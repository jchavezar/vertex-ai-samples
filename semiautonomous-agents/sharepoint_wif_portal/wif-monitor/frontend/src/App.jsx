import { useState, useEffect, useRef } from 'react'
import Markdown from 'react-markdown'
import './App.css'

const API = 'http://localhost:8002'

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function shortenResource(r) {
  if (!r) return ''
  return r.replace(/projects\/\d+\/locations\/global\//, '').replace(/collections\//, '').replace(/default_collection\//, '')
}

// ===== Detail Panel =====
function DetailPanel({ entry, onClose, onExplain, explanation, explaining }) {
  if (!entry) return null
  return (
    <>
      <div className="detail-overlay" onClick={onClose} />
      <div className="detail-panel">
        <div className="detail-header">
          <h3>{entry.methodLabel}</h3>
          <button className="detail-close" onClick={onClose}>x</button>
        </div>
        <div className="detail-body">
          <div className="detail-section">
            <h4>Summary</h4>
            <div className="detail-json">
              <div><strong>Method:</strong> {entry.method}</div>
              <div><strong>Principal:</strong> {entry.principal}</div>
              <div><strong>Permission:</strong> {entry.permission}</div>
              <div><strong>Granted:</strong> {entry.granted ? 'Yes' : 'No'}</div>
              <div><strong>Resource:</strong> {entry.resource}</div>
              <div><strong>Caller IP:</strong> {entry.callerIp}</div>
              <div><strong>User Agent:</strong> {entry.userAgent}</div>
              <div><strong>Timestamp:</strong> {entry.timestamp}</div>
            </div>
          </div>

          <div className="detail-section">
            <h4>Request</h4>
            <pre className="detail-json">{JSON.stringify(entry.request, null, 2)}</pre>
          </div>

          <div className="detail-section">
            <h4>Response</h4>
            <pre className="detail-json">{JSON.stringify(entry.response, null, 2)}</pre>
          </div>

          <div className="detail-section">
            <h4>Gemini Explanation</h4>
            {explaining ? (
              <div className="loading"><div className="spinner" /><div>Analyzing...</div></div>
            ) : explanation ? (
              <div className="explanation-box"><Markdown>{explanation}</Markdown></div>
            ) : (
              <button className="explain-btn" onClick={onExplain}>Explain with Gemini</button>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

// ===== Dashboard =====
function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [minutes, setMinutes] = useState(60)
  const [selected, setSelected] = useState(null)
  const [explanation, setExplanation] = useState('')
  const [explaining, setExplaining] = useState(false)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/logs?minutes=${minutes}`)
      setData(await res.json())
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => { fetchLogs() }, [minutes])

  useEffect(() => {
    const interval = setInterval(fetchLogs, 30000)
    return () => clearInterval(interval)
  }, [minutes])

  const handleExplain = async () => {
    setExplaining(true)
    try {
      const res = await fetch(`${API}/api/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_entry: selected })
      })
      const d = await res.json()
      setExplanation(d.explanation)
    } catch (e) {
      setExplanation('Error: ' + e.message)
    }
    setExplaining(false)
  }

  if (loading && !data) return <div className="loading"><div className="spinner" /><div>Loading audit logs...</div></div>

  const methodCounts = {}
  data?.entries?.forEach(e => {
    methodCounts[e.methodLabel] = (methodCounts[e.methodLabel] || 0) + 1
  })

  return (
    <div>
      <div className="dashboard-controls">
        <select value={minutes} onChange={e => setMinutes(Number(e.target.value))}>
          <option value={15}>Last 15 min</option>
          <option value={30}>Last 30 min</option>
          <option value={60}>Last 1 hour</option>
          <option value={120}>Last 2 hours</option>
          <option value={360}>Last 6 hours</option>
          <option value={1440}>Last 24 hours</option>
        </select>
        <button onClick={fetchLogs}>Refresh</button>
        <span style={{ color: '#8b949e', fontSize: 12 }}>{data?.total || 0} events, {data?.chains?.length || 0} chains</span>
      </div>

      <div className="stats-bar">
        {Object.entries(methodCounts).map(([method, count]) => (
          <div className="stat-card" key={method}>
            <div className="label">{method}</div>
            <div className="value">{count}</div>
          </div>
        ))}
      </div>

      {data?.chains?.length === 0 && (
        <div className="empty-state">
          <div className="icon">--</div>
          <div>No auth events found in the last {minutes} minutes</div>
        </div>
      )}

      {data?.chains?.map((chain, i) => (
        <div className="chain-card" key={i}>
          <div className="chain-header">
            <div>
              <div className="chain-principal">{chain.principalHash.slice(0, 20)}...</div>
              <div className="chain-methods">
                {chain.methods.map(m => {
                  const color = { 'STS Exchange': 'blue', StreamAssist: 'purple', AcquireAccessToken: 'orange', CreateSession: 'green' }[m] || 'gray'
                  return <span className={`method-badge ${color}`} key={m}>{m}</span>
                })}
              </div>
            </div>
            <div className="chain-time">{formatTime(chain.startTime)}</div>
          </div>
          <div className="chain-events">
            {chain.events.map((evt, j) => (
              <div className="event-row" key={j} onClick={() => { setSelected(evt); setExplanation('') }}>
                <div className="event-connector">
                  <div className={`event-dot ${evt.color}`} />
                  {j < chain.events.length - 1 && <div className={`event-line ${evt.color}`} />}
                </div>
                <div className="event-details">
                  <div className="event-method">{evt.methodLabel}</div>
                  <div className="event-resource">{shortenResource(evt.resource)}</div>
                </div>
                <div className="event-status">
                  {evt.granted !== null && (
                    <span className={evt.granted ? 'granted' : 'denied'}>{evt.granted ? 'GRANTED' : 'DENIED'}</span>
                  )}
                </div>
                <div className="event-time">{formatTime(evt.timestamp)}</div>
              </div>
            ))}
          </div>
        </div>
      ))}

      <DetailPanel
        entry={selected}
        onClose={() => { setSelected(null); setExplanation('') }}
        onExplain={handleExplain}
        explanation={explanation}
        explaining={explaining}
      />
    </div>
  )
}

// ===== Mapping Panel =====
function MappingPanel({ mapping, consentGrants }) {
  if (!mapping) return null
  const { wif, connector, proof, microsoft_integration, all_sharepoint_apps } = mapping
  const discovered = connector?.discovered_client_id
  const grants = consentGrants?.oauth2PermissionGrants || []
  const aclProof = consentGrants?.aclProof
  return (
    <div className="chain-card" style={{ marginBottom: 24 }}>
      <div className="chain-header" style={{ cursor: 'default' }}>
        <div>
          <div className="chain-principal" style={{ fontSize: 15 }}>WIF ↔ Connector Identity Mapping</div>
          <div style={{ fontSize: 12, color: '#8b949e', marginTop: 4 }}>
            Shared Tenant: <span style={{ color: proof.shared_tenant ? '#3fb950' : '#f85149' }}>{proof.tenant_id}</span>
            {microsoft_integration && <span style={{ marginLeft: 12, color: '#3fb950' }}>Microsoft Graph: Connected</span>}
          </div>
        </div>
      </div>
      <div style={{ padding: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ background: '#0d1117', border: '1px solid rgba(88,166,255,0.3)', borderRadius: 8, padding: 16 }}>
          <h4 style={{ color: '#58a6ff', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>WIF Portal App</h4>
          <div style={{ fontSize: 13, lineHeight: 1.8 }}>
            <div><span style={{ color: '#8b949e' }}>Client ID:</span> <code style={{ color: '#f0f6fc', background: '#21262d', padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>{proof.wif_client_id}</code></div>
            <div><span style={{ color: '#8b949e' }}>Pool:</span> <span style={{ color: '#c9d1d9' }}>{wif.pool}</span></div>
            <div><span style={{ color: '#8b949e' }}>Provider:</span> <span style={{ color: '#c9d1d9' }}>entra-provider</span></div>
            <div><span style={{ color: '#8b949e' }}>Audience:</span> <code style={{ color: '#bc8cff', background: '#21262d', padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>api://{proof.wif_client_id}</code></div>
            <div><span style={{ color: '#8b949e' }}>Issuer:</span> <span style={{ color: '#c9d1d9', fontSize: 11 }}>{wif.issuer}</span></div>
            <div><span style={{ color: '#8b949e' }}>Maps:</span> <span style={{ color: '#c9d1d9' }}>assertion.sub → google.subject</span></div>
          </div>
        </div>
        <div style={{ background: '#0d1117', border: discovered ? '2px solid #f0883e' : '1px solid rgba(240,136,62,0.3)', borderRadius: 8, padding: 16 }}>
          <h4 style={{ color: '#f0883e', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            SharePoint Connector App
            {discovered && <span style={{ fontSize: 10, marginLeft: 8, color: '#3fb950', textTransform: 'none' }}>DISCOVERED</span>}
          </h4>
          <div style={{ fontSize: 13, lineHeight: 1.8 }}>
            <div>
              <span style={{ color: '#8b949e' }}>Client ID:</span>{' '}
              {discovered
                ? <code style={{ color: '#f0883e', background: '#21262d', padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>{discovered}</code>
                : <span style={{ color: '#8b949e', fontSize: 12, fontStyle: 'italic' }}>Hidden by GCP (enable Microsoft Graph to discover)</span>
              }
            </div>
            {connector?.discovered_display_name && (
              <div><span style={{ color: '#8b949e' }}>Display Name:</span> <span style={{ color: '#f0f6fc', fontWeight: 600 }}>{connector.discovered_display_name}</span></div>
            )}
            <div><span style={{ color: '#8b949e' }}>Connector:</span> <span style={{ color: '#c9d1d9' }}>{connector.name}</span></div>
            <div><span style={{ color: '#8b949e' }}>Type:</span> <span style={{ color: '#c9d1d9' }}>{connector.type}</span></div>
            <div><span style={{ color: '#8b949e' }}>SharePoint:</span> <span style={{ color: '#c9d1d9' }}>{connector.instance_uri}</span></div>
            <div><span style={{ color: '#8b949e' }}>Auth:</span> <span style={{ color: '#c9d1d9' }}>{connector.auth_type} (delegated)</span></div>
            <div><span style={{ color: '#8b949e' }}>Modes:</span> <span style={{ color: '#c9d1d9' }}>{connector.connectorModes?.join(', ')}</span></div>
          </div>
        </div>
      </div>

      {/* All SharePoint Apps from Entra ID */}
      {all_sharepoint_apps?.length > 0 && (
        <div style={{ padding: '0 20px 20px' }}>
          <div style={{ background: '#0d1117', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
            <h4 style={{ color: '#bc8cff', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              All Entra ID Apps with SharePoint Permissions ({all_sharepoint_apps.length})
            </h4>
            <div style={{ display: 'grid', gap: 8 }}>
              {all_sharepoint_apps.map((app, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 14px', borderRadius: 6,
                  background: app.appId === discovered ? 'rgba(240,136,62,0.1)' : 'rgba(139,148,158,0.05)',
                  border: app.appId === discovered ? '1px solid rgba(240,136,62,0.3)' : '1px solid #21262d',
                }}>
                  <div>
                    <div style={{ fontSize: 13, color: app.isPortalApp ? '#58a6ff' : app.appId === discovered ? '#f0883e' : '#c9d1d9', fontWeight: 600 }}>
                      {app.displayName}
                      {app.isPortalApp && <span style={{ fontSize: 10, marginLeft: 8, color: '#58a6ff' }}>PORTAL APP</span>}
                      {app.appId === discovered && <span style={{ fontSize: 10, marginLeft: 8, color: '#f0883e' }}>CONNECTOR</span>}
                    </div>
                    <code style={{ fontSize: 11, color: '#8b949e' }}>{app.appId}</code>
                  </div>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    {app.sharePointPermissions?.map((p, j) => (
                      <span key={j} style={{
                        fontSize: 10, padding: '2px 6px', borderRadius: 4,
                        background: p.type === 'Delegated' ? 'rgba(63,185,80,0.1)' : 'rgba(240,136,62,0.1)',
                        color: p.type === 'Delegated' ? '#3fb950' : '#f0883e',
                        border: `1px solid ${p.type === 'Delegated' ? 'rgba(63,185,80,0.2)' : 'rgba(240,136,62,0.2)'}`,
                      }}>{p.name}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* OAuth2 Consent Grants — ACL Proof */}
      {grants.length > 0 && (
        <div style={{ padding: '0 20px 20px' }}>
          <div style={{ background: '#0d1117', border: '1px solid rgba(63,185,80,0.3)', borderRadius: 8, padding: 16 }}>
            <h4 style={{ color: '#3fb950', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              OAuth2 Delegated Consent Grants — ACL Proof
              {aclProof?.isAdminConsent && <span style={{ fontSize: 10, marginLeft: 8, color: '#f0883e', textTransform: 'none' }}>ADMIN CONSENT</span>}
            </h4>
            <div style={{ display: 'grid', gap: 12 }}>
              {grants.map((grant, i) => (
                <div key={i} style={{
                  padding: '12px 16px', borderRadius: 6,
                  background: 'rgba(63,185,80,0.05)',
                  border: '1px solid rgba(63,185,80,0.15)',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: '#f0f6fc' }}>{grant.resourceName}</span>
                    <span style={{
                      fontSize: 10, padding: '2px 8px', borderRadius: 4,
                      background: grant.consentType === 'AllPrincipals' ? 'rgba(240,136,62,0.15)' : 'rgba(88,166,255,0.15)',
                      color: grant.consentType === 'AllPrincipals' ? '#f0883e' : '#58a6ff',
                      border: `1px solid ${grant.consentType === 'AllPrincipals' ? 'rgba(240,136,62,0.3)' : 'rgba(88,166,255,0.3)'}`,
                    }}>
                      {grant.consentType === 'AllPrincipals' ? 'All Users (Admin Consent)' : grant.consentType}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {grant.scope.split(' ').filter(Boolean).map((scope, j) => (
                      <code key={j} style={{
                        fontSize: 11, padding: '3px 8px', borderRadius: 4,
                        background: '#21262d', color: '#3fb950',
                        border: '1px solid rgba(63,185,80,0.2)',
                      }}>{scope}</code>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            {aclProof && (
              <div style={{
                marginTop: 12, padding: '10px 14px',
                background: 'rgba(63,185,80,0.08)', border: '1px solid rgba(63,185,80,0.2)',
                borderRadius: 6, fontSize: 13, color: '#3fb950', lineHeight: 1.6,
              }}>
                <strong>ACL Enforcement Proof:</strong> {aclProof.explanation}
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{ padding: '0 20px 20px' }}>
        <div style={{ background: '#0d1117', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
          <h4 style={{ color: '#3fb950', fontSize: 13, marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>How the Mapping Works</h4>
          <div style={{ fontSize: 13, lineHeight: 1.8 }}>
            {proof.flow.map((step, i) => (
              <div key={i} style={{ color: '#c9d1d9', borderLeft: '2px solid #30363d', marginBottom: 4, paddingTop: 2, paddingBottom: 2, paddingLeft: 12 }}>{step}</div>
            ))}
          </div>
          <div style={{ marginTop: 12, padding: '10px 14px', background: 'rgba(63,185,80,0.08)', border: '1px solid rgba(63,185,80,0.2)', borderRadius: 6, fontSize: 13, color: '#3fb950' }}>
            Proof: The same <code style={{ background: '#21262d', padding: '2px 6px', borderRadius: 4 }}>principalSubject</code> appears in both <span style={{ color: '#bc8cff' }}>StreamAssist</span> and <span style={{ color: '#f0883e' }}>AcquireAccessToken</span> logs — proving Discovery Engine passes the WIF user identity to the Connector for ACL enforcement.
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== Chain Explorer =====
function ChainExplorer() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [principals, setPrincipals] = useState([])
  const [selectedPrincipal, setSelectedPrincipal] = useState('')
  const [chainData, setChainData] = useState(null)
  const [explanation, setExplanation] = useState('')
  const [explaining, setExplaining] = useState(false)
  const [mapping, setMapping] = useState(null)
  const [consentGrants, setConsentGrants] = useState(null)
  const [selected, setSelected] = useState(null)
  const [selectedExplanation, setSelectedExplanation] = useState('')
  const [selectedExplaining, setSelectedExplaining] = useState(false)

  useEffect(() => {
    fetch(`${API}/api/mapping`).then(r => r.json()).then(setMapping).catch(() => {})
    fetch(`${API}/api/microsoft/consent-grants`).then(r => r.json()).then(setConsentGrants).catch(() => {})
    fetch(`${API}/api/logs?minutes=1440`)
      .then(r => r.json())
      .then(d => {
        setPrincipals(d.principals || [])
        setData(d)
        setLoading(false)
        if (d.principals?.length > 0) setSelectedPrincipal(d.principals[0])
      })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedPrincipal) return
    fetch(`${API}/api/chain/${selectedPrincipal}?minutes=1440`)
      .then(r => r.json())
      .then(d => setChainData(d))
  }, [selectedPrincipal])

  const handleExplainChain = async (chain) => {
    setExplaining(true)
    try {
      const res = await fetch(`${API}/api/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chain })
      })
      const d = await res.json()
      setExplanation(d.explanation)
    } catch (e) {
      setExplanation('Error: ' + e.message)
    }
    setExplaining(false)
  }

  const handleExplainEntry = async () => {
    setSelectedExplaining(true)
    try {
      const res = await fetch(`${API}/api/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_entry: selected })
      })
      const d = await res.json()
      setSelectedExplanation(d.explanation)
    } catch (e) {
      setSelectedExplanation('Error: ' + e.message)
    }
    setSelectedExplaining(false)
  }

  if (loading) return <div className="loading"><div className="spinner" /><div>Loading...</div></div>

  const allChains = chainData?.chains || []
  // Aggregate counts across ALL chains for the flow diagram
  const methodGroups = {}
  allChains.forEach(c => c.events?.forEach(e => {
    methodGroups[e.methodLabel] = (methodGroups[e.methodLabel] || 0) + 1
  }))
  // Find the most interesting chain (one with the most distinct methods)
  const bestChain = [...allChains].sort((a, b) => b.methods.length - a.methods.length)[0]

  const flowNodes = [
    { label: 'STS Exchange', desc: 'WIF Token Exchange', color: 'blue', key: 'STS Exchange' },
    { label: 'CreateSession', desc: 'Session Init', color: 'green', key: 'CreateSession' },
    { label: 'StreamAssist', desc: 'User Query', color: 'purple', key: 'StreamAssist' },
    { label: 'AcquireAccessToken', desc: 'Connector Auth', color: 'orange', key: 'AcquireAccessToken' },
  ]

  return (
    <div>
      <div className="chain-explorer-controls">
        <select value={selectedPrincipal} onChange={e => setSelectedPrincipal(e.target.value)}>
          {principals.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      <MappingPanel mapping={mapping} consentGrants={consentGrants} />

      {allChains.length > 0 && (
        <>
          <div className="flow-diagram">
            {flowNodes.map((node, i) => (
              <div key={node.key} style={{ display: 'flex', alignItems: 'center' }}>
                <div className={`flow-node ${node.color}`}>
                  <div className="node-label">{node.label}</div>
                  <div className="node-count">{methodGroups[node.key] || 0}</div>
                  <div className="node-desc">{node.desc}</div>
                </div>
                {i < flowNodes.length - 1 && <div className="flow-arrow">--&gt;</div>}
              </div>
            ))}
          </div>

          {bestChain && bestChain.methods.length > 1 && (
            <>
              <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ color: '#f0f6fc', fontSize: 14, fontWeight: 600 }}>Key Chain @ {formatTime(bestChain.startTime)}</span>
                <button className="explain-btn" onClick={() => handleExplainChain(bestChain)} style={{ padding: '8px 16px', fontSize: 13 }}>
                  Explain this chain with Gemini
                </button>
              </div>

              {explaining && <div className="loading"><div className="spinner" /><div>Gemini analyzing chain...</div></div>}
              {explanation && <div className="explanation-box" style={{ marginBottom: 20 }}><Markdown>{explanation}</Markdown></div>}

              <div className="chain-card" style={{ marginBottom: 24 }}>
                <div className="chain-header">
                  <div>
                    <div className="chain-principal">Primary Auth Chain</div>
                    <div className="chain-methods">
                      {bestChain.methods.map(m => {
                        const color = { 'STS Exchange': 'blue', StreamAssist: 'purple', AcquireAccessToken: 'orange', CreateSession: 'green' }[m] || 'gray'
                        return <span className={`method-badge ${color}`} key={m}>{m}</span>
                      })}
                    </div>
                  </div>
                  <div className="chain-time">{formatTime(bestChain.startTime)}</div>
                </div>
                <div className="chain-events">
                  {bestChain.events.map((evt, j) => (
                    <div className="event-row" key={j} onClick={() => { setSelected(evt); setSelectedExplanation('') }}>
                      <div className="event-connector">
                        <div className={`event-dot ${evt.color}`} />
                        {j < bestChain.events.length - 1 && <div className={`event-line ${evt.color}`} />}
                      </div>
                      <div className="event-details">
                        <div className="event-method">{evt.methodLabel}</div>
                        <div className="event-resource">{shortenResource(evt.resource)}</div>
                        <div style={{ fontSize: 11, color: '#8b949e', marginTop: 2 }}>
                          {evt.permission} {evt.granted !== null && `| ${evt.granted ? 'GRANTED' : 'DENIED'}`}
                        </div>
                      </div>
                      <div className="event-time">{formatTime(evt.timestamp)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          <h3 style={{ color: '#f0f6fc', fontSize: 14, marginBottom: 12 }}>All Chains ({allChains.length})</h3>
          {allChains.map((chain, i) => (
            <div className="chain-card" key={i}>
              <div className="chain-header">
                <div>
                  <div className="chain-methods">
                    {chain.methods.map(m => {
                      const color = { 'STS Exchange': 'blue', StreamAssist: 'purple', AcquireAccessToken: 'orange', CreateSession: 'green' }[m] || 'gray'
                      return <span className={`method-badge ${color}`} key={m}>{m}</span>
                    })}
                  </div>
                </div>
                <div className="chain-time">{formatTime(chain.startTime)} ({chain.events.length} events)</div>
              </div>
              <div className="chain-events">
                {chain.events.map((evt, j) => (
                  <div className="event-row" key={j} onClick={() => { setSelected(evt); setSelectedExplanation('') }}>
                    <div className="event-connector">
                      <div className={`event-dot ${evt.color}`} />
                      {j < chain.events.length - 1 && <div className={`event-line ${evt.color}`} />}
                    </div>
                    <div className="event-details">
                      <div className="event-method">{evt.methodLabel}</div>
                      <div className="event-resource">{shortenResource(evt.resource)}</div>
                    </div>
                    <div className="event-status">
                      {evt.granted !== null && (
                        <span className={evt.granted ? 'granted' : 'denied'}>{evt.granted ? 'GRANTED' : 'DENIED'}</span>
                      )}
                    </div>
                    <div className="event-time">{formatTime(evt.timestamp)}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </>
      )}

      {allChains.length === 0 && !loading && (
        <div className="empty-state">
          <div className="icon">--</div>
          <div>Select a principal to view their auth chain</div>
        </div>
      )}

      <DetailPanel
        entry={selected}
        onClose={() => { setSelected(null); setSelectedExplanation('') }}
        onExplain={handleExplainEntry}
        explanation={selectedExplanation}
        explaining={selectedExplaining}
      />
    </div>
  )
}

// ===== Chat =====
function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEnd = useRef(null)

  const suggestions = [
    "How does the WIF token exchange work?",
    "Why are there 2 app registrations?",
    "How does ACL enforcement happen?",
    "What does AcquireAccessToken do?",
    "How does the principalSubject map between StreamAssist and AcquireAccessToken?",
  ]

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (msg) => {
    const text = msg || input
    if (!text.trim()) return
    setInput('')

    const newMessages = [...messages, { role: 'user', content: text }]
    setMessages(newMessages)
    setSending(true)

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: newMessages.map(m => ({ role: m.role, content: m.content }))
        })
      })
      const d = await res.json()
      setMessages([...newMessages, { role: 'model', content: d.response }])
    } catch (e) {
      setMessages([...newMessages, { role: 'model', content: 'Error: ' + e.message }])
    }
    setSending(false)
  }

  return (
    <div className="chat-container">
      {messages.length === 0 && (
        <div>
          <h3 style={{ color: '#f0f6fc', marginBottom: 12 }}>Ask about the WIF auth flow</h3>
          <div className="chat-suggestions">
            {suggestions.map(s => (
              <button className="suggestion-btn" key={s} onClick={() => sendMessage(s)}>{s}</button>
            ))}
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div className={`chat-msg ${m.role === 'user' ? 'user' : 'assistant'}`} key={i}>
            {m.role === 'user' ? m.content : <Markdown>{m.content}</Markdown>}
          </div>
        ))}
        {sending && (
          <div className="chat-msg assistant">
            <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
          </div>
        )}
        <div ref={messagesEnd} />
      </div>

      <div className="chat-input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !sending && sendMessage()}
          placeholder="Ask about WIF, STS, Discovery Engine, ACLs..."
          disabled={sending}
        />
        <button onClick={() => sendMessage()} disabled={sending || !input.trim()}>Send</button>
      </div>
    </div>
  )
}

// ===== App =====
function App() {
  const [page, setPage] = useState('dashboard')

  const pages = {
    dashboard: { label: 'Dashboard', icon: '~' },
    chain: { label: 'Chain Explorer', icon: '#' },
    chat: { label: 'Ask Gemini', icon: '>' },
  }

  return (
    <>
      <div className="sidebar">
        <div className="sidebar-title">
          WIF Auth Monitor
          <span>sharepoint-wif-agent</span>
        </div>
        {Object.entries(pages).map(([key, { label, icon }]) => (
          <div
            key={key}
            className={`nav-item ${page === key ? 'active' : ''}`}
            onClick={() => setPage(key)}
          >
            <span>{icon}</span> {label}
          </div>
        ))}
      </div>
      <div className="main-content">
        <div className="header">
          <h1>{pages[page].label}</h1>
          <div className="header-info">
            Project: sharepoint-wif-agent | WIF Pool: sp-wif-pool-v2
          </div>
        </div>
        <div className="page">
          {page === 'dashboard' && <Dashboard />}
          {page === 'chain' && <ChainExplorer />}
          {page === 'chat' && <Chat />}
        </div>
      </div>
    </>
  )
}

export default App
