import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { LiveAPIProvider } from './contexts/LiveAPIContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LiveAPIProvider>
      <App />
    </LiveAPIProvider>
  </React.StrictMode>,
)
