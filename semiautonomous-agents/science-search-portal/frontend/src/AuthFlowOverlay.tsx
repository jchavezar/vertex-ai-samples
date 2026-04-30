import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, X, RotateCcw, Shield } from 'lucide-react';

interface Source {
  title: string;
  url: string;
  snippet: string;
}

export interface ConnectorInfo {
  sites: string[];
  scopes: string[];
  connector_app_client_id: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  username: string;
  jwtIat: Date | null;
  jwtExp: Date | null;
  tenant?: string;
  sources: Source[];
  connectorInfo: ConnectorInfo | null;
  poolId?: string;
  providerId?: string;
}

interface PhaseConfig {
  title: string;
  details: React.ReactNode;
}

function formatTime(d: Date | null): string {
  if (!d) return '—';
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatCountdown(d: Date | null): string {
  if (!d) return '—';
  const ms = d.getTime() - Date.now();
  if (ms <= 0) return 'expired';
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return m > 0 ? `${m}m ${r}s` : `${r}s`;
}

function shortTenant(t?: string): string {
  if (!t) return 'de46a3fd-…';
  if (t.length <= 12) return t;
  return `${t.slice(0, 8)}-…`;
}

export default function AuthFlowOverlay({
  isOpen,
  onClose,
  username,
  jwtIat,
  jwtExp,
  tenant,
  sources,
  connectorInfo,
  poolId = 'sp-wif-pool-v2',
  providerId = 'entra-provider',
}: Props) {
  // animationKey changes whenever we re-trigger the stagger animation
  const [animationKey, setAnimationKey] = useState(0);
  // 1Hz tick to keep the JWT countdown fresh while the modal is open
  const [, setTick] = useState(0);

  // Re-run the stagger every time the modal opens
  useEffect(() => {
    if (isOpen) setAnimationKey((k) => k + 1);
  }, [isOpen]);

  // Tick once per second while open so the countdown updates live
  useEffect(() => {
    if (!isOpen) return;
    const id = setInterval(() => setTick((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, [isOpen]);

  // ESC closes
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const sites = connectorInfo?.sites ?? [];
  const scopes = connectorInfo?.scopes ?? [];
  const connectorAppId = connectorInfo?.connector_app_client_id ?? '22c127d8-f3e5-4bbe-8b06-c37da3159068';
  const sourceCount = sources?.length ?? 0;

  const phases: PhaseConfig[] = useMemo(
    () => [
      {
        title: 'Microsoft Entra ID',
        details: (
          <>
            <div><span className="kv-key">user</span> {username || 'unknown@user'}</div>
            <div>
              <span className="kv-key">jwt</span> issued {formatTime(jwtIat)} · expires{' '}
              {formatTime(jwtExp)} <span className="kv-aside">({formatCountdown(jwtExp)})</span>
            </div>
            <div><span className="kv-key">tenant</span> {shortTenant(tenant)}</div>
          </>
        ),
      },
      {
        title: 'STS Token Exchange (WIF)',
        details: (
          <>
            <div><span className="kv-key">pool</span> {poolId}</div>
            <div><span className="kv-key">provider</span> {providerId}</div>
            <div><span className="kv-key">grant</span> token-exchange → cloud-platform</div>
            <div><span className="kv-key">latency</span> ~300ms</div>
          </>
        ),
      },
      {
        title: 'Discovery Engine',
        details: (
          <>
            <div><span className="kv-key">engine</span> gemini-enterprise</div>
            <div><span className="kv-key">scope</span> 5 SharePoint datastores (file/page/comment/event/attachment)</div>
            <div><span className="kv-key">caller</span> your WIF identity (principalSet://...)</div>
          </>
        ),
      },
      {
        title: 'SharePoint Connector',
        details: (
          <>
            <div><span className="kv-key">app</span> {connectorAppId.slice(0, 8)}-…</div>
            <div><span className="kv-key">grant</span> OAuth refresh token bound to your identity</div>
            <div>
              <span className="kv-key">scopes</span>{' '}
              {(scopes.length > 0
                ? scopes
                : ['Sites.Read.All', 'Files.Read.All', 'Sites.Search.All', 'AllSites.Read']
              ).join(', ')}
            </div>
          </>
        ),
      },
      {
        title: 'SharePoint (per-user ACL)',
        details: (
          <>
            <div>
              <span className="kv-key">sites</span>{' '}
              {connectorInfo === null ? <span className="kv-aside">loading…</span> : null}
            </div>
            <ul className="auth-flow-site-list">
              {(sites.length > 0
                ? sites
                : ['/', '/sites/FinancialDocument', '/sites/Centura', '/sites/allcompany']
              ).map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
            <div className="kv-aside">enforced by admin_filter.Site on the connector</div>
          </>
        ),
      },
      {
        title: 'Grounded Response',
        details: (
          <>
            <div>
              <span className="kv-key">answer</span> composed with{' '}
              <strong>{sourceCount > 0 ? sourceCount : '—'}</strong>{' '}
              citation{sourceCount === 1 ? '' : 's'}
            </div>
            <div className="kv-aside">
              {sourceCount > 0
                ? 'Each [n] in the answer maps to one of these sources.'
                : 'Ask a question to populate citations.'}
            </div>
          </>
        ),
      },
    ],
    [
      username,
      jwtIat,
      jwtExp,
      tenant,
      poolId,
      providerId,
      sites,
      scopes,
      connectorAppId,
      sourceCount,
      connectorInfo,
    ]
  );

  if (!isOpen) return null;

  return (
    <div
      className="auth-flow-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-label="Authentication flow"
    >
      <div className="auth-flow-modal">
        <div className="auth-flow-header">
          <div className="auth-flow-title">
            <Shield size={18} />
            <span>Auth Flow · per-user ACL chain</span>
          </div>
          <button
            className="auth-flow-close"
            onClick={onClose}
            aria-label="Close auth flow overlay"
            title="Close (Esc)"
          >
            <X size={16} />
          </button>
        </div>

        <div className="auth-flow-body">
          <ol className="auth-flow-list" key={animationKey}>
            {phases.map((p, i) => (
              <li
                key={i}
                className="auth-flow-phase"
                data-verified="true"
                style={{ animationDelay: `${i * 0.2}s` }}
              >
                <div className="auth-flow-phase-rail">
                  <div className="auth-flow-phase-number">{i + 1}</div>
                  {i < phases.length - 1 && <div className="auth-flow-phase-line" />}
                </div>
                <div className="auth-flow-phase-body">
                  <div className="auth-flow-phase-head">
                    <span className="auth-flow-phase-title">{p.title}</span>
                    <CheckCircle2 size={14} className="auth-flow-check" />
                  </div>
                  <div className="auth-flow-phase-details">{p.details}</div>
                </div>
              </li>
            ))}
          </ol>
        </div>

        <div className="auth-flow-footer">
          <span className="auth-flow-hint">
            <kbd>Esc</kbd> to close · <kbd>Shift</kbd>+<kbd>S</kbd> to summon
          </span>
          <button
            className="auth-flow-replay"
            onClick={() => setAnimationKey((k) => k + 1)}
          >
            <RotateCcw size={12} />
            Replay flow
          </button>
        </div>
      </div>
    </div>
  );
}
