import streamlit as st
import subprocess
import sys
import re
import os

# Set page configuration
st.set_page_config(
    page_title="Vertex AI Search Agent Comparison",
    layout="wide",
)

st.title("Vertex AI Search Agent Comparison")
st.markdown("""
Compare the behavior of two Vertex AI Search agents:
- **Standard ADK Tool**: Uses `VertexAiSearchTool`
- **Custom Client**: Uses `discoveryengine_v1` client with custom logic
""")

# Input Query
query = st.text_input("Enter your query:", "how was the revenue for factset?")

# Paths to agents
ADK_AGENT_PATH = "agent_adk_tool.py"
CUSTOM_AGENT_PATH = "agent_custom_client.py"
PYTHON_EXEC = sys.executable  # Use the same python environment

def run_agent(script_path, query_text):
    """Runs the agent script and returns (response_text, full_log)"""
    try:
        # Run script with query as argument
        result = subprocess.run(
            [PYTHON_EXEC, script_path, query_text],
            capture_output=True,
            text=True,
            timeout=60 # Timeout after 60 seconds
        )
        
        full_log = result.stdout + "\n" + result.stderr
        
        # Parse for "Agent: ..." response
        response_match = re.search(r"^Agent: (.*)", result.stdout, re.MULTILINE)
        response_text = response_match.group(1) if response_match else "No 'Agent:' response found."
        
        return response_text, full_log
        
    except subprocess.TimeoutExpired:
        return "Error: Timeout", "Agent execution timed out."
    except Exception as e:
        return f"Error: {e}", str(e)

if st.button("Compare Agents"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Standard ADK Tool")
        with st.spinner("Running ADK Agent..."):
            adk_resp, adk_log = run_agent(ADK_AGENT_PATH, query)
        
        st.subheader("Response")
        st.info(adk_resp)
        
        with st.expander("Debug Logs"):
            st.code(adk_log, language="text")

    with col2:
        st.header("Custom Client")
        with st.spinner("Running Custom Client Agent..."):
            custom_resp, custom_log = run_agent(CUSTOM_AGENT_PATH, query)
        
        st.subheader("Response")
        st.success(custom_resp)
        
        with st.expander("Debug Logs"):
            st.code(custom_log, language="text")
