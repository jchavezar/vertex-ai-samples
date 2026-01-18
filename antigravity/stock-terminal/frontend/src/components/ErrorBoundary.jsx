import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div style={{
          padding: '20px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
          color: '#333',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          gap: '12px',
          height: '100%',
          overflow: 'auto',
          backgroundColor: '#fff'
        }}>
          <h2 style={{ color: '#dc3545', margin: 0 }}>Something went wrong.</h2>
          <p style={{ margin: 0, color: '#666' }}>The application encountered an unexpected error.</p>

          <div style={{
            marginTop: '10px',
            padding: '12px',
            background: '#f8d7da',
            borderRadius: '6px',
            border: '1px solid #f5c6cb',
            width: '100%',
            maxWidth: '800px',
            boxSizing: 'border-box'
          }}>
            <details style={{ cursor: 'pointer' }}>
              <summary style={{ fontWeight: 'bold', color: '#721c24' }}>View Error Details</summary>
              <pre style={{
                marginTop: '10px',
                whiteSpace: 'pre-wrap',
                fontSize: '12px',
                color: '#333',
                overflowX: 'auto'
              }}>
                {this.state.error && this.state.error.toString()}
                {'\n'}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          </div>

          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              background: '#004b87',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            Reload Application
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
