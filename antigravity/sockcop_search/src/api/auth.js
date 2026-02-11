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

