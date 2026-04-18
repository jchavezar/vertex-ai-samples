import React, { useState } from 'react'
import './App.css'

function App() {
  const [showBanner, setShowBanner] = useState(true);
  return (
    <div className="app-container">
      {/* Top Bar / Audience Selector */}
      <div className="top-bar">
        <div className="logo-section">
          <img src="/logo_cchs.svg" alt="Caja Los Andes Logo" className="corporate-logo" />
        </div>
        <div className="nav-links">
          <span>Trabajadores</span>
          <span>Somos Andes</span>
          <span>Pensionados</span>
          <span>Empresas</span>
          <span>Ex afiliados</span>
        </div>
      </div>

      {/* Sub Header Nav */}
      <header className="main-header">
        <nav className="main-nav">
          <a href="#" className="active"><span className="home-icon">🏠</span> Inicio</a>
          <a href="#">Licencias Médicas</a>
          <a href="#">Créditos</a>
          <a href="#">Seguros</a>
          <a href="#">Ahorro</a>
          <a href="#">Turismo</a>
          <a href="#">Beneficios</a>
          <a href="#">Apoyo Social</a>
        </nav>
        <div className="actions">
          <button className="ingresar-btn">Ingresar</button>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span>Inicio</span> | <span>Centro de Ayuda</span> | <span>Accede a tu Sucursal Virtual</span>
      </div>

      {/* Main Content: Sucursal Virtual */}
      <main className="main-content">
        <div className="text-section">
          <div className="back-arrow">⬅️</div>
          <h1>Accede a tu Sucursal Virtual</h1>
          <p>
            Ahórrate las filas realizando tus trámites en línea. Podrás gestionar la mayoría
            de los productos, servicios y beneficios de Caja Los Andes a través de tu
            cuenta. Solo necesitas tu usuario y clave.
          </p>
        </div>
        <div className="visual-section">
          <div className="circle-img-container">
            <img 
              src="/caja_los_andes_mockup_image_1776471826515.png" 
              alt="Caja Los Andes Mockup" 
              className="circle-img" 
            />
          </div>
          <div className="wavy-line"></div>
        </div>
      </main>

      {/* Bottom Icons Section */}
      <section className="bottom-icons">
        <div className="icon-box">
          <span className="material-icons">directions_car</span>
          <span>Cotiza tu seguro</span>
        </div>
        <div className="icon-box">
          <span className="material-icons">medical_services</span>
          <span>Gestiona tu licencia</span>
        </div>
        <div className="icon-box">
          <span className="material-icons">paid</span>
          <span>Paga tu crédito</span>
        </div>
        <div className="icon-box">
          <span className="material-icons">corporate_fare</span>
          <span>Agenda tu visita</span>
        </div>
        <div className="icon-box">
          <span className="material-icons">check_circle</span>
          <span>Revisa tus beneficios</span>
        </div>
      </section>

      {/* Cookie Banner Mock */}
      {showBanner && (
        <div className="cookie-banner">
        <span>Al aceptar todas las cookies, nos ayudas a que tu experiencia en nuestro sitio web sea mejor...</span>
        <div className="banner-buttons">
          <button className="accept-btn" onClick={() => setShowBanner(false)}>Aceptar</button>
          <button className="reject-btn">Rechazar</button>
          <button className="config-btn">Configuración</button>
        </div>
        <span className="close-banner">✖️</span>
      </div>
      )}

      {/* 2040 Futuristic Agentic AI Hub */}
      <div className="futuristic-ai-hub">
        <div className="hub-header">
          <div className="pulse-indicator"></div>
          <span>Andes AI - Quantum Hub</span>
        </div>
        <div className="hub-body">
          <div className="message incoming">
            ¡Hola! Soy tu asistente de Caja Los Andes del futuro. ¿En qué beneficio puedo ayudarte hoy?
          </div>
        </div>
        <div className="hub-footer">
          <input type="text" placeholder="Habla o escribe en español..." />
          <button className="voice-btn">🎤</button>
          <button className="send-btn">🚀</button>
        </div>
      </div>
    </div>
  )
}

export default App
