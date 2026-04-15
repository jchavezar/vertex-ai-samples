declare namespace google {
  namespace accounts {
    namespace oauth2 {
      interface CodeClient {
        requestCode(): void;
      }
      interface CodeClientConfig {
        client_id: string;
        scope: string;
        ux_mode?: 'popup' | 'redirect';
        callback: (response: CodeResponse) => void;
        error_callback?: (error: { type: string; message?: string }) => void;
      }
      interface CodeResponse {
        code: string;
        scope: string;
        error?: string;
        error_description?: string;
      }
      function initCodeClient(config: CodeClientConfig): CodeClient;
    }
  }
}
