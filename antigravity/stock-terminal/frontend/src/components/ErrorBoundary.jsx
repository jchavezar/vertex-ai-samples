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
        <div style={{ padding: '10px', color: '#dc3545', fontSize: '12px', border: '1px solid #dc3545', borderRadius: '4px', background: '#ffe6e6' }}>
          <strong>Visualization Error</strong>
          <p style={{ margin: '4px 0 0' }}>Something went wrong displaying the reasoning chain.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
