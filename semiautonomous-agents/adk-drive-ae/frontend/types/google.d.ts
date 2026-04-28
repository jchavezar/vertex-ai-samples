// Minimal typing for the Google Identity Services token client we use.
// Loaded via <Script src="https://accounts.google.com/gsi/client" />.

export {};

declare global {
  interface Window {
    google?: {
      accounts: {
        oauth2: {
          initTokenClient(config: {
            client_id: string;
            scope: string;
            prompt?: string;
            callback: (response: { access_token?: string; error?: string; error_description?: string }) => void;
          }): { requestAccessToken: (overrideConfig?: { prompt?: string }) => void };
          revoke(token: string, done?: () => void): void;
        };
      };
    };
  }
}
