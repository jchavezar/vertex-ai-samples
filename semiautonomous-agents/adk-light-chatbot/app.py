"""
Google ADK Chatbot - Streamlit Light Theme UI
A clean, elegant, and responsive graphical interface for Google Agent Development Kit (ADK)
powered by Gemini (Gemini 2.5 Flash / Gemini 3 Flash Preview).
"""

import asyncio
import uuid
import streamlit as st
from agent_engine import (
    ADKChatbotManager,
    SUPPORTED_MODELS,
    DEFAULT_MODEL,
    DEFAULT_INSTRUCTION
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Google ADK Chatbot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Light Theme CSS (Google Material Design Inspired)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Google Material Light Aesthetic */
    :root {
        --primary-blue: #1a73e8;
        --primary-hover: #1557b0;
        --bg-white: #ffffff;
        --bg-surface: #f8fafd;
        --bg-user-bubble: #e8f0fe;
        --text-main: #202124;
        --text-muted: #5f6368;
        --border-subtle: #dadce0;
        --shadow-card: 0 1px 3px rgba(60,64,67,0.12), 0 1px 2px rgba(60,64,67,0.24);
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 920px;
    }

    /* Top Header Banner */
    .adk-header {
        background: linear-gradient(135deg, #ffffff 0%, #f1f6fd 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-card);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .adk-title-box h1 {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-main);
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .adk-title-box p {
        font-size: 0.92rem;
        color: var(--text-muted);
        margin: 0;
    }

    .adk-badge-online {
        background-color: #e6f4ea;
        color: #137333;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid #ceead6;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .adk-badge-online::before {
        content: "";
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34a853;
        display: inline-block;
    }

    /* Suggestion Chips */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafd;
        border-right: 1px solid var(--border-subtle);
    }

    /* Grounding sources box */
    .grounding-box {
        background-color: #f1f3f4;
        border-left: 4px solid var(--primary-blue);
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 0.85rem;
    }

    .grounding-box a {
        color: var(--primary-blue);
        text-decoration: none;
        font-weight: 500;
    }
    .grounding-box a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "manager" not in st.session_state:
    st.session_state.manager = ADKChatbotManager(
        model=DEFAULT_MODEL,
        instruction=DEFAULT_INSTRUCTION,
        enable_search=False
    )

# ---------------------------------------------------------
# Sidebar Controls & Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuración del Agente")
    st.caption("Google ADK (Agent Development Kit) con Gemini")

    # 1. Model Selector
    model_options = list(SUPPORTED_MODELS.keys())
    model_labels = {
        k: f"{SUPPORTED_MODELS[k]['name']} ({SUPPORTED_MODELS[k]['badge']})"
        for k in model_options
    }
    
    selected_model = st.selectbox(
        "🤖 Modelo Gemini",
        options=model_options,
        index=0,
        format_func=lambda k: model_labels[k],
        help="Modelos optimizados y autorizados de la familia Gemini."
    )
    
    st.info(SUPPORTED_MODELS[selected_model]["description"], icon="ℹ️")

    # 2. Google Search Grounding Tool
    st.markdown("---")
    st.markdown("### 🛠️ Herramientas ADK")
    enable_search = st.toggle(
        "🌐 Grounding con Google Search",
        value=False,
        help="Permite al agente consultar la web en tiempo real mediante la herramienta oficial google_search de ADK."
    )

    # 3. System Persona / Instructions
    st.markdown("---")
    st.markdown("### 🧠 Personalidad del Asistente")
    
    preset_personas = {
        "Asistente General": DEFAULT_INSTRUCTION,
        "Experto en Código Python": "Eres un ingeniero de software senior experto en Python, Google ADK y Vertex AI. Proporciona código limpio, tipado, modular y bien documentado.",
        "Analista de Datos": "Eres un consultor analítico de datos senior. Explica hallazgos cuantitativos con rigor, sugiere visualizaciones y sintetiza información clave.",
        "Tutor Didáctico": "Eres un profesor universitario paciente y amigable. Explica conceptos paso a paso con analogías sencillas y preguntas de verificación."
    }
    
    selected_preset = st.selectbox(
        "Plantilla rápida",
        options=list(preset_personas.keys()),
        index=0
    )
    
    system_instruction = st.text_area(
        "Instrucción del Sistema (Prompt)",
        value=preset_personas[selected_preset],
        height=110,
        help="Directiva que guía el comportamiento y tono del agente ADK."
    )

    # Update Manager if configuration changed
    st.session_state.manager.update_configuration(
        model=selected_model,
        instruction=system_instruction,
        enable_search=enable_search
    )

    # 4. Session Controls
    st.markdown("---")
    st.markdown("### 💬 Control de Sesión")
    st.caption(f"**Session ID:** `{st.session_state.session_id}`")
    st.caption(f"**Mensajes en memoria:** {len(st.session_state.messages)}")
    
    if st.button("🧹 Nueva Conversación", use_container_width=True, type="secondary"):
        st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.manager._initialize_agent()
        st.rerun()

# ---------------------------------------------------------
# Main UI Header
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="adk-header">
        <div class="adk-title-box">
            <h1>✨ Google ADK Chatbot</h1>
            <p>Agente conversacional impulsado por <strong>Google ADK 2.1.0</strong> y <strong>{SUPPORTED_MODELS[selected_model]['name']}</strong></p>
        </div>
        <div>
            <span class="adk-badge-online">ADK InMemoryRunner Activo</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Render Existing Chat History
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])
        
        # Display saved grounding citations if present
        if msg.get("grounding"):
            g = msg["grounding"]
            sources = g.get("sources", [])
            if sources:
                with st.expander("🌐 Fuentes consultadas en la web", expanded=False):
                    for src in sources:
                        st.markdown(f"- [{src.get('title', 'Fuente')}]({src.get('uri', '#')})")

