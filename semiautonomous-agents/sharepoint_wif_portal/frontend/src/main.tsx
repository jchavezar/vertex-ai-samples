import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { PublicClientApplication } from '@azure/msal-browser'
import { MsalProvider, useMsal, useIsAuthenticated } from '@azure/msal-react'
import { msalConfig, loginRequest } from './authConfig'
import './index.css'
import App from './App'
import AgentPanel from './AgentPanel'
import { useEffect, useState } from 'react'

// Initialize MSAL instance
const msalInstance = new PublicClientApplication(msalConfig)

// Wrapper to provide auth token to AgentPanel
function AppWithAgent() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [accessToken, setAccessToken] = useState<string | undefined>();

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = { ...loginRequest, account: accounts[0] };
      instance.acquireTokenSilent(request)
        .then(response => setAccessToken(response.accessToken))
        .catch(() => setAccessToken(undefined));
    } else {
      setAccessToken(undefined);
    }
  }, [isAuthenticated, accounts, instance]);

  return (
    <>
      <App />
      <AgentPanel accessToken={accessToken} />
    </>
  );
}

// Handle redirect promise (for popup/redirect flows)
msalInstance.initialize().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <AppWithAgent />
      </MsalProvider>
    </StrictMode>,
  )
})
