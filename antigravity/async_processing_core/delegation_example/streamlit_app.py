import streamlit as st
import asyncio
import os
import queue
import time
import threading
import uuid
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from agents import create_main_agent, DelegationTools

# Page Config
st.set_page_config(page_title="ADK Async Demo", page_icon="⚡")
st.title("⚡ ADK Async Delegation Demo")

# Sidebar
st.sidebar.markdown("""
### How it works
1. **Delegation**: Ask the agent to do "heavy work" (e.g. "analyze usage logs").
2. **Background**: The agent triggers a background pipeline and returns immediately.
3. **Notification**: When the pipeline finishes (approx 5s), you'll see a notification.
""")

class ThreadedDelegationTools(DelegationTools):
    def start_background_task(self, task_description: str) -> str:
        """
        Starts a background pipeline in a separate thread to survive Streamlit re-runs.
        Returns immediately telling the user the task has started.
        """
        task_id = str(uuid.uuid4())
        
        def run_sync():
            try:
                asyncio.run(self._run_background_pipeline(task_id, task_description))
            except Exception as e:
                print(f"Background thread error: {e}")
                
        t = threading.Thread(target=run_sync)
        t.start()

        return f"Task {task_id} started in background. I can continue chatting."

# Setup Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "params" not in st.session_state:
    # Setup infrastructure once
    session_service = InMemorySessionService()
    # Queue for background results to communicate to UI thread
    result_queue = queue.Queue()
    
    def on_background_complete(task_id, result):
        result_queue.put({"id": task_id, "result": result})
    
    # Use Threaded Tools
    delegation_tools = ThreadedDelegationTools(session_service, on_complete=on_background_complete)
    main_agent = create_main_agent(session_service, on_complete=on_background_complete, delegation_tools=delegation_tools)
    
    runner = Runner(
        agent=main_agent,
        session_service=session_service,
        app_name="main_app"
    )
    
    st.session_state.params = {
        "session_service": session_service,
        "runner": runner,
        "queue": result_queue,
        "session_id": "streamlit_user"
    }
    
    # Initialize session
    asyncio.run(session_service.create_session(app_name="main_app", session_id="streamlit_user", user_id="stream_user"))

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check for background results (Polling)
q = st.session_state.params["queue"]
item_processed = False
while not q.empty():
    item = q.get()
    item_processed = True
    st.toast(f"✅ Task {item['id'][:8]} Complete!", icon="🎉")
    
    # Decrement pending count
    if "pending_tasks" in st.session_state and st.session_state.pending_tasks > 0:
        st.session_state.pending_tasks -= 1

    # Add to history
    if "task_history" not in st.session_state:
        st.session_state.task_history = []
    st.session_state.task_history.append(item)
    
    # Add to Chat
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"✅ **Task {item['id'][:8]} Completed**\n\n{item['result']}"
    })

# Auto-rerun if tasks are pending OR if we just processed an item (to update chat)
if item_processed or ("pending_tasks" in st.session_state and st.session_state.pending_tasks > 0):
    time.sleep(2)  # Short delay to let user see toast if needed, though toast persists
    st.rerun()

# Sidebar: Task History
st.sidebar.markdown("### 📝 Completed Tasks")
if "task_history" in st.session_state and st.session_state.task_history:
    for task in reversed(st.session_state.task_history):
        with st.sidebar.expander(f"Task {task['id'][:8]}...", expanded=False):
            st.markdown(task['result'])
else:
    st.sidebar.caption("No tasks completed yet.")

# Input
if prompt := st.chat_input("Ask me something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run Agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        runner = st.session_state.params["runner"]
        session_id = st.session_state.params["session_id"]
        
        async def run_turn():
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            events = runner.run_async(session_id=session_id, new_message=content, user_id="stream_user")
            
            response_text = ""
            async for event in events:
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text
            return response_text

        try:
            full_response = asyncio.run(run_turn())
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Heuristic: If response indicates a background task started, track it.
            if "started" in full_response and "background task" in full_response:
                if "pending_tasks" not in st.session_state:
                    st.session_state.pending_tasks = 0
                st.session_state.pending_tasks += 1
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# Manual Refresh Button
if st.sidebar.button("Refresh Status"):
    st.rerun()
