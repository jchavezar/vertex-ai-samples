from k import *
import streamlit as st

st.title("Under construction...")
with st.sidebar:
    st.markdown(
        """
        ---
        Follow me on:

        

        ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)


        GitHub → [jchavezar](https://github.com/jchavezar)
        
        LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
        
        Medium -> [jchavezar](https://medium.com/@jchavezar)
        """
    )

button = f'''<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  agent-id="{dialogflow_id}"
  language-code="en">
  <df-messenger-chat-bubble
   chat-title="infobot"
   bot-writing-text="..."
   placeholder-text="Tell me something!">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {{
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }}
</style>'''

st.components.v1.html(button, height=700, width=350)

st.markdown(
    """
    <style>
        iframe[width="350"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