# ---------------------------------------------------------
# Welcome State & Quick Suggestions (When chat is empty)
# ---------------------------------------------------------
if len(st.session_state.messages) == 0:
    st.markdown("##### 💡 Sugerencias para comenzar:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 ¿Cómo funciona Google ADK y cuáles son sus ventajas?", use_container_width=True):
            st.session_state.pending_prompt = "¿Cómo funciona Google ADK (Agent Development Kit) y cuáles son sus ventajas para crear agentes inteligentes?"
            st.rerun()
        if st.button("⚡ Escribe un ejemplo de Agente en Python con ADK", use_container_width=True):
            st.session_state.pending_prompt = "Escribe un ejemplo de código en Python que use Google ADK (Agent, InMemoryRunner) para crear un asistente con streaming."
            st.rerun()

    with col2:
        if st.button("🌐 ¿Cuáles son las capacidades de Gemini 2.5 Flash?", use_container_width=True):
            st.session_state.pending_prompt = "¿Cuáles son las principales capacidades y ventajas de Gemini 2.5 Flash en términos de velocidad y razonamiento?"
            st.rerun()
        if st.button("📊 Explica el patrón de memoria y sesiones en ADK", use_container_width=True):
            st.session_state.pending_prompt = "Explica cómo gestiona Google ADK las sesiones conversacionales con InMemorySessionService."
            st.rerun()

# Check if a suggestion was clicked
user_query = None
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    user_query = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# Chat Input Bar
prompt_input = st.chat_input("Escribe tu mensaje para el agente Google ADK...")
if prompt_input:
    user_query = prompt_input

# ---------------------------------------------------------
# Process User Message & Stream ADK Agent Response
# ---------------------------------------------------------
if user_query:
    # 1. Append & render User Message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # 2. Render Assistant Message Container & Stream response
    with st.chat_message("assistant", avatar="✨"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()
        
        full_response = ""
        grounding_data = {}
        tool_invocations = []

        async def run_adk_stream():
            nonlocal full_response, grounding_data, tool_invocations
            
            async for event in st.session_state.manager.stream_turn(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                user_message=user_query
            ):
                ev_type = event.get("type")
                
                if ev_type == "text":
                    chunk = event.get("content", "")
                    full_response += chunk
                    response_placeholder.markdown(full_response + " ▌")
                
                elif ev_type == "tool_call":
                    tool_name = event.get("name")
                    tool_invocations.append(tool_name)
                    status_placeholder.info(f"🛠️ El agente está ejecutando la herramienta: `{tool_name}`...", icon="🔍")
                
                elif ev_type == "grounding":
                    grounding_data = event
                
                elif ev_type == "error":
                    st.error(event.get("message", "Error inesperado."))

        # Run the async ADK generator in the Streamlit loop
        asyncio.run(run_adk_stream())
        
        # Clear temporary tool status indicator
        status_placeholder.empty()
        
        # Render final formatted response
        response_placeholder.markdown(full_response if full_response else "_No se recibió respuesta del modelo._")
        
        # Render citations if grounding was triggered
        if grounding_data and grounding_data.get("sources"):
            sources = grounding_data.get("sources", [])
            with st.expander("🌐 Fuentes consultadas en la web", expanded=False):
                for src in sources:
                    st.markdown(f"- [{src.get('title', 'Fuente')}]({src.get('uri', '#')})")

        # Save assistant message to session state history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "grounding": grounding_data if grounding_data else None
        })
