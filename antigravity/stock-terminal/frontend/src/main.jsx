import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { LiveAPIProvider } from './contexts/LiveAPIContext';

import ErrorBoundary from './components/ErrorBoundary';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LiveAPIProvider>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </LiveAPIProvider>
  </React.StrictMode>,
)
