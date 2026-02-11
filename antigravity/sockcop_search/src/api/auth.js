import axios from 'axios';
import { CONFIG } from './config';

const STS_URL = 'https://sts.googleapis.com/v1/token';

export const getWifLoginUrl = () => {
  const redirect = window.location.origin + '/'; // Match Azure's trailing slash
  console.log('Initiating WIF Login with Redirect:', redirect);

  return `${CONFIG.ISSUER.replace('/v2.0', '')}/oauth2/v2.0/authorize?client_id=${CONFIG.MS_APP_ID}&response_type=id_token&redirect_uri=${encodeURIComponent(redirect)}&scope=openid%20profile%20email&response_mode=fragment&nonce=${Math.random().toString(36).substring(7)}`;
};

export const exchangeForGoogleToken = async (idToken) => {
  const audience = `//iam.googleapis.com/locations/global/workforcePools/${CONFIG.WIF_POOL}/providers/${CONFIG.WIF_PROVIDER}`;

  const payload = {
    audience,
    grantType: 'urn:ietf:params:oauth:grant-type:token-exchange',
    requestedTokenType: 'urn:ietf:params:oauth:token-type:access_token',
    scope: 'https://www.googleapis.com/auth/cloud-platform',
    subjectToken: idToken,
    subjectTokenType: 'urn:ietf:params:oauth:token-type:id_token',
  };

  try {
    const resp = await axios.post(STS_URL, payload);
    return resp.data;
  } catch (err) {
    console.error('STS Exchange Failed:', err.response?.data || err.message);
    throw err;
  }
};

export const getSharePointAuthUrl = () => {
  const redirect = window.location.origin + '/';
  return `https://login.microsoftonline.com/${CONFIG.TENANT_ID}/oauth2/v2.0/authorize?client_id=${CONFIG.SP_APP_ID}&response_type=code&redirect_uri=${encodeURIComponent(redirect)}&scope=offline_access%20Sites.Read.All%20User.Read&state=sp_auth`;
};

export const acquireAndStoreRefreshToken = async (googleToken, authCode) => {
  const fullRedirectUri = window.location.href;
  // Restore the /collections/default_collection segment as verified in documentation
  const url = `/google-api/v1alpha/projects/${CONFIG.PROJECT_NUMBER}/locations/${CONFIG.LOCATION}/collections/default_collection/dataConnector:acquireAndStoreRefreshToken`;

  console.log('[AUTH DEBUG] acquireAndStoreRefreshToken URL:', url);

  return axios.post(url, {
    fullRedirectUri: fullRedirectUri,
    scopes: ["offline_access", "Sites.Read.All", "User.Read"]
  }, {
    headers: {
      Authorization: `Bearer ${googleToken}`
    }
  });
};

export const checkSharePointStatus = async (googleToken) => {
  // Bypass legacy Check for Gemini Enterprise flow
  console.log('[AUTH DEBUG] Bypassing SharePoint Status Check for Gemini Enterprise');
  return true;
};

